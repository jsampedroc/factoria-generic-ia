from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime
from typing import Any


def _resolve_output_dir() -> Path:
    # Prefer the pipeline output dir if provided; fall back to ./outputs
    out = Path(os.getenv("FACTORIA_OUTPUT_DIR", "outputs")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out


def generate_report(state: Any) -> Path:
    """Write a human-readable report into FACTORIA_OUTPUT_DIR/report.md.

    The report is intended to exist for:
    - successful runs
    - NEEDS_INPUT runs (question-asking)
    - failed runs (best-effort)
    """
    output_dir = _resolve_output_dir()
    report_path = output_dir / "report.md"

    status = getattr(state, "status", "OK")
    idea = getattr(state, "idea", None)

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Execution Report\n\n")
        f.write(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"- Status: {status}\n")
        if idea:
            f.write(f"- Idea: {idea}\n")
        f.write("\n")

        if status == "NEEDS_INPUT":
            f.write("## Additional information required\n\n")
            f.write(
                "The execution requires additional information before continuing.\n\n"
            )
            f.write("Open questions:\n")
            for q in getattr(state, "open_questions", []) or []:
                f.write(f"- {q}\n")
            f.write("\n")
            return report_path

        # If there was an error, include it when available
        err = getattr(state, "last_error", None) or getattr(state, "error", None)
        if status in ("ERROR", "FAILED") and err:
            f.write("## Error\n\n")
            f.write(f"{err}\n\n")

        if hasattr(state, "domain_model"):
            f.write("## Domain Model\n\n")
            f.write(f"{getattr(state, 'domain_model')}\n\n")

        if hasattr(state, "architecture"):
            f.write("## Architecture\n\n")
            f.write(f"{getattr(state, 'architecture')}\n\n")

        if hasattr(state, "backend"):
            f.write("## Backend\n\n")
            f.write(f"{getattr(state, 'backend')}\n\n")

        if hasattr(state, "infrastructure"):
            f.write("## Infrastructure\n\n")
            f.write(f"{getattr(state, 'infrastructure')}\n\n")

    return report_path
