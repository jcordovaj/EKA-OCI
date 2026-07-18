from typing import Any
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

    """ def update_job(self, job_id: int, status: Any):
        # Convertir Enum a string
        status_value = status.value if hasattr(status, "value") else status
        return self.jobs.update_status(self.db, job_id, status_value) """
        
    """ def update_job(self, job_id: int, status: Any):
        try:
            # Convertir Enum a string
            status_value = status.value if hasattr(status, "value") else status
            return self.jobs.update_status(self.db, job_id, status_value)
        except Exception as e:
            # Esto imprimirá la traza completa antes de que el Orquestador la oculte
            print(f"DEBUG CRÍTICO: El error real es: {type(e).__name__}: {str(e)}")
            raise e  """   

    def update_job(self, job_id: int, status: Any):
        # NORMALIZACIÓN SEGURA:
        # Si 'status' es un objeto que tiene un atributo llamado 'value' (como un Enum), tómalo.
        # Si 'status' es el Enum mismo, conviértelo a string.
        if hasattr(status, "value"):
            status_value = status.value
        elif isinstance(status, str):
            status_value = status
        else:
            status_value = str(status) # Fallback seguro
            
        return self.jobs.update_status(self.db, job_id, status_value)

    def save_metadata(self, job_id: int, manifesto):
        return self.metadata.create(self.db, job_id, manifesto)