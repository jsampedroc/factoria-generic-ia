from __future__ import annotations

from ai.tasks.domain_model_task import build_domain_model_task

def tasks_for_idea(idea: str):
    return [build_domain_model_task(idea)]
