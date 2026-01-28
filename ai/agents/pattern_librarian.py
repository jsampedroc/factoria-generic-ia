from crewai import Agent
from ai.llm.llm_config import llm
# Bien
from ai.tools.file_writer import file_writer

pattern_librarian = Agent(
    role="Pattern Librarian",
    goal="Detectar patrones reutilizables y almacenarlos.",
    backstory=(
        "Eres el bibliotecario de la factoría. "
        "Detectas cuándo una solución es reutilizable."
    ),
    llm=llm,
    tools=[file_writer],
    verbose=True
)