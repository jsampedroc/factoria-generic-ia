from crewai import Agent
from ai.llm.llm_config import llm

software_architect = Agent(
    role="Software Architect",
    goal="Definir la arquitectura técnica del sistema en JSON",
    backstory=(
        "Arquitecto senior.\n"
        "Defines capas, tecnologías y dependencias.\n"
        "Cumples architecture.schema.json."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)