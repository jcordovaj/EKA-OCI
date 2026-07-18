from sqlalchemy.orm import Session
from persistence.database import SessionLocal

class UnitOfWork:
    """
    Controla una transacción completa sobre la base de datos.

    Uso:

    with UnitOfWork() as uow:
        ...
        uow.commit()
    """

    def __init__(self):
        self.db: Session | None = None

    def __enter__(self):
        self.db = SessionLocal()
        return self

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def close(self):
        self.db.close()

    def __exit__(self, exc_type, exc_val, exc_tb):

        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

        self.close()