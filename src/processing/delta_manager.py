import hashlib
import logging
from typing import Any
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DeltaManager:
    """
    Gestiona la detección de cambios (deltas) mediante hashing y control de versiones 
    relacionando 'documentos' y 'processing_jobs'.
    """
    def __init__(self, db_session: Any = None):
        self.db_session = db_session

    def calculate_hash_from_stream(self, stream) -> str:
        """Calcula el SHA-256 directamente desde un stream de bytes."""
        sha256 = hashlib.sha256()
        for chunk in iter(lambda: stream.read(8192), b""):
            sha256.update(chunk)
        stream.seek(0)
        return sha256.hexdigest()

    def needs_processing(self, object_key: str, storage_provider: Any = None) -> bool:
        """
        Verifica en BBDD si el documento ya fue procesado con éxito o si su hash (binary_hash) cambió.
        """
        filename = object_key.split('/')[-1]

        if not self.db_session:
            return True

        try:
            # Consulta adaptada al esquema relacional real (documentos <-> processing_jobs)
            query = text("""
                SELECT pj.status, d.binary_hash 
                FROM processing_jobs pj
                JOIN documentos d ON pj.document_source_id = d.id
                WHERE d.original_filename = :filename 
                ORDER BY pj.created_at DESC 
                LIMIT 1;
            """)
            result = self.db_session.execute(query, {"filename": filename}).fetchone()
            
            if not result:
                logger.info(f"Documento nuevo detectado (sin historial previo): {filename}")
                return True

            last_status, last_hash = result

            if last_status == 'COMPLETED':
                if storage_provider:
                    try:
                        stream = storage_provider.get_object_stream(object_key)
                        current_hash = self.calculate_hash_from_stream(stream)
                        
                        if last_hash and last_hash == current_hash:
                            logger.info(f"Idempotencia estricta: El archivo '{filename}' ya registra estado COMPLETED y su hash coincide. Omitiendo.")
                            return False
                        else:
                            logger.info(f"Cambio de versión detectado: El archivo '{filename}' modificó su contenido (binary_hash). Se procesará de nuevo.")
                            return True
                    except Exception as e:
                        logger.warning(f"No se pudo recalcular el stream hash para deltas en {object_key}: {e}")
                
                logger.info(f"El documento '{filename}' ya registra estado COMPLETED. Omitiendo por defecto.")
                return False

        except Exception as e:
            logger.warning(f"Error al consultar el delta relacional en BBDD para {object_key}: {e}")

        return True

    def update_registry(self, object_key: str, current_hash: str) -> None:
        """
        Actualiza el binary_hash en la tabla 'documentos' y el estado del job asociado.
        """
        filename = object_key.split('/')[-1]

        if not self.db_session:
            return

        try:
            query = text("""
                UPDATE documentos 
                SET binary_hash = :current_hash, status = 'COMPLETED'
                WHERE original_filename = :filename;
            """)
            self.db_session.execute(query, {"current_hash": current_hash, "filename": filename})
            self.db_session.commit()
            logger.info(f"Registro delta actualizado en la entidad 'documentos' para: {filename} [Hash: {current_hash[:8]}...]")
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error crítico al actualizar el registro delta para {object_key}: {e}")
            