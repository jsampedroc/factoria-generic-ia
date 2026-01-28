from crewai import Task
from agents.domain_reasoner import domain_reasoner

domain_modeling_task = Task(
    agent=domain_reasoner,
    description=(
        "Recibir una idea de software en lenguaje natural y transformarla "
        "en un modelo de dominio siguiendo principios de Domain-Driven Design."
    ),
    expected_output=(
        "Un único objeto JSON válido y bien formado con la siguiente estructura:\n\n"
        "{\n"
        '  "domain_name": "...",\n'
        '  "description": "...",\n'
        '  "bounded_contexts": [ ... ]\n'
        "}\n\n"
        "No incluyas explicaciones, comentarios ni texto adicional. "
        "Devuelve EXCLUSIVAMENTE el JSON."
    )
)