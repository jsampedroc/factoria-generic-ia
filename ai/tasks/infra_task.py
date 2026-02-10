from crewai import Task
import json

def build_infra_task(agent, domain_model: dict, architecture: dict) -> Task:
    # Añadimos explícitamente Lombok y pom.xml a los requerimientos
    description = f"""
    You are a Senior SRE. Generate the infrastructure and build configuration for: {domain_model.get('domain_name')}
    
    TECH STACK:
    {json.dumps(architecture.get('architecture_overview'))}
    - Java 17
    - Spring Boot 3
    - Lombok (MUST be included in the build configuration)

    REQUIREMENTS:
    1. pom.xml: Generate a complete Maven pom.xml. 
       CRITICAL: You MUST include the Lombok dependency (org.projectlombok:lombok) and the annotation processor in the maven-compiler-plugin.
    2. docker-compose.yml (App + PostgreSQL).
    3. .env.example with all database and spring environment keys.
    4. README-infrastructure.md with deployment instructions.

    OUTPUT FORMAT (JSON):
    {{
      "artifacts": [
        {{ "path": "pom.xml", "content": "..." }},
        {{ "path": "docker-compose.yml", "content": "..." }},
        {{ "path": ".env.example", "content": "..." }},
        {{ "path": "README-infrastructure.md", "content": "..." }}
      ]
    }}
    """
    return Task(
        description=description,
        expected_output="Infrastructure and Maven artifacts in JSON (including pom.xml with Lombok).",
        agent=agent
    )