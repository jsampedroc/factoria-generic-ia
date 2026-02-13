from crewai import Task
import json

def build_architecture_task(agent, domain_model: dict) -> Task:
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
    1. Define a Layered Hexagonal structure using Maven standard: 'src/main/java' and 'src/test/java'.
    2. For EACH entity listed above, YOU MUST include the following 10 files (8 code + 2 tests):
       - Domain: src/main/java/com/daycaremanagement/domain/model/[Entity].java
       - Domain: src/main/java/com/daycaremanagement/domain/repository/[Entity]RepositoryPort.java
       - Domain: src/main/java/com/daycaremanagement/domain/valueobject/[Entity]Id.java
       - Application: src/main/java/com/daycaremanagement/application/services/[Entity]Service.py (will be converted to .java)
       - Application: src/main/java/com/daycaremanagement/application/dto/[Entity]DTO.java
       - Infrastructure: src/main/java/com/daycaremanagement/infrastructure/persistence/entity/[Entity]JpaEntity.java
       - Infrastructure: src/main/java/com/daycaremanagement/infrastructure/persistence/repository/[Entity]JpaRepository.java
       - Infrastructure: src/main/java/com/daycaremanagement/infrastructure/web/controllers/[Entity]Controller.java
       - TEST 1: src/test/java/com/daycaremanagement/application/services/[Entity]ServiceTest.java
       - TEST 2: src/test/java/com/daycaremanagement/domain/model/[Entity]Test.java
    
    3. Include common files: pom.xml (with JUnit 5 and Mockito), Dockerfile, and Main Application class.
    
    DO NOT summarize. I need the full list of paths in 'file_inventory'.

    OUTPUT FORMAT (JSON):
    {{
      "architecture_overview": "...",
      "file_inventory": ["path1", "path2", ...]
    }}
    """
    return Task(
        description=description,
        expected_output="JSON with architecture overview and complete file inventory including mandatory tests.",
        agent=agent
    )