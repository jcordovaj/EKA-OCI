import mimetypes
from pathlib import Path
from dataclasses import dataclass
from dataclasses import dataclass

@dataclass
class InspectionResult:
    original_filename: str
    mime_type: str
    file_size: int
    file_path: Path
    page_count: int         # Añadido para cumplimiento de D6
    classification: str

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