from crewai import Task
from ai.agents.devops_agent import devops_agent

devops_task = Task(
    description=(
        "Toma el código Java generado y crea la infraestructura de contenedores. "
        "Debes generar: 1. Dockerfile (JDK 17 Alpine), 2. docker-compose.yml (App + Base de Datos), "
        "3. Scripts de utilidad (deploy.sh, stop.sh). "
        "USA la herramienta 'file_writer' para guardar estos archivos."
    ),
    agent=devops_agent,
    expected_output="Archivos Dockerfile, docker-compose.yml y scripts de shell creados en el disco."
)