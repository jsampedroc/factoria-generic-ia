from __future__ import annotations

from typing import Any, Dict, List

from ai.utils.llm_output import normalize_llm_output


def _is_artifact(obj: Any) -> bool:
    return (
        isinstance(obj, dict)
        and isinstance(obj.get("path"), str)
        and obj.get("path").strip() != ""
        and isinstance(obj.get("content"), str)
    )


def normalize_backend_output(raw_output: object) -> dict:
    """
    Normalize and validate backend generation output.

    Accepts two shapes:
    A) { "status": "OK", "artifacts": [ {path, content}, ... ] }
    B) { "status": "OK", "modules": [ { artifacts: [ {path, content}, ... ] }, ... ] }

    Returns canonical shape:
    { "status": "OK", "artifacts": [...], ...other fields preserved... }
    """
    output = normalize_llm_output(raw_output)

    if not isinstance(output, dict):
        raise ValueError("Backend output is not a JSON object")

    status = output.get("status")
    if status not in ("OK", "NEEDS_INPUT", "ERROR"):
        raise ValueError(f"Invalid backend status: {status}")

    # NEEDS_INPUT is allowed
    if status == "NEEDS_INPUT":
        oq = output.get("open_questions", [])
        if not isinstance(oq, list):
            raise ValueError("open_questions must be a list")
        return output

    # ERROR is allowed (but should include reason)
    if status == "ERROR":
        # Keep as-is; main/report can show diagnostics
        return output

    # status == OK -> must contain artifacts (direct or nested)
    artifacts: List[Dict[str, str]] = []

    # A) Root artifacts
    root_artifacts = output.get("artifacts", [])
    if isinstance(root_artifacts, list):
        artifacts.extend([a for a in root_artifacts if _is_artifact(a)])

    # B) Modules -> artifacts
    modules = output.get("modules", [])
    if isinstance(modules, list):
        for m in modules:
            if not isinstance(m, dict):
                continue
            m_arts = m.get("artifacts", [])
            if isinstance(m_arts, list):
                artifacts.extend([a for a in m_arts if _is_artifact(a)])

    # Remove duplicates by path (keep first)
    seen = set()
    uniq: List[Dict[str, str]] = []
    for a in artifacts:
        p = a["path"]
        if p in seen:
            continue
        seen.add(p)
        uniq.append({"path": p, "content": a["content"]})

    if not uniq:
        raise ValueError(
            "Backend output status=OK but no valid artifacts were found "
            "(expected root 'artifacts' or 'modules[*].artifacts')."
        )

    # Canonicalize
    output["artifacts"] = uniq
    return output