from pathlib import Path
from datetime import datetime
import sys
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
from ai.tasks.backend_generation_task import build_single_file_task # Nueva tarea

from ai.pipeline.state import PipelineState
from ai.llm.llm_config import build_llm

def main() -> int:
    idea = " ".join(sys.argv[1:]).strip()
    if not idea: return 1

    timestamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    out_dir = Path("outputs") / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    tee = tee_to_file(out_dir / f"{timestamp}.log")

    state = PipelineState(idea, out_dir)
    llm = build_llm()

    try:
        # FASE 1: DOMINIO
        print("\n🔹 FASE 1: MODELADO DE DOMINIO")
        domain_agent = build_domain_reasoner(llm)
        res = domain_agent.execute_task(build_domain_model_task(domain_agent, idea))
        state.domain_model = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))

        # FASE 2: ARQUITECTURA E INVENTARIO
        print("\n🔹 FASE 2: ARQUITECTURA E INVENTARIO")
        architect = build_software_architect(llm)
        res = architect.execute_task(build_architecture_task(architect, state.domain_model))
        state.architecture = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))

        inventory = state.architecture.get("file_inventory", [])
        if not inventory:
            # Fallback: Si el arquitecto no dio inventario, generamos los básicos
            inventory = ["pom.xml", "Dockerfile"]

        # FASE 3: GENERACIÓN ITERATIVA (Archivo por Archivo)
        print(f"\n🔹 FASE 3: GENERACIÓN ITERATIVA ({len(inventory)} archivos)")
        backend_builder = build_backend_builder(llm)
        all_artifacts = []

        for i, file_path in enumerate(inventory, 1):
            print(f"   [{i}/{len(inventory)}] Generando: {file_path}...", end="\r")
            
            file_task = build_single_file_task(
                backend_builder, 
                file_path, 
                state.domain_model, 
                state.architecture
            )
            
            res = backend_builder.execute_task(file_task)
            file_output = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))
            
            if "content" in file_output:
                all_artifacts.append(file_output)
                # Escribimos el archivo inmediatamente para no perder progreso
                write_artifacts([file_output], out_dir / "generated" / "backend")

        state.backend = {"artifacts": all_artifacts}
        state.status = "COMPLETED"
        generate_report(state)
        print(f"\n\n✅ Factoría completada. {len(all_artifacts)} archivos generados.")
        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    finally:
        tee.close()

if __name__ == "__main__":
    sys.exit(main())