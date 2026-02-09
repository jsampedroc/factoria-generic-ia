from crewai import Task
import json

def build_architecture_task(agent, domain_model: dict) -> Task:
    # Extraemos las entidades de forma segura (soporta lista de strings o lista de dicts)
    raw_entities = domain_model.get('core_entities', [])
    entities_names = []
    
    for e in raw_entities:
        if isinstance(e, dict):
            entities_names.append(e.get('name', 'UnknownEntity'))
        else:
            entities_names.append(str(e))

    domain_name = domain_model.get('domain_name', 'Generic System')

    description = f"""
    You are a Senior Software Architect. Design the technical architecture and FILE INVENTORY for: 
    DOMAIN: {domain_name}
    
    CORE ENTITIES TO IMPLEMENT:
    {', '.join(entities_names)}

    INSTRUCTIONS:
    1. Define a Layered Hexagonal structure (Spring Boot 3, Java 17).
    2. Create a complete list of file paths (file_inventory) needed to implement the FULL domain.
    3. For EACH entity, you MUST include: Entity, Repository, Service, and Controller.

    OUTPUT FORMAT (Strict JSON):
    {{
      "architecture_overview": "Summary of patterns",
      "file_inventory": [
         "pom.xml",
         "src/main/java/com/app/DaycareApplication.java",
         "src/main/java/com/app/entity/Child.java",
         ... (all other files)
      ]
    }}
    """

    return Task(
        description=description,
        expected_output="JSON with architecture_overview and file_inventory.",
        agent=agent
    )