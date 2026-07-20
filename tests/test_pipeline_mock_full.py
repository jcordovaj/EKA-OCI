import sys
from pathlib import Path

# Añadir la ruta src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.settings import settings
from domain.inspector import DocumentInspector
from processing.processor import DocumentProcessor
from processing.ingestion_watcher import IngestionWatcher
# Nota: Ajusta la importación de DeltaManager o storage si tu clase las requiere explícitamente

def run_integration_test():
    print("=== INICIANDO PRUEBA DE INTEGRACIÓN EKA-OCI ===")
    
    # 1. Definir directorio inbox temporal de prueba
    inbox_dir = Path("./data/inbox")
    inbox_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Crear un archivo de prueba plano en el inbox
    test_file = inbox_dir / "manual_prueba.md"
    test_file.write_text("# Arquitectura EKA-OCI\n\nPrueba de integración de punta a punta.", encoding="utf-8")
    print(f"[OK] Archivo de prueba creado en inbox: {test_file}")
    
    # 3. Construir las dependencias reales requeridas por el IngestionWatcher
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    # Instanciar el procesador y el inspector de dominio
    processor = DocumentProcessor()
    inspector = DocumentInspector()
    
    # Si tu constructor exige storage_provider o delta_manager, instáncialos aquí según tu arquitectura actual.
    # Ejemplo inyectando los componentes reales:
    try:
        watcher = IngestionWatcher(
            db_session=db_session,
            storage_provider=processor.minio_client, # O el cliente de storage que utilices
            settings=settings,
            inspector=inspector,
            delta_manager=None # O pasa la instancia correspondiente si aplica
        )
    except TypeError:
        # Fallback por si la firma exacta difiere levemente en algún parámetro opcional
        watcher = IngestionWatcher(
            db_session=db_session,
            storage_provider=processor,
            settings=settings,
            inspector=inspector,
            delta_manager=None
        )

    print("\n--- Ejecutando escaneo del Inbox (Primer paso: Nuevo documento) ---")
    # Nota: Asegúrate de llamar al método correcto que tiene tu ingestion_watcher (ej. process_inbox_files o scan_inbox)
    if hasattr(watcher, "process_inbox_files"):
        watcher.process_inbox_files(inbox_dir)
    else:
        watcher.scan_inbox(inbox_dir)
    
    print("\n--- Ejecutando escaneo del Inbox por SEGUNDA vez (Probando Idempotencia) ---")
    if hasattr(watcher, "process_inbox_files"):
        watcher.process_inbox_files(inbox_dir)
    else:
        watcher.scan_inbox(inbox_dir)
        
    db_session.close()
    print("\n=== PRUEBA DE INTEGRACIÓN FINALIZADA ===")

if __name__ == "__main__":
    run_integration_test()