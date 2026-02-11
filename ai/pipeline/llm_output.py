import re
import json

def normalize_llm_output(raw_output: str) -> dict:
    if not raw_output: 
        return {"status": "ERROR", "message": "Respuesta vacía"}
    
    # 1. Limpieza de bloques Markdown (incluyendo variaciones de mayúsculas y espacios)
    cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', raw_output, flags=re.IGNORECASE).strip()
    
    # 2. Búsqueda del bloque {...} principal (por si hay texto antes o después)
    # Buscamos desde la primera '{' hasta la última '}'
    match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
    
    # 3. REPARACIÓN DINÁMICA: Si el JSON está truncado
    # Contamos llaves para intentar cerrarlo si DeepSeek cortó por límite de tokens
    open_braces = cleaned.count('{')
    close_braces = cleaned.count('}')
    
    if open_braces > close_braces:
        # Si estamos dentro de un string de "content", cerramos la comilla primero
        # Un truco sucio pero efectivo: si el último carácter no es ", lo añadimos
        last_char = cleaned.rstrip()[-1]
        if last_char != '"' and last_char != '}':
            cleaned = cleaned.rstrip() + '"'
        
        # Añadimos las llaves que falten
        cleaned += '}' * (open_braces - close_braces)

    try:
        data = json.loads(cleaned)
        # Aseguramos que siempre existan las claves mínimas para los templates
        if "content" not in data:
            data["content"] = data.get("code", "") # Fallback si usa 'code' en vez de 'content'
        if "imports" not in data:
            data["imports"] = []
        return data
        
    except json.JSONDecodeError:
        # 4. ÚLTIMO RECURSO: Extracción manual de campos si el JSON es basura total
        content_match = re.search(r'"content":\s*"(.*?)"', cleaned, re.DOTALL)
        if content_match:
            return {
                "status": "RECOVERED",
                "content": content_match.group(1).encode().decode('unicode_escape'),
                "imports": []
            }
        
        return {"status": "ERROR", "message": "JSON irreparable", "raw": raw_output}