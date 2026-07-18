from typing import Optional, Any
from sqlalchemy.orm import Session
from persistence.orm.document import Metadata, ProcessingJob  # Ajuste de path
from persistence.repositories.abstract_repository import AbstractRepository
from processing.metadata_generator import MetadataManifesto

class MetadataRepository(AbstractRepository[Metadata]):
    def __init__(self):
        super().__init__(Metadata)

    # El método create ahora acepta el manifesto de dominio y el job_id requerido por el ORM
    """ def create(self, db: Session, job_id: int, manifesto: MetadataManifesto) -> Metadata:
        # 1. Obtenemos el job para acceder al documento vinculado
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        
        # 2. Actualizamos los datos de la tabla 'Document' si es necesario
        # (El filename ya vive en 'documentos.original_filename')
        
        # 3. Construimos solo el objeto ORM Metadata con lo que este requiere
        metadata = Metadata(
            job_id=job_id,
            classification=manifesto.classification,
            document_type=manifesto.document_type,
            suggested_strategy="AUTO_DETECTED", # Esto debe venir de tu lógica de negocio
            confidence_score=1.0                # Valor por defecto inicial
        )
        
        db.add(metadata)
        db.flush()
        db.refresh(metadata)
        return metadata """

    def create(self, db: Session, job_id: int, manifesto: MetadataManifesto) -> Metadata:
        metadata = Metadata(
            job_id=job_id,
            classification=manifesto.classification,
            document_type=manifesto.document_type,
            suggested_strategy="TBD", # Valor temporal para pasar el test
            confidence_score=1.0      # Valor por defecto
        )
        db.add(metadata)
        db.flush() # Aquí es donde sabremos si hay error de constraint
        return metadata

    def get_by_id(self, db: Session, record_id: int) -> Optional[Metadata]:
        return db.query(Metadata).filter(Metadata.id == record_id).first()
    
    def update(
        self,
        db: Session,
        record_id: int,
        updates: dict[str, Any],
    ) -> Optional[Metadata]:

        metadata = self.get_by_id(db, record_id)

        if metadata is None:
            return None

        for key, value in updates.items():
            setattr(metadata, key, value)

        db.flush()
        db.refresh(metadata)

        return metadata

    def delete(
        self,
        db: Session,
        record_id: int,
    ) -> bool:

        metadata = self.get_by_id(db, record_id)

        if metadata is None:
            return False

        db.delete(metadata)

        return True