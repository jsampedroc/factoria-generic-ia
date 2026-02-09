import json
import re

def normalize_llm_output(raw_output: str) -> dict:
    if not raw_output: return {"status": "ERROR"}
    
    # Limpiar markdown
    cleaned = re.sub(r'```json\s*|```', '', raw_output).strip()
    
    # REPARACIÓN: Si el JSON terminó a la mitad (común en archivos grandes)
    if cleaned.startswith('{') and not cleaned.endswith('}'):
        # Intentamos cerrar el campo "content" y el objeto
        if '"content":' in cleaned:
            cleaned = cleaned.rstrip()
            if not cleaned.endswith('"'): cleaned += '"'
            if not cleaned.endswith('}'): cleaned += '}'

    try:
        return json.loads(cleaned)
    except:
        # Fallback: Extraer el primer bloque JSON válido que encuentre
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: pass
        return {"status": "ERROR", "message": "JSON irreparable", "raw": raw_output}