from crewai import Task
import json

def build_backend_generation_task(agent, domain_model: dict, architecture: dict) -> Task:
    # Simplificamos el contexto para no saturar la ventana de salida
    entities = [e.get('name') for e in domain_model.get('core_entities', [])]
    
    description = f"""
    Generate the core Spring Boot 3 backend for: {domain_model.get('domain_name')}.
    Entities to implement: {', '.join(entities)}

    OUTPUT INSTRUCTIONS:
    1. You must return a JSON with an "artifacts" array.
    2. Focus ONLY on the most critical files to avoid truncation:
       - pom.xml
       - Dockerfile
       - Main Application class
       - One Entity, one Repository and one Controller as a baseline.
    
    Each artifact must have 'path' and 'content'.
    """

    return Task(
        description=description,
        expected_output="JSON with an 'artifacts' array containing core files.",
        agent=agent
    )