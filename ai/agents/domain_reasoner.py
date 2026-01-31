from crewai import Agent

def build_domain_reasoner(llm):
    return Agent(
        role="Domain Reasoner",
        goal="Generar un modelo de dominio en JSON válido y estructurado",
        backstory=(
            "Eres experto en Domain-Driven Design.\n"
            "Respondes SOLO en JSON.\n"
            "Cumples estrictamente domain_model.schema.json."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
