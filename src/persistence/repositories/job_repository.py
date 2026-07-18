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
        # Si 'status' viene como Enum, extraemos su valor (string)
        if "status" in job_attrs and hasattr(job_attrs["status"], "value"):
            job_attrs["status"] = job_attrs["status"].value
            
        job = ProcessingJob(document_source_id=document_source_id, **job_attrs)
        db.add(job)
        db.flush()
        db.refresh(job)
        return job

    def update_status(self, db: Session, job_id: int, status: Any) -> Optional[ProcessingJob]:
        # FUERZA la conversión a string. Si es Enum, .value; si es objeto, str().
        # No dependemos de hasattr ni de lógica compleja.
        status_value = str(status.value) if hasattr(status, "value") else str(status)
        
        job = self.get_by_id(db, job_id)
        if not job:
            return None
        
        job.status = status_value
        db.flush()
        return job

    def update(self, db: Session, record_id: int, updates: dict[str, Any]) -> Optional[ProcessingJob]:
        job = self.get_by_id(db, record_id)
        if not job:
            return None
        for key, value in updates.items():
            setattr(job, key, value)
        db.flush()
        db.refresh(job)
        return job

    def delete(self, db: Session, record_id: int) -> bool:
        job = self.get_by_id(db, record_id)
        if not job:
            return False
        db.delete(job)
        db.flush()
        return True