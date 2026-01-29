from pathlib import Path
from typing import Dict, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os

# Definimos el esquema que el LLM debe seguir obligatoriamente
class FileWriterInput(BaseModel):
    """Esquema de entrada para la herramienta de escritura de archivos."""
    files: Dict[str, str] = Field(
        ..., 
        description="Un diccionario donde la clave es la ruta del archivo y el valor es su contenido."
    )

class FileWriterTool(BaseTool):
    name: str = "file_writer"
    description: str = (
        "Escribe múltiples archivos en el disco. "
        "Recibe un diccionario 'files' donde cada clave es una ruta y el valor es el contenido."
    )
    args_schema: Type[BaseModel] = FileWriterInput

    def _run(self, *, files: Dict[str, str]) -> str:
        base_dir = Path(os.getenv("FACTORIA_OUTPUT_DIR", "outputs")).resolve()
        base_dir.mkdir(parents=True, exist_ok=True)

        escritos = []
        try:
            for rel_path, content in files.items():
                target = base_dir / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                escritos.append(rel_path)
            return f"ÉXITO: Archivos creados: {', '.join(escritos)}"
        except Exception as e:
            return f"ERROR: {str(e)}"

# Instanciamos la herramienta para usarla en el agente
file_writer = FileWriterTool()