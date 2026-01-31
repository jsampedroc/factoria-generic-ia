from __future__ import annotations

from ai.llm.llm_config import build_llm
from ai.agents import build_domain_reasoner
from ai.tasks.domain_model_task import build_domain_model_task

def build_workflow(idea: str):
    """Build agents + tasks for domain modeling workflow."""
    llm = build_llm()
    domain_reasoner = build_domain_reasoner(llm)
    task = build_domain_model_task(domain_reasoner)
    task.context = {"idea": idea}
    return {"agents": [domain_reasoner], "tasks": [task]}
