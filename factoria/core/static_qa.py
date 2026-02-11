import subprocess
from pathlib import Path

class StaticQA:
    @staticmethod
    def check_python(file_path):
        """Ejecuta flake8 para verificar sintaxis y estilo en Python."""
        result = subprocess.run(['flake8', str(file_path), '--count', '--select=E9,F63,F7,F82'], 
                                capture_output=True, text=True)
        return result.returncode == 0, result.stdout

    @staticmethod
    def check_java(file_path):
        """En Java, confiamos en el check de Maven que ya tienes, 
        pero podríamos añadir un linter ligero aquí."""
        # Por ahora, devolvemos True si el archivo existe
        return Path(file_path).exists(), ""

def run_static_qa(file_path):
    ext = Path(file_path).suffix
    qa = StaticQA()
    if ext == ".py":
        return qa.check_python(file_path)
    return True, "" # Java se valida en la Fase 5 (Maven)