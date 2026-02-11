from crewai import Task

def build_repair_task(builder, rel_path, broken_code, error_msg, domain_model):
    """
    Construye una tarea de reparación optimizada para el modelo de templates.
    """
    prompt = f"""
    Eres un agente de reparación experto. Tu objetivo es arreglar el código que está fallando en la compilación.
    
    ARCHIVO: {rel_path}
    ERROR DE COMPILACIÓN: {error_msg}
    
    CÓDIGO ACTUAL (CON ERRORES):
    ---
    {broken_code}
    ---
    
    INSTRUCCIONES ESTRICTAS:
    1. Analiza el error y el modelo de dominio: {domain_model}
    2. Genera la solución técnica.
    3. NO devuelvas el archivo completo.
    4. Devuelve ÚNICAMENTE un objeto JSON con este formato:
    {{
        "imports": ["lista.de.nuevos.imports.necesarios", "otro.import"],
        "content": "aquí va únicamente el bloque de código de la lógica o métodos reparados"
    }}
    
    Asegúrate de que el código en 'content' mantenga la indentación correcta para una clase.
    """
    
    # Aquí asumo que usas el método de tu builder para crear la tarea
    return builder.create_task(prompt=prompt, target_file=rel_path)