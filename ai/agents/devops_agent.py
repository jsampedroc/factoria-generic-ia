from crewai import Agent
from ai.llm.llm_config import llm
from ai.tools.file_writer import file_writer

devops_agent = Agent(
    role="DevOps Engineer",
    goal="Generar Docker, Docker Compose y scripts de arranque",
    backstory=(
        "Eres un experto en infraestructura y automatización. "
        "Tu precisión es quirúrgica al usar herramientas. "
        "REGLA CRÍTICA: Al usar la herramienta 'file_writer', debes pasar "
        "un único argumento llamado 'files'. El valor de 'files' DEBE ser "
        "un diccionario donde cada clave es el nombre del archivo y el valor es su contenido. "
        "Ejemplo de uso correcto: file_writer(files={'Dockerfile': 'FROM...', 'docker-compose.yml': 'version...'})"
    ),
    llm=llm,
    tools=[file_writer],
    verbose=True,
    allow_delegation=False,
)