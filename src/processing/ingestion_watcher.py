# src/processing/ingestion_watcher.py
import logging
from sqlalchemy.orm import Session
from domain.contracts import FileStorageProvider
from processing.orchestrator import ProcessingOrchestrator
from persistence.repositories.orchestrator_repository import OrchestratorRepository

class IngestionWatcher:
    def __init__(self, db_session: Session, storage_provider: FileStorageProvider):
        self.db = db_session  # Guardamos la sesión
        self.storage = storage_provider
        # Usamos la fachada unificada para gestionar los repositorios
        self.repo_facade = OrchestratorRepository(db_session)
        # El orquestador ahora recibe la fachada o los repositorios específicos
        self.orchestrator = ProcessingOrchestrator(db_session, self.repo_facade, storage_provider)

    def run(self):
        """Escanea el inbox y procesa archivos nuevos."""
        files = self.storage.list_objects("inbox/")
        if not files:
            print("No hay archivos en inbox.")
            return

        for file_key in files:
            try:
                # 1. Procesar
                self.orchestrator.process_document(file_key)
                
                # 2. Cierre del autómata (CRÍTICO)
                self.storage.move(file_key, "processed/" + file_key.split('/')[-1])
                print(f"Archivo {file_key} procesado y movido exitosamente.")
                
            except Exception as e:
                # 3. Gestión de errores (mover a 'failed/' si el proceso falla)
                self.storage.move(file_key, "failed/" + file_key.split('/')[-1])
                print(f"Error procesando {file_key}: {e}")  
                
                # El movimiento a 'rejected' ya es gestionado por el Orchestrator 
                # en caso de fallo, manteniendo la atomicidad.