from pathlib import Path
from processing.document_inspector import DocumentInspector, InspectionResult
from processing.metadata_generator import MetadataGenerator

def test_metadata_generation():
    # 1. Setup: Simular datos de entrada de etapas previas
    fake_path = Path("data/inbox/test.pdf")
    inspection = InspectionResult(
        original_filename="test.pdf",
        mime_type="application/pdf",
        file_size=1024,
        file_path=fake_path
    )
    md_content = "# Título del Documento\nEste es un contenido de prueba para el manifesto."
    
    # 2. Generar Manifesto
    gen = MetadataGenerator()
    manifesto = gen.generate(inspection, md_content)
    
    # 3. Validaciones
    assert manifesto.filename == "test.pdf"
    assert manifesto.mime_type == "application/pdf"
    assert "Título del Documento" in manifesto.content_summary
    assert manifesto.status == "PROCESSED"
    
    print("METADATA GENERATOR TEST PASSED")

if __name__ == "__main__":
    test_metadata_generation()