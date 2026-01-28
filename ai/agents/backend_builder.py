from crewai import Agent
from ai.llm.llm_config import llm
# Bien
from ai.tools.file_writer import file_writer


backend_builder = Agent(
    role="Backend Builder",
    goal=(
        "Generar un proyecto backend Java/Spring Boot "
        "siguiendo exactamente backend_plan.schema.json"
    ),
    backstory=(
        "Eres un generador de código.\n"
        "NO explicas nada.\n"
        "NO produces texto fuera de archivos.\n"
        "Usas EXCLUSIVAMENTE el tool file_writer."
    ),
    llm=llm,
    tools=[file_writer],  # ✅ FUNCIÓN, NO clase
    verbose=True,
    allow_delegation=False,
)