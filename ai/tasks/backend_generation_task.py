from crewai import Task
import json

def build_single_file_task(agent, file_path: str, domain_model: dict, architecture: dict) -> Task:
    """
    Crea una tarea para generar el contenido de UN SOLO archivo específico.
    """
    description = f"""
    You are an Expert Java Developer. Generate the content for the following file:
    FILE PATH: {file_path}
    
    CONTEXT:
    Domain: {domain_model.get('domain_name')}
    Architecture: {architecture.get('architecture_overview')}
    
    REQUIREMENTS:
    1. Write high-quality, production-ready Java 17 code.
    2. Use Spring Boot 3 standards.
    3. Ensure the code is consistent with the provided domain model.

    OUTPUT FORMAT:
    Return ONLY a JSON object with:
    {{
      "path": "{file_path}",
      "content": "... (the full source code) ..."
    }}
    """

    return Task(
        description=description,
        expected_output=f"A JSON with the path and the complete content for {file_path}",
        agent=agent
    )