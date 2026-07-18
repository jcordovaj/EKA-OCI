import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from persistence.orm.document import ProcessingJob

# 1. FORZAMOS EL PUERTO CORRECTO AQUÍ
DATABASE_URL = "postgresql+psycopg2://admin:password@localhost:5433/eka_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sys.path.append(str(Path(__file__).parent / "src"))


try:
    # Intentamos buscar el modelo en la ubicación más probable según tu árbol
    from persistence.orm.document import ProcessingJob
    print("Modelo encontrado en: persistence.orm.document")
except ImportError:
    try:
        from persistence.models import ProcessingJob
        print("Modelo encontrado en: persistence.models")
    except ImportError:
        print("Error: No pude encontrar la definición de ProcessingJob en las rutas habituales.")
        sys.exit(1)

def verificar_job_21():
    print(f"DEBUG: Engine URL forzado a: {engine.url}")
    db = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == 21).first()
        if job:
            print(f"\n--- Contenido del Job 21 ---")
            print(job.__dict__)
        else:
            print("\nEl Job 21 no existe en la base de datos.")
    except Exception as e:
        print(f"❌ ERROR AL CONSULTAR DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_job_21()
