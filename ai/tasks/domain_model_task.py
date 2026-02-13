from crewai import Task
import json

def build_domain_model_task(agent, idea: str) -> Task:
    description = f"""
    Analyze the following business idea and extract a formal Domain Model for a Hexagonal Architecture.
    IDEA: {idea}

    YOUR GOAL IS TO IDENTIFY:
    1. **domain_name**: Name of the system.
    2. **core_entities**: List of entities (PascalCase, singular). For each entity, specify its main attributes.
    3. **value_objects**: Identify the ID class for each entity (e.g., ChildId, StaffId) and any other value objects (e.g., Address, Money).
    4. **enums**: Critical for business logic (e.g., Status, Roles, Types). List their possible values.
    5. **key_use_cases**: Main business flows.

    STRICT OUTPUT FORMAT (JSON):
    {{
      "domain_name": "...",
      "core_entities": {{
         "EntityName": {{ "attributes": ["attr1", "attr2"], "repository_port": ["save", "findById"] }}
      }},
      "value_objects": ["ChildId", "StaffId", "Money"],
      "enums": {{ "Status": ["ACTIVE", "INACTIVE"] }},
      "key_use_cases": []
    }}
    """

    return Task(
        description=description,
        expected_output="A structured JSON Domain Model including entities, value_objects, and enums.",
        agent=agent
    )