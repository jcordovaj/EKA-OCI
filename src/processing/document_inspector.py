import mimetypes
from pathlib import Path
from dataclasses import dataclass

@dataclass
class InspectionResult:
    # Campos obligatorios primero
    original_filename: str
    mime_type: str
    file_size: int
    file_path: Path
    # Valores por defecto después
    page_count: int = 1
    classification: str = "SIMPLE"

class DocumentInspector:
    """
    Responsabilidad única: Inspeccionar el archivo físico (contenedor).
    """
    
    def inspect(self, file_path: Path) -> InspectionResult:
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        # Obtenemos MIME type basado en extensión
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return InspectionResult(
            original_filename=file_path.name,
            mime_type=mime_type or "application/octet-stream",
            file_size=file_path.stat().st_size,
            file_path=file_path
        )