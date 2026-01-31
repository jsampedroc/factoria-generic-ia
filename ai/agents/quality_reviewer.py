from crewai import Agent

def build_quality_reviewer(llm):
    return Agent(
        role="Quality Reviewer",
        goal="Revisar salidas para calidad, coherencia y completitud",
        backstory=(
            "Eres un revisor meticuloso. Identificas huecos, inconsistencias y riesgos. "
            "No inventas hechos; propones preguntas abiertas cuando falta información."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
