from pathlib import Path
from processing.document_inspector import DocumentInspector
from processing.markdown_extractor import MarkdownExtractor

def test_pipeline_first_steps():
    # Setup
    inbox = Path("data/inbox")
    artifacts = Path("data/artifacts")
    inbox.mkdir(parents=True, exist_ok=True)
    
    test_file = inbox / "pipeline_test.pdf"
    test_file.write_text("Contenido ficticio de PDF")
    
    # 1. Inspector
    inspector = DocumentInspector()
    inspection_result = inspector.inspect(test_file)
    assert inspection_result.original_filename == "pipeline_test.pdf"
    
    # 2. Extractor
    extractor = MarkdownExtractor()
    content = extractor.extract(inspection_result.file_path)
    md_path = extractor.save_as_markdown(content, inspection_result.file_path)
    
    # Validaciones
    assert md_path.exists()
    assert md_path.suffix == ".md"
    assert "Contenido extraído" in md_path.read_text()
    
    # Limpieza
    test_file.unlink()
    md_path.unlink()
    print("PIPELINE STEP 1-2 TEST PASSED")

if __name__ == "__main__":
    test_pipeline_first_steps()
    