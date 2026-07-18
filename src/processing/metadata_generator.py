from pathlib import Path
from dataclasses import dataclass, asdict
from domain.contracts import ProcessingJobStatus
from processing.document_inspector import InspectionResult

@dataclass
class MetadataManifesto:
    filename: str
    mime_type: str
    file_size: int
    content_summary: str
    classification: str     
    document_type: str      
    page_count: int         
    status: ProcessingJobStatus  # Se usa el Enum, no un string plano

class MetadataGenerator:
    """
    Responsabilidad única: Construir el manifesto a partir de los datos físicos 
    y el contenido extraído.
    """
    
    def generate(self, inspection: InspectionResult, markdown_content: str) -> MetadataManifesto:
        # Lógica de resumen determinista para MVP
        summary = markdown_content[:200] + "..."
        
        return MetadataManifesto(
            filename=inspection.original_filename,
            mime_type=inspection.mime_type,
            file_size=inspection.file_size,
            content_summary=summary,
            classification=inspection.classification,
            document_type="TEXT_PDF" if inspection.page_count > 0 else "UNKNOWN",
            page_count=inspection.page_count,
            status=ProcessingJobStatus.PENDING # Uso del Enum
        )

    def to_dict(self, manifesto: MetadataManifesto) -> dict:
        # Convertimos a dict asegurando que el Enum se serialice bien
        data = asdict(manifesto)
        data['status'] = manifesto.status.value 
        return data
    