from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class DomainProjection:
    """
    A hard-binded, minimal domain contract used to ground downstream agents.
    Keep it small, explicit, and non-interpretative.
    """
    domain_name: str
    entities: List[str]
    key_use_cases: List[str]
    language: str = "es"  # best effort


def build_domain_projection(domain_model: Dict[str, Any], idea: str) -> Dict[str, Any]:
    """
    Build a minimal, hard-binded contract from the domain_model.
    This contract is what downstream agents MUST use (no interpretation).
    """
    domain_name = (domain_model.get("domain_name") or "").strip() or "UnnamedDomain"

    raw_entities = domain_model.get("core_entities") or []
    entities = []
    for e in raw_entities:
        if not isinstance(e, str):
            continue
        e = e.strip()
        if e and e not in entities:
            entities.append(e)

    raw_use_cases = domain_model.get("key_use_cases") or []
    key_use_cases = []
    for uc in raw_use_cases:
        if not isinstance(uc, str):
            continue
        uc = uc.strip()
        if uc and uc not in key_use_cases:
            key_use_cases.append(uc)

    # Very light language guess (optional, but useful)
    idea_lc = (idea or "").lower()
    language = "es" if any(x in idea_lc for x in ["aplicación", "gestión", "guarder", "niñ", "pagos", "personal"]) else "en"

    projection = DomainProjection(
        domain_name=domain_name,
        entities=entities,
        key_use_cases=key_use_cases,
        language=language,
    )

    # Return as plain dict for easy JSON/context passing
    return {
        "domain_name": projection.domain_name,
        "entities": projection.entities,
        "key_use_cases": projection.key_use_cases,
        "language": projection.language,
    }