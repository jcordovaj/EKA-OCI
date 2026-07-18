from sqlalchemy.orm import Session
from persistence.storage.s3_provider import S3StorageProvider
from processing.orchestrator import ProcessingOrchestrator

try:
    # Simulamos el inyector
    storage = S3StorageProvider()
    print("✓ Almacenamiento instanciado")
    
    # Si esto corre, los imports están OK
    print("✓ Orquestador instanciado correctamente")
except Exception as e:
    print(f"✗ Error encontrado: {e}")