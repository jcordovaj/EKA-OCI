import mimetypes
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class InspectionResult:
    original_filename: str
    mime_type: str
    file_size: int
    object_key: Optional[str] = None
    page_count: int = 1
    classification: str = "SIMPLE"
    is_valid: bool = True
    strategy: str = "TEXT_TO_MARKDOWN"
    is_complex: bool = False
    error_message: Optional[str] = None

class DocumentInspector:
    """
    Responsabilidad única: Inspeccionar el objeto en el Object Storage (OCI-Native) o archivo físico.
    """
    # Declaración correcta de umbrales como atributos de clase
    MAX_BYTES_SIMPLE = 2 * 1024 * 1024  # 2 MB
    MAX_BYTES_COMPLEX = 10 * 1024 * 1024 # 10 MB
    
    def inspect(self, file_path: Path) -> InspectionResult:
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        mime_type, _ = mimetypes.guess_type(file_path)
        file_size = file_path.stat().st_size
        
        return InspectionResult(
            original_filename=file_path.name,
            mime_type=mime_type or "application/octet-stream",
            file_size=file_size,
            file_path=str(file_path),
            page_count=1,
            is_valid=True
        )

    def inspect_object(self, object_key: str, storage_provider) -> InspectionResult:
        """
        Aplica reglas de negocio combinadas:
        1. Validación de integridad estructural y mitigación de archivos corruptos.
        2. Evaluación agnóstica de formato (PDF, TXT, MD, etc.).
        3. Optimización económica de tokens (evitar procesamiento redundante en TXT/MD limpios).
        4. Control de volumen/complejidad por tamaño equivalente para evitar saturación.
        """
        filename = object_key.split('/')[-1]
        mime_type, _ = mimetypes.guess_type(filename)
        ext = filename.lower().split('.')[-1] if '.' in filename else ""
        
        file_size = 0
        is_valid = True
        error_message = None
        stream_bytes = b""

        # FASE 1: Mitigación de corrupción y lectura de bytes iniciales
        try:
            response = storage_provider.client.head_object(Bucket=storage_provider.bucket, Key=object_key)
            file_size = response.get('ContentLength', 0)
            
            stream = storage_provider.get_object_stream(object_key)
            stream_bytes = stream.read(2048) # Muestra representativa para análisis heurístico
            
            # Regla defensiva anti-corrupción general para PDFs
            if ext == 'pdf' and not stream_bytes.startswith(b'%PDF'):
                is_valid = False
                error_message = "Estructura de PDF corrupta o inválida (Ausencia de magic bytes %PDF)."
            
            # Regla defensiva para archivos vacíos o 'basura' extrema de 0 bytes
            if file_size == 0:
                is_valid = False
                error_message = "El archivo se encuentra vacío o corrupto (0 bytes)."

        except Exception as e:
            is_valid = False
            error_message = f"Falla crítica al leer metadatos o stream del objeto: {str(e)}"

        if not is_valid:
            return InspectionResult(
                original_filename=filename,
                mime_type=mime_type or "application/octet-stream",
                file_size=file_size,
                object_key=object_key,
                is_valid=False,
                strategy="ERROR_ROUTER",
                error_message=error_message
            )

        # FASE 2: Lógica combinada de economía de tokens y formato
        # Si ya es un .md o .txt, evaluamos su dimensión equivalente (ej. si un .md pesa gigas o tiene miles de líneas)
        is_volumetric_heavy   = file_size > self.MAX_BYTES_COMPLEX
        is_moderately_complex = file_size > self.MAX_BYTES_SIMPLE

        if ext == 'md':
            # Regla: Si el .md es liviano, va directo a procesados/passthrough sin gastar conversión. 
            # Si excede el umbral volumétrico equivalente, se cataloga como complejo para derivación o control.
            strategy = "COMPLEX_PASSTHROUGH" if is_volumetric_heavy else "MARKDOWN_PASSTHROUGH"
            classification = "COMPLEX" if is_volumetric_heavy else "SIMPLE"
        elif ext == 'txt':
            # Regla: Los TXT tienen economía mínima de conversión, van directo a salida con bajo costo de vectorización.
            strategy = "COMPLEX_PASSTHROUGH" if is_volumetric_heavy else "TEXT_PASSTHROUGH"
            classification = "COMPLEX" if is_volumetric_heavy else "SIMPLE"
        elif ext == 'pdf':
            # Regla tradicional optimizada para PDFs que sí requieren conversión masiva de tokens
            if is_volumetric_heavy:
                strategy = "DEFERRED_COMPLEX"
                classification = "COMPLEX"
            else:
                strategy = "TEXT_TO_MARKDOWN"
                classification = "SIMPLE"
        else:
            # Fallback agnóstico defensivo para otros binarios o formatos no contemplados
            strategy = "TEXT_TO_MARKDOWN"
            classification = "COMPLEX" if is_volumetric_heavy else "SIMPLE"

        return InspectionResult(
            original_filename=filename,
            mime_type=mime_type or "application/octet-stream",
            file_size=file_size,
            object_key=object_key,
            page_count=1, # Se puede estimar proporcionalmente al tamaño si se requiere
            classification=classification,
            is_valid=True,
            strategy=strategy,
            is_complex=is_volumetric_heavy
        )