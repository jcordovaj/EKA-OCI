import logging
import mimetypes
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class InspectionResult:
    def __init__(
        self, 
        is_valid: bool, 
        mime_type: str, 
        classification: str,        # SIMPLE, LARGE, MULTI_DOCUMENT, SCANNED, COMPLEX_LAYOUT, CORRUPTED, UNSUPPORTED, STRUCTURED_DATA
        suggested_strategy: str, 
        page_count: int = 0, 
        error_message: str = None
    ):
        self.is_valid = is_valid
        self.mime_type = mime_type
        self.classification = classification
        self.suggested_strategy = suggested_strategy
        self.page_count = page_count
        self.error_message = error_message

class DocumentInspector:
    def inspect(self, file_path: Path) -> InspectionResult:
        """
        Inspección exhaustiva y agnóstica. No descarta PDFs complejos ni estructurados;
        los clasifica correctamente para que el motor aplique la estrategia adecuada.
        """
        logger.info(f"Inspección exhaustiva de archivo: {file_path}")
        
        if not file_path.exists():
            return InspectionResult(
                is_valid=False, 
                mime_type="application/octet-stream", 
                classification="CORRUPTED", 
                suggested_strategy="REJECT", 
                error_message="File does not exist on disk"
            )

        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"
        ext = file_path.suffix.lower()

        try:
            # 1. Datos Estructurados (JSON / JSONL)
            if ext in [".json", ".jsonl"] or mime_type in ["application/json", "application/x-jsonlines"]:
                return self._inspect_json_structure(file_path, mime_type, ext)

            # 2. Documentos PDF (Con detección de escaneados y complejidad)
            elif mime_type == "application/pdf":
                return self._inspect_pdf_deep(file_path, mime_type)

            # 3. Texto plano, Markdown, CSV
            elif mime_type in ["text/plain", "text/markdown", "text/csv"]:
                return InspectionResult(
                    is_valid=True,
                    mime_type=mime_type,
                    classification="SIMPLE",
                    suggested_strategy="TEXT_TO_MARKDOWN",
                    page_count=1
                )

            # 4. Imágenes
            elif mime_type.startswith("image/"):
                return InspectionResult(
                    is_valid=True,
                    mime_type=mime_type,
                    classification="SCANNED",
                    suggested_strategy="OCR_VISION_PROCESSOR",
                    page_count=1
                )

            else:
                return InspectionResult(
                    is_valid=False,
                    mime_type=mime_type,
                    classification="UNSUPPORTED",
                    suggested_strategy="REJECT",
                    error_message=f"Unsupported format: {mime_type}"
                )

        except Exception as e:
            logger.error(f"Fallo crítico al inspeccionar {file_path}: {e}")
            return InspectionResult(
                is_valid=False,
                mime_type=mime_type,
                classification="CORRUPTED",
                suggested_strategy="REJECT",
                error_message=str(e)
            )

    def _inspect_json_structure(self, file_path: Path, mime_type: str, ext: str) -> InspectionResult:
        with open(file_path, "r", encoding="utf-8") as f:
            if ext == ".jsonl":
                for line in f:
                    if line.strip():
                        json.loads(line)
            else:
                json.load(f)
        
        return InspectionResult(
            is_valid=True,
            mime_type=mime_type,
            classification="STRUCTURED_DATA",
            suggested_strategy="JSON_PARSER_TO_MARKDOWN",
            page_count=1
        )

    def _inspect_pdf_deep(self, file_path: Path, mime_type: str) -> InspectionResult:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
        
        try:
            reader = PdfReader(str(file_path))
            page_count = len(reader.pages)
            
            # Análisis heurístico de texto para detectar si es un PDF escaneado (sin texto extraíble)
            total_text_length = 0
            for i in range(min(page_count, 3)): # Revisa las primeras páginas
                total_text_length += len(reader.pages[i].extract_text() or "")

            if total_text_length < 50 and page_count > 0:
                classification = "SCANNED"
                strategy = "OCR_REQUIRED_PROCESSOR"
            elif page_count > 50:
                classification = "LARGE"
                strategy = "BATCH_CHUNK_PROCESSOR"
            else:
                # Verificación simple de complejidad estructural por cantidad de imágenes incrustadas o tablas
                classification = "SIMPLE"
                strategy = "STANDARD_PROCESSOR"

            return InspectionResult(
                is_valid=True,
                mime_type=mime_type,
                classification=classification,
                suggested_strategy=strategy,
                page_count=page_count
            )
        except PdfReadError as e:
            return InspectionResult(
                is_valid=False,
                mime_type=mime_type,
                classification="CORRUPTED",
                suggested_strategy="REJECT",
                error_message=f"PDF Corruption: {e}"
            )