from crewai import Task
from ai.prompts import load_prompt


def build_domain_model_task(idea: str) -> Task:
    """
    Build the domain modeling task with the USER APPLICATION IDEA
    embedded directly in the task description, to avoid meta-reasoning.
    """
    prompt = load_prompt("domain_model.md")

    description = (
        "You are given a USER APPLICATION IDEA.\n\n"
        "This is NOT a system description, NOT an AI configuration, "
        "and NOT a description of an assistant.\n\n"
        "USER APPLICATION IDEA:\n"
        "----------------------------------------\n"
        f"{idea}\n"
        "----------------------------------------\n\n"
        "Based ONLY on the above idea, perform domain modeling "
        "according to the following rules and constraints:\n\n"
        f"{prompt}"
    )

    return Task(
        description=description,
        expected_output="A JSON object strictly following the specified format."
    )