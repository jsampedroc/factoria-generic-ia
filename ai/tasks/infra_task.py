from crewai import Task
import json

def build_infra_task(agent, domain_model: dict, architecture: dict) -> Task:
    description = f"""
    You are a Senior SRE. Generate the infrastructure for: {domain_model.get('domain_name')}
    
    ARCHITECTURE CONTEXT:
    {json.dumps(architecture, indent=2)}

    REQUIREMENTS:
    1. A 'docker-compose.yml' with the app and a PostgreSQL database.
    2. A '.env.example' with DB_URL, DB_USER, DB_PASSWORD.
    """

    return Task(
        description=description,
        expected_output="JSON with path and content for infrastructure files.",
        agent=agent
    )