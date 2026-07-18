# Smoke test para el flujo completo de procesamiento de documentos
from pathlib import Path
from persistence.repositories.orchestrator_repository import OrchestratorRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import Settings
from persistence.repositories.metadata_repository import MetadataRepository
from persistence.storage.s3_provider import S3StorageProvider
from processing.orchestrator import ProcessingOrchestrator

# 1. Instanciar settings correctamente
settings = Settings()

# 2. Construir la URL de conexión (Ajusta según si es SQLite o Postgres)
# Si usas SQLite: "sqlite:///./eka.db"
# Si usas Postgres: f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}"
db_url = f"sqlite:///./eka_test.db" 
engine = create_engine(db_url, echo=False)

# Crear tablas si no existen (necesario para el smoke test)
from persistence.models import Base 
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
db_session = SessionLocal()

# --- Setup de Fixtures ---
FIXTURES_DIR = Path("tests/fixtures")
FIXTURES_DIR.mkdir(exist_ok=True)
test_file = FIXTURES_DIR / "sample_document.pdf"
test_file.write_text("dummy content")

def run_test():
    # El repositorio no recibe la sesión en el init porque tu diseño es stateless
    repo = OrchestratorRepository(db_session)
    storage = S3StorageProvider()
    
    # El orquestador recibe las dependencias que necesita
    orchestrator = ProcessingOrchestrator(db_session, repo, storage)
    
    try:
        # Al ejecutar el flujo, el orquestador llamará a los métodos del repo
        # pasando la db_session internamente según tu diseño actual.
        print(f"Iniciando procesamiento de: {test_file.name}")
        orchestrator.process_document(test_file)
        print("✓ Flujo exitoso")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    run_test()