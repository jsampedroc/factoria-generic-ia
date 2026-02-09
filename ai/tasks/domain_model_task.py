from crewai import Task
import json

def build_domain_model_task(agent, idea: str) -> Task:
    """
    Crea la tarea de descubrimiento de dominio usando la clase oficial de CrewAI.
    """
    # En CrewAI, el 'description' actúa como el prompt principal
    description = f"""
    Analyze the following business idea and extract a formal Domain Model.
    IDEA: {idea}

    Your goal is to identify:
    - The name of the domain.
    - Core business entities (singular, PascalCase).
    - Key use cases.
    - Assumptions made.
    - Any open questions.

    STRICT OUTPUT FORMAT:
    You must return a valid JSON object.
    """

    return Task(
        description=description,
        expected_output="A JSON object containing: domain_name, core_entities, key_use_cases, assumptions, and open_questions.",
        agent=agent
    )