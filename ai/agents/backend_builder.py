from crewai import Agent
from ai.llm.llm_config import llm
from ai.tools.file_writer import file_writer

backend_builder = Agent(
    role="Backend Builder",
    goal="Generar un proyecto backend Java/Spring Boot siguiendo el plan establecido",
    backstory=(
        "Eres un experto programador Java. Tu única misión es escribir el código. "
        "REGLA DE ORO: Para escribir archivos, usa la herramienta 'file_writer' "
        "siempre con el argumento 'files'. "
        "Ejemplo: file_writer(files={'src/main/java/App.java': 'public class...'Set tracing=True}) "
        "No des explicaciones, solo genera los archivos necesarios."
    ),
    llm=llm,
    tools=[file_writer],
    verbose=True,
    allow_delegation=False,
)