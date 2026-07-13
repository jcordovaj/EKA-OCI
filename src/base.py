from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from uuid import uuid4

# --- DOM 1: Document Management ---
class Document(BaseModel):
    document_id: UUID4 = Field(default_factory=uuid4)
    filename: str
    binary_hash: str
    current_version: int = 1
    manifesto: Dict[str, Any]
    status: Literal["INBOX", "PROCESSING", "READY", "FAILED"] = "INBOX"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentVersion(BaseModel):
    version_id: UUID4 = Field(default_factory=uuid4)
    document_id: UUID4
    version_number: int
    content_hash: str
    change_summary: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- DOM 2: Knowledge Processing ---
class Chunk(BaseModel):
    chunk_id: UUID4 = Field(default_factory=uuid4)
    version_id: UUID4
    chunk_index: int
    chunk_hash: str
    content: str
    context_header: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Embedding(BaseModel):
    embedding_id: UUID4 = Field(default_factory=uuid4)
    chunk_id: UUID4
    embedding_model: str
    vector: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChunkLineage(BaseModel):
    lineage_id: UUID4 = Field(default_factory=uuid4)
    old_chunk_id: Optional[UUID4]
    new_chunk_id: UUID4
    change_type: Literal["UNCHANGED", "UPDATED", "CREATED", "DELETED"]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- DOM 3 & 4: Control & Agent ---
class ProcessingJob(BaseModel):
    job_id: UUID4 = Field(default_factory=uuid4)
    document_id: UUID4
    stage: str
    status: Literal["PENDING", "RUNNING", "SUCCESS", "FAILED"]
    details: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)