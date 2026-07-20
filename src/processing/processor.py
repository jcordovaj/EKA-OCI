import logging
import io
from pathlib import Path
from minio import Minio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.settings import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        # Inicialización de MinIO utilizando la configuración central
        self.minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = getattr(settings, "MINIO_BUCKET_NAME", "eka-artifacts")
        
        # Inicialización de la base de datos para actualizar processing_jobs
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Asegurar que el bucket exista en MinIO al arrancar
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)
            logger.info(f"Bucket de MinIO creado automáticamente: {self.bucket_name}")

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

    def _upload_to_minio(self, file_path: Path, artifact_content: str, destination_path: str):
        """Sube el contenido procesado (ej. Markdown) directamente a MinIO."""
        content_bytes = artifact_content.encode("utf-8")
        data_stream = io.BytesIO(content_bytes)
        
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=destination_path,
            data=data_stream,
            length=len(content_bytes),
            content_type="text/markdown"
        )
        logger.info(f"Artefacto persistido exitosamente en MinIO -> s3://{self.bucket_name}/{destination_path}")

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