# ai/agents/sre_agent

from crewai import Agent

def build_sre_agent(llm):
    return Agent(
        role="Senior SRE & DevOps Engineer",
        goal="Generar configuraciones de infraestructura y despliegue listas para producción (Docker, K8s).",
        backstory="""Experto en Dockerización de apps Spring Boot y despliegue en Kubernetes. 
        Generas Dockerfiles multi-stage eficientes y manifiestos de K8s seguros y escalables.""",
        llm=llm,
        allow_delegation=False,
        verbose=True
    )