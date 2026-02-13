from pathlib import Path
import re

def calculate_package(file_path: str) -> str:
    """Extrae el package name de una ruta standard de Java."""
    path_parts = list(Path(file_path).parts)
    if "java" in path_parts:
        idx = path_parts.index("java")
        package_parts = path_parts[idx+1:-1]
        return ".".join(package_parts)
    return "com.gen.default"

def slugify(text: str) -> str:
    """Nombre seguro para el archivo de especificaciones."""
    text = text.lower()
    text = re.sub(r'[áéíóúñ]', 'a', text)
    return re.sub(r'[\W_]+', '_', text).strip('_')[:50]