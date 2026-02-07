from crewai import Task

def build_backend_generation_task(backend_builder):
    return Task(
        description="""
Generate a Spring Boot backend based on the provided DOMAIN MODEL and ARCHITECTURE.

You will receive:
- A validated domain model
- A validated architecture design

Produce a backend contract or implementation as requested.
""",
        expected_output="Valid JSON describing the backend artifacts.",
        agent=backend_builder,
    )