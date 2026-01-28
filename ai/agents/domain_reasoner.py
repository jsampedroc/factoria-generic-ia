from crewai import Agent
from ai.llm.llm_config import llm

domain_reasoner = Agent(
    role="Domain Reasoner",
    goal="Generar un modelo de dominio en JSON válido y estructurado",
    backstory=(
        "Eres experto en Domain-Driven Design.\n"
        "Respondes SOLO en JSON.\n"
        "Cumples estrictamente domain_model.schema.json."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)