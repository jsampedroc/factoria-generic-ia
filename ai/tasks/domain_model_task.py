from crewai import Task
from ai.agents.domain_reasoner import domain_reasoner

domain_model_task = Task(
    description=(
        "Analiza la solicitud del usuario y genera un modelo de dominio DDD completo. "
        "Devuelve exclusivamente un JSON puro, sin bloques de código markdown."
    ),
    agent=domain_reasoner,
    expected_output="JSON válido con el modelo de dominio (entidades, agregados, value objects)."
)