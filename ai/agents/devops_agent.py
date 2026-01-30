from crewai import Agent
from ai.llm.llm_config import llm
from ai.tools.file_writer import file_writer

devops_agent = Agent(
    role="DevOps Engineer",
    goal="Generar Dockerfile y Docker Compose funcionales en la raíz del proyecto",
    backstory=(
        "Eres un experto en infraestructura. "
        "REGLA DE ORO: En los Dockerfiles, usa SIEMPRE rutas relativas directas. "
        "NUNCA escribas 'COPY output/backend/'. Usa SIEMPRE 'COPY pom.xml .' y 'COPY src ./src'. "
        "Asume que todos los archivos necesarios están en el mismo nivel que el Dockerfile."
    ),
    llm=llm,
    tools=[file_writer],
    verbose=True,
    allow_delegation=False,
)