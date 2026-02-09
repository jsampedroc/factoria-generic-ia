from crewai import Task
import json

def build_architecture_task(agent, domain_model: dict) -> Task:
    domain_str = json.dumps(domain_model, indent=2)

    description = f"""
    You are a Senior Software Architect. Design the technical architecture and the FILE INVENTORY for:
    {domain_str}
    
    INSTRUCTIONS:
    1. Define the Layered Hexagonal structure.
    2. List ALL necessary files to implement the FULL domain (Entities, Repositories, Services, Controllers for ALL entities).
    
    OUTPUT FORMAT:
    You MUST return a JSON with:
    {{
      "architecture_overview": "...",
      "file_inventory": [
        "src/main/java/com/daycare/entity/Child.java",
        "src/main/java/com/daycare/entity/Staff.java",
        "src/main/java/com/daycare/repository/ChildRepository.java",
        ... (all other files)
      ]
    }}
    """

    return Task(
        description=description,
        expected_output="JSON containing architecture details and a complete list of file paths (file_inventory).",
        agent=agent
    )