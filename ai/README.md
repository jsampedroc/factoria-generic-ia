# Orquestador IA (CrewAI)

Este directorio contiene el **orquestador** (en Python) que coordina agentes para transformar una *idea* en:

- Modelo de dominio (DDD)
- Arquitectura
- Backend (Spring Boot) + OpenAPI + tests
- Artefactos de despliegue (Docker Compose)

## Ejecutar

Desde la raíz del repo:

```bash
python -m ai.main --idea "Una app para gestionar pedidos..." --mode backend
```

Los archivos generados se escriben en `output/` (por defecto).

## Estructura

- `agents/`: definiciones de agentes (core)
- `tasks/`: tareas que ejecuta el crew
- `workflows/`: composición de tareas por modo
- `tools/`: utilidades (p.ej. `file_writer`)
- `orchestration/`: factory para construir el crew
