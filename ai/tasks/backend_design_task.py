from __future__ import annotations

import json
from crewai import Task


def build_backend_design_task(
    backend_agent,
    *,
    backend_contract: dict,
    architecture: dict,
    allowed_entities: list[str],
    allowed_modules: list[str],
) -> Task:
    """
    Backend Design – Level 2 (ADL / Design-only, HARD-BOUND)

    Inputs are embedded to avoid CrewAI context typing issues.
    Output: VALID JSON with only {"backend_design": {...}}.
    """

    contract_json = json.dumps(backend_contract, ensure_ascii=False, indent=2)
    arch_json = json.dumps(architecture, ensure_ascii=False, indent=2)
    allowed_entities_json = json.dumps(allowed_entities, ensure_ascii=False, indent=2)
    allowed_modules_json = json.dumps(allowed_modules, ensure_ascii=False, indent=2)

    description = f"""
You are a Senior Backend Architect operating under an Agentic Development Lifecycle (ADL)
within an Enterprise Multi-Agent Orchestration (EMAO).

========================
GOAL (LEVEL 2 ONLY)
========================
Produce a BACKEND DESIGN (technical blueprint), NOT code and NOT files.

========================
HARD BINDING (MANDATORY)
========================
SOURCE OF TRUTH:
- allowed_entities (ONLY allowed domain entities)
- allowed_modules (ONLY allowed module names)

allowed_entities:
{allowed_entities_json}

allowed_modules:
{allowed_modules_json}

RULES:
1) You MUST NOT introduce any entity outside allowed_entities.
2) You MUST NOT introduce any module outside allowed_modules.
3) Entities MUST use the EXACT same names as allowed_entities.
4) Modules MUST use the EXACT same names as allowed_modules.

If you cannot comply, output ONLY:
{{ "backend_design": {{ "open_questions": ["Unable to comply with allowed_entities/allowed_modules"] }} }}

========================
INPUTS (EMBEDDED)
========================
BACKEND CONTRACT (Level 1):
----------------------------------------
{contract_json}
----------------------------------------

ARCHITECTURE:
----------------------------------------
{arch_json}
----------------------------------------

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
{{
  "backend_design": {{
    "project": {{
      "language": "Java",
      "framework": "Spring Boot",
      "java_version": "17",
      "build_tool": "Maven",
      "packaging": "jar"
    }},
    "modules": [
      {{
        "name": "string (must be in allowed_modules)",
        "responsibility": "string",
        "entities": ["EntityA (must be in allowed_entities)"]
      }}
    ],
    "entities": [
      {{
        "name": "EntityName (must be in allowed_entities)",
        "table": "snake_case_table",
        "id_type": "UUID",
        "fields": [
          {{"name": "id", "type": "UUID", "required": true}},
          {{"name": "createdAt", "type": "Instant", "required": true}},
          {{"name": "updatedAt", "type": "Instant", "required": true}}
        ]
      }}
    ],
    "relationships": [],
    "dtos": [],
    "repositories": [],
    "services": [],
    "controllers": [],
    "endpoints": [],
    "config": {{
      "database": {{ "type": "PostgreSQL", "migration_tool": "Flyway" }}
    }},
    "assumptions": [],
    "open_questions": []
  }}
}}
"""

    expected_output = 'VALID JSON ONLY: { "backend_design": { ... } }'

    return Task(
        description=description,
        expected_output=expected_output,
        agent=backend_agent,
    )
