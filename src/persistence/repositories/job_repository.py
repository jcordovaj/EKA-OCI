# src/persistence/repositories/document_repository.py
from typing import Optional, Any
from sqlalchemy.orm import Session
from persistence.orm.document import ProcessingJob
from persistence.repositories.abstract_repository import AbstractRepository

class ProcessingJobRepository(AbstractRepository[ProcessingJob]):
    """
    Repositorio concreto para el Job de Procesamiento.
    """
    def __init__(self):
        super().__init__(ProcessingJob)

    def get_by_id(self, db: Session, job_id: int) -> Optional[ProcessingJob]:
        return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    def create(self, db: Session, document_source_id: int, **job_attrs: Any) -> ProcessingJob:
        """Crea y persiste una nueva instancia del Job."""
        job = ProcessingJob(document_source_id=document_source_id, **job_attrs)
        db.add(job)
        db.flush()  # Usamos flush para mantener la atomicidad en el orquestador
        db.refresh(job)
        return job

    def update_status(self, db: Session, job_id: int, status: str) -> Optional[ProcessingJob]:
        """Actualiza el estado del Job."""
        job = self.get_by_id(db, job_id)
        if not job:
            return None

        job.status = status
        db.flush()
        return job