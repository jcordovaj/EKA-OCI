import logging
import sys
from core.settings import Settings
from persistence.database import get_db
from persistence.storage.s3_provider import S3StorageProvider
from processing.delta_manager import DeltaManager
from processing.processor import DocumentProcessor
from processing.ingestion_watcher import IngestionWatcher
from processing.document_inspector import DocumentInspector
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("EKA_OCI_MAIN")

def print_database_dashboard(db_url: str):
    """Consulta la BBDD PostgreSQL e imprime la tabla resumen en consola al finalizar el ciclo."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT 
                    d.id, 
                    d.original_filename, 
                    d.ingestion_timestamp, 
                    COALESCE(j.markdown_artifact_uri, 'N/A') AS artifact_uri, 
                    d.status
                FROM documentos d
                LEFT JOIN processing_jobs j ON d.id = j.document_source_id
                ORDER BY d.id ASC;
            """))
            rows = result.fetchall()

            if not rows:
                print("\n[INFO] La tabla de documentos en base de datos está vacía.\n")
                return

            header = f"| {'ID':<3} | {'Nombre Original':<25} | {'Timestamp Ingesta':<19} | {'URI Artefacto MinIO':<35} | {'Estado':<10} |"
            separator = "-" * len(header)
            
            print("\n" + "=" * len(header))
            print(" DASHBOARD DE INGESTA OCI-NATIVE (ESTADO EN POSTGRESQL) ".center(len(header), "="))
            print("=" * len(header))
            print(header)
            print(separator)
            
            for row in rows:
                doc_id, filename, timestamp, artifact, status = row
                f_name = (filename[:22] + '...') if len(filename) > 25 else filename
                art_name = (artifact[:32] + '...') if len(artifact) > 35 else artifact
                print(f"| {str(doc_id):<3} | {f_name:<25} | {str(timestamp)[:19]:<19} | {art_name:<35} | {status:<10} |")
                
            print(separator + "\n")
    except Exception as e:
        print(f"[ERROR] No se pudo renderizar el dashboard desde la BBDD: {e}")

def main():
    logger.info("=== INICIANDO WORKER DE INGESTA EKA-OCI (OCI-DOCKER) ===")
    settings = Settings()
    
    # 1. Inicializar infraestructura real (PostgreSQL + S3/MinIO)
    db_session = next(get_db())
    storage = S3StorageProvider()
    
    # 2. Instanciar componentes de dominio y procesamiento
    inspector = DocumentInspector()
    delta_manager = DeltaManager(db_session=db_session)
    processor = DocumentProcessor(storage_provider=storage, delta_manager=delta_manager) 
    
    # 3. Ensamblar el IngestionWatcher nativo
    watcher = IngestionWatcher(
        db_session=db_session,
        storage_provider=storage,
        settings=settings,
        inspector=inspector,
        delta_manager=delta_manager,
        processor=processor
    )
    
    # 4. Ejecución del ciclo y renderizado posterior del dashboard
    try:
        watcher.run()
        logger.info("=== CICLO DE INGESTA FINALIZADO EXITOSAMENTE ===")
        
        # Desplegar la tabla resumen consultando la BBDD al terminar con éxito
        print_database_dashboard(settings.DATABASE_URL)
        
    except Exception as e:
        logger.critical(f"Falla crítica en la ejecución del worker OCI: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()