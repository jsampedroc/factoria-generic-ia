from crewai import Task
import json

def build_single_file_task(agent, file_path: str, domain_model: dict, architecture: dict) -> Task:
    # Limpieza de entidades para el prompt
    raw_entities = domain_model.get('core_entities', [])
    entities_info = []
    for e in raw_entities:
        if isinstance(e, dict):
            entities_info.append(f"{e.get('name')} ({e.get('description', 'no desc')})")
        else:
            entities_info.append(str(e))

    description = f"""
    You are an Expert Java Developer. Generate the content for:
    FILE: {file_path}

    CONTEXT:
    - Domain: {domain_model.get('domain_name')}
    - Entities context: {', '.join(entities_info)}
    - Architecture: {architecture.get('architecture_overview')}

    REQUIREMENTS:
    1. Java 17 / Spring Boot 3.2.
    2. Follow Clean Code and SOLID.
    3. Implement full logic if it's a Repository, Service or Controller.

    OUTPUT FORMAT (Strict JSON):
    {{
      "path": "{file_path}",
      "content": "..."
    }}
    """

    return Task(
        description=description,
        expected_output=f"JSON with the source code for {file_path}",
        agent=agent
    )