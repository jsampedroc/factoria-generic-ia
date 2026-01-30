from __future__ import annotations
from typing import Any, Dict
from datetime import datetime


class PipelineState:
    """
    Estado central del pipeline.
    Guarda resultados, errores, retries y contexto global.
    """

    def __init__(self, idea: str):
        self.idea = idea
        self.context: Dict[str, Any] = {}
        self.steps: Dict[str, Dict[str, Any]] = {}
        self.started_at = datetime.utcnow().isoformat()
        self.finished_at: str | None = None

    def start(self, step: str) -> None:
        self.steps.setdefault(step, {
            "status": "pending",
            "retries": 0,
            "output": None,
            "error": None,
        })
        self.steps[step]["status"] = "running"

    def success(self, step: str, output: Any) -> None:
        self.steps[step]["status"] = "success"
        self.steps[step]["output"] = output

    def fail(self, step: str, error: Exception | str) -> None:
        self.steps[step]["status"] = "failed"
        self.steps[step]["error"] = str(error)
        self.steps[step]["retries"] += 1

    def get_retries(self, step: str) -> int:
        return self.steps.get(step, {}).get("retries", 0)

    def set_context(self, key: str, value: Any) -> None:
        self.context[key] = value

    def finish(self) -> None:
        self.finished_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idea": self.idea,
            "context": self.context,
            "steps": self.steps,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }