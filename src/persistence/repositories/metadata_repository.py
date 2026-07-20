# src/persistence/repositories/metadata_repository.py
from typing import Optional, Any
from sqlalchemy.orm import Session
from persistence.orm.document import Metadata
from persistence.repositories.abstract_repository import AbstractRepository
from processing.metadata_generator import MetadataManifesto

class MetadataRepository(AbstractRepository[Metadata]):
    def __init__(self):
        super().__init__(Metadata)

    def create(self, db: Session, job_id: int, manifesto: MetadataManifesto) -> Metadata:
        metadata = Metadata(
            job_id=job_id,
            classification=manifesto.classification,
            document_type=manifesto.document_type,
            suggested_strategy="TBD",
            confidence_score=1.0
        )
        db.add(metadata)
        db.flush()
        return metadata

    def get_by_id(self, db: Session, record_id: int) -> Optional[Metadata]:
        return db.query(Metadata).filter(Metadata.id == record_id).first()
    
    def update(self, db: Session, metadata: Metadata):
        db.merge(metadata)
        db.flush()

    def delete(self, db: Session, metadata_id: int):
        # Asumiendo que Metadata tiene un atributo 'id'
        meta = db.query(Metadata).filter_by(id=metadata_id).first()
        if meta:
            db.delete(meta)
            db.flush()