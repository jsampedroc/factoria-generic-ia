# ai/agents/qa_agent.py

from crewai import Agent

def build_qa_agent(llm):
    return Agent(
        role="Senior QA Automation Engineer",
        goal="Revisar el código generado buscando errores de sintaxis, bugs y coherencia arquitectónica.",
        backstory="""Eres un desarrollador Java perfeccionista. Tu misión es asegurar que el código 
        entregado por el Backend Builder compile mentalmente, respete la Arquitectura Hexagonal 
        y use correctamente las anotaciones de Lombok.""",
        llm=llm,
        allow_delegation=False,
        verbose=True
    )