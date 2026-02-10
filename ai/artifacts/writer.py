from pathlib import Path
from typing import List, Dict

def write_artifacts(artifacts: List[Dict[str, str]], base_dir: Path) -> List[Path]:
    """
    Escribe los artefactos en disco y devuelve la lista de rutas escritas.
    """
    written_files = []
    
    if not artifacts:
        return written_files

    base_dir.mkdir(parents=True, exist_ok=True)

    for artifact in artifacts:
        rel_path = artifact.get("path")
        content = artifact.get("content", "")

        if not rel_path:
            continue

        file_path = (base_dir / rel_path).resolve()
        
        # Seguridad: Evitar Path Traversal
        if not str(file_path).startswith(str(base_dir.resolve())):
            continue

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            written_files.append(file_path)
        except Exception as e:
            print(f"   ❌ Error escribiendo {rel_path}: {e}")

    return written_files