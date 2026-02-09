from crewai import Task
import json

def build_single_file_task(agent, file_path: str, domain_model: dict, architecture: dict) -> Task:
    # Resumen de entidades para el contexto
    entities = [e.get('name') if isinstance(e, dict) else str(e) for e in domain_model.get('core_entities', [])]
    
    description = f"""
    You are an Expert Backend Developer. Generate the source code for:
    FILE PATH: {file_path}

    CONTEXT:
    - Project: {domain_model.get('domain_name')}
    - Entities: {', '.join(entities)}
    - Style: Hexagonal Architecture

    STRICT GUIDELINES:
    1. Language: Java 17 / Spring Boot 3.2.
    2. Focus on implementation logic. 
    3. DO NOT include class-level Javadoc or extensive comments (save tokens).
    4. Use Lombok to reduce boilerplate.
    5. Ensure the code is complete and syntactically correct.

    OUTPUT FORMAT (Return ONLY this JSON):
    {{
      "path": "{file_path}",
      "content": "Full code here..."
    }}
    """

    return Task(
        description=description,
        expected_output=f"The source code for {file_path}",
        agent=agent
    )