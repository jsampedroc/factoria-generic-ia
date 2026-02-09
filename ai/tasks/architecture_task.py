from crewai import Task
import json

def build_architecture_task(agent, domain_model: dict) -> Task:
    """
    Crea la tarea de arquitectura usando la clase oficial de CrewAI.
    """
    domain_str = json.dumps(domain_model, indent=2)

    description = f"""
    You are a Senior Software Architect. Your goal is to design the technical architecture for the following domain:
    
    {domain_str}
    
    INSTRUCTIONS:
    1. Define a Layered Hexagonal architecture.
    2. Focus on Spring Boot 3 / Java 17.
    3. Specify layers (api, application, domain, infrastructure).
    4. Define persistence (PostgreSQL) and security (JWT).
    
    STRICT OUTPUT FORMAT:
    Return ONLY a JSON object with the architecture details.
    """

    return Task(
        description=description,
        expected_output="A JSON object defining the system architecture, layers, components, and technology stack.",
        agent=agent
    )