from crewai import Task
from ai.agents.backend_builder import backend_builder

backend_generation_task = Task(
    description=(
        "Implementa el sistema backend en Java/Spring Boot siguiendo la arquitectura definida. "
        "Crea las entidades, repositorios, servicios y controladores necesarios. "
        "Usa 'file_writer' para escribir cada archivo en su ruta (ej: src/main/java/...). "
        "No te limites a un plan, ESCRIBE los archivos reales."
    ),
    agent=backend_builder,
    expected_output="Estructura de proyecto Maven con todo el código Java escrito en disco."
)