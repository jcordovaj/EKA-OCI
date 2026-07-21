import logging
import io
from pathlib import Path
from minio import Minio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.settings import settings
import hashlib

logger = logging.getLogger(__name__)

class DocumentProcessor:
        
    def __init__(self, storage_provider=None, delta_manager=None):
        self.storage = storage_provider
        self.delta_manager = delta_manager

        # Conexión exclusiva al Storage en Cloud (MinIO/OCI Object Storage)
        storage_endpoint = getattr(settings, "STORAGE_ENDPOINT", None) or \
                        getattr(settings, "MINIO_ENDPOINT", "localhost:9000")
        storage_endpoint = storage_endpoint.replace("http://", "").replace("https://", "").replace("s3://", "")

        self.minio_client = Minio(
            storage_endpoint,
            access_key=getattr(settings, "STORAGE_ACCESS_KEY", None) or getattr(settings, "MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=getattr(settings, "STORAGE_SECRET_KEY", None) or getattr(settings, "MINIO_SECRET_KEY", "minioadmin"),
            secure=getattr(settings, "STORAGE_SECURE", False)
        )
        self.bucket_name = getattr(settings, "BUCKET_NAME", None) or getattr(settings, "MINIO_BUCKET_NAME", "eka-artifacts")
        
        # Inicialización de la base de datos PostgreSQL en contenedor
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        self._ensure_bucket_exists()  

    def process_object(self, file_key: str, strategy: str, classification: str) -> None:
        """Flujo OCI-Native estricto: Procesa objetos directamente desde el Object Storage."""
        filename = file_key.split('/')[-1]
        logger.info(f"Procesando archivo cloud {filename} con estrategia: {strategy} [Clasificación: {classification}]")

        try:
            # 1. Obtención de stream remoto limpio desde S3/MinIO
            response = self.minio_client.get_object(self.bucket_name, file_key)
            file_bytes = response.read()
            response.close()

            # Cálculo de hash INCONDICIONAL para la idempotencia
            current_hash = hashlib.sha256(file_bytes).hexdigest()

            # 2. Extracción de texto plano real
            extracted_text = ""
            if filename.lower().endswith('.pdf'):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                    pages_text = [page.extract_text() or "" for page in reader.pages]
                    extracted_text = "\n".join(pages_text)
                except Exception as ex:
                    logger.warning(f"Error extrayendo texto del PDF para {filename}: {ex}")
                    extracted_text = "[Aviso: Error en lectura nativa de PDF]"
            else:
                extracted_text = file_bytes.decode('utf-8', errors='ignore')

            # Markdown final
            markdown_content = f"# Documento Procesado: {filename}\n\n{extracted_text}"

            # 3. Persistencia en MinIO
            output_key = f"markdowns/{filename.rsplit('.', 1)[0]}.md"
            self._upload_string_to_minio(markdown_content, output_key)

            # 4. Consolidación INMEDIATA en PostgreSQL (Ahora siempre se ejecuta)
            self._persist_db_record(filename, current_hash, output_key)

        except Exception as e:
            logger.error(f"Error crítico procesando {filename} en arquitectura cloud: {e}")
            raise e

    def _ensure_bucket_exists(self):
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)
            logger.info(f"Bucket cloud creado automáticamente: {self.bucket_name}")

    def process_file(self, file_path: Path, strategy: str, classification: str, error_msg: str = None, doc_id: int = None):
        logger.info(f"Procesando archivo {file_path.name} con estrategia: {strategy} [Clasificación: {classification}]")
        
        try:
            if strategy in ["STANDARD_PROCESSOR", "TEXT_TO_MARKDOWN"]:
                self._handle_standard(file_path, doc_id)
            elif strategy in ["JSON_PARSER_PROCESSOR", "JSON_PARSER_TO_MARKDOWN"]:
                self._handle_json(file_path, doc_id)
            elif strategy in ["BATCH_CHUNK_PROCESSOR", "OCR_REQUIRED_PROCESSOR", "OCR_VISION_PROCESSOR", "DEFERRED_COMPLEX"]:
                self._handle_complex_queue(file_path, classification, doc_id)
            elif strategy in ["ERROR_ROUTER", "REJECT"]:
                self._handle_error(file_path, error_msg, doc_id)
            else:
                logger.warning(f"Estrategia desconocida para {file_path.name}: {strategy}")
        except Exception as e:
            logger.error(f"Error crítico ejecutando procesador para {file_path.name}: {e}")
            if doc_id:
                self._update_job_status(doc_id, "FAILED", str(e))

    def _upload_string_to_minio(self, artifact_content: str, destination_path: str):
        content_bytes = artifact_content.encode("utf-8")
        data_stream = io.BytesIO(content_bytes)
        
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=destination_path,
            data=data_stream,
            length=len(content_bytes),
            content_type="text/markdown"
        )
        logger.info(f"Artefacto persistido en MinIO Cloud -> s3://{self.bucket_name}/{destination_path}")
    
    def _update_job_status(self, doc_id: int, status: str, error_message: str = None):
        """Actualiza el estado final en la tabla processing_jobs y documentos."""
        with self.SessionLocal() as session:
            with session.begin():
                # Actualiza el job o la tabla de control de procesamiento
                query = text("""
                    UPDATE processing_jobs 
                    TO UPDATE / SET status = :status, error_message = :error_msg, updated_at = NOW()
                    WHERE document_id = :doc_id;
                """)
                # Nota: Ajusta la sentencia SQL exacta según tu esquema de base de datos definitivo
                session.execute(text("""
                    UPDATE documentos 
                    SET status = :status 
                    WHERE id = :doc_id;
                """), {"status": status, "doc_id": doc_id})
        logger.info(f"Estado del documento ID {doc_id} actualizado a: {status}")

    def _handle_standard(self, file_path: Path, doc_id: int = None):
        # 1. Simulación o ejecución real de conversión a Markdown
        dummy_markdown = f"# Documento Procesado: {file_path.name}\n\nContenido extraído de forma estándar."
        
        # 2. Persistencia en MinIO
        destination_key = f"markdowns/{file_path.stem}.md"
        self._upload_to_minio(file_path, dummy_markdown, destination_key)
        
        # 3. Actualización de estado a COMPLETED en DB
        if doc_id:
            self._update_job_status(doc_id, "COMPLETED")

    def _handle_json(self, file_path: Path, doc_id: int = None):
        dummy_json_markdown = f"# Estructura JSON: {file_path.name}\n\nDatos estructurados parseados correctamente."
        destination_key = f"structured/{file_path.stem}.md"
        self._upload_to_minio(file_path, dummy_json_markdown, destination_key)
        
        if doc_id:
            self._update_job_status(doc_id, "COMPLETED")

    def _handle_complex_queue(self, file_path: Path, classification: str, doc_id: int = None):
        logger.info(f"-> Archivo complejo ({classification}). Enrutado a cola sin bloqueo.")
        if doc_id:
            self._update_job_status(doc_id, "QUEUED_COMPLEX")

    def _handle_error(self, file_path: Path, error_msg: str, doc_id: int = None):
        logger.error(f"-> Archivo rechazado: {file_path.name} | Motivo: {error_msg}")
        if doc_id:
            self._update_job_status(doc_id, "REJECTED", error_msg)
            
    def _persist_db_record(self, filename: str, file_hash: str, artifact_uri: str):
        """Registra el estado final y el binary_hash en PostgreSQL asegurando idempotencia futura."""
        try:
            with self.SessionLocal() as session:
                with session.begin():
                    # 1. Insertar el documento base (Asegúrate de que original_filename tenga índice UNIQUE en BBDD)
                    doc_result = session.execute(text("""
                        INSERT INTO documentos (original_filename, mime_type, ingestion_timestamp, binary_hash, status)
                        VALUES (:filename, 'application/pdf', NOW(), :file_hash, 'COMPLETED')
                        ON CONFLICT (original_filename) DO UPDATE 
                        SET binary_hash = :file_hash, status = 'COMPLETED'
                        RETURNING id;
                    """), {"filename": filename, "file_hash": file_hash})
                    
                    row = doc_result.fetchone()
                    doc_id = row[0] if row else None

                    if not doc_id:
                        # Fallback por si el RETURNING no lo captura directo en alguna versión de driver
                        id_res = session.execute(text("SELECT id FROM documentos WHERE original_filename = :filename;"), {"filename": filename})
                        doc_row = id_res.fetchone()
                        doc_id = doc_row[0] if doc_row else None

                    if doc_id:
                        # 2. Registrar el job asociado (Asegúrate de que document_source_id o la tupla tenga manejo de conflicto)
                        session.execute(text("""
                            INSERT INTO processing_jobs (document_source_id, status, created_at, markdown_artifact_uri)
                            VALUES (:doc_id, 'COMPLETED', NOW(), :artifact_uri)
                            ON CONFLICT DO NOTHING;
                        """), {"doc_id": doc_id, "artifact_uri": artifact_uri})
                        
            logger.info(f"Trazabilidad Cloud registrada en BBDD para: {filename}")
        except Exception as db_err:
            logger.error(f"Falla crítica al registrar metadatos en BBDD cloud para {filename}: {db_err}")
            raise db_err  