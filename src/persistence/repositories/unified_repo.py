from persistence.repositories.job_repository import ProcessingJobRepository
from persistence.repositories.metadata_repository import MetadataRepository

class UnifiedRepository:
    def __init__(self):
        self.jobs = ProcessingJobRepository()
        self.metadata = MetadataRepository()

    def create_job(self, document_name, status):
        # Aquí asignamos un ID ficticio o lógica de documento si es necesario
        return self.jobs.create(self.db_temp, document_source_id=1, status=status)
    