from pydantic import BaseModel, Field

class UploadDocument(BaseModel):
    original_filename: str
    mime_type: str
    file_bytes: bytes = Field(...)