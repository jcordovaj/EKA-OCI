# src/persistence/repositories/orchestrator_repository.py
from sqlalchemy.orm import Session
from persistence.repositories.job_repository import ProcessingJobRepository
from persistence.repositories.metadata_repository import MetadataRepository

class OrchestratorRepository:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.jobs = ProcessingJobRepository()
        self.metadata = MetadataRepository()

    def create_job(self, filename: str, status: str):
        # Mantenemos la lógica de negocio de crear el job
        return self.jobs.create(self.db, document_source_id=1, original_filename=filename, status=status)

    def update_job_status(self, job_id: int, status: str):
        return self.jobs.update_status(self.db, job_id, status)

    def save_metadata(self, job_id: int, manifesto):
        return self.metadata.create(self.db, job_id, manifesto)

    def get_job_by_filename(self, filename: str):
        return self.jobs.get_by_filename(self.db, filename)