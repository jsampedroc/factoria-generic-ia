from crewai import Task
from pathlib import Path
from ai.agents.domain_reasoner import domain_reasoner
from ai.validation.json_validator import validate_json

def post_process_domain_model(output: dict):
    validate_json(
        output,
        Path("ai/schemas/domain_model.schema.json")
    )
    return output

domain_model_task = Task(
    description=(
        "A partir de la idea proporcionada, genera un modelo de dominio "
        "siguiendo DDD. Devuelve SOLO JSON válido."
    ),
    agent=domain_reasoner,
    expected_output="JSON con entidades, agregados, value_objects y casos de uso",
    post_process=post_process_domain_model,
)