from crewai import Task
from ai.prompts import load_prompt


def build_architecture_task(domain_model: dict) -> Task:
    """
    Build the architecture task embedding the DOMAIN MODEL directly
    in the task description to avoid meta-reasoning and context leakage.
    """
    prompt = load_prompt("architecture.md")

    description = (
        "You are given a DOMAIN MODEL (JSON) for a SINGLE user application.\n\n"
        "This is NOT a system description, NOT an AI configuration, "
        "and NOT a description of an assistant.\n\n"
        "DOMAIN MODEL (JSON):\n"
        "----------------------------------------\n"
        f"{domain_model}\n"
        "----------------------------------------\n\n"
        "Design the software architecture based ONLY on the above domain model.\n\n"
        f"{prompt}"
    )

    return Task(
        description=description,
        expected_output="A JSON object strictly following the specified format."
    )