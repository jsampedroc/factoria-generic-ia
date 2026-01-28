from crewai import Agent
from ai.llm.llm_config import llm
# Bien
from ai.tools.file_writer import file_writer

devops_agent = Agent(
    role="DevOps Engineer",
    goal="Generar Docker, Docker Compose y scripts de arranque",
    backstory="Especialista en infraestructura reproducible.",
    llm=llm,
    tools=[file_writer],
    verbose=True,
    allow_delegation=False,
)