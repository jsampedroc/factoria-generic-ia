# ai/agents/domain_reasoner.py

from crewai import Agent

def build_domain_reasoner(llm):
    return Agent(
        role="Domain Reasoner",
        goal="Generar un modelo de dominio estructurado y coherente basado en la idea de negocio.",
        backstory="""Experto en Domain-Driven Design (DDD). Tu misión es extraer las entidades 
        core, sus atributos y relaciones para que sirvan de base a todo el desarrollo técnico.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )