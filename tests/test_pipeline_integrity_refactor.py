# tests/test_pipeline_integrity.py
import sys
import os

from processing.ingestion_watcher import IngestionWatcher
from processing.markdown_extractor import MarkdownExtractor

# Forzar el volcado de consola
sys.stdout.reconfigure(line_buffering=True)

print("--- 1. TEST DE CONFIGURACIÓN ---")
try:
    # Ajusta el import según tu estructura, asumo src.core.settings o core.settings
    from core.settings import settings
    print("[EXITO] Configuración cargada correctamente.")
    print(f"[INFO] Bucket: {settings.minio_bucket}")
    print(f"[INFO] Endpoint: {settings.minio_endpoint}")
except Exception as e:
    print(f"[ERROR CRÍTICO] Fallo al cargar settings: {e}")
    sys.exit(1)

print("\n--- 2. TEST DE IMPORTACIONES ---")
try:
    from persistence.unit_of_work import UnitOfWork
    from persistence.storage.s3_provider import S3StorageProvider
    from persistence.orm.document import ProcessingJob
    print("[EXITO] Módulos importados correctamente.")
except Exception as e:
    print(f"[ERROR CRÍTICO] Fallo al importar módulos: {e}")
    sys.exit(1)

def test_conexiones():
    print("\n--- 3. TEST DE CONEXIONES ---")
    
    # Prueba de Base de Datos
    try:
        print("[INFO] Conectando a Base de Datos...")
        with UnitOfWork() as uow:
            jobs = uow.session.query(ProcessingJob).all()
            print(f"[EXITO] BD conectada. Trabajos registrados: {len(jobs)}")
    except Exception as e:
        print(f"[ERROR CRÍTICO] Fallo en la Base de Datos: {e}")
        return # Salimos de la función si falla la BD

    # Prueba de MinIO
    try:
        print("[INFO] Conectando a MinIO...")
        storage = S3StorageProvider()
        # Intentamos listar la raíz del bucket para forzar la comunicación
        objetos = storage.list_objects("")
        print(f"[EXITO] MinIO conectado. Objetos encontrados en '{storage.bucket}': {len(objetos)}")
        print("\n--- 4. TEST DE INGESTION WATCHER ---")
        try:
            # 1. Necesitamos una sesión de base de datos
            with UnitOfWork() as uow:
                # 2. Necesitamos nuestro proveedor de almacenamiento configurado
                storage = S3StorageProvider()
                extractor = extract_pdf() # La clase que extrae el contenido del PDF
                
                
                # 3. Instanciamos el watcher pasando los argumentos requeridos
                watcher = IngestionWatcher(db_session=uow.session, storage_provider=storage, extractor=extractor)
                
                print("[INFO] IngestionWatcher instanciado correctamente. Ejecutando...")
                
                # Asumiendo que 'run()' procesa los archivos
                watcher.run() 
                
        except Exception as e:
            print(f"[ERROR CRÍTICO] El watcher falló: {e}")
            # Esto te dará el traceback completo si es un error dentro de la lógica de run()
            import traceback
            traceback.print_exc()
        """ storage = S3StorageProvider()
        archivos = storage.list_objects("inbox/")

        if archivos:
            archivo_prueba = archivos[0]
            print(f"[DEBUG] Intentando mover: {archivo_prueba}")
            try:
                # Esto es lo que el watcher debería hacer internamente
                storage.copy(archivo_prueba, archivo_prueba.replace("inbox/", "processing/"))
                storage.delete(archivo_prueba)
                print("[EXITO] Archivo movido manualmente.")
            except Exception as e:
                print(f"[ERROR] Falló el movimiento del archivo: {e}") """
    
    except Exception as e:
        print(f"[ERROR CRÍTICO] Fallo de conexión o permisos en MinIO: {e}")
        return

    print("\n--- DIAGNÓSTICO COMPLETADO CON ÉXITO ---")

# Bloque de ejecución principal vital para que la función se llame
if __name__ == "__main__":
    test_conexiones()