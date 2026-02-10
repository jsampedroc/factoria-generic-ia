from crewai import Task

def build_single_file_task(agent, file_path: str, domain_model: dict, architecture: dict) -> Task:
    description = f"""
    You are an Expert Java Developer. Generate the source code for:
    FILE: {file_path}

    CONTEXT:
    - Domain: {domain_model.get('domain_name')}
    - Architecture: {architecture.get('architecture_overview')}

    REQUIREMENTS:
    1. Java 17 / Spring Boot 3.2.
    2. Clean Code & SOLID principles.
    3. If 'src/domain', NO Spring/JPA annotations.
    4. If 'src/infrastructure', add necessary @Entity, @Repository, or @RestController.
    5. No Javadoc (save tokens).

    OUTPUT FORMAT (Strict JSON):
    {{
      "path": "{file_path}",
      "content": "Full source code here"
    }}
    """
    return Task(
        description=description,
        expected_output=f"JSON with path and content for {file_path}",
        agent=agent
    )