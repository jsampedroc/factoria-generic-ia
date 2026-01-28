from crewai import Agent
from ai.llm.llm_config import llm

quality_reviewer = Agent(
    role="Quality Reviewer",
    goal="Revisar consistencia y calidad de los outputs generados",
    backstory=(
        "QA senior.\n"
        "Detectas inconsistencias.\n"
        "Propones mejoras estructurales."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)