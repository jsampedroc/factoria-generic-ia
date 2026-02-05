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
from ai.tasks.backend_design_task import build_backend_design_task
from ai.tasks.backend_code_task import build_backend_code_task

from ai.validators.backend_design_gate import validate_backend_design_gate
from ai.validators.backend_design_soft_validator import soft_validate_backend_design

from ai.artifacts.writer import write_artifacts


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
    if isinstance(output, dict):
        return output

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

    if isinstance(output, str):
        try:
            import json
            return json.loads(output)
        except Exception:
            pass

    raise RuntimeError(f"Unable to normalize LLM output: {type(output)}")


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
    from ai.pipeline.decision_engine import DecisionEngine, Decision

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
    backend_design_task = build_backend_design_task(backend_builder)
    backend_code_task = build_backend_code_task(backend_builder)

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
        # 3) BACKEND LEVEL 1 (CONTRACT)
        # -----------------------------------------------------------
        raw_backend_output = run_step(
            "backend_contract",
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
        print("✅ Backend Level 1 (contract) OK")

        allowed_entities = [
            e for e in backend_contract.get("entities", []) if isinstance(e, str)
        ]
        allowed_modules = [
            m["name"]
            for m in backend_contract.get("modules", [])
            if isinstance(m, dict) and m.get("name")
        ]

        # -----------------------------------------------------------
        # 4) BACKEND LEVEL 2 (DESIGN)
        # -----------------------------------------------------------
        raw_design_output = run_step(
            "backend_design",
            backend_builder,
            backend_design_task,
            {
                "backend_contract": backend_contract,
                "architecture": architecture_output,
                "allowed_entities": allowed_entities,
                "allowed_modules": allowed_modules,
            },
        )

        design_output = normalize_llm_output(raw_design_output)
        backend_design = design_output.get("backend_design")
        if not backend_design:
            raise RuntimeError("Backend Level 2 missing backend_design")

        backend_design, soft_questions = soft_validate_backend_design(
            backend_contract=backend_contract,
            backend_design=backend_design,
        )

        state.set_context("backend_design", backend_design)

        decision = decision_engine.decide(
            step="backend_design",
            success=True,
            retries=0,
            open_questions=soft_questions,
            idea=state.idea,
        )

        if decision == Decision.NEEDS_INPUT:
            unresolved = decision_engine.last_unresolved_questions
            state.status = "NEEDS_INPUT"
            state.open_questions = unresolved

            print("\n🟡 ESTADO: NEEDS_INPUT (BACKEND DESIGN)\n")
            for i, q in enumerate(unresolved, start=1):
                print(f"{i}. {q}")

            state.finish()
            generate_report(state)
            log_file.close()
            return 0

        print("✅ Backend Level 2 (design) OK")

        # -----------------------------------------------------------
        # HARD ADL GATE
        # -----------------------------------------------------------
        validate_backend_design_gate(
            backend_contract=backend_contract,
            backend_design=backend_design,
        )

        print("🔒 ADL Gate passed")

        # -----------------------------------------------------------
        # 5) BACKEND LEVEL 3 (CODE – Spring Boot MVP)
        # -----------------------------------------------------------
        raw_code_output = run_step(
            "backend_code",
            backend_builder,
            backend_code_task,
            {
                "backend_contract": backend_contract,
                "backend_design": backend_design,
                "base_package": "com.factoria.app",
                "app_name": "daycare",
                "allowed_entities": allowed_entities,
                "allowed_modules": allowed_modules,
            },
        )

        code_output = normalize_llm_output(raw_code_output)
        backend_code = code_output.get("backend_code")
        if not backend_code:
            raise RuntimeError("Backend Level 3 missing backend_code")

        artifacts = backend_code.get("artifacts", [])
        if not artifacts:
            raise RuntimeError("Backend Level 3 returned no artifacts")

        backend_root = out_dir / "generated" / "backend"
        written = write_artifacts(artifacts, backend_root)

        state.set_context(
            "written_artifacts",
            [str(p.relative_to(out_dir)) for p in written],
        )

        print(f"✅ Backend written to: {backend_root}")

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