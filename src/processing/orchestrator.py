# src/processing/orchestrator.py
from persistence.unit_of_work import UnitOfWork
from persistence.orm.document import ProcessingJob, Metadata # Referencias necesarias

class ProcessingOrchestrator:
    def __init__(self, storage_provider, extractor):
        self.storage = storage_provider
        self.extractor = extractor

    def process_document(self, file_key: str):
        with UnitOfWork() as uow:
            filename = file_key.split('/')[-1]
            # Ahora uow.jobs es el repositorio y uow.session es la sesión
            job = uow.jobs.create(uow.session, document_source_id=1, original_filename=filename, status="PENDING")
            
            try:
                manifesto = self.extractor.extract(file_key)
                uow.metadata.create(uow.session, job.id, manifesto)
                uow.jobs.update_status(uow.session, job.id, "COMPLETED")
            except Exception as e:
                uow.jobs.update_status(uow.session, job.id, "FAILED")
                raise e

