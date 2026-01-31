from crewai import Agent

def build_verifier(llm):
    return Agent(
        role="Verifier",
        goal="Detectar alucinaciones y afirmaciones no verificadas",
        backstory=(
            "Eres un auditor estricto. No generas contenido nuevo. "
            "Solo verificas si las afirmaciones están soportadas por el CONTEXTO."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
