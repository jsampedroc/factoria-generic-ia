from pathlib import Path
from datetime import datetime
import sys
import json
import traceback
import re

from ai.pipeline.llm_output import normalize_llm_output
from ai.reporting.report_generator import generate_report
from ai.artifacts.writer import write_artifacts
from ai.logging.tee_stdout import tee_to_file

from ai.agents import (
    build_domain_reasoner,
    build_software_architect,
    build_backend_builder,
    build_sre_agent,
    build_qa_agent # <--- Nuevo Agente
)

from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_single_file_task
from ai.tasks.infra_task import build_infra_task
from ai.tasks.qa_task import build_qa_review_task # <--- Nueva Tarea

from ai.pipeline.state import PipelineState
from ai.llm.llm_config import build_llm

def slugify(text: str) -> str:
    """Convierte la idea en un nombre de archivo seguro para la caché de specs."""
    text = text.lower()
    text = re.sub(r'[áéíóúñ]', 'a', text)
    return re.sub(r'[\W_]+', '_', text).strip('_')[:50]

def main() -> int:
    # -----------------------
    # 1. ENTRADA Y PREPARACIÓN
    # -----------------------
    input_value = " ".join(sys.argv[1:]).strip()
    if not input_value:
        print("❌ Error: Proporciona una idea de aplicación.")
        return 1

    timestamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    out_dir = Path("outputs") / timestamp
    spec_dir = Path("specs")
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    tee = tee_to_file(out_dir / f"{timestamp}.log")
    state = PipelineState(input_value, out_dir)
    llm = build_llm()

    spec_file = spec_dir / f"{slugify(input_value)}.json"

    try:
        # -----------------------
        # 2. FASE 1: DOMINIO (Persistencia)
        # -----------------------
        if spec_file.exists():
            print(f"\n♻️  Cargando diseño de negocio existente: {spec_file}")
            with open(spec_file, 'r', encoding='utf-8') as f:
                state.domain_model = json.load(f)
        else:
            print("\n" + "="*50)
            print("🔹 FASE 1: MODELADO DE DOMINIO")
            print("="*50)
            domain_agent = build_domain_reasoner(llm)
            res_domain = domain_agent.execute_task(build_domain_model_task(domain_agent, idea=input_value))
            state.domain_model = normalize_llm_output(res_domain.raw if hasattr(res_domain, 'raw') else str(res_domain))
            
            if state.domain_model and "core_entities" in state.domain_model:
                with open(spec_file, 'w', encoding='utf-8') as f:
                    json.dump(state.domain_model, f, indent=2, ensure_ascii=False)
                print(f"💾 Especificación guardada: {spec_file}")

        # -----------------------
        # 3. FASE 2: ARQUITECTURA E INVENTARIO
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 2: DEFINICIÓN DE ARQUITECTURA E INVENTARIO")
        print("="*50)
        architect = build_software_architect(llm)
        res_arch = architect.execute_task(build_architecture_task(architect, state.domain_model))
        state.architecture = normalize_llm_output(res_arch.raw if hasattr(res_arch, 'raw') else str(res_arch))

        inventory = state.architecture.get("file_inventory", [])
        if not isinstance(inventory, list): inventory = []

        # -----------------------
        # 4. FASE 3: GENERACIÓN + QA LOOP (Iterativo)
        # -----------------------
        print("\n" + "="*50)
        print(f"🔹 FASE 3: GENERACIÓN Y CONTROL DE CALIDAD ({len(inventory)} archivos)")
        print("="*50)
        
        backend_builder = build_backend_builder(llm)
        qa_agent = build_qa_agent(llm)
        all_artifacts = []
        backend_dir = out_dir / "generated" / "backend"

        for idx, file_path in enumerate(inventory, 1):
            clean_path = str(file_path).strip()
            print(f"🚀 [{idx}/{len(inventory)}] Procesando: {clean_path}")
            
            # --- Sub-fase A: Generación ---
            task = build_single_file_task(backend_builder, clean_path, state.domain_model, state.architecture)
            res_file = backend_builder.execute_task(task)
            file_output = normalize_llm_output(res_file.raw if hasattr(res_file, 'raw') else str(res_file))

            if "content" in file_output:
                # --- Sub-fase B: Revisión de QA ---
                print(f"   🔍 QA analizando código...")
                qa_task = build_qa_review_task(qa_agent, clean_path, file_output["content"])
                res_qa = qa_agent.execute_task(qa_task)
                qa_report = normalize_llm_output(res_qa.raw if hasattr(res_qa, 'raw') else str(res_qa))

                # --- Sub-fase C: Corrección si el QA falla ---
                if qa_report.get("is_valid") is False:
                    print(f"   ⚠️ QA detectó errores: {qa_report.get('feedback')[:100]}...")
                    print(f"   🛠️ Backend Builder corrigiendo archivo...")
                    # Podríamos pasar el feedback al prompt aquí para mejorar la corrección
                    res_file = backend_builder.execute_task(task) 
                    file_output = normalize_llm_output(res_file.raw if hasattr(res_file, 'raw') else str(res_file))

                # Escritura definitiva
                write_artifacts([file_output], backend_dir)
                all_artifacts.append(file_output)
            else:
                print(f"   ❌ Error de formato persistente en {clean_path}")

        state.backend = {"artifacts": all_artifacts}

        # -----------------------
        # 5. FASE 4: INFRAESTRUCTURA (SRE)
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 4: INFRAESTRUCTURA Y DESPLIEGUE")
        print("="*50)
        sre_agent = build_sre_agent(llm)
        infra_task = build_infra_task(sre_agent, state.domain_model, state.architecture)
        res_infra = sre_agent.execute_task(infra_task)
        infra_output = normalize_llm_output(res_infra.raw if hasattr(res_infra, 'raw') else str(res_infra))
        
        if "artifacts" in infra_output:
            infra_dir = out_dir / "generated" / "infra"
            write_artifacts(infra_output["artifacts"], infra_dir)
            print(f"🐳 Entorno Docker y K8s generado en: {infra_dir}")

        # -----------------------
        # 6. CIERRE
        # -----------------------
        state.status = "COMPLETED"
        generate_report(state)
        print("\n✅ FACTORÍA FINALIZADA CON ÉXITO")
        return 0

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        traceback.print_exc()
        state.status = "FAILED"
        state.errors.append(str(e))
        generate_report(state)
        return 1
    finally:
        if 'tee' in locals(): tee.close()

if __name__ == "__main__":
    sys.exit(main())