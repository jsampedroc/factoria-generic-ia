from ai.tasks.domain_model_task import domain_model_task
from ai.tasks.architecture_task import architecture_task
from ai.tasks.backend_generation_task import backend_generation_task
from ai.tasks.devops_task import devops_task

# EL ORDEN ES VITAL:
# 1. Entender el negocio (Domain)
# 2. Diseñar los planos (Architecture)
# 3. Construir el edificio (Backend)
# 4. Poner la electricidad y gas (DevOps)
ALL_TASKS = [
    domain_model_task,
    architecture_task,
    backend_generation_task,
    devops_task,
    
]