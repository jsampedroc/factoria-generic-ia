from pathlib import Path
from typing import Dict, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import re

class FileWriterInput(BaseModel):
    files: Dict[str, str] = Field(..., description="Diccionario de archivos y contenido.")

class FileWriterTool(BaseTool):
    name: str = "file_writer"
    description: str = "Escribe archivos y sanea RUTAS DE DOCKER obligatoriamente."
    args_schema: Type[BaseModel] = FileWriterInput

    def _run(self, *, files: Dict[str, str]) -> str:
        base_dir = Path(os.getenv("FACTORIA_OUTPUT_DIR", "outputs")).resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        escritos = []

        print(f"\n[FILE_WRITER] Iniciando escritura en: {base_dir}")

        try:
            for rel_path, content in files.items():
                # 1. Aplanar la ruta del archivo (que siempre caiga en la raíz de outputs/)
                filename = os.path.basename(rel_path)
                if "src/" in rel_path:
                    clean_path = "src/" + rel_path.split("src/")[-1]
                else:
                    clean_path = filename

                # 2. LIMPIEZA TOTAL DE CONTENIDO
                # Forzamos la eliminación de cualquier ruta que empiece por 'output'
                if "Dockerfile" in clean_path or "docker-compose" in clean_path:
                    print(f"[FILE_WRITER] Corrigiendo rutas en: {clean_path}")
                    # Borra 'output/backend/', 'output/frontend/', 'output/', etc.
                    content = re.sub(r'output/(backend|frontend)/', '', content)
                    content = content.replace('output/', '')
                    # Por si el agente puso rutas absolutas o relativas raras
                    content = content.replace('./output/', '')

                target = base_dir / clean_path
                target.parent.mkdir(parents=True, exist_ok=True)
                
                target.write_text(content, encoding="utf-8")
                escritos.append(str(clean_path))
                print(f"[FILE_WRITER] Archivo guardado: {clean_path}")
                
            return f"SANEAMIENTO OK: {', '.join(escritos)}"
        except Exception as e:
            print(f"[FILE_WRITER] ERROR: {str(e)}")
            return f"ERROR: {str(e)}"

file_writer = FileWriterTool()