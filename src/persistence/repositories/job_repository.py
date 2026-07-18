# src/persistence/repositories/document_repository.py
from persistence.repositories.abstract_repository import AbstractRepository
from sqlalchemy.orm import Session # Importamos la sesión de base de datos y SQLAlchemy ORM
from typing import Optional, List 
import datetime as dt

class ProcessingJobRepository(AbstractRepository[ProcessingJob]):
    """
    Repositorio concreto para el Job de Procesamiento.
    """
    def get_by_id(self, db: Session, job_id: int) -> Optional[ProcessingJob]:
        """Busca un documento por su ID."""
        return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    def create(self, db: Session, document_source_id: str, **job_attrs: Any) -> ProcessingJob:
        """
        Crea y persiste una nueva instancia del Job.
        Algunas de las claves primarias se deben definir previamente en los argumentos.
        job_attrs son parámetros adicionales que no se pueden recuperar desde el contexto
        (por ejemplo: 'suggested_strategy', etc.).
        """
        # Usamos el modelo del dominio para asegurar que los datos son correctos
        # Esto es igual a document.validate().save()
        job = ProcessingJob(**job_attrs)
        job.document_source_id = document_source_id 
        db.add(job)
        db.commit()
        db.refresh(job)        
        return job

    def update_status(self, db: Session, record_id: int, status: str) -> Optional[ProcessingJob]:
        """Actualiza el estado del Job concreto."""
        # Usamos el modelo del dominio para asegurar que los datos son correctos
        # Esto es igual a document.validate(status).save()
        job = self.get_by_id(db, record_id)
        if not job:
            return None

        job.status = status
        db.commit()
        return job

    def update_metadata(self, db: Session, job_record: ProcessingJob) -> Optional[ProcessingJob]:
        """Actualiza el Metadata asociado al Job."""

        # Usamos el modelo del dominio para asegurar que los datos son correctos
        # Esto es igual a document.validate(status).save()
        job = self.get_by_id(db, record_id)
        if not job:
            return None

        # Actualizamos la metadata con nuevos campos.
        # job.status = status 
        # db.commit() ** No olvidar! **
        
        return job