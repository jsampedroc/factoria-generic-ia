from crewai import Task
import json

def build_infra_task(agent, domain_model: dict, architecture: dict) -> Task:
    description = f"""
    You are a Senior SRE. Generate the infrastructure for: {domain_model.get('domain_name')}
    
    TECH STACK:
    {json.dumps(architecture.get('architecture_overview'))}

    REQUIREMENTS:
    1. docker-compose.yml (App + PostgreSQL).
    2. .env.example with all keys.
    3. README-infrastructure.md with deployment instructions.

    OUTPUT FORMAT (JSON):
    {{
      "artifacts": [
        {{ "path": "docker-compose.yml", "content": "..." }},
        {{ "path": ".env.example", "content": "..." }}
      ]
    }}
    """
    return Task(
        description=description,
        expected_output="Infrastructure artifacts in JSON.",
        agent=agent
    )