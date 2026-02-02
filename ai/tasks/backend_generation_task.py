from crewai import Task
from ai.prompts import load_prompt


def build_backend_generation_task(architecture: dict) -> Task:
    """
    Build the backend generation task embedding the ARCHITECTURE (JSON)
    directly into the task description to avoid meta-reasoning and template defaults.
    """
    prompt = load_prompt("backend.md")

    description = (
        "You are given a SOFTWARE ARCHITECTURE (JSON) for a SINGLE user application.\n\n"
        "This is NOT a system description, NOT an AI configuration, and NOT a description of an assistant.\n\n"
        "SOFTWARE ARCHITECTURE (JSON):\n"
        "----------------------------------------\n"
        f"{architecture}\n"
        "----------------------------------------\n\n"
        "Generate the backend artifacts based ONLY on the above architecture.\n\n"
        f"{prompt}"
    )

    return Task(
        description=description,
        expected_output="A JSON object strictly following the specified format."
    )