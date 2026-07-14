# src/persistence/orm/document.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON, func
from sqlalchemy.orm import relationship
from datetime import datetime

# Asumimos que 'Base' ha sido definido previamente en la capa de ORM o se importa:
from src.persistence.orm.base import Base # Asumiendo una clase base para las tablas

# ==========================================
# 1. Documento (El Contenedor Fuente)
# Mapea la entidad 'Document' del dominio.
# ==========================================
class Document(Base):
    __tablename__ = "documentos"
    # PRIMARY KEY: El ID gestionado por la BD.
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Atributos directos del dominio
    original_filename = Column(String, nullable=False, index=True)
    mime_type = Column(String, nullable=False)
    ingestion_timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Referencias a objetos relacionados:
    # Debe haber al menos un job de procesamiento asociado por defecto.
    processing_jobs = relationship("ProcessingJob", back_populates="document_source")

    # Nota: Los bytes de archivo (file_bytes) son mejores para manejar en Object Storage 
    # y solo se almacenará la referencia o hash aquí, no el binario completo.

# ==========================================
# 2. MetadataBundle (Los Atributos Generados)
# Mapea el Bundle de Metadatos generado por el Inspector.
# ==========================================
class Metadata(Base):
    """Almacena los metadatos clave generados durante el procesamiento."""
    __tablename__ = "metadata_artifacts"
    id = Column(Integer, primary_key=True)

    # FOREIGN KEY: Relaciona este metadata con un job específico.
    job_id = Column(Integer, ForeignKey("processing_jobs.id"), nullable=False, unique=True)

    classification = Column(String, nullable=False, index=True) # Enum del InspectorResult
    suggested_strategy = Column(String, nullable=False)        # Estrategia detectada
    document_type = Column(String, nullable=False)           # Tipo de contenido (ej: 'Reporte')
    confidence_score = Column(Float, default=1.0)            # Score de confianza

    # Campos flexibles para keywords y otros datos semiestructurados
    extracted_keywords = Column(JSON, default=[]) # Usamos JSONB si es PostgreSQL real
    created_at = Column(DateTime, default=func.now())

    # Relación con el Job que generó estos metadatos.
    job: "ProcessingJob" = relationship("ProcessingJob", back_populates="metadata")


# ==========================================
# 3. ProcessingJob (El Registro del Flujo)
# Mapea la entidad 'ProcessingJob'. Contiene el historial y las referencias de salida.
# ==========================================
class ProcessingJob(Base):
    """Registro maestro del proceso de ingestión/procesamiento."""
    __tablename__ = "processing_jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)

    # FOREIGN KEY: Referencia al documento fuente.
    document_source_id = Column(Integer, ForeignKey("documentos.id"), nullable=False)

    status = Column(String, nullable=False) # Status (Enum del dominio)
    created_at = Column(DateTime, default=func.now(), index=True)
    last_updated = Column(DateTime, default=func.now())

    # Referencias a los artifacts y metadatos generados:
    metadata: "Metadata" = relationship("Metadata", back_populates="job")
    
    # EL ARTEFACTO (el archivo Markdown final o JSON de artefactos)
    markdown_artifact_uri = Column(String, nullable=True, index=True) 
    # Nota crítica: NO guardamos los bytes; solo la URI donde MinIO/OCI lo almacenan.

    processing_log = Column(JSON, default=[]) # Lista para almacenar mensajes de log detallados

    # Relación con el Documento Fuente (para navegación en SQLAlchemy)
    document_source = relationship("Document", back_populates="processing_jobs")

# ... Aquí irían otros modelos si se necesita historial de versiones o chunking avanzado.
