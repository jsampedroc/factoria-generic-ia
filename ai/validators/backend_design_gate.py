from __future__ import annotations

from typing import Any, Dict, Set


def validate_backend_design_gate(
    backend_contract: Dict[str, Any],
    backend_design: Dict[str, Any],
) -> bool:
    """
    HARD ADL Gate: Backend Design Validation

    Raises RuntimeError on hard violations:
    - entities not in contract
    - modules not in contract
    - stack not Spring Boot / PostgreSQL
    - missing required structure
    """

    if not backend_contract:
        raise RuntimeError("ADL Gate: Missing backend_contract")

    if not backend_design:
        raise RuntimeError("ADL Gate: Missing backend_design")

    # ---------------------------------------------------------
    # Allowed entities/modules (from contract)
    # ---------------------------------------------------------
    allowed_entities: Set[str] = set()
    for e in backend_contract.get("entities", []):
        if isinstance(e, str) and e.strip():
            allowed_entities.add(e.strip())

    allowed_modules: Set[str] = set()
    for m in backend_contract.get("modules", []):
        if isinstance(m, dict):
            name = (m.get("name") or "").strip()
            if name:
                allowed_modules.add(name)
            for ent in m.get("entities", []) or []:
                if isinstance(ent, str) and ent.strip():
                    allowed_entities.add(ent.strip())

    # ---------------------------------------------------------
    # Validate design entities
    # ---------------------------------------------------------
    design_entities = backend_design.get("entities") or []
    if not isinstance(design_entities, list):
        raise RuntimeError("ADL Gate failed: backend_design.entities must be a list")

    design_entity_names = set()
    for e in design_entities:
        if isinstance(e, dict):
            n = (e.get("name") or "").strip()
            if n:
                design_entity_names.add(n)

    invalid_entities = design_entity_names - allowed_entities
    if invalid_entities:
        raise RuntimeError(
            f"ADL Gate failed: design contains entities not in contract: {sorted(invalid_entities)}"
        )

    # ---------------------------------------------------------
    # Validate design modules
    # ---------------------------------------------------------
    design_modules = backend_design.get("modules") or []
    if not isinstance(design_modules, list):
        raise RuntimeError("ADL Gate failed: backend_design.modules must be a list")

    design_module_names = set()
    for m in design_modules:
        if isinstance(m, dict):
            n = (m.get("name") or "").strip()
            if n:
                design_module_names.add(n)

    invalid_modules = design_module_names - allowed_modules
    if invalid_modules:
        raise RuntimeError(
            f"ADL Gate failed: design contains modules not in contract: {sorted(invalid_modules)}"
        )

    # ---------------------------------------------------------
    # Validate stack constraints
    # ---------------------------------------------------------
    project = backend_design.get("project") or {}
    if not isinstance(project, dict):
        raise RuntimeError("ADL Gate failed: backend_design.project must be an object")

    if (project.get("framework") or "").strip() != "Spring Boot":
        raise RuntimeError("ADL Gate failed: backend must use Spring Boot")

    config = backend_design.get("config") or {}
    if isinstance(config, dict):
        db = config.get("database") or {}
        if isinstance(db, dict):
            if (db.get("type") or "").strip() not in ("PostgreSQL", "Postgres"):
                raise RuntimeError("ADL Gate failed: backend must use PostgreSQL")
        else:
            # If config.database missing, still a hard failure at this stage
            raise RuntimeError("ADL Gate failed: backend_design.config.database missing")
    else:
        raise RuntimeError("ADL Gate failed: backend_design.config must be an object")

    return True