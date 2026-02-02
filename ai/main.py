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
from ai.utils.backend_output import normalize_backend_output
from ai.cli.interactive import ask_user_questions
from ai.artifacts.writer import write_artifacts


# ---------------------------------------------------------------------------

def _ensure_output_dir() -> Path:
    out = Path(os.getenv("FACTORIA_OUTPUT_DIR", "outputs")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out


def _read_idea_from_cli() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


# ---------------------------------------------------------------------------

def main() -> int:
    load_dotenv()

    idea = _read_idea_from_cli()
    if not idea:
        print(
            "\nFalta la idea. Ejemplos:\n"
            "  python -m ai.main \"App de reservas para un gimnasio...\"\n"
            "  cat idea.txt | python -m ai.main\n"
        )
        return 2

    out_dir = _ensure_output_dir()
    os.environ["FACTORIA_OUTPUT_DIR"] = str(out_dir)

    log_path = out_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file = tee_to_file(log_path)
    print(f"📝 Logging activado en: {log_path}")

    from ai.pipeline.state import PipelineState
    from ai.pipeline.decision_engine import DecisionEngine, Decision
    from ai.golden_path.resolver import load_yaml, apply_run_config

    state = PipelineState(idea=idea)
    decision_engine = DecisionEngine(max_retries=2)

    try:
        golden_path = load_yaml(Path("golden_path.yaml"))
        run_config = load_yaml(Path("run_config.yaml"))
        resolved = apply_run_config(golden_path, run_config)
        state.set_context("golden_path", resolved)
    except Exception as e:
        print("❌ Error cargando Golden Path / Run Config")
        print(str(e))
        log_file.close()
        return 1

    llm = build_llm()
    domain_reasoner = build_domain_reasoner(llm)
    software_architect = build_software_architect(llm)
    backend_builder = build_backend_builder(llm)
    devops_agent = build_devops_agent(llm)

    # -----------------------------------------------------------------------
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

                raise RuntimeError(f"Unexpected decision: {decision}")

            except Exception as e:
                state.fail(step_name, e)

                decision = decision_engine.decide(
                    step=step_name,
                    success=False,
                    retries=state.get_retries(step_name),
                    error=e,
                )

                if decision == Decision.RETRY:
                    inputs = dict(inputs or {})
                    inputs["_retry_context"] = {
                        "step": step_name,
                        "attempt": state.get_retries(step_name),
                        "last_error": str(e),
                    }
                    continue

                raise

    # =======================
    # PIPELINE LOOP
    # =======================
    while True:
        try:
            # -----------------------
            # DOMAIN
            # -----------------------
            domain_task = build_domain_model_task(state.idea)
            raw_domain = run_step("domain_model", domain_reasoner, domain_task, {})
            domain_output = normalize_llm_output(raw_domain)
            state.domain_model = domain_output

            open_q = domain_output.get("open_questions", [])
            if open_q:
                additional_info = ask_user_questions(open_q)
                state.idea += "\n\nAdditional information provided:\n" + additional_info
                continue

            validate_domain_alignment(state.idea, domain_output)

            # -----------------------
            # ARCHITECTURE
            # -----------------------
            arch_task = build_architecture_task(domain_output)
            raw_arch = run_step("architecture", software_architect, arch_task, {})
            architecture_output = normalize_llm_output(raw_arch)
            state.architecture = architecture_output

            open_q = architecture_output.get("open_questions", [])
            if open_q:
                additional_info = ask_user_questions(open_q)
                state.idea += "\n\nAdditional information provided:\n" + additional_info
                continue

            # -----------------------
            # BACKEND (PROFESSIONAL FIX)
            # -----------------------
            backend_task = build_backend_generation_task(architecture_output)
            raw_backend = run_step("backend", backend_builder, backend_task, {})

            try:
                backend_output = normalize_backend_output(raw_backend)
            except ValueError as e:
                print("\n⚠️ Backend output invalid. Retrying with stricter constraints...\n")

                backend_task = build_backend_generation_task({
                    **architecture_output,
                    "_generation_constraints": {
                        "require_artifacts": True,
                        "output_format": "json",
                        "strict": True,
                    },
                })

                raw_backend = run_step("backend", backend_builder, backend_task, {})
                backend_output = normalize_backend_output(raw_backend)

            state.backend = backend_output

            # -----------------------
            # WRITE ARTIFACTS
            # -----------------------
            artifacts = backend_output.get("artifacts", [])
            if artifacts:
                backend_dir = out_dir / "generated"
                written = write_artifacts(artifacts, backend_dir)
                state.set_context(
                    "written_artifacts",
                    [str(p.relative_to(out_dir)) for p in written],
                )

            # -----------------------
            # INFRA
            # -----------------------
            devops_task = build_devops_task(devops_agent)
            raw_infra = run_step("infra", devops_agent, devops_task, backend_output)
            infra_output = normalize_llm_output(raw_infra)
            state.infrastructure = infra_output

            open_q = infra_output.get("open_questions", [])
            if open_q:
                additional_info = ask_user_questions(open_q)
                state.idea += "\n\nAdditional information provided:\n" + additional_info
                continue

            break  # ✅ pipeline completed

        except Exception as e:
            print("\n❌ Pipeline finalizado con errores técnicos")
            print(str(e))
            state.status = "ERROR"
            state.finish()
            generate_report(state)
            log_file.close()
            return 1

    state.status = "OK"
    state.finish()
    generate_report(state)
    log_file.close()

    print(f"\n✅ Pipeline completado. Outputs en: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())