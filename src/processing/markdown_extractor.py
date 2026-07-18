from pathlib import Path

class MarkdownExtractor:
    """
    Responsabilidad única: Extraer el contenido de un archivo y convertirlo a Markdown.
    """
    
    def extract(self, file_path: Path) -> str:
        """
        Temporalmente, implementamos una lógica base y progresiva. 
        Siguiente sprint, se integrará la lógica de OCR o parsers de documentos.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"No se puede extraer contenido de un archivo inexistente: {file_path}")
            
        # Simulación de extracción (aquí irá la lógica de conversión real según el tipo de archivo)
        # Por ahora, retornamos un string que simula el contenido en markdown
        return f"# Contenido extraído de {file_path.name}\n\n[Contenido procesado...]"

    def save_as_markdown(self, content: str, original_path: Path) -> Path:
        """Guarda el artefacto resultante en un directorio de salida (ej: artifacts/)."""
        output_dir = Path("data/artifacts")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{original_path.stem}.md"
        output_path.write_text(content, encoding="utf-8")
        return output_path