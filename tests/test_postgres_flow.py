# test_postgres_flow.py
from sqlalchemy import Column, Integer, String
from persistence.database import SessionLocal, engine
from persistence.models import Base

# Definimos una tabla simple para el test
class TestInfrastructure(Base):
    __tablename__ = 'test_infrastructure'
    id            = Column(Integer, primary_key=True)
    status        = Column(String)

# Crear tabla en Postgres
Base.metadata.create_all(bind=engine)

def test_insertion():
    db = SessionLocal()
    try:
        test_data = TestInfrastructure(status="Conexión PostgreSQL OK")
        db.add(test_data)
        db.commit()
        print("✅ ÉXITO: Registro insertado en PostgreSQL (5433).")
    except Exception as e:
        print(f"❌ FALLO CRÍTICO: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_insertion()