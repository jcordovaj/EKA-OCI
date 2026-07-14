from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, UTC
from typing import Optional, List, Dict

# ==========================================
# ENUMERATIONS (Fuentes de verdad categóricas)
# ==========================================

class DocumentStatus(str, Enum):
    """Estado del documento en el sistema."""
    PENDING   = "PENDIENTE"        # Recibido, sin procesar.
    INSPECTED = "INSPECCIONADO"    # Clasificado y con estrategia definida.
    PROCESSING_FAILED = "FALLIDO"  # Error en la conversión o procesamiento.
    COMPLETED = "COMPLETADO"       # Markdown generado y artefactos guardados.

class DocumentInspectorResult(str, Enum):
    """Clasificación inicial basada en el análisis documental."""
    SIMPLE         = "SIMPLE"          # Texto limpio, flujo lineal.
    LARGE          = "LARGE"            # Gran volumen de contenido.
    MULTI_DOCUMENT = "MULTI_DOCUMENT" # Varios documentos juntos (PDF/ZIP).
    SCANNED        = "SCANNED"        # Imagen o escaneo requiere Tesseract/OCR (futuro).
    COMPLEX_LAYOUT = "COMPLEX_LAYOUT" # Tablas, columnas, etc. Requiere procesamiento avanzado.
    CORRUPTED      = "CORRUPTED"    # Archivo dañado o ilegible.
    UNSUPPORTED    = "UNSUPPORTED"# Tipo de archivo no admitido en el MVP.

# ==========================================
# DOMAIN MODELS (Pydantic Models)
# ==========================================
storage_uri: Optional[str]
binary_hash: str
size_bytes : int
class Document(BaseModel):
    """Representa el documento tal como fue cargado por el usuario."""
    source_id          : Optional[str] = Field(None, description="ID único generado al cargar.")
    original_filename  : str           = Field(..., description="Nombre original del archivo.");
    #file_bytes         : bytes         = Field(..., description="Contenido binario del documento (temporal).")
    storage_uri        : Optional[str] = Field(None, description="URI del documento almacenado en MinIO/OCI.")
    binary_hash        : str           = Field(..., description="SHA-256 del documento original.")
    size_bytes         : int           = Field(..., ge=0, description="Tamaño del documento en bytes.")
    mime_type          : str           = Field(..., description="Tipo MIME detectado del archivo.");
    ingestion_timestamp: datetime      = Field(default_factory=lambda: datetime.now(UTC), description="Fecha de carga en EKA-OCI.")

class MetadataBundle(BaseModel):
    """Conjunto estructurado de metadatos generados por el Document Inspector."""
    classification    : DocumentInspectorResult # El resultado del triaje inicial.
    suggested_strategy: str       = Field("MARKDOWN_DIRECT", description="Estrategia recomendada (Ej: SIMPLE, COMPLEX_LAYOUT).")
    document_type     : str       = Field(..., description="Tipo de documento (ej: Informe Financiero, Manual Técnico).");
    extracted_keywords: List[str] = Field(default_factory=list, description="Palabras clave detectadas.");
    confidence_score  : float     = Field(1.0, ge=0.0, le=1.0)

class ProcessingJob(BaseModel):
    """Representa un trabajo de procesamiento (Pipeline execution). Vincula el Input con el Output."""
    job_id            : str            = Field(..., description="ID único del job de procesamiento.");
    document_source_id: Optional[str]  = Field(None, description="Referencia al Documento original que generó este job.");
    created_at        : datetime       = Field(default_factory=lambda: datetime.now(UTC));
    status            : DocumentStatus = Field(DocumentStatus.PENDING);
    
    # Output Modelos de Artifacts
    markdown_artifact_bytes: Optional[bytes] = None
    metadata      : MetadataBundle  = Field(..., description="Los metadatos generados durante el job.");
    processing_log: List[str]       = Field(default_factory=list, description="Registro detallado de pasos y advertencias del pipeline.");
