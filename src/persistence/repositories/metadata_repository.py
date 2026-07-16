from typing import Optional, Any
from sqlalchemy.orm import Session
from src.persistence.orm.document import Metadata
from src.persistence.repositories.abstract_repository import AbstractRepository

class MetadataRepository(AbstractRepository[Metadata]):

    def __init__(self):
        super().__init__(Metadata)

    def get_by_id(self, db: Session, record_id: int) -> Optional[Metadata]:
        return (
            db.query(Metadata)
            .filter(Metadata.id == record_id)
            .first()
        )

    def create(self, db: Session, **data: Any) -> Metadata:
        metadata = Metadata(**data)

        db.add(metadata)
        db.flush()
        db.refresh(metadata)

        return metadata

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