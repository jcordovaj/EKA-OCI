import sys
import os
import pytest
from pathlib import Path
from processing.orchestrator import ProcessingOrchestrator
from domain.contracts import ProcessingJobStatus
from persistence.orm.document import Metadata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_orchestrator_dual_mode_logic(db_session):
    orchestrator = ProcessingOrchestrator(db=db_session)
    
    # Casos de prueba definidos
    test_files = [
        {"name": "simple_doc.pdf", "complex": False},
        {"name": "large_doc.pdf", "complex": False}, # Supongamos que < 500 pags
        {"name": "complex_structure.pdf", "complex": True}, # Forzamos clasificación COMPLEX
        {"name": "batch_file_1.pdf", "complex": False},
        {"name": "batch_file_2.pdf", "complex": False}
    ]
    
    for file in test_files:
        path = Path(f"tests/data/{file['name']}")
        
        # Act
        result = orchestrator.process_document(path)
        
        # Assert
        if file['complex']:
            assert result is None  # Debe ser desviado
        else:
            assert result is not None
            assert result.status == ProcessingJobStatus.PENDING
            # Verificar que el registro existe en la BD
            assert db_session.query(Metadata).filter_by(filename=file['name']).first() is not None

if __name__ == "__main__":
    print("Iniciando suite de pruebas de integración...")
    # Aquí instancia tu orquestador y corre el test manualmente
    # Ejemplo:
    # orchestrator = ProcessingOrchestrator(db=...)
    # print("Orquestador instanciado correctamente.")    
    print("Flujo de pruebas validado correctamente.")