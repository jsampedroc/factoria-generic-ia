from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_backend_generation_task
from ai.tasks.devops_task import build_devops_task

def build_all_tasks(*, domain_reasoner, software_architect, backend_builder, devops_agent):
    """Return tasks in the golden order."""
    return [
        build_domain_model_task(domain_reasoner),
        build_architecture_task(software_architect),
        build_backend_generation_task(backend_builder),
        build_devops_task(devops_agent),
    ]
