from pathlib import Path
from datetime import datetime
import sys
import traceback

from ai.pipeline.llm_output import normalize_llm_output
from ai.reporting.report_generator import generate_report
from ai.artifacts.writer import write_artifacts
from ai.logging.tee_stdout import tee_to_file

from ai.agents import (
    build_domain_reasoner,
    build_software_architect,
    build_backend_builder,
)

from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_backend_generation_task

from ai.pipeline.state import PipelineState

from ai.llm.llm_config import build_llm


def main() -> int:
    # -----------------------
    # IDEA INPUT
    # -----------------------
    idea = " ".join(sys.argv[1:]).strip()
    if not idea:
        print("❌ No idea provided. Use CLI argument.")
        return 1

    # -----------------------
    # OUTPUTS & LOGGING
    # -----------------------
    timestamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    out_dir = Path("outputs") / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = out_dir / f"{timestamp}.log"
    tee = tee_to_file(log_path)

    state = PipelineState(idea, out_dir)
    
    llm = build_llm()

    try:
        # -----------------------
        # DOMAIN
        # -----------------------
        print("\n🔹 DOMAIN MODEL")
        domain_agent = build_domain_reasoner(llm)
        domain_task = build_domain_model_task(domain_agent)
        raw_domain = domain_agent.execute_task(domain_task)
        domain_output = normalize_llm_output(raw_domain)
        state.domain_model = domain_output

        if domain_output.get("status") == "NEEDS_INPUT":
            state.status = "NEEDS_INPUT"
            state.open_questions = domain_output.get("open_questions", [])
            generate_report(state)
            return 0

        # -----------------------
        # ARCHITECTURE
        # -----------------------
        print("\n🔹 ARCHITECTURE")
        architect = build_software_architect(llm)
        architecture_task = build_architecture_task(architect)
        raw_arch = architect.execute_task(architecture_task)
        architecture_output = normalize_llm_output(raw_arch)
        state.architecture = architecture_output

        if architecture_output.get("status") == "NEEDS_INPUT":
            state.status = "NEEDS_INPUT"
            state.open_questions = architecture_output.get("open_questions", [])
            generate_report(state)
            return 0

        # -----------------------
        # BACKEND
        # -----------------------
        print("\n🔹 BACKEND")
        backend_builder = build_backend_builder(llm)
        backend_task = build_backend_generation_task(backend_builder)
        raw_backend = backend_builder.execute_task(backend_task)
        backend_output = normalize_llm_output(raw_backend)
        state.backend = backend_output

        # -----------------------
        # WRITE ARTIFACTS (SAFE)
        # -----------------------
        artifacts = backend_output.get("artifacts", [])
        if isinstance(artifacts, list) and artifacts:
            backend_dir = out_dir / "generated" / "backend"
            written = write_artifacts(artifacts, backend_dir)
            state.written_artifacts = [str(p.relative_to(out_dir)) for p in written]

        # -----------------------
        # FINAL REPORT
        # -----------------------
        generate_report(state)

        print("\n✅ Pipeline completed successfully")
        return 0

    except Exception as e:
        print("\n❌ Pipeline finalizado con errores")
        print(str(e))
        traceback.print_exc()
        try:
            state.errors.append(str(e))
            generate_report(state)
        except Exception as report_error:
            print(f"⚠️ Error generando report.md: {report_error}")
        return 1

    finally:
        tee.close()


if __name__ == "__main__":
    raise SystemExit(main())