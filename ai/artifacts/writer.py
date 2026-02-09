from pathlib import Path
from typing import List, Dict

def write_artifacts(artifacts: List[Dict[str, str]], base_dir: Path) -> List[Path]:
    """
    Escribe los artefactos generados en disco, creando las subcarpetas necesarias.
    Cada artefacto debe ser: {"path": "ruta/al/archivo.py", "content": "..."}
    """
    written_files = []
    
    if not artifacts:
        print("⚠️ No hay artefactos para escribir.")
        return written_files

    # Asegurar que el directorio base existe
    base_dir.mkdir(parents=True, exist_ok=True)

    for artifact in artifacts:
        rel_path = artifact.get("path")
        content = artifact.get("content", "")

        if not rel_path:
            continue

        # Crear la ruta completa del archivo
        file_path = (base_dir / rel_path).resolve()
        
        # Seguridad: Evitar escribir fuera del base_dir (Path Traversal)
        if not str(file_path).startswith(str(base_dir.resolve())):
            print(f"🚫 Intento de escritura fuera de rango saltado: {rel_path}")
            continue

        try:
            # 1. CREAR CARPETAS PADRE (Crítico para Java/Spring Boot)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 2. ESCRIBIR CONTENIDO
            # Usamos utf-8 para evitar errores en Windows/Unix
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            written_files.append(file_path)
            print(f"📄 Escrito: {rel_path}")

        except Exception as e:
            print(f"❌ Error escribiendo {rel_path}: {e}")

    return written_files