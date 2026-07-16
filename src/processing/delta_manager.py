import hashlib
import json
from pathlib import Path
from typing import Optional

class DeltaManager:
    """
    Gestiona la detección de cambios (deltas) mediante hashing.
    Vive en processing/ junto a document_inspector.py.
    """
    def __init__(self, registry_path: str = "data/local_registry.json"):
        self.registry_path = Path(registry_path)
        # Asegura que el directorio exista
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text())
        return {}

    def calculate_hash(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def needs_processing(self, file_path: Path) -> bool:
        """Retorna True si el archivo cambió o es nuevo."""
        current_hash = self.calculate_hash(file_path)
        stored_hash = self.registry.get(str(file_path))
        return current_hash != stored_hash

    def update_registry(self, file_path: Path):
        """Marca el archivo como procesado guardando su hash actual."""
        self.registry[str(file_path)] = self.calculate_hash(file_path)
        self.registry_path.write_text(json.dumps(self.registry, indent=2))
        