from crewai import Task
import json

def build_architecture_task(agent, domain_model: dict) -> Task:
    # PROTECCIÓN: Convertimos core_entities en nombres de texto siempre
    raw_entities = domain_model.get('core_entities', [])
    entities_names = []
    for e in raw_entities:
        if isinstance(e, dict):
            entities_names.append(e.get('name', 'Unknown'))
        else:
            entities_names.append(str(e))

    description = f"""
    Design the technical architecture for the domain: "{domain_model.get('domain_name')}".
    CORE ENTITIES: {', '.join(entities_names)}

    INSTRUCTIONS:
    1. Define a Hexagonal Architecture.
    2. Create a 'file_inventory' list with paths for: Entity, Repository Port, Service and Controller for EACH entity.
    
    OUTPUT FORMAT (JSON):
    {{
      "architecture_overview": "...",
      "file_inventory": ["path1", "path2", ...]
    }}
    """
    return Task(description=description, agent=agent, expected_output="Architecture JSON with file inventory.")