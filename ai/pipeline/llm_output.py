import json
import re

def normalize_llm_output(raw_output: str) -> dict:
    if not raw_output:
        return {"status": "ERROR", "message": "Empty output"}

    # 1. Limpieza de Markdown
    cleaned = re.sub(r'```json\s*', '', raw_output)
    cleaned = re.sub(r'```\s*$', '', cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # 2. Reparación de JSON Truncado (Caso de archivos Java largos)
        # Si detectamos que es un objeto de artefacto pero le falta el cierre
        if '"path":' in cleaned and '"content":' in cleaned:
            # Intentamos cerrar el string del 'content' y el objeto
            # Buscamos si el último carácter no es }
            if not cleaned.endswith('"}'):
                # Eliminamos posibles caracteres rotos al final y cerramos
                repaired = cleaned.rstrip()
                # Si termina en una barra de escape o comilla, la limpiamos
                repaired = re.sub(r'\\+$', '', repaired)
                if not repaired.endswith('"'): repaired += '"'
                if not repaired.endswith('}'): repaired += '}'
                try:
                    return json.loads(repaired)
                except: pass

        # 3. Búsqueda por Regex del bloque principal
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except: pass

        return {"status": "ERROR", "message": "JSON irreparable", "raw": raw_output}