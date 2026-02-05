from crewai import Task


def build_backend_generation_task(backend_agent):
    """
    Backend Generation – Level 1 (ADL / Contract-only)

    This task MUST generate a backend contract (blueprint), NOT code.
    No files, no artifacts, no writers, no tools.
    """

    description = """
You are a Backend Technical Lead operating under an Agentic Development Lifecycle (ADL)
within an Enterprise Multi-Agent Orchestration (EMAO).

========================
GOAL (LEVEL 1 ONLY)
========================
Produce a BACKEND CONTRACT (blueprint) for the application.
You MUST NOT generate code or files.

========================
INPUT CONTEXT
========================
You will receive:
- domain_model: JSON describing the business domain
- architecture: JSON describing the chosen architecture

You MUST strictly derive the backend contract from these inputs.

========================
STRICT RULES
========================
1. Output MUST be VALID JSON ONLY.
2. Output MUST contain ONLY ONE top-level key: "backend_contract".
3. DO NOT generate artifacts, files, or code.
4. DO NOT introduce entities outside domain_model["core_entities"].
5. Use Java + Spring Boot.
6. Use PostgreSQL.
7. If something is unclear, put it in "open_questions".
   NEVER invent details.

========================
OUTPUT FORMAT (STRICT)
========================
{
  "backend_contract": {
    "stack": {
      "language": "Java",
      "framework": "Spring Boot",
      "build_tool": "Maven",
      "java_version": "17"
    },
    "database": {
      "type": "PostgreSQL",
      "migration_tool": "Flyway"
    },
    "modules": [
      {
        "name": "string",
        "responsibility": "string",
        "entities": ["EntityA", "EntityB"]
      }
    ],
    "entities": [
      {
        "name": "EntityName",
        "purpose": "string"
      }
    ],
    "relationships": [],
    "repositories": [],
    "services": [],
    "controllers": [],
    "endpoints": [],
    "non_functional": {
      "logging": "SLF4J",
      "validation": "Jakarta Validation",
      "security": "out_of_scope_level_1"
    },
    "assumptions": [],
    "open_questions": []
  }
}

========================
FAILURE MODE
========================
If you cannot comply, output ONLY:
{
  "backend_contract": {
    "open_questions": ["Unable to produce backend contract from input"]
  }
}
"""

    expected_output = """
A VALID JSON object with ONLY:
{
  "backend_contract": { ... }
}
"""

    return Task(
        description=description,
        expected_output=expected_output,
        agent=backend_agent,
    )