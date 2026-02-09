from pathlib import Path
from datetime import datetime
import sys
import traceback
import json

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
    # 1. ENTRADA DE LA IDEA
    # -----------------------
    idea = " ".join(sys.argv[1:]).strip()
    if not idea:
        print("❌ Error: No se ha proporcionado una idea. Uso: python main.py 'mi idea de app'")
        return 1

    # -----------------------
    # 2. CONFIGURACIÓN DE SALIDA Y LOGS
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
        # 3. FASE DE DOMINIO (Domain Reasoner)
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 1: MODELADO DE DOMINIO")
        print("="*50)
       
        domain_agent = build_domain_reasoner(llm)
        domain_task = build_domain_model_task(domain_agent, idea=idea)
        
        # CrewAI devuelve un objeto TaskOutput, extraemos .raw
        result_domain = domain_agent.execute_task(domain_task)
        raw_domain = result_domain.raw if hasattr(result_domain, 'raw') else str(result_domain)
        
        domain_output = normalize_llm_output(raw_domain)
        state.domain_model = domain_output

        if domain_output.get("status") == "NEEDS_INPUT":
            print("\n⚠️ El agente requiere más información para continuar.")
            state.status = "NEEDS_INPUT"
            state.open_questions = domain_output.get("open_questions", [])
            generate_report(state)
            return 0

        if not state.domain_model or "core_entities" not in state.domain_model:
            raise ValueError("El modelo de dominio generado es inválido o está vacío.")

        # -----------------------
        # 4. FASE DE ARQUITECTURA (Software Architect)
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 2: DEFINICIÓN DE ARQUITECTURA")
        print("="*50)
        
        architect = build_software_architect(llm)
        architecture_task = build_architecture_task(
            architect, 
            domain_model=state.domain_model
        )
        
        result_arch = architect.execute_task(architecture_task)
        raw_arch = result_arch.raw if hasattr(result_arch, 'raw') else str(result_arch)
        
        architecture_output = normalize_llm_output(raw_arch)
        state.architecture = architecture_output

        if not state.architecture:
            raise ValueError("La definición de arquitectura no pudo ser generada.")

        # -----------------------
        # 5. FASE DE BACKEND (Backend Builder)
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 3: GENERACIÓN DE BACKEND Y ARTEFACTOS")
        print("="*50)
        
        backend_builder = build_backend_builder(llm)
        backend_task = build_backend_generation_task(
            backend_builder,
            domain_model=state.domain_model,
            architecture=state.architecture
        )
        
        result_backend = backend_builder.execute_task(backend_task)
        raw_backend = result_backend.raw if hasattr(result_backend, 'raw') else str(result_backend)
        
        backend_output = normalize_llm_output(raw_backend)
        state.backend = backend_output

        # -----------------------
        # 6. ESCRITURA DE ARTEFACTOS
        # -----------------------
        artifacts = backend_output.get("artifacts", [])
        if isinstance(artifacts, list) and artifacts:
            print(f"\n💾 Escribiendo {len(artifacts)} artefactos en disco...")
            backend_dir = out_dir / "generated" / "backend"

            written = write_artifacts(artifacts, backend_dir)

            out_dir_resolved = out_dir.resolve()
            state.written_artifacts = []

            for p in written:
                try:
                    p_resolved = p.resolve()
                    if p_resolved.is_relative_to(out_dir_resolved):
                        state.written_artifacts.append(
                            str(p_resolved.relative_to(out_dir_resolved))
                        )
                    else:
                        state.written_artifacts.append(str(p_resolved))
                except Exception:
                    state.written_artifacts.append(str(p))
        else:
            print("\n⚠️ No se generaron artefactos de código en esta ejecución.")

        # -----------------------
        # 7. REPORTE FINAL
        # -----------------------
        state.status = "COMPLETED"
        generate_report(state)

        print("\n" + "="*50)
        print("✅ Pipeline finalizado con éxito")
        print(f"📂 Resultados en: {out_dir}")
        print("="*50)
        return 0

    except Exception as e:
        print("\n" + "!"*50)
        print("❌ ERROR CRÍTICO EN EL PIPELINE")
        print(f"Mensaje: {str(e)}")
        print("!"*50)
        
        traceback.print_exc()
        
        try:
            state.status = "FAILED"
            state.errors.append(str(e))
            generate_report(state)
        except Exception as report_error:
            print(f"⚠️ Error adicional al intentar generar el reporte de error: {report_error}")
        return 1

    finally:
        if 'tee' in locals():
            tee.close()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Ejecución cancelada por el usuario.")
        sys.exit(130)