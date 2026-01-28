from crewai import Task
from pathlib import Path
# Importa el agente de devops en lugar del backend_builder
from ai.agents.devops_agent import devops_agent 
from ai.validation.json_validator import validate_json

def post_process_devops(output: dict):
   validate_json(
        output,
        Path("ai/schemas/domain_model.schema.json")
    )
   
   return output

devops_task = Task(
    description=(
        "Genera los archivos de infraestructura: Dockerfile, "
        "docker-compose.yml y scripts de despliegue necesarios."
    ),
    agent=devops_agent, # Usa el agente de DevOps
    expected_output="Archivos de configuración de contenedores y despliegue",
    post_process=post_process_devops,
)