from crewai import Agent
from ai.llm.llm_config import llm
# Bien
from ai.tools.file_writer import file_writer

pattern_librarian = Agent(
    role="Pattern Librarian",
    goal="Detectar patrones reutilizables y almacenarlos.",
    backstory=(
        "Eres el bibliotecario de la factoría. Detectas soluciones genéricas. "
        "Cuando guardes un patrón, usa 'file_writer' pasando el diccionario "
        "en el parámetro 'files'. No olvides nunca la clave 'files'."
    ),
    llm=llm,
    tools=[file_writer],
    verbose=True
)