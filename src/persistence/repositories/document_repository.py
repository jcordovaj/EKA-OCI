# src/persistence/repositories/document_repository.py
from sqlalchemy.orm import Session
from typing import Optional, List
from src.domain.document import Document # Usamos el modelo del dominio para los datos entrantes
from src.persistence.orm.document import Document as ORMDocument

