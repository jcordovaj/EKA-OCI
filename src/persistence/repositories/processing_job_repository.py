from typing import Optional, Any
from sqlalchemy.orm import Session
from persistence.orm.document import ProcessingJob
from persistence.repositories.abstract_repository import AbstractRepository

class ProcessingJobRepository(AbstractRepository[ProcessingJob]):

    def __init__(self):
        super().__init__(ProcessingJob)

    def get_by_id(self, db: Session, record_id: int) -> Optional[ProcessingJob]:
        return (
            db.query(ProcessingJob)
            .filter(ProcessingJob.id == record_id)
            .first()
        )

    def create(self, db: Session, **data: Any) -> ProcessingJob:
        job = ProcessingJob(**data)

        db.add(job)
        db.flush()
        db.refresh(job)

        return job

    def update(
        self,
        db: Session,
        record_id: int,
        updates: dict[str, Any],
    ) -> Optional[ProcessingJob]:

        job = self.get_by_id(db, record_id)

        if job is None:
            return None

        for key, value in updates.items():
            setattr(job, key, value)

        db.flush()
        db.refresh(job)

        return job

    def delete(
        self,
        db: Session,
        record_id: int,
    ) -> bool:

        job = self.get_by_id(db, record_id)

        if job is None:
            return False

        db.delete(job)

        return True