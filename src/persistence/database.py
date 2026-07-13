from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

# Creamos el motor de base de datos usando el contrato de configuración
engine = create_engine(settings.database_url)

# Creamos una fábrica de sesiones para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generador para obtener sesiones de base de datos de forma segura."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()