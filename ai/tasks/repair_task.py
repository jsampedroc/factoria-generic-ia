from crewai import Task
from pathlib import Path

def build_repair_task(agent, file_path, broken_code, error_message, domain_model):
    file_name = Path(file_path).stem
    
    # Buscamos el contrato del repositorio en el dominio para evitar métodos inventados
    entities = domain_model.get("core_entities", {})
    repo_context = "Usa métodos estándar: save, findById, findAll, deleteById."
    for name, data in entities.items():
        if name in file_name:
            repo_context = f"Contrato del Repositorio: {data.get('repository_port')}"

    prompt = f"""
### TAREA: REPARACIÓN TÉCNICA DDD ###
El archivo {file_path} tiene errores de compilación.

### ERROR DE MAVEN ###
{error_message}

### CÓDIGO ACTUAL ###
{broken_code}

### INSTRUCCIONES DE REPARACIÓN ###
1. **Error de Tipos**: Si ves "incompatible types: Long/String cannot be converted to Id", envuelve el valor: `new ChildId(id)`.
2. **Error de Símbolo**: {repo_context}
3. **Duplicidad**: Asegúrate de devolver SOLO el contenido interno, sin repetir la declaración "public class".

### FORMATO DE SALIDA (JSON) ###
{{
  "imports": ["imports adicionales si son necesarios"],
  "content": "// Tu lógica corregida aquí...",
  "explanation": "Breve descripción del fix"
}}
"""
    return Task(
        description=prompt,
        agent=agent,
        expected_output="JSON con el fragmento de lógica reparado."
    )