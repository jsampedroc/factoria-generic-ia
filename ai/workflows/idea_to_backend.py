from __future__ import annotations

from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_backend_generation_task
from ai.tasks.devops_task import build_devops_task

def tasks_for_idea(idea: str):
    # Note: in CrewAI, later tasks can refer to previous outputs by context;
    # here we keep it simple, each task will receive prior outputs by the LLM.
    t1 = build_domain_model_task(idea)
    t2 = build_architecture_task("Usa el output del task anterior como entrada.")
    t3 = build_backend_generation_task("Usa el output del task de arquitectura como entrada.")
    t4 = build_devops_task()
    return [t1, t2, t3, t4]
