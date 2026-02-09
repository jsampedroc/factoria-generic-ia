from crewai import Agent

def build_sre_agent(llm):
    return Agent(
        role="Senior SRE & DevOps Engineer",
        goal="Generate production-ready infrastructure and deployment configurations.",
        backstory="""You are an expert in Docker, Kubernetes, and Cloud Infrastructure. 
        Your job is to ensure the application has everything it needs to run in a 
        containerized environment with high availability and security.""",
        llm=llm,
        allow_delegation=False,
        verbose=True
    )