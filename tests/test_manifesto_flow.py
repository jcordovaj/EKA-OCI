import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Ajusta estos imports según la estructura de tu proyecto
from core.settings import settings
from persistence.models import ProcessingJob # Asegúrate de importar tu modelo base

def inspect_job_data(job_id: int):
    print(f"--- Consultando Job ID: {job_id} ---")
    
    # 1. Configurar conexión
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 2. Buscar el job
        job = session.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        
        if not job:
            print(f"Error: No se encontró el job {job_id}")
            return

        print(f"Job Status: {job.status}")
        
        # 3. Verificar metadatos asociados
        # Asumiendo una relación job.metadata o que el repositorio lo guarda ahí
        if hasattr(job, 'metadata') and job.metadata:
            print("\n--- Metadatos Encontrados ---")
            print(job.metadata.content if hasattr(job.metadata, 'content') else "Contenido no accesible")
        else:
            print("\nNota: No se encontraron registros de metadatos vinculados a este Job.")

    except Exception as e:
        print(f"Error al consultar el repositorio: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Puedes pasar el ID por argumento o dejar el 21 fijo
    target_id = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    inspect_job_data(target_id)