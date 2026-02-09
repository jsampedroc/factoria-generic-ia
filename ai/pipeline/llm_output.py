import json
import re

def normalize_llm_output(raw_output: str) -> dict:
    if not raw_output:
        return {"status": "ERROR", "message": "Empty output"}

    # Eliminar bloques de código markdown si existen
    cleaned = re.sub(r'```json\s*', '', raw_output)
    cleaned = re.sub(r'```\s*$', '', cleaned)
    cleaned = cleaned.strip()

    # Si el JSON está truncado (no cierra con }), intentamos cerrarlo mínimamente
    # para que al menos no rompa el script, aunque los datos estén incompletos.
    if cleaned.startswith('{') and not cleaned.endswith('}'):
        cleaned += '"}]}' # Intento de cierre de emergencia para el array de artifacts

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Intento final: buscar el primer { y el último }
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end+1])
            except:
                pass
        
        print(f"⚠️ Error crítico de formato. Longitud: {len(raw_output)} chars.")
        return {"status": "ERROR", "raw_payload": raw_output}