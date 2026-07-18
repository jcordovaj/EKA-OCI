from enum import Enum
from typing import Protocol

class FileStorageProvider(Protocol):
    def upload(self, local_path: str, destination: str) -> None: ...
    def delete(self, remote_path: str) -> None: ...    

class PipelineStage(Enum):
    HASHING     = "HASHING"
    INSPECTION  = "INSPECTION"
    EXTRACTION  = "EXTRACTION"
    METADATA    = "METADATA"
    PERSISTENCE = "PERSISTENCE"

class ProcessingJobStatus(Enum):
    PENDING                = "PENDING"
    RUNNING                = "RUNNING"
    SUCCESS                = "SUCCESS"
    FAILED                 = "FAILED"
    ROLLED_BACK            = "ROLLED_BACK"
    SKIPPED                = "SKIPPED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    