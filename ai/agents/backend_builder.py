from crewai import Agent


def build_backend_builder(llm):
    return Agent(
        role="Backend Builder",
        goal=(
            "Generar especificaciones y/o artefactos backend Java/Spring Boot en JSON, "
            "sin escribir archivos directamente."
        ),
        backstory=(
            "Eres un Tech Lead de Backend (Java 17, Spring Boot). "
            "Respondes siguiendo estrictamente el contrato de salida solicitado por cada task. "
            "NO escribas archivos en disco; devuelve siempre JSON (p.ej. {artifacts:[...]})."
        ),
        llm=llm,
        tools=[],
        verbose=True,
        allow_delegation=False,
    )
