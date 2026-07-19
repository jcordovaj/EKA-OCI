# tests/test_pipeline_integrity.py
import sys
import os
from processing.ingestion_watcher import IngestionWatcher
from persistence.unit_of_work import UnitOfWork
from persistence.storage.s3_provider import S3StorageProvider
from domain.contracts import FileStorageProvider
from persistence.orm.document import ProcessingJob, Metadata

sys.stdout.reconfigure(line_buffering=True)
print("--- DIAGNÓSTICO INICIADO ---", flush=True)

def test_full_pipeline_verification():
    print("\n--- INICIANDO DIAGNÓSTICO DE INTEGRIDAD ---")
    
    # 1. Inspección previa de BBDD
    with UnitOfWork() as uow:
        jobs = uow.session.query(ProcessingJob).all()
        if not jobs:
            print("[INFO] BBDD Vacía. Iniciando flujo desde cero.")
        else:
            print(f"[INFO] BBDD con {len(jobs)} registros previos. Inspeccionando...")
            for job in jobs:
                meta = uow.session.query(Metadata).filter_by(job_id=job.id).first()
                hash_val = meta.hash_value if meta else "SIN HASH"
                print(f"DEBUG: Archivo: {job.original_filename} | Estado: {job.status} | Hash: {hash_val}")

    # 2. Ejecución forzada (Aseguramos que el stdout se vacíe)
    sys.stdout.flush()
    print("[INFO] Lanzando IngestionWatcher...")
    
    # Aquí tu llamada al watcher
    IngestionWatcher.run()
    
    # 3. Verificación post-ejecución
    print("[INFO] Verificando estado post-ejecución...")
    with UnitOfWork() as uow:
        final_jobs = uow.session.query(ProcessingJob).all()
        if len(final_jobs) == len(jobs):
            print("[ALERTA] NO se procesaron archivos nuevos. El watcher no detectó cambios.")
        else:
            print(f"[EXITO] Procesados {len(final_jobs) - len(jobs)} archivos nuevos.")
            
    print("--- FIN DEL DIAGNÓSTICO ---\n")