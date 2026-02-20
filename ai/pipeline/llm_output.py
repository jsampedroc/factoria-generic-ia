import json
import re

def clean_imports(imports_list):
    """Limpia el error de 'import import ...;;'"""
    cleaned = []
    if not imports_list: return cleaned
    
    for imp in imports_list:
        # Eliminamos la palabra 'import', puntos y coma y espacios
        item = imp.replace("import ", "").replace(";", "").strip()
        if item and item not in cleaned:
            cleaned.append(item)
    return cleaned

def normalize_llm_output(raw_output: str) -> dict:
    if not raw_output: return {"status": "ERROR"}
    
    # Limpiar bloques de código markdown
    cleaned = re.sub(r'```json\s*|```', '', raw_output).strip()
    
    try:
        data = json.loads(cleaned)
    except:
        match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
        if match:
            try: data = json.loads(match.group(1))
            except: return {"status": "ERROR", "message": "JSON irreparable"}
        else:
            return {"status": "ERROR", "message": "No JSON found"}

    # PROCESADO DE IMPORTS: Evitamos el doble import antes de que llegue al writer
    if isinstance(data, dict) and "imports" in data:
        data["imports"] = clean_imports(data["imports"])

    return data