from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _ensure_output_dir() -> Path:
    out = Path(os.getenv("FACTORIA_OUTPUT_DIR", "outputs")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out


def _read_idea_from_cli() -> str:
    # Uso:
    #   python -m ai.main "Mi idea..."
    #   python -m ai.main < idea.txt
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def main() -> int:
    # 1) Cargar .env ANTES de importar agents/llm_config (usan os.getenv en import-time)
    load_dotenv()

    idea = _read_idea_from_cli()
    if not idea:
        print("\nFalta la idea. Ejemplos:\n"
              "  python -m ai.main \"App de reservas para un gimnasio...\"\n"
              "  cat idea.txt | python -m ai.main\n")
        return 2

    out_dir = _ensure_output_dir()
    os.environ["FACTORIA_OUTPUT_DIR"] = str(out_dir)

    from crewai import Crew
    from ai.agents import domain_reasoner, software_architect, backend_builder, devops_agent
    from ai.tasks.core_tasks import (
        domain_model_task,
        architecture_task,
        backend_generation_task,
        devops_task,
    )

    crew = Crew(
        agents=[domain_reasoner, software_architect, backend_builder, devops_agent],
        tasks=[domain_model_task, architecture_task, backend_generation_task, devops_task],
        verbose=True,
    )

    result = crew.kickoff(inputs={"idea": idea})
    print("\n✅ Ejecución completada")
    print(f"📁 Outputs: {out_dir}")
    if result:
        print("\n--- Resultado final (resumen) ---")
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
