# src/processing/ingestion_watcher.py
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class IngestionWatcher:
    def __init__(self, db_session: Any, storage_provider: Any, settings: Any, inspector: Any, delta_manager: Any):
        self.db = db_session
        self.storage = storage_provider
        self.settings = settings
        self.inspector = inspector
        self.delta = delta_manager

    def run(self) -> None:
        """Ejecuta el ciclo de triage, diagnóstico y despacho defensivo de la bandeja de entrada."""
        logger.info(f"Iniciando ciclo de ingesta en el directorio: {self.settings.INBOX_PATH}")
        
        try:
            files = self.storage.list_objects(self.settings.INBOX_PATH)
        except Exception as e:
            logger.error(f"Fie de conexión o lectura en el storage al listar {self.settings.INBOX_PATH}: {e}")
            return

        if not files:
            logger.info("Inbox vacío. No hay documentos pendientes de ingesta.")
            return

        # 1. Estructura del Diccionario de Estrategia (Triage Map)
        dispatch_map = {
            "immediate": [],
            "lazy": [],
            "rejected": []
        }

        # 2. Fase de Reconocimiento y Diagnóstico unitario
        for file_key in files:
            file_path = Path(file_key)
            
            # A. Delta Check rápido (Omite si no hay cambios)
            if not self.delta.needs_processing(file_path):
                logger.info(f"Documento sin cambios detectados por delta: {file_key}. Omitiendo.")
                continue

            # B. Diagnóstico físico a través del Inspector agnóstico
            inspection = self.inspector.inspect(file_path)

            # C. Clasificación defensiva en el mapa de despacho
            if not inspection.is_valid:
                logger.warning(f"Documento corrupto o inválido detectado: {file_key}")
                dispatch_map["rejected"].append({
                    "file_key": file_key,
                    "reason": getattr(inspection, "error_message", "Invalid format")
                })
            elif getattr(inspection, "page_count", 0) > self.settings.MAX_PDF_PAGES or getattr(inspection, "is_complex", False):
                logger.info(f"Documento complejo o excede páginas ({getattr(inspection, 'page_count', 0)}): {file_key}. Derivando a Lazy.")
                dispatch_map["lazy"].append(file_key)
            else:
                dispatch_map["immediate"].append(file_key)

        # 3. Aplicación de la política de batch operativo en inmediatos
        batch_to_process = dispatch_map["immediate"][:self.settings.MAX_BATCH_UPLOAD]
        overflow_to_lazy = dispatch_map["immediate"][self.settings.MAX_BATCH_UPLOAD:]
        dispatch_map["lazy"].extend(overflow_to_lazy)

        # 4. Ejecución del Despacho Final
        self._handle_rejected(dispatch_map["rejected"])
        self._handle_dispatch_valid(batch_to_process, dispatch_map["lazy"])

        logger.info("Ciclo de triage y despacho de IngestionWatcher finalizado correctamente.")

    def _handle_rejected(self, rejected_files: list) -> None:
        """Aisla los archivos defectuosos moviéndolos a la carpeta de fallos y registra auditoría."""
        for item in rejected_files:
            file_key = item["file_key"]
            reason = item["reason"]
            dest_key = f"{self.settings.REJECTS_PATH}{Path(file_key).name}"
            
            try:
                self.storage.move_object(file_key, dest_key)
                self._log_document_status(file_key=file_key, status="REJECTED", details=reason)
                logger.error(f"Archivo aislado en rejects -> {dest_key} | Motivo: {reason}")
            except Exception as e:
                logger.critical(f"Error crítico al mover archivo rechazado {file_key}: {e}")

    def _handle_dispatch_valid(self, immediate_files: list, lazy_files: list) -> None:
        """Despacha los lotes válidos hacia su estrategia de procesamiento correspondiente."""
        if immediate_files:
            logger.info(f"Despachando {len(immediate_files)} archivos para procesamiento INMEDIATO.")
            # Conexión futura con el orquestador inmediato

        if lazy_files:
            logger.info(f"Despachando {len(lazy_files)} archivos a la cola DIFERIDA (Lazy Strategy).")
            # Conexión futura con la cola de procesamiento asíncrono

    def _log_document_status(self, file_key: str, status: str, details: str) -> None:
        """Punto de registro para la trazabilidad atómica en Base de Datos."""
        # Se integrará directamente con el UnitOfWork / MetadataRepository
        pass
    
    
    
    