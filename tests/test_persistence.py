from persistence.database import SessionLocal
from persistence.repositories.document_repository import DocumentRepository
from persistence.orm.document import Document
from persistence.models import Base
from persistence.database import engine

# Esto crea todas las tablas definidas en los modelos en la base de datos
Base.metadata.create_all(bind=engine)

db   = SessionLocal()
repo = DocumentRepository()

try:
    print("== TEST PERSISTENCE ==")

    # CREATE
    document = repo.create(
        db,
        original_filename="test.pdf",
        mime_type="application/pdf",
    )

    db.commit()

    print(f"CREATE OK -> ID={document.id}")

    # READ
    recovered = repo.get_by_id(db, document.id)

    assert recovered is not None

    print(f"READ OK -> {recovered.original_filename}")

    # DELETE
    repo.delete(db, document.id)

    db.commit()

    deleted = repo.get_by_id(db, document.id)

    assert deleted is None

    print("DELETE OK")

    print()
    print("PERSISTENCE TEST PASSED")

except Exception as ex:
    db.rollback()
    raise ex

finally:
    db.close()