# test_ingestion_trigger.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from processing.ingestion_watcher import IngestionWatcher
from persistence.storage.s3_provider import S3StorageProvider 

def test_trigger_real_bucket():
    # Inicialización directa ya que el S3StorageProvider toma credenciales de env
    engine = create_engine("postgresql://...") # Tu URL de BD
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    storage = S3StorageProvider() 
    watcher = IngestionWatcher(db_session, storage)
    
    print("--- Iniciando prueba de detección en MinIO (S3Provider) ---")
    watcher.run()
    print("--- Escaneo finalizado ---")

if __name__ == "__main__":
    test_trigger_real_bucket()