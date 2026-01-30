from __future__ import annotations

import os
import sys
from pathlib import Path
from ai.agents import backend_builder, devops_agent, domain_reasoner, software_architect

from ai.reporting.report_generator import generate_reports


from ai.logging import tee_to_file
from datetime import datetime

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
    # 1️⃣ Cargar .env
    load_dotenv()

    idea = _read_idea_from_cli()
    if not idea:
        print(
            "\nFalta la idea. Ejemplos:\n"
            "  python -m ai.main \"App de reservas para un gimnasio...\"\n"
            "  cat idea.txt | python -m ai.main\n"
        )
        return 2

    # 2️⃣ Preparar outputs
    out_dir = _ensure_output_dir()
    os.environ["FACTORIA_OUTPUT_DIR"] = str(out_dir)


    # 🔴 ACTIVAR LOGGING TIPO TEE
    log_path = out_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file = tee_to_file(log_path)

    print(f"📝 Logging activado en: {log_path}")

    # 3️⃣ Importes tardíos (seguros)
    from ai.pipeline.state import PipelineState
    from ai.pipeline.decision_engine import DecisionEngine, Decision

    from ai.golden_path.resolver import load_yaml, apply_run_config

    from ai.tasks.domain_model_task import domain_model_task
    from ai.tasks.architecture_task import architecture_task
    from ai.tasks.backend_generation_task import backend_generation_task
    from ai.tasks.devops_task import devops_task

    # 4️⃣ Inicializar estado y motor de decisiones
    state = PipelineState(idea=idea)
    decision_engine = DecisionEngine(max_retries=2)

    # =========================
    # 🟡 GOLDEN PATH (PASO 1-2-3)
    # =========================
    try:
        golden_path = load_yaml(Path("golden_path.yaml"))
        run_config = load_yaml(Path("run_config.yaml"))

        resolved_golden_path = apply_run_config(
            golden_path,
            run_config
        )

        state.set_context("golden_path", resolved_golden_path)

        print("🟡 Golden Path cargado y aplicado correctamente")

    except Exception as e:
        print("❌ Error cargando Golden Path / Run Config")
        print(str(e))
        return 1

    # Helper para ejecutar pasos con retries + feedback
    def run_step(step_name, agent, task, inputs):
     while True:
        try:
            print(f"\n🔹 Ejecutando paso: {step_name}")
            state.start(step_name)

            # 🔥 Inyectar inputs en el task
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
                inputs = dict(inputs)
                inputs["_retry_context"] = {
                    "step": step_name,
                    "attempt": state.get_retries(step_name),
                    "last_error": str(e),
                }
                print(f"🔁 Reintentando {step_name} con feedback...")
                continue

            print(f"❌ Abortando pipeline en paso: {step_name}")
            raise


    try:
        # =========================
        # 1️⃣ DOMAIN MODEL
        # =========================
        domain_output = run_step(
            "domain_model",
            domain_reasoner,
            domain_model_task,
            {"idea": idea},
        )

        # =========================
        # 2️⃣ ARCHITECTURE
        # =========================
        architecture_output = run_step(
            "architecture",
            software_architect,
            architecture_task,
            domain_output,
        )

        # =========================
        # 3️⃣ BACKEND
        # =========================
        backend_output = run_step(
            "backend",
            backend_builder,
            backend_generation_task,
            architecture_output,
        )

        # =========================
        # 4️⃣ DEVOPS / INFRA
        # =========================
        infra_output = run_step(
            "infra",
            devops_agent,
            devops_task,
            backend_output,
        )

        print("\n✅ Pipeline completado correctamente")

    except Exception:
        print("\n❌ Pipeline finalizado con errores")
        return 1

    print(f"\n📁 Outputs generados en: {out_dir}")


    state.finish()
    generate_reports(state)

    # Cerrar fichero de log limpiamente
    log_file.close()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())