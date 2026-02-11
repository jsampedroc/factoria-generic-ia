import subprocess

def run_fast_lint(file_path):
    """Linter ultra-rápido que no consume tokens."""
    if file_path.endswith(".py"):
        # Solo errores críticos de sintaxis
        res = subprocess.run(["python", "-m", "py_compile", file_path], capture_output=True)
        return res.returncode == 0, res.stderr.decode()
    
    if file_path.endswith(".java"):
        # Verificación básica de llaves balanceadas antes de Maven
        with open(file_path, 'r') as f:
            content = f.read()
            return content.count('{') == content.count('}'), "Error: Llaves desbalanceadas"
    
    return True, ""