from crewai import Task
from pathlib import Path
from ai.agents.domain_reasoner import domain_reasoner
from ai.validation.json_validator import validate_json

def post_process_domain_model(output: str):
    # Nota: Si usas CrewAI moderno, el output puede ser un string que requiere limpieza
    return output

domain_model_task = Task(
    description=(
        "Analiza la idea del usuario y genera un modelo de dominio DDD. "
        "Devuelve exclusivamente un JSON que cumpla con domain_model.schema.json."
    ),
    agent=domain_reasoner,
    expected_output="JSON estructurado con el modelo de dominio.",
    # post_process=post_process_domain_model # Desactiva temporalmente si da errores de validación
)