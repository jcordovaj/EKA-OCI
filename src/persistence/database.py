from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings
import logging

# Configuración del engine optimizada para PostgreSQL + pgvector
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def init_db():
    """Inicialización explícita para asegurar extensiones como pgvector."""
    with engine.connect() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()