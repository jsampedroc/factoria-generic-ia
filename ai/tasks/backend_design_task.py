from crewai import Task


def build_backend_design_task(backend_agent):
    """
    Backend Design – Level 2 (ADL / Design-only, HARD-BOUND)

    INPUT (task.context):
    - backend_contract: dict
    - architecture: dict
    - allowed_entities: list[str]   (SOURCE OF TRUTH)
    - allowed_modules: list[str]    (SOURCE OF TRUTH)

    OUTPUT (STRICT JSON ONLY):
    { "backend_design": { ... } }

    NOTE:
    - NO code, NO artifacts
    """

    description = """
You are a Senior Backend Architect operating under an Agentic Development Lifecycle (ADL)
within an Enterprise Multi-Agent Orchestration (EMAO).

========================
GOAL (LEVEL 2 ONLY)
========================
Produce a BACKEND DESIGN (technical blueprint), NOT code and NOT files.

========================
HARD BINDING (MANDATORY)
========================
You MUST use ONLY the following lists as SOURCE OF TRUTH:

- allowed_entities: the ONLY allowed domain entities
- allowed_modules: the ONLY allowed module names

RULES:
1) You MUST NOT introduce any entity outside allowed_entities.
2) You MUST NOT introduce any module outside allowed_modules.
3) Entities MUST use the EXACT same names as allowed_entities.
4) Modules MUST use the EXACT same names as allowed_modules.

If you cannot comply, output ONLY:
{ "backend_design": { "open_questions": ["Unable to comply with allowed_entities/allowed_modules"] } }

========================
INPUTS
========================
You will also receive:
- backend_contract (Level 1 output): structure + responsibilities
- architecture: stack and style guidance

You MUST derive the design strictly from those inputs AND the hard-binding lists above.

========================
STRICT OUTPUT RULES
========================
- Output MUST be VALID JSON ONLY (no markdown).
- Output MUST contain ONLY ONE top-level key: "backend_design".
- DO NOT output "artifacts". DO NOT write files. DO NOT generate code.
- Level 2 means: fields, relationships, DTOs, endpoints, method signatures (no logic).

========================
STACK (MANDATORY)
========================
- Java 17
- Spring Boot
- PostgreSQL
- Flyway

========================
OUTPUT FORMAT (STRICT)
========================
{
  "backend_design": {
    "project": {
      "language": "Java",
      "framework": "Spring Boot",
      "java_version": "17",
      "build_tool": "Maven",
      "packaging": "jar"
    },
    "modules": [
      {
        "name": "string (must be in allowed_modules)",
        "responsibility": "string",
        "entities": ["EntityA (must be in allowed_entities)"]
      }
    ],
    "entities": [
      {
        "name": "EntityName (must be in allowed_entities)",
        "table": "snake_case_table",
        "id_type": "UUID",
        "fields": [
          {"name": "id", "type": "UUID", "required": true},
          {"name": "createdAt", "type": "Instant", "required": true},
          {"name": "updatedAt", "type": "Instant", "required": true}
        ]
      }
    ],
    "relationships": [],
    "dtos": [],
    "repositories": [],
    "services": [],
    "controllers": [],
    "endpoints": [],
    "config": {
      "database": { "type": "PostgreSQL", "migration_tool": "Flyway" }
    },
    "assumptions": [],
    "open_questions": []
  }
}
"""

    expected_output = """
A VALID JSON object with ONLY:
{ "backend_design": { ... } }
"""

    return Task(
        description=description,
        expected_output=expected_output,
        agent=backend_agent,
    )