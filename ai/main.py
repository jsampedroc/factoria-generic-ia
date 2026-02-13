import sys
import os
from pathlib import Path
from ai.logging.tee_stdout import tee_to_file
from ai.pipeline.state import PipelineState
from ai.llm.llm_config import build_llm
from ai.reporting.report_generator import generate_report
from ai.utils.java_helpers import slugify
from ai.pipeline.state_manager import StateManager
from ai.pipeline.phase_executor import PhaseExecutor
from ai.agents import (
    build_domain_reasoner, 
    build_software_architect, 
    build_backend_builder, 
    build_qa_agent, 
    build_sre_agent
)
from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.pipeline.llm_output import normalize_llm_output
from factoria.core.template_builder import TemplateBuilder

def main() -> int:
    # ------------------------------------------------------------------
    # 0. PREPARACIÓN DE ENTRADA
    # ------------------------------------------------------------------
    input_value = " ".join(sys.argv[1:]).strip()
    if not input_value:
        print("❌ Error: Proporciona una idea de aplicación.")
        return 1

    # ------------------------------------------------------------------
    # 1. GESTIÓN DE RUTAS Y PROYECTO (Versión Industrial)
    # ------------------------------------------------------------------
    project_slug = slugify(input_value)
    run_id = "run_stable" 
    
    # Ruta: outputs/nombre_proyecto/run_stable/
    out_dir = (Path("outputs") / project_slug / run_id).resolve()
    spec_dir = Path("specs").resolve()

    out_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    # Iniciamos el LOG
    tee = tee_to_file(str(out_dir / "execution.log"))

    state = PipelineState(input_value, out_dir)
    spec_file = spec_dir / f"{project_slug}.json"
    
    print(f"🚀 Proyecto: {project_slug.upper()}")
    print(f"📂 Salida en: {out_dir}")

    # ------------------------------------------------------------------
    # 2. CONFIGURACIÓN DE NIVELES DE LLM (Smart vs Cheap)
    # ------------------------------------------------------------------
    llm_smart = build_llm(tier="smart") # Para Fase 1 y 2 (Arquitectura)
    llm_cheap = build_llm(tier="cheap") # Para Fase 3, 4 y 5 (Código e Infra)

    try:
        # ------------------------------------------------------------------
        # FASES 1 & 2: DISEÑO (Con persistencia en Specs)
        # ------------------------------------------------------------------
        if not StateManager.load_specs(spec_file, state):
            print("\n🔹 FASE 1: MODELADO DE DOMINIO (Smart LLM)")
            domain_agent = build_domain_reasoner(llm_smart)
            res_domain = domain_agent.execute_task(build_domain_model_task(domain_agent, input_value))
            state.domain_model = normalize_llm_output(res_domain.raw if hasattr(res_domain, 'raw') else str(res_domain))
            StateManager.save_specs(spec_file, state.domain_model)

            print("\n🔹 FASE 2: ARQUITECTURA (Smart LLM)")
            architect = build_software_architect(llm_smart)
            res_arch = architect.execute_task(build_architecture_task(architect, state.domain_model))
            state.architecture = normalize_llm_output(res_arch.raw if hasattr(res_arch, 'raw') else str(res_arch))
            # Guardamos el diseño completo con el inventario de archivos
            StateManager.save_specs(spec_file, state.domain_model, state.architecture)
        else:
            print(f"✅ Diseño cargado desde caché: {spec_file.name}")

        # ------------------------------------------------------------------
        # INICIALIZAR EXECUTOR (Encargado de las Fases 3, 4 y 5)
        # ------------------------------------------------------------------
        executor = PhaseExecutor(
            state=state,
            llm=llm_cheap,
            template_engine=TemplateBuilder(),
            backend_builder=build_backend_builder(llm_cheap),
            qa_agent=build_qa_agent(llm_cheap),
            sre_agent=build_sre_agent(llm_cheap)
        )

        # ------------------------------------------------------------------
        # FASE 3: GENERACIÓN DE CÓDIGO (Lógica + POJOs + Tests)
        # ------------------------------------------------------------------
        inventory = state.architecture.get("file_inventory", [])
        executor.execute_generation(inventory)

        # ------------------------------------------------------------------
        # FASE 4: INFRAESTRUCTURA (pom.xml, Dockerfile, docker-compose)
        # ------------------------------------------------------------------
        executor.execute_infrastructure()

        # ------------------------------------------------------------------
        # FASE 5: AUTO-CURACIÓN (Reparación de errores Maven)
        # ------------------------------------------------------------------
        executor.execute_healing()

        state.status = "COMPLETED"
        return 0
    
    except Exception as e:
        print(f"❌ Error Crítico: {e}")
        import traceback
        traceback.print_exc()
        state.status = "FAILED"
        return 1
    
    finally:
        # ------------------------------------------------------------------
        # CIERRE Y REPORTE
        # ------------------------------------------------------------------
        try:
            print(f"\n📊 Generando reporte final...")
            generate_report(state)
            print(f"✅ Reporte guardado en {out_dir}/report.md")
        except Exception as e_rep:
            print(f"⚠️ Error al generar reporte: {e_rep}")

        if 'tee' in locals():
            try:
                sys.stdout.flush()
                tee.close()
                # Restauramos los flujos originales para evitar errores al cerrar
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            except:
                pass

if __name__ == "__main__":
    sys.exit(main())