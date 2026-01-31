from __future__ import annotations

from ai.llm.llm_config import build_llm
from ai.agents import (
    build_domain_reasoner,
    build_software_architect,
    build_backend_builder,
    build_devops_agent,
)
from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_backend_generation_task
from ai.tasks.devops_task import build_devops_task

def build_workflow(idea: str):
    """Build agents + tasks for the full idea -> backend -> infra workflow."""
    llm = build_llm()

    domain_reasoner = build_domain_reasoner(llm)
    software_architect = build_software_architect(llm)
    backend_builder = build_backend_builder(llm)
    devops_agent = build_devops_agent(llm)

    t1 = build_domain_model_task(domain_reasoner)
    t1.context = {"idea": idea}

    t2 = build_architecture_task(software_architect)
    t3 = build_backend_generation_task(backend_builder)
    t4 = build_devops_task(devops_agent)

    return {
        "agents": [domain_reasoner, software_architect, backend_builder, devops_agent],
        "tasks": [t1, t2, t3, t4],
    }
