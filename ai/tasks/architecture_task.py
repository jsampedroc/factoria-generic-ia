from crewai import Task
from pathlib import Path
from ai.agents.software_architect import software_architect
from ai.validation.json_validator import validate_json

def post_process_architecture(output: dict):
    validate_json(
        output,
        Path("ai/schemas/architecture.schema.json")
    )
    return output

architecture_task = Task(
    description=(
        "Diseña la arquitectura del sistema a partir del modelo de dominio. "
        "Devuelve SOLO JSON válido."
    ),
    agent=software_architect,
    expected_output="JSON con módulos, capas, tecnologías y decisiones",
    post_process=post_process_architecture,
)