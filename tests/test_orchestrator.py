from pathlib import Path
from processing.orchestrator import ProcessingOrchestrator

def test_orchestrator():
    # Setup
    inbox = Path("data/inbox")
    inbox.mkdir(parents=True, exist_ok=True)
    test_file = inbox / "orchestrator_test.pdf"
    test_file.write_text("Contenido para el orquestador")
    
    # Ejecución
    orchestrator = ProcessingOrchestrator()
    manifesto = orchestrator.process_document(test_file)
    
    # Validaciones
    assert manifesto.filename == "orchestrator_test.pdf"
    assert Path("data/artifacts/orchestrator_test.md").exists()
    
    # Limpieza
    test_file.unlink()
    Path("data/artifacts/orchestrator_test.md").unlink()
    print("ORCHESTRATOR TEST PASSED")

if __name__ == "__main__":
    test_orchestrator()