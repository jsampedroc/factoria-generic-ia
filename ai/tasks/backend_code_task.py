from __future__ import annotations

import json
from crewai import Task


def build_backend_code_task(
    backend_agent,
    *,
    backend_contract: dict,
    backend_design: dict,
    base_package: str,
    app_name: str,
    allowed_entities: list[str],
    allowed_modules: list[str],
) -> Task:
    """
    Backend Code – Level 3 (ADL / MVP enterprise)

    Inputs are embedded to avoid CrewAI context typing issues.
    Output: VALID JSON with only {"backend_code": {...}}.
    """

    contract_json = json.dumps(backend_contract, ensure_ascii=False, indent=2)
    design_json = json.dumps(backend_design, ensure_ascii=False, indent=2)
    allowed_entities_json = json.dumps(allowed_entities, ensure_ascii=False, indent=2)
    allowed_modules_json = json.dumps(allowed_modules, ensure_ascii=False, indent=2)

    description = f"""
You are a Senior Backend Engineer operating under an Agentic Development Lifecycle (ADL)
within an Enterprise Multi-Agent Orchestration (EMAO).

========================
GOAL (LEVEL 3 ONLY)
========================
Generate a COMPLETE Spring Boot backend MVP (enterprise skeleton) as FILE ARTIFACTS.
You MUST output VALID JSON ONLY.

The generated project MUST be runnable with:
- Java 17
- Maven
- Spring Boot
- PostgreSQL
- Flyway

========================
HARD BINDING (MANDATORY)
========================
allowed_entities:
{allowed_entities_json}

allowed_modules:
{allowed_modules_json}

RULES:
1) You MUST NOT introduce any entity outside allowed_entities.
2) You MUST NOT introduce any module outside allowed_modules.
3) Use EXACT names from allowed_entities.
4) Do NOT invent extra domain concepts.

========================
INPUT SOURCE OF TRUTH (EMBEDDED)
========================
BACKEND CONTRACT (Level 1):
----------------------------------------
{contract_json}
----------------------------------------

BACKEND DESIGN (Level 2):
----------------------------------------
{design_json}
----------------------------------------

base_package: {base_package}
app_name: {app_name}

========================
STRICT OUTPUT RULES
========================
1) Output MUST be VALID JSON ONLY.
2) Output MUST contain ONLY ONE top-level key: "backend_code".
3) backend_code.root_dir MUST be exactly "backend".
4) backend_code.artifacts MUST be a list of objects {{path, content}}.
5) Each artifact.path MUST be:
   - relative (no leading "/")
   - MUST NOT contain ".."
   - MUST start with one of:
       - "pom.xml"
       - "Dockerfile"
       - "docker-compose.yml"
       - "src/main/java/"
       - "src/main/resources/"
       - "src/test/java/"

========================
MANDATORY FILES
========================
You MUST include at least these artifacts:

A) Build & runtime:
- pom.xml (Spring Boot 3.x, Java 17, deps: web, validation, data-jpa, flyway, actuator, postgres)
- Dockerfile
- docker-compose.yml (postgres)

B) Spring Boot app:
- src/main/java/<base_package_path>/Application.java

C) Layers (enterprise skeleton):
- api/controller/*Controller.java
- application/service/*Service.java
- domain/model/* (JPA entities)
- infrastructure/persistence/*Repository.java
- config/SecurityConfig.java (minimal placeholder)

D) Resources:
- src/main/resources/application.yml
- src/main/resources/application-dev.yml
- src/main/resources/db/migration/V1__init.sql

E) Tests (smoke):
- src/test/java/<base_package_path>/ApplicationContextTest.java

========================
OUTPUT FORMAT (STRICT)
========================
{{
  "backend_code": {{
    "root_dir": "backend",
    "base_package": "{base_package}",
    "artifacts": [
      {{"path": "pom.xml", "content": "..."}}
    ],
    "assumptions": [],
    "open_questions": []
  }}
}}

FAILURE MODE:
If you cannot comply, output ONLY:
{{ "backend_code": {{ "root_dir": "backend", "base_package": "", "artifacts": [], "open_questions": ["Unable to generate backend MVP artifacts from input"] }} }}
"""

    expected_output = 'VALID JSON ONLY: { "backend_code": { "root_dir": "backend", "base_package": "...", "artifacts": [...], "assumptions": [], "open_questions": [] } }'

    return Task(
        description=description,
        expected_output=expected_output,
        agent=backend_agent,
    )
