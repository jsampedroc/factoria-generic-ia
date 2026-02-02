from __future__ import annotations
from typing import Any, Iterable


# Common example domains frequently hallucinated by LLMs.
# These are NOT business rules and do NOT define supported domains.
# They are guardrails to prevent unintended reuse of training templates
# when the user idea does not explicitly mention them.
HALLUCINATION_EXAMPLE_DOMAINS = [
    "library", "book", "loan",
    "ecommerce", "order", "product",
    "blog", "post", "comment",
]


def _to_text_list(values: Iterable[Any]) -> list[str]:
    """
    Normalize arbitrary LLM outputs into a list of strings.
    Safely handles strings, dicts, and other objects.
    """
    result: list[str] = []

    for v in values or []:
        if isinstance(v, str):
            result.append(v)
        elif isinstance(v, dict):
            # Flatten dict values into a single textual representation
            result.append(" ".join(str(x) for x in v.values()))
        else:
            result.append(str(v))

    return result


def validate_domain_alignment(idea: str, domain_model: dict):
    """
    Validate that the generated domain model is aligned with the user idea
    and does not introduce unrelated example domains.
    """

    idea_lc = idea.lower()

    domain_text = " ".join(
        _to_text_list([
            domain_model.get("domain_name", ""),
            *domain_model.get("core_entities", []),
            *domain_model.get("key_use_cases", []),
        ])
    ).lower()

    # 🔒 Guardrail against hallucinated example domains
    for word in HALLUCINATION_EXAMPLE_DOMAINS:
        if word in domain_text and word not in idea_lc:
            raise RuntimeError(
                f"Domain misalignment detected: '{word}' not present in idea"
            )

    # 🔍 Minimal structural sanity checks
    if not domain_model.get("core_entities"):
        raise RuntimeError("Domain model has no core entities")

    if not domain_model.get("key_use_cases"):
        raise RuntimeError("Domain model has no key use cases")