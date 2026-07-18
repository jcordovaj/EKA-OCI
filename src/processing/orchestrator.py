import os
from pathlib import Path
from sqlalchemy.orm import Session 
from core.settings import Settings
from domain.contracts import ProcessingJobStatus, FileStorageProvider
from processing.document_inspector import DocumentInspector
from processing.markdown_extractor import MarkdownExtractor
from processing.metadata_generator import MetadataGenerator, MetadataManifesto
from persistence.repositories.metadata_repository import MetadataRepository

class ProcessingOrchestrator:
    def __init__(self, db_session: Session, repo, storage_provider: FileStorageProvider):
        self.db           = db_session
        self.repo         = repo
        self.storage      = storage_provider
        self.config       = Settings()
        self.inspector    = DocumentInspector()
        self.extractor    = MarkdownExtractor()
        self.metadata_gen = MetadataGenerator()

    def _move_to_storage(self, file_path: Path, bucket_folder: str):
        destination = f"{bucket_folder}/{file_path.name}"
        self.storage.upload(str(file_path), destination)
        os.remove(file_path)

    def process_document(self, file_path: Path):
        job = self.repo.create_job(file_path.name, status=ProcessingJobStatus.PENDING)
        self.db.commit()
        
        try:
            inspection = self.inspector.inspect(file_path)
            
            if self._is_complex(inspection):
                self.repo.update_job(job.id, status=ProcessingJobStatus.FAILED)
                self._move_to_storage(file_path, "complex")
                return None
            
            raw_content = self.extractor.extract(file_path)
            manifesto = self.metadata_gen.generate(inspection, raw_content)
            
            self.repo.save_metadata(job.id, manifesto) 
            self.repo.update_job(job.id, status=ProcessingJobStatus.COMPLETED)
            self._move_to_storage(file_path, "processed")
            
            self.db.commit()
            return manifesto
            
        except Exception as e:
            self.db.rollback()
            self.repo.update_job(job.id, status=ProcessingJobStatus.FAILED)
            self._move_to_storage(file_path, "rejected")
            raise

    def _is_complex(self, inspection) -> bool:
        return inspection.page_count > self.config.MAX_PDF_PAGES or inspection.classification == "COMPLEX"