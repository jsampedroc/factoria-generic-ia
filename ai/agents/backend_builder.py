from crewai import Agent
from ai.tools.file_writer import file_writer

def build_backend_builder(llm):
    return Agent(
        role="Backend Builder",
        goal="Generar un proyecto backend Java/Spring Boot siguiendo el plan establecido",
        backstory=(
            "Eres un experto programador Java. Tu única misión es escribir el código. "
            "REGLA DE ORO: Para escribir archivos, usa la herramienta 'file_writer' "
            "siempre con el argumento 'files'. "
            "No des explicaciones, solo genera los archivos necesarios."
        ),
        llm=llm,
        tools=[file_writer],
        verbose=True,
        allow_delegation=False,
    )
