# src/persistence/repositories/document_repository.py
from sqlalchemy.orm import Session
from typing import Optional, List
from src.domain.document import Document # Usamos el modelo del dominio para los datos entrantes
from src.persistence.orm.document import Document as ORMDocument
from typing import Optional, Any
from src.persistence.repositories.abstract_repository import AbstractRepository

class DocumentRepository(AbstractRepository[Document]):

    def __init__(self):
        super().__init__(Document)

    def get_by_id(self, db: Session, record_id: int) -> Optional[Document]:
        return (
            db.query(Document)
            .filter(Document.id == record_id)
            .first()
        )

    def create(self, db: Session, **data: Any) -> Document:
        document = Document(**data)

        db.add(document)
        db.flush()
        db.refresh(document)

        return document

    def update(
        self,
        db: Session,
        record_id: int,
        updates: dict[str, Any],
    ) -> Optional[Document]:

        document = self.get_by_id(db, record_id)

        if document is None:
            return None

        for key, value in updates.items():
            setattr(document, key, value)

        db.flush()
        db.refresh(document)

        return document

    def delete(
        self,
        db: Session,
        record_id: int,
    ) -> bool:

        document = self.get_by_id(db, record_id)

        if document is None:
            return False

        db.delete(document)

        return True
