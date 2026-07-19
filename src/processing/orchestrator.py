from persistence.unit_of_work import UnitOfWork

class ProcessingOrchestrator:
    def __init__(self, storage_provider):
        self.storage = storage_provider

    def process_document(self, file_key: str):
        # El UoW ahora es el dueño de la transacción y los repositorios
        with UnitOfWork() as uow:
            filename = file_key.split('/')[-1]
            
            # 1. Crear Job usando el repositorio del UoW
            job = uow.jobs.create(uow.session, document_source_id=1, original_filename=filename, status="PENDING")
            
            try:
                # 2. Lógica de extracción/procesamiento
                # manifesto = self.extractor.extract(file_key)
                
                # 3. Guardar metadatos
                uow.metadata.create(uow.session, job.id, manifesto)
                
                # 4. Actualizar estado
                uow.jobs.update_status(uow.session, job.id, "COMPLETED")
                
            except Exception as e:
                # El bloque 'with' ejecutará rollback automáticamente al salir si hay error
                uow.jobs.update_status(uow.session, job.id, "FAILED")
                raise e
            
