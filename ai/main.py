from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

from ai.logging import tee_to_file
from ai.reporting.report_generator import generate_report

from ai.llm.llm_config import build_llm
from ai.agents import (
    build_backend_builder,
    build_devops_agent,
    build_domain_reasoner,
    build_software_architect,
)

from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_backend_generation_task
from ai.tasks.devops_task import build_devops_task

from ai.validators.domain import validate_domain_alignment
from ai.utils.llm_output import normalize_llm_output


# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------

def main() -> int:
    # 1) Cargar .env
    load_dotenv()

    idea = _read_idea_from_cli()
    if not idea:
        print(
            "\nFalta la idea. Ejemplos:\n"
            "  python -m ai.main \"App de reservas para un gimnasio...\"\n"
            "  cat idea.txt | python -m ai.main\n"
        )
        return 2

    # 2) Preparar outputs
    out_dir = _ensure_output_dir()
    os.environ["FACTORIA_OUTPUT_DIR"] = str(out_dir)

    # 3) Logging tipo tee
    log_path = out_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file = tee_to_file(log_path)
    print(f"📝 Logging activado en: {log_path}")

    # 4) Importes tardíos (evitan side-effects)
    from ai.pipeline.state import PipelineState
    from ai.pipeline.decision_engine import DecisionEngine, Decision
    from ai.golden_path.resolver import load_yaml, apply_run_config

    # 5) Inicializar estado y motor de decisiones
    state = PipelineState(idea=idea)
    decision_engine = DecisionEngine(max_retries=2)

    # 6) Cargar golden path / run config
    try:
        golden_path = load_yaml(Path("golden_path.yaml"))
        run_config = load_yaml(Path("run_config.yaml"))

        resolved_golden_path = apply_run_config(golden_path, run_config)
        state.set_context("golden_path", resolved_golden_path)
        print("🟡 Golden Path cargado y aplicado correctamente")
    except Exception as e:
        print("❌ Error cargando Golden Path / Run Config")
        print(str(e))
        log_file.close()
        return 1

    # 7) Construir LLM + agentes
    llm = build_llm()
    domain_reasoner = build_domain_reasoner(llm)
    software_architect = build_software_architect(llm)
    backend_builder = build_backend_builder(llm)
    devops_agent = build_devops_agent(llm)

    # 8) Construir tasks que NO dependen de outputs previos
    domain_model_task = build_domain_model_task(idea)
    backend_generation_task = build_backend_generation_task(backend_builder)
    devops_task = build_devops_task(devops_agent)

    # -----------------------------------------------------------------------
    # Helper para ejecutar pasos con retries + feedback
    def run_step(step_name, agent, task, inputs):
        while True:
            try:
                print(f"\n🔹 Ejecutando paso: {step_name}")
                state.start(step_name)

                if inputs is not None:
                    task.context = inputs

                result = agent.execute_task(task)

                state.success(step_name, result)

                decision = decision_engine.decide(
                    step=step_name,
                    success=True,
                    retries=state.get_retries(step_name),
                )

                if decision == Decision.CONTINUE:
                    return result

                raise RuntimeError(f"Decisión inesperada: {decision}")

            except Exception as e:
                state.fail(step_name, e)

                decision = decision_engine.decide(
                    step=step_name,
                    success=False,
                    retries=state.get_retries(step_name),
                    error=e,
                )

                print(f"⚠️ Error en {step_name}: {e}")
                print(f"🧠 Decisión: {decision.value}")

                if decision == Decision.RETRY:
                    inputs = dict(inputs or {})
                    inputs["_retry_context"] = {
                        "step": step_name,
                        "attempt": state.get_retries(step_name),
                        "last_error": str(e),
                    }
                    print(f"🔁 Reintentando {step_name} con feedback...")
                    continue

                print(f"❌ Abortando pipeline en paso: {step_name}")
                raise

    # -----------------------------------------------------------------------
    try:
        # =======================
        # 1) DOMAIN MODEL
        # =======================
        raw_domain_output = run_step(
            "domain_model",
            domain_reasoner,
            domain_model_task,
            {},  # la idea ya está embebida en el Task
        )

        domain_output = normalize_llm_output(raw_domain_output)
        state.domain_model = domain_output

        open_questions = domain_output.get("open_questions", [])

        if open_questions:
            print("\n🟡 ESTADO: NEEDS_INPUT (DOMAIN)\n")
            for i, q in enumerate(open_questions, start=1):
                print(f"{i}. {q}")

            state.status = "NEEDS_INPUT"
            state.open_questions = open_questions

            generate_report(state)
            log_file.close()
            print("\nℹ️ Execution paused. Awaiting additional input.")
            return 0

        # 🔒 Validación crítica de coherencia del dominio
        validate_domain_alignment(idea, domain_output)

        # =======================
        # 2) ARCHITECTURE
        # =======================
        architecture_task = build_architecture_task(domain_output)

        raw_architecture_output = run_step(
            "architecture",
            software_architect,
            architecture_task,
            {},  # domain_model embebido en el Task
        )

        architecture_output = normalize_llm_output(raw_architecture_output)
        state.architecture = architecture_output

        if architecture_output.get("status") == "NEEDS_INPUT":
            open_q = architecture_output.get("open_questions", [])

            print("\n🟡 ESTADO: NEEDS_INPUT (ARCHITECTURE)\n")
            for i, q in enumerate(open_q, start=1):
                print(f"{i}. {q}")

            state.status = "NEEDS_INPUT"
            state.open_questions = open_q

            generate_report(state)
            log_file.close()
            print("\nℹ️ Execution paused. Awaiting additional input.")
            return 0

        # =======================
        # 3) BACKEND
        # =======================
        raw_backend_output = run_step(
            "backend",
            backend_builder,
            backend_generation_task,
            architecture_output,
        )

        backend_output = normalize_llm_output(raw_backend_output)
        state.backend = backend_output

        # =======================
        # 4) DEVOPS / INFRA
        # =======================
        raw_infra_output = run_step(
            "infra",
            devops_agent,
            devops_task,
            backend_output,
        )

        infra_output = normalize_llm_output(raw_infra_output)
        state.infrastructure = infra_output

        print("\n✅ Pipeline completado correctamente")

    except Exception:
        print("\n❌ Pipeline finalizado con errores")
        state.status = "ERROR"
        generate_report(state)
        log_file.close()
        return 1

    # -----------------------------------------------------------------------
    state.finish()
    generate_report(state)

    print(f"\n📁 Outputs generados en: {out_dir}")
    log_file.close()
    return 0


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    raise SystemExit(main())