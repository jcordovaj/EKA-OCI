from sqlalchemy.orm import Session
from persistence.repositories.job_repository import JobRepository
from persistence.repositories.metadata_repository import MetadataRepository

class OrchestratorRepository:
    def __init__(self, db: Session):
        self.db = db
        self.jobs = JobRepository()
        self.metadata = MetadataRepository()

    def create_job(self, filename, status):
        # Aquí delega al repositorio de Jobs real
        return self.jobs.create(self.db, filename, status)

    def update_job(self, job_id, status):
        return self.jobs.update_status(self.db, job_id, status)

    def save_metadata(self, job_id, manifesto):
        return self.metadata.create(self.db, job_id, manifesto)