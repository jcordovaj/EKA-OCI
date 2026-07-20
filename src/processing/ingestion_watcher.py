# src/processing/ingestion_watcher.py
import logging
from typing import Any

logger = logging.getLogger(__name__)

class IngestionWatcher:
    def __init__(self, db_session: Any, storage_provider: Any, settings: Any,
                inspector: Any, delta_manager: Any, processor: Any = None):
        self.db = db_session
        self.storage = storage_provider
        self.settings = settings
        self.inspector = inspector
        self.delta = delta_manager
        self.processor = processor

    def run(self) -> None:
        """Ejecuta el ciclo de triage y diagnóstico directamente sobre el Object Storage (OCI/MinIO)."""
        inbox_prefix = self.settings.INBOX_PATH  # Debe ser el prefijo o bucket ej: "inbox/"
        logger.info(f"Iniciando ciclo de ingesta en el object storage [Prefix/Bucket]: {inbox_prefix}")
        
        try:
            # Listado nativo de keys en el Object Storage
            file_keys = self.storage.list_objects(inbox_prefix)
        except Exception as e:
            logger.error(f"Falla de conexión o lectura en el object storage al listar {inbox_prefix}: {e}")
            return

        if not file_keys:
            logger.info("Inbox vacío en Object Storage. No hay objetos pendientes.")
            return

        dispatch_map = {
            "immediate": [],
            "lazy": [],
            "rejected": []
        }

        for file_key in file_keys:
            # Omitir si es directorio raíz o placeholder vacío
            if file_key.endswith('/'):
                continue

            # A. Delta Check basado en Object Key y su metadata/hash en DB
            if not self.delta.needs_processing(file_key):
                logger.info(f"Objeto sin cambios detectados por delta: {file_key}. Omitiendo.")
                continue

            # B. Diagnóstico a través del Inspector consumiendo el stream/objeto remoto
            try:
                inspection = self.inspector.inspect_object(file_key, self.storage)
            except Exception as e:
                logger.error(f"Error al inspeccionar el objeto {file_key}: {e}")
                continue

            # C. Clasificación defensiva
            if not inspection.is_valid:
                logger.warning(f"Objeto corrupto o inválido detectado: {file_key}")
                dispatch_map["rejected"].append({
                    "file_key": file_key,
                    "reason": getattr(inspection, "error_message", "Invalid format")
                })
            elif getattr(inspection, "page_count", 0) > self.settings.MAX_PDF_PAGES or getattr(inspection, "is_complex", False):
                logger.info(f"Objeto complejo o excede páginas: {file_key}. Derivando a Lazy.")
                dispatch_map["lazy"].append(file_key)
            else:
                dispatch_map["immediate"].append(file_key)

        # 3. Aplicación de política de batch
        batch_to_process = dispatch_map["immediate"][:self.settings.MAX_BATCH_UPLOAD]
        overflow_to_lazy = dispatch_map["immediate"][self.settings.MAX_BATCH_UPLOAD:]
        dispatch_map["lazy"].extend(overflow_to_lazy)

        # 4. Ejecución del Despacho Final
        self._handle_rejected(dispatch_map["rejected"])
        self._handle_dispatch_valid(batch_to_process, dispatch_map["lazy"])

        logger.info("Ciclo de triage y despacho en Object Storage finalizado.")

    def _handle_rejected(self, rejected_files: list) -> None:
        """Mueve el objeto defectuoso dentro del Object Storage hacia el prefijo de rechazos."""
        for item in rejected_files:
            file_key = item["file_key"]
            reason = item["reason"]
            file_name = file_key.split('/')[-1]
            dest_key = f"{self.settings.REJECTS_PATH}{file_name}"
            
            try:
                self.storage.move_object(file_key, dest_key)
                logger.error(f"Objeto aislado en rejects -> {dest_key} | Motivo: {reason}")
            except Exception as e:
                logger.critical(f"Error crítico al mover objeto rechazado {file_key}: {e}")

    def _handle_dispatch_valid(self, immediate_files: list, lazy_files: list) -> None:
        """Despacha los objetos válidos al DocumentProcessor nativo de OCI."""
        if immediate_files:
            logger.info(f"Despachando {len(immediate_files)} objetos para procesamiento INMEDIATO.")
            for file_key in immediate_files:
                inspection = self.inspector.inspect_object(file_key, self.storage)
                strategy = getattr(inspection, "strategy", "TEXT_TO_MARKDOWN")
                classification = getattr(inspection, "classification", "STANDARD")
                
                if self.processor:
                    self.processor.process_object(file_key=file_key, strategy=strategy, classification=classification)
                else:
                    logger.warning(f"DocumentProcessor no inyectado para procesar key: {file_key}")

        if lazy_files:
            logger.info(f"Despachando {len(lazy_files)} objetos a la cola DIFERIDA (Lazy Strategy).")
            for file_key in lazy_files:
                inspection = self.inspector.inspect_object(file_key, self.storage)
                strategy = getattr(inspection, "strategy", "DEFERRED_COMPLEX")
                classification = getattr(inspection, "classification", "COMPLEX")
                
                if self.processor:
                    self.processor.process_object(file_key=file_key, strategy=strategy, classification=classification)

    def _log_document_status(self, file_key: str, status: str, details: str) -> None:
        """Punto de registro para la trazabilidad atómica en Base de Datos."""
        # Se integrará directamente con el UnitOfWork / MetadataRepository
        pass
    
    
    
    