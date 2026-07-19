# src/persistence/unit_of_work.py
from sqlalchemy.orm import Session
from persistence.database import SessionLocal
from persistence.repositories.job_repository import ProcessingJobRepository
from persistence.repositories.metadata_repository import MetadataRepository

class UnitOfWork:
    def __init__(self):
        self.session: Session = SessionLocal()
        # Inyectamos los repositorios inicializados con la misma sesión
        self.jobs = ProcessingJobRepository()
        self.metadata = MetadataRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()