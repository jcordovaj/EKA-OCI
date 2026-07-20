import logging
import sys
from core.settings import Settings
from persistence.database import get_db
from persistence.storage.s3_provider import S3StorageProvider
from processing.delta_manager import DeltaManager
from processing.processor import DocumentProcessor
from processing.ingestion_watcher import IngestionWatcher
from processing.document_inspector import DocumentInspector
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("EKA_OCI_MAIN")

def main():
    logger.info("=== INICIANDO WORKER DE INGESTA EKA-OCI (OCI-DOCKER) ===")
    settings = Settings()
    
    # 1. Inicializar infraestructura real (PostgreSQL + S3/MinIO)
    db_session = create_engine(settings.DATABASE_URL)
    storage = S3StorageProvider(settings)
    
    # 2. Instanciar componentes de dominio y procesamiento
    inspector = DocumentInspector()
    delta_manager = DeltaManager(db_session)
    processor = DocumentProcessor(db_session=db_session, storage_provider=storage, settings=settings)
    
    # 3. Ensamblar el IngestionWatcher nativo
    watcher = IngestionWatcher(
        db_session=db_session,
        storage_provider=storage,
        settings=settings,
        inspector=inspector,
        delta_manager=delta_manager,
        processor=processor
    )
    
    # 4. Ejecución del ciclo
    try:
        watcher.run()
        logger.info("=== CICLO DE INGESTA FINALIZADO EXITOSAMENTE ===")
    except Exception as e:
        logger.critical(f"Falla crítica en la ejecución del worker OCI: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()