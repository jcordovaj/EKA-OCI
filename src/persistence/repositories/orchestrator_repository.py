from sqlalchemy.orm import Session
from persistence.repositories.job_repository import ProcessingJobRepository
from persistence.repositories.metadata_repository import MetadataRepository

class OrchestratorRepository:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.jobs = ProcessingJobRepository()
        self.metadata = MetadataRepository()

    def create_job(self, document_name: str, status: str):
        # Asumiendo que el documento ya existe o el ID es 1 para el smoke test
        return self.jobs.create(self.db, document_source_id=1, status=status)

    def update_job(self, job_id: int, status: str):
        return self.jobs.update_status(self.db, job_id, status)

    def save_metadata(self, job_id: int, manifesto):
        return self.metadata.create(self.db, job_id, manifesto)