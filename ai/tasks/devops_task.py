from crewai import Task

def build_devops_task(devops_agent):
    return Task(
        description=(
            "Genera la infraestructura Docker para el proyecto. "
            "1. Escribe un Dockerfile multi-etapa. "
            "   - PROHIBIDO usar el prefijo 'output/backend/' en los comandos COPY. "
            "   - Usa exclusivamente: 'COPY pom.xml .' y 'COPY src ./src'. "
            "2. Escribe el docker-compose.yml vinculando la app con postgres. "
            "Usa la herramienta 'file_writer' para guardar los archivos."
        ),
        agent=devops_agent,
        expected_output="Dockerfile y docker-compose.yml con rutas relativas locales (sin prefijos de carpeta).",
    )
