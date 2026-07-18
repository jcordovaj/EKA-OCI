from pathlib import Path
from processing.document_inspector import DocumentInspector

def test_inspector():
    # Setup: Archivo temporal
    inbox_path = Path("data/inbox")
    inbox_path.mkdir(parents=True, exist_ok=True)
    test_file = inbox_path / "test_doc.pdf"
    test_file.write_text("dummy content")
    
    # Ejecución
    inspector = DocumentInspector()
    result = inspector.inspect(test_file)
    
    # Validaciones
    assert result.original_filename == "test_doc.pdf"
    assert result.file_size > 0
    assert result.mime_type == "application/pdf"
    
    # Limpieza
    test_file.unlink()
    print("INSPECTOR TEST PASSED")

if __name__ == "__main__":
    test_inspector()