# src/persistence/repositories/abstract_repository.py
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Optional, Any

# Definimos un tipo genérico para el modelo de SQLAlchemy (Type safety)
T = TypeVar('T')

class AbstractRepository(ABC, Generic[T]):
    """
    Clase base abstracta que define los contratos estándar de acceso a datos.
    Cualquier repositorio concreto debe heredar de esta clase.
    """
    def __init__(self, model: type[T]):
        # El modelo SQLAlchemy (Document, ProcessingJob, etc.) es el argumento inicial
        self.model = model

    @abstractmethod
    def get_by_id(self, db: Session, record_id: int) -> Optional[T]:
        """Busca un registro por su ID primario."""
        pass

    @abstractmethod
    def create(self, db: Session, **data: Any) -> T:
        """Crea y persiste una nueva instancia del modelo en la sesión de DB."""
        pass

    @abstractmethod
    def update(self, db: Session, record_id: int, updates: dict[str, Any]) -> Optional[T]:
        """Actualiza un registro existente con datos parciales."""
        pass

    @abstractmethod
    def delete(self, db: Session, record_id: int) -> bool:
        """Elimina un registro por ID."""
        pass
