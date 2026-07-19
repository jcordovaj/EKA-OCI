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
        
        for file_key in files:
            if file_key.endswith('/'): 
                continue
            
            filename = file_key.split('/')[-1]
            
            # Idempotencia: Consultamos mediante la fachada unificada
            if self.repo_facade.get_job_by_filename(filename):
                print(f"Archivo ya registrado en BD: {filename}. Saltando.")
                continue
            
            try:
                print(f"Iniciando proceso: {file_key}")
                self.orchestrator.process_document(file_key)
            except Exception as e:
                logging.error(f"Falla crítica en ingesta de {file_key}: {e}")
                
                # El movimiento a 'rejected' ya es gestionado por el Orchestrator 
                # en caso de fallo, manteniendo la atomicidad.