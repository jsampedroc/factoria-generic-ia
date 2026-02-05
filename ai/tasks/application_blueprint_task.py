from crewai import Task
from ai.prompts import load_prompt


def build_application_blueprint_task(
    domain_model: dict,
    architecture: dict,
) -> Task:
    """
    Builds the Application Blueprint task.
    """

    prompt = load_prompt("application_blueprint.md")

    return Task(
        description=prompt,
        expected_output=(
            "A single JSON object describing the application blueprint "
            "including evolution stages."
        ),
        context={
            "domain_model": domain_model,
            "architecture": architecture,
        },
    )