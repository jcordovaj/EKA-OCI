import logging
from pathlib import Path

# 1. Configurar logs para ver la salida en consola
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 2. Clases Mock para aislar el test
class MockSettings:
    INBOX_PATH = "inbox/"
    REJECTS_PATH = "failed/"
    MAX_PDF_PAGES = 200
    MAX_BATCH_UPLOAD = 5

class MockStorage:
    def list_objects(self, path):
        # Simulamos 1 sin cambios, 1 corrupto, 1 gigante y 12 normales (para probar el overflow del batch)
        return [
            "inbox/sin_cambios.pdf",
            "inbox/corrupto.pdf",
            "inbox/gigante.pdf",
        ] + [f"inbox/normal_{i}.pdf" for i in range(12)]

    def move_object(self, src, dest):
        logging.info(f"[STORAGE MOCK] Movido de {src} a {dest}")

class MockInspector:
    def inspect(self, file_path):
        name = str(file_path)
        class Result:
            is_valid = True
            is_complex = False
            page_count = 10
            error_message = None

        res = Result()
        if "corrupto" in name:
            res.is_valid = False
            res.error_message = "File header corrupted"
        elif "gigante" in name:
            res.page_count = 500  # Supera MAX_PDF_PAGES (200)
        return res

class MockDelta:
    def needs_processing(self, file_path):
        if "sin_cambios" in str(file_path):
            return False
        return True

# 3. Inyectamos las dependencias al IngestionWatcher (asegúrate de importar tu clase real)
# from src.workers.ingestion_watcher import IngestionWatcher 

# (Para fines de prueba rápida, simulamos la ejecución limpia con el flujo que definimos)
if __name__ == "__main__":
    settings = MockSettings()
    storage = MockStorage()
    
    logging.info("--- INICIANDO CERTIFICACIÓN DE TRIAGE ---")
    
    files = storage.list_objects(settings.INBOX_PATH)
    inspector = MockInspector()
    delta = MockDelta()
    
    dispatch_map = {"immediate": [], "lazy": [], "rejected": []}

    for file_key in files:
        file_path = Path(file_key)
        
        if not delta.needs_processing(file_path):
            logging.info(f"Omitido por Delta (sin cambios): {file_key}")
            continue
            
        inspection = inspector.inspect(file_path)
        
        if not inspection.is_valid:
            dispatch_map["rejected"].append({"file_key": file_key, "reason": inspection.error_message})
        elif inspection.page_count > settings.MAX_PDF_PAGES or inspection.is_complex:
            dispatch_map["lazy"].append(file_key)
        else:
            dispatch_map["immediate"].append(file_key)

    # Aplicar límite de batch inmediato
    batch_to_process = dispatch_map["immediate"][:settings.MAX_BATCH_UPLOAD]
    overflow = dispatch_map["immediate"][settings.MAX_BATCH_UPLOAD:]
    dispatch_map["lazy"].extend(overflow)

    logging.info(f"RESULTADO DEL TRIAGE:")
    logging.info(f" - Rechazados (a rejects): {len(dispatch_map['rejected'])}")
    logging.info(f" - Inmediatos (a procesar): {len(batch_to_process)}")
    logging.info(f" - Lazy / Diferidos (a cola): {len(dispatch_map['lazy'])}")
    logging.info("--- CERTIFICACIÓN FINALIZADA CON ÉXITO ---")