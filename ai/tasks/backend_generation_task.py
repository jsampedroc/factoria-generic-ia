from crewai import Task
from pathlib import Path
from ai.agents.backend_builder import backend_builder
from ai.validation.json_validator import validate_json

def post_process_backend(output: dict):
    validate_json(
        output,
        Path("ai/schemas/backend_plan.schema.json")
    )
    return output

backend_generation_task = Task(
    description=(
        "Genera el plan de generación del backend Java (Spring Boot). "
        "Incluye estructura de paquetes, entidades, repositorios y config."
    ),
    agent=backend_builder,
    expected_output="JSON con estructura y ficheros a generar",
    post_process=post_process_backend,
)