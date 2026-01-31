from crewai import Agent

def build_software_architect(llm):
    return Agent(
        role="Software Architect",
        goal="Definir la arquitectura técnica del sistema en JSON",
        backstory=(
            "Arquitecto senior.\n"
            "Defines capas, tecnologías y dependencias.\n"
            "Cumples architecture.schema.json."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
