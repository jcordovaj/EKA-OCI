# src/persistence/repositories/document_repository.py
# src/persistence/repositories/job_repository.py
from typing import Optional, Any
from sqlalchemy.orm import Session
from persistence.orm.document import ProcessingJob
from persistence.repositories.abstract_repository import AbstractRepository


class ProcessingJobRepository(AbstractRepository[ProcessingJob]):
    def __init__(self):
        super().__init__(ProcessingJob)

    def get_by_id(self, db: Session, job_id: int) -> Optional[ProcessingJob]:
        return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    def get_by_filename(self, db: Session, filename: str) -> Optional[ProcessingJob]:
        """Consulta centralizada para idempotencia."""
        return db.query(ProcessingJob).filter(ProcessingJob.original_filename == filename).first()

    def create(self, db: Session, document_source_id: int, **job_attrs: Any) -> ProcessingJob:
        if "status" in job_attrs and hasattr(job_attrs["status"], "value"):
            job_attrs["status"] = job_attrs["status"].value
        job = ProcessingJob(document_source_id=document_source_id, **job_attrs)
        db.add(job)
        db.flush()
        db.refresh(job)
        return job

    def update_status(self, db: Session, job_id: int, status: Any) -> Optional[ProcessingJob]:
        status_value = str(status.value) if hasattr(status, "value") else str(status)
        job = self.get_by_id(db, job_id)
        if not job: return None
        job.status = status_value
        db.flush()
        return job
