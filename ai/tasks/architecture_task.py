from crewai import Task
from ai.agents.software_architect import software_architect

architecture_task = Task(
    description=(
        "Diseña la arquitectura técnica detallada basada en el modelo de dominio. "
        "Debes definir: 1. Estructura de paquetes (com.example.app...), "
        "2. Capas (Controller, Service, Repository, Entity), "
        "3. Dependencias de Maven/Gradle. "
        "IMPORTANTE: Entrega un JSON puro que sirva de guía exacta para el programador."
    ),
    agent=software_architect,
    expected_output="Un objeto JSON técnico que detalle paquetes, clases y dependencias de Spring Boot."
)