# ai/tools/file_writer.py

from pathlib import Path
from typing import Dict
from crewai.tools import tool
import os


@tool("file_writer")
def file_writer(files: Dict[str, str]) -> str:
    """
    Escribe múltiples archivos en disco.

    Input:
      files: dict[str, str]
        - clave: ruta relativa del archivo
        - valor: contenido del archivo

    Output:
      str: resumen de archivos escritos
    """
    base_dir = Path(
        os.getenv("FACTORIA_OUTPUT_DIR", "outputs")
    ).resolve()

    base_dir.mkdir(parents=True, exist_ok=True)

    written = []

    for rel_path, content in files.items():
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(str(target))

    return f"Archivos escritos: {len(written)}"