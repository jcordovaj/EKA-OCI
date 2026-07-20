import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("DB_INTEGRATION_TEST")

def test_rag_management_flow():
    logger.info("=== INICIANDO PRUEBA DE INTEGRACIÓN CON POSTGRESQL (DOCKER) ===")
    
    # 1. Crear motor y sesión usando la configuración existente de settings
    engine       = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        try:
            # 2. Insertar un documento de prueba en la tabla 'documentos'
            # Usamos SQL directo o modelos ORM según tengas mapeado. 
            # Aquí usamos SQL puro compatible con tu esquema exacto para garantizar cero fricción:
            from sqlalchemy import text
            
            logger.info("Registrando documento de prueba en la tabla 'documentos'...")
            doc_query = text("""
                INSERT INTO documentos (original_filename, mime_type, ingestion_timestamp, binary_hash, status)
                VALUES (:filename, :mime, :timestamp, :hash, :status)
                RETURNING id;
            """)
            
            result = session.execute(doc_query, {
                "filename": "manual_arquitectura_eka.pdf",
                "mime": "application/pdf",
                "timestamp": datetime.utcnow(),
                "hash": "sha256_mock_hash_abc123789",
                "status": "INGESTED"
            })
            doc_id = result.fetchone()[0]
            
            # 3. Registrar el job asociado en la tabla 'processing_jobs'
            logger.info(f"Registrando job de procesamiento para el documento ID {doc_id}...")
            job_query = text("""
                INSERT INTO processing_jobs (document_source_id, status, created_at, last_updated, markdown_artifact_uri)
                VALUES (:doc_id, :status, :created, :updated, :uri)
                RETURNING id;
            """)
            
            job_result = session.execute(job_query, {
                "doc_id": doc_id,
                "status": "COMPLETED",
                "created": datetime.utcnow(),
                "updated": datetime.utcnow(),
                "uri": "s3://artifacts/manual_arquitectura_eka.md"
            })
            job_id = job_result.fetchone()[0]
            
            session.commit()
            logger.info(f"¡Transacción exitosa! Documento ID: {doc_id}, Job ID: {job_id}")

            # 4. Consultar la "Tabla de Gestión del RAG" uniendo las tablas (Simulando el Panel)
            logger.info("\n--- CONSULTANDO EL PANEL DE GESTIÓN DEL RAG (ESTADO ACTUAL) ---")
            report_query = text("""
                SELECT 
                    d.id,
                    d.original_filename,
                    d.binary_hash,
                    d.status as doc_status,
                    p.status as job_status,
                    p.markdown_artifact_uri,
                    d.ingestion_timestamp
                FROM documentos d
                LEFT JOIN processing_jobs p ON d.id = p.document_source_id;
            """)
            
            rows = session.execute(report_query).fetchall()
            for row in rows:
                logger.info(
                    f"[RAG MANAGEMENT] Doc ID: {row.id} | "
                    f"Archivo: {row.original_filename} | "
                    f"Hash: {row.binary_hash[:10]}... | "
                    f"Estado Doc: {row.doc_status} | "
                    f"Estado Job: {row.job_status} | "
                    f"URI Artefacto: {row.markdown_artifact_uri}"
                )

        except Exception as e:
            session.rollback()
            logger.error(f"Error en la operación de base de datos: {e}", exc_info=True)

    logger.info("=== PRUEBA DE INTEGRACIÓN FINALIZADA ===")

if __name__ == "__main__":
    test_rag_management_flow()