from crewai import Task


def build_backend_code_task(backend_agent):
    """
    Backend Code – Level 3 (ADL / MVP enterprise)

    Input (task.context):
      - backend_contract (dict)
      - backend_design (dict)
      - base_package (str)  e.g. "com.factoria.app"
      - app_name (str)      e.g. "daycare"
      - allowed_entities (list[str])  HARD BIND
      - allowed_modules (list[str])   HARD BIND

    Output (STRICT JSON ONLY):
    {
      "backend_code": {
        "root_dir": "backend",
        "base_package": "...",
        "artifacts": [{"path": "...", "content": "..."}],
        "assumptions": [],
        "open_questions": []
      }
    }
    """

    description = """
You are a Senior Backend Engineer operating under an Agentic Development Lifecycle (ADL)
within an Enterprise Multi-Agent Orchestration (EMAO).

========================
GOAL (LEVEL 3 ONLY)
========================
Generate a COMPLETE Spring Boot backend MVP (enterprise skeleton) as FILE ARTIFACTS.
You MUST NOT output markdown. You MUST output VALID JSON ONLY.

The generated project MUST be runnable with:
- Java 17
- Maven
- Spring Boot
- PostgreSQL
- Flyway

========================
HARD BINDING (MANDATORY)
========================
You will receive:
- allowed_entities: the ONLY allowed entity names
- allowed_modules: the ONLY allowed module names

RULES:
1) You MUST NOT introduce any entity outside allowed_entities.
2) You MUST NOT introduce any module outside allowed_modules.
3) Use EXACT names from allowed_entities.
4) Do NOT invent extra domain concepts.

========================
INPUT SOURCE OF TRUTH
========================
- backend_design is the primary source for entities, fields, endpoints, services, packages.
- backend_contract provides boundaries and responsibilities.
- base_package is mandatory and MUST be used for Java packages.

========================
STRICT OUTPUT RULES
========================
1) Output MUST be VALID JSON ONLY.
2) Output MUST contain ONLY ONE top-level key: "backend_code".
3) backend_code.root_dir MUST be exactly "backend".
4) backend_code.artifacts MUST be a list of objects {path, content}.
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
6) DO NOT use file writing tools. Only return artifacts.

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
- api/controller/*Controller.java (based on backend_design.controllers/endpoints)
- application/service/*Service.java (+ impl if you prefer)
- domain/model/* (JPA entities for allowed_entities)
- infrastructure/persistence/*Repository.java (Spring Data JPA)
- config/JpaConfig.java (optional minimal)
- config/SecurityConfig.java (minimal allow-all OR basic placeholder; keep simple)

D) Resources:
- src/main/resources/application.yml
- src/main/resources/application-dev.yml
- src/main/resources/db/migration/V1__init.sql (Flyway baseline minimal)

E) Tests (smoke):
- src/test/java/<base_package_path>/ApplicationContextTest.java

========================
QUALITY RULES
========================
- Keep code minimal but clean and compilable.
- Use UUID ids, Instant timestamps.
- JPA annotations correctly.
- Validation annotations where obvious.
- REST controllers return ResponseEntity.
- No complex business logic (Level 3 MVP).

========================
OUTPUT FORMAT (STRICT)
========================
{
  "backend_code": {
    "root_dir": "backend",
    "base_package": "com.example.app",
    "artifacts": [
      {"path": "pom.xml", "content": "..."},
      {"path": "src/main/java/com/example/app/Application.java", "content": "..."}
    ],
    "assumptions": [],
    "open_questions": []
  }
}

FAILURE MODE:
If you cannot comply, output ONLY:
{ "backend_code": { "root_dir": "backend", "base_package": "", "artifacts": [], "open_questions": ["Unable to generate backend MVP artifacts from input"] } }
"""

    expected_output = """
VALID JSON ONLY:
{ "backend_code": { "root_dir":"backend", "base_package":"...", "artifacts":[...], "assumptions":[], "open_questions":[] } }
"""

    return Task(
        description=description,
        expected_output=expected_output,
        agent=backend_agent,
    )