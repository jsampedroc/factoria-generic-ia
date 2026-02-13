from crewai import Task
import json

def build_infra_task(agent, domain_model: dict, architecture: dict) -> Task:
    # Definimos el stack tecnológico basándonos en la arquitectura
    tech_stack = architecture.get('architecture_overview', 'Spring Boot Hexagonal')
    domain_name = domain_model.get('domain_name', 'daycare-management-system')

    description = f"""
    You are a Senior SRE and DevOps Engineer. Generate the infrastructure and build configuration for: {domain_name}
    
    TECH STACK:
    {tech_stack}
    - Java 17
    - Spring Boot 3.x
    - Lombok (CRITICAL)
    - PostgreSQL (Default Database)

    REQUIREMENTS:
    1. **pom.xml**: Generate a complete Maven pom.xml for Spring Boot 3. 
       - MUST include: 'spring-boot-starter-data-jpa', 'spring-boot-starter-web', 'postgresql'.
       - CRITICAL: Include 'org.projectlombok:lombok' AND the 'annotationProcessorPaths' in the 'maven-compiler-plugin' to ensure Lombok works.
    
    2. **Dockerfile**: Multi-stage build for Java 17 Maven.
    
    3. **docker-compose.yml**: 
       - Service 'app': depends on 'db', port 8080:8080.
       - Service 'db': use postgres:15-alpine, include POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD.
    
    4. **src/main/resources/application.yml**: 
       - Configuration to connect to the 'db' service in docker-compose.
       - ddl-auto: update.
    
    5. **.env**: Environment variables for DB_URL, DB_USER, DB_PASSWORD.
    
    6. **README-infrastructure.md**: Instructions to run 'docker-compose up'.

    OUTPUT FORMAT (JSON):
    {{
      "artifacts": [
        {{ "path": "pom.xml", "content": "..." }},
        {{ "path": "Dockerfile", "content": "..." }},
        {{ "path": "docker-compose.yml", "content": "..." }},
        {{ "path": "src/main/resources/application.yml", "content": "..." }},
        {{ "path": ".env", "content": "..." }},
        {{ "path": "README-infrastructure.md", "content": "..." }}
      ]
    }}
    """
    return Task(
        description=description,
        expected_output="Complete infrastructure JSON including pom.xml (with Lombok), Dockerfile, docker-compose, and application.yml.",
        agent=agent
    )