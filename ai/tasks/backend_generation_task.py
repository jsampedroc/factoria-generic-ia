from crewai import Task

def build_methods_logic_task(agent, class_name: str, domain_model: dict, architecture: dict) -> Task:
    description = f"""
    ACT AS: Senior Java Developer.
    TASK: Genera exclusivamente la lógica interna para los métodos de la clase {class_name}.

    CONTEXT:
    - Domain: {domain_model.get('domain_name')}
    - Architecture: {architecture.get('architecture_overview')}

    CONSTRAINTS:
    1. PROHIBIDO: Incluir la definición de la clase, imports base o decoradores de infraestructura.
    2. Requisitos técnicos: Java 17, SOLID y Clean Code.
    3. No incluyas Javadoc ni comentarios innecesarios.
    4. El código debe estar listo para ser insertado directamente dentro de una clase existente.

    FORMATO DE SALIDA (Strict JSON):
    {{
      "content": "Solo el cuerpo de las funciones e implementación de métodos, indentado a 4 espacios."
    }}
    """

    return Task(
        description=description,
        expected_output=f"JSON con la clave 'content' conteniendo exclusivamente la lógica de los métodos para {class_name}.",
        agent=agent
    )