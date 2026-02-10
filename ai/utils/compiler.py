import subprocess
import re
from pathlib import Path

def run_maven_compile(project_dir: Path):
    """
    Ejecuta mvn compile y devuelve una lista de errores con rutas RELATIVAS 
    al directorio del proyecto.
    """
    try:
        print(f"DEBUG: Ejecutando Maven en {project_dir}")
        result = subprocess.run(
            ['mvn', 'clean', 'compile'],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return []

        # Regex mejorada para capturar la ruta y el mensaje
        # El patrón busca: [ERROR] ruta:[linea,columna] mensaje
        error_pattern = re.compile(r"\[ERROR\]\s+(.*?\.java):\[(\d+),(\d+)\]\s+(.*)")
        errors = []
        
        for line in result.stdout.split('\n'):
            match = error_pattern.search(line)
            if match:
                full_path_str = match.group(1)
                message = match.group(4)
                
                # Convertimos la ruta absoluta de Maven en ruta relativa al proyecto
                try:
                    full_path = Path(full_path_str)
                    # Si la ruta es absoluta, intentamos hacerla relativa al project_dir
                    if full_path.is_absolute():
                        rel_path = full_path.relative_to(project_dir)
                    else:
                        rel_path = full_path
                except ValueError:
                    # Si falla (por ejemplo, el error es en un archivo fuera del proyecto)
                    # intentamos limpiar la ruta manualmente o la dejamos como está
                    rel_path = full_path_str

                errors.append({
                    "file": str(rel_path),
                    "line": match.group(2),
                    "message": message
                })
        
        # Eliminar duplicados (a veces Maven reporta el mismo error varias veces)
        unique_errors = { (e['file'], e['message']): e for e in errors }.values()
        
        return list(unique_errors)

    except Exception as e:
        print(f"❌ Error al ejecutar Maven: {e}")
        return []