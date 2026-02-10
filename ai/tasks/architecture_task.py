from crewai import Task
import json

def build_architecture_task(agent, domain_model: dict) -> Task:
    # Normalizamos las entidades para el prompt
    raw_entities = domain_model.get('core_entities', [])
    entities_names = []
    for e in raw_entities:
        if isinstance(e, dict):
            entities_names.append(e.get('name', 'Unknown'))
        else:
            entities_names.append(str(e))

    description = f"""
    You are a Senior Software Architect. Design a FULL Hexagonal Architecture for: {domain_model.get('domain_name')}.
    
    CORE ENTITIES: {', '.join(entities_names)}

    INSTRUCTIONS:
    1. Define a Layered Hexagonal structure.
    2. Create a 'file_inventory' list. YOU MUST INCLUDE EVERY SINGLE FILE needed for a production app.
    3. For EACH entity listed above, you MUST include: 
       - Domain: src/domain/model/[Entity].java
       - Domain: src/domain/repository/[Entity]RepositoryPort.java
       - Application: src/application/services/[Entity]Service.java
       - Application: src/application/dto/[Entity]DTO.java
       - Infrastructure: src/infrastructure/persistence/entity/[Entity]JpaEntity.java
       - Infrastructure: src/infrastructure/persistence/repository/[Entity]JpaRepository.java
       - Infrastructure: src/infrastructure/web/controllers/[Entity]Controller.java
    
    Plus: pom.xml, Dockerfile, and Main Application class.
    
    DO NOT summarize. I need the full list of paths to iterate.

    OUTPUT FORMAT (JSON):
    {{
      "architecture_overview": "...",
      "file_inventory": ["path1", "path2", ...]
    }}
    """
    return Task(
        description=description,
        expected_output="JSON with architecture overview and complete file inventory.",
        agent=agent
    )