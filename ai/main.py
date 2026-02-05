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
    build_domain_reasoner,
    build_software_architect,
)

from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_backend_generation_task


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

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


def normalize_llm_output(output):
    """
    Normalize CrewAI / LLM outputs to a plain dict.
    Handles dict, JSON string, or CrewAI output objects.
    """
    if isinstance(output, dict):
        return output

    # CrewAI output objects may expose different attributes
    for attr in ("output", "result", "raw"):
        if hasattr(output, attr):
            value = getattr(output, attr)
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                try:
                    import json
                    return json.loads(value)
                except Exception:
                    pass

    # Raw JSON string
    if isinstance(output, str):
        try:
            import json
            return json.loads(output)
        except Exception:
            pass

    raise RuntimeError(f"Unable to normalize backend output: {type(output)}")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> int:
    load_dotenv()

    idea = _read_idea_from_cli()
    if not idea:
        print("❌ No idea provided")
        return 2

    out_dir = _ensure_output_dir()
    os.environ["FACTORIA_OUTPUT_DIR"] = str(out_dir)

    log_path = out_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file = tee_to_file(log_path)
    print(f"📝 Logging activado en: {log_path}")

    from ai.pipeline.state import PipelineState
    from ai.pipeline.decision_engine import DecisionEngine

    state = PipelineState(idea=idea)
    decision_engine = DecisionEngine(max_retries=1)

    # ---------------------------------------------------------------
    # Build LLM + Agents
    # ---------------------------------------------------------------
    llm = build_llm()

    domain_reasoner = build_domain_reasoner(llm)
    software_architect = build_software_architect(llm)
    backend_builder = build_backend_builder(llm)

    domain_model_task = build_domain_model_task(domain_reasoner)
    architecture_task = build_architecture_task(software_architect)
    backend_generation_task = build_backend_generation_task(backend_builder)

    # ---------------------------------------------------------------
    # Runner helper
    # ---------------------------------------------------------------
    def run_step(step_name, agent, task, inputs):
        print(f"\n🔹 Ejecutando paso: {step_name}")
        state.start(step_name)

        task.context = inputs
        result = agent.execute_task(task)

        state.success(step_name, result)
        return result

    try:
        # -----------------------------------------------------------
        # 1) DOMAIN MODEL
        # -----------------------------------------------------------
        domain_output = run_step(
            "domain_model",
            domain_reasoner,
            domain_model_task,
            {"idea": idea},
        )

        # -----------------------------------------------------------
        # 2) ARCHITECTURE
        # -----------------------------------------------------------
        architecture_output = run_step(
            "architecture",
            software_architect,
            architecture_task,
            domain_output,
        )

        # -----------------------------------------------------------
        # 3) BACKEND LEVEL 1 (CONTRACT-ONLY)
        # -----------------------------------------------------------
        raw_backend_output = run_step(
            "backend",
            backend_builder,
            backend_generation_task,
            {
                "domain_model": domain_output,
                "architecture": architecture_output,
            },
        )

        backend_output = normalize_llm_output(raw_backend_output)

        backend_contract = backend_output.get("backend_contract")
        if not backend_contract:
            raise RuntimeError("Backend Level 1 missing backend_contract")

        state.set_context("backend_contract", backend_contract)

        print("\n✅ Backend Level 1 contract generated successfully")

    except Exception as e:
        print("\n❌ Pipeline finalizado con errores")
        print(str(e))
        log_file.close()
        return 1

    state.finish()
    generate_report(state)
    log_file.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())