from typing import Optional, Any
from sqlalchemy.orm import Session
from persistence.orm.document import Metadata  # Ajuste de path
from persistence.repositories.abstract_repository import AbstractRepository
from processing.metadata_generator import MetadataManifesto

class MetadataRepository(AbstractRepository[Metadata]):
    def __init__(self):
        super().__init__(Metadata)

    # El método create ahora acepta nuestro objeto de dominio
    def create(self, db: Session, manifesto: MetadataManifesto) -> Metadata:
        # Convertimos nuestro Dataclass de dominio a un dict para el ORM
        data = manifesto.to_dict() 
        metadata = Metadata(**data)

        db.add(metadata)
        db.flush()
        db.refresh(metadata)

        return metadata

    """ def get_by_id(self, db: Session, record_id: int) -> Optional[Metadata]:
            return (
                db.query(Metadata)
                .filter(Metadata.id == record_id)
                .first()
            ) """

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