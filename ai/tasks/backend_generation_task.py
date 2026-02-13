from pathlib import Path
from crewai import Task

def build_single_file_task(agent, file_path, relevant_domain, architecture):
    file_name = Path(file_path).stem
    ext = Path(file_path).suffix
    path_lower = file_path.lower()
    
    is_test = "test" in path_lower
    is_vo = "domain/valueobject" in path_lower
    is_model = "domain/model" in path_lower
    is_dto = "application/dto" in path_lower
    is_main = "mainapplication" in path_lower

    attributes = relevant_domain.get('attributes', [])

    extra_instructions = ""
    if is_main:
        extra_instructions = "Solo genera: // Main entry point."
    elif is_test:
        extra_instructions = "### TEST UNITARIO ### Usa JUnit 5 y Mockito. Genera SOLO métodos @Test."
    elif is_vo or is_model or is_dto:
        extra_instructions = f"### POJO/DATA OBJECT ### Genera campos privados, getters y setters para estos atributos: {attributes}. Usa tipos DDD."
    else:
        extra_instructions = "### LÓGICA ### Genera campos @Autowired y el cuerpo de los métodos de servicio."

    # REGLAS ESPECÍFICAS (Control de Capas)
    if "services" in file_path.lower():
        INJECTION_RULE = "Genera SOLO los métodos de orquestación y la inyección de repositorios. NO uses anotaciones de Spring (@RestController, @GetMapping)."
    elif "controllers" in file_path.lower():
        INJECTION_RULE = "Genera SOLO métodos Spring (@GetMapping, @PostMapping) y las llamadas a los servicios. Convierte DTOs a Dominios y viceversa. NO implementes la lógica de negocio."
    else:
        INJECTION_RULE = "Genera solo el contenido básico del modelo/POJO/ValueObject."


    prompt = f"""
### ROLE ###
Senior Java Expert. Escribiendo para: {file_name}

{extra_instructions}

### ¡¡PROHIBICIÓN CRÍTICA!! ###
- NO escribas "public class {file_name} {{ ... }}".
- NO escribas "package" ni "import" estándar.
- EMPIEZA directamente con los atributos o métodos.
- Si incluyes la declaración de la clase, el sistema no podrá compilar.

### CONTEXTO ###
{relevant_domain.get('entity')}

### FORMATO DE SALIDA (JSON ESTRICTO) ###
{{
  "imports": ["com.daycaremanagement.domain.valueobject.*"],
  "content": "// Escribe aquí solo el interior de la clase"
}}
"""
    return Task(description=prompt, agent=agent, expected_output="JSON con fragmento de código.")