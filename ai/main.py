from pathlib import Path
from datetime import datetime
import sys
import json
import traceback
import re
import time # Para controlar el ritmo de la API

from ai.pipeline.llm_output import normalize_llm_output
from ai.reporting.report_generator import generate_report
from ai.artifacts.writer import write_artifacts
from ai.logging.tee_stdout import tee_to_file

from ai.agents import (
    build_domain_reasoner,
    build_software_architect,
    build_backend_builder,
    build_sre_agent,
    build_qa_agent
)

from ai.tasks.domain_model_task import build_domain_model_task
from ai.tasks.architecture_task import build_architecture_task
from ai.tasks.backend_generation_task import build_single_file_task
from ai.tasks.infra_task import build_infra_task
from ai.tasks.qa_task import build_qa_review_task

from ai.pipeline.state import PipelineState
from ai.llm.llm_config import build_llm
from ai.tasks.repair_task import build_repair_task
from ai.utils.compiler import run_maven_compile

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
    
    #====================================================================================================================================================================
    # REANUDACIÓN: Ajusta out_dir según necesites
    #====================================================================================================================================================================
    # Para nueva ejecución:
    # out_dir = (Path("outputs") / timestamp).resolve()
       
    # Para reanudar la ejecución fallida:
    out_dir = (Path("outputs") / "run_20260209_193933").resolve()
    #=====================================================================================================================================================================
    
    spec_dir = Path("specs").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    tee = tee_to_file(out_dir / f"execution.log")
    state = PipelineState(input_value, out_dir)
    llm = build_llm()

    spec_file = spec_dir / f"{slugify(input_value)}.json"

    try:
        # -----------------------
        # 2. FASE 1: DOMINIO (Persistente)
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
        # 4. FASE 3: GENERACIÓN + QA LOOP
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
            target_file = backend_dir / clean_path
            
            if target_file.exists() and target_file.stat().st_size > 0:
                print(f"⏩ [{idx}/{len(inventory)}] Saltando (ya existe): {clean_path}")
                state.written_artifacts.append(str(target_file.relative_to(out_dir)))
                continue

            print(f"🚀 [{idx}/{len(inventory)}] Procesando: {clean_path}")
            time.sleep(1)

            try:
                task = build_single_file_task(backend_builder, clean_path, state.domain_model, state.architecture)
                res_file = backend_builder.execute_task(task)
                file_output = normalize_llm_output(res_file.raw if hasattr(res_file, 'raw') else str(res_file))

                if "content" in file_output:
                    print(f"   🔍 QA analizando código...")
                    qa_task = build_qa_review_task(qa_agent, clean_path, file_output["content"])
                    res_qa = qa_agent.execute_task(qa_task)
                    qa_report = normalize_llm_output(res_qa.raw if hasattr(res_qa, 'raw') else str(res_qa))

                    if qa_report.get("is_valid") is False:
                        print(f"   ⚠️ QA detectó errores. Intentando corrección rápida...")
                        state.qa_stats["fixed"] += 1
                        res_file = backend_builder.execute_task(task) 
                        file_output = normalize_llm_output(res_file.raw if hasattr(res_file, 'raw') else str(res_file))
                    else:
                        state.qa_stats["passed"] += 1

                    if "content" in file_output:
                        written_paths = write_artifacts([file_output], backend_dir)
                        for p in written_paths:
                            state.written_artifacts.append(str(p.relative_to(out_dir)))
                    all_artifacts.append(file_output)
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    print("\n🛑 ERROR: Límite de API alcanzado.")
                    sys.exit(1)
                print(f"   ❌ Error en este archivo: {e}")

        state.backend = {"artifacts": all_artifacts}

        # -----------------------
        # 5. FASE 4: INFRAESTRUCTURA (Ajustada para Maven)
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 4: INFRAESTRUCTURA Y DESPLIEGUE")
        print("="*50)
        sre_agent = build_sre_agent(llm)
        infra_task = build_infra_task(sre_agent, state.domain_model, state.architecture)
        res_infra = sre_agent.execute_task(infra_task)
        infra_output = normalize_llm_output(res_infra.raw if hasattr(res_infra, 'raw') else str(res_infra))
        
        if "artifacts" in infra_output:
            # CAMBIO CLAVE: Usamos backend_dir en lugar de crear una carpeta 'infra' separada
            # Esto permite que el pom.xml quede al mismo nivel que la carpeta 'src'
            infra_dir = backend_dir 
            
            written_infra = write_artifacts(infra_output["artifacts"], infra_dir)
            for p in written_infra:
                state.written_artifacts.append(str(p.relative_to(out_dir)))
            print(f"🐳 Entorno Docker y Maven generado en la raíz del backend.")
            



       # -----------------------
        # 6. FASE 5: AUTO-CURACIÓN (Compilación Maven)
        # -----------------------
        print("\n" + "="*50)
        print("🔹 FASE 5: AUTO-CURACIÓN (Compilación Maven)")
        print("="*50)
        
        for heal_attempt in range(5): 
            errors = run_maven_compile(backend_dir)
            
            if not errors or not isinstance(errors, list):
                print("✅ ¡El proyecto compila correctamente!")
                break
            
            print(f"⚠️ Intento {heal_attempt+1}: Quedan {len(errors)} errores. Reparando...")
            
            # Procesamos de 10 en 10 para avanzar
            for err in errors[:10]:
                try:
                    rel_path = err['file']
                    file_to_fix = backend_dir / rel_path
                    
                    if file_to_fix.exists():
                        # --- ESCENARIO A: El archivo EXISTE pero está mal ---
                        print(f"   🔧 Reparando archivo: {rel_path}")
                        with open(file_to_fix, 'r', encoding='utf-8') as f:
                            broken_code = f.read()
                        
                        # MEJORA PARA TRUNCAMIENTO:
                        msg = err['message']
                        if "reached end of file" in msg.lower():
                            msg = (
                                "CRITICAL: The file is truncated and ends abruptly. "
                                "Please rewrite the FULL class, ensuring all methods, builders, "
                                "and braces are properly closed. Keep it concise to avoid token limits."
                            )
                        
                        task = build_repair_task(
                            backend_builder, 
                            rel_path, 
                            broken_code, 
                            msg,
                            state.domain_model
                        )
                    else:
                        # --- ESCENARIO B: El archivo NO EXISTE (Símbolos faltantes) ---
                        print(f"   🆕 Generando componente faltante: {rel_path}")
                        file_to_fix.parent.mkdir(parents=True, exist_ok=True)
                        
                        task = build_single_file_task(
                            backend_builder, 
                            rel_path, 
                            state.domain_model, 
                            state.architecture
                        )
                    
                    # Ejecución y escritura
                    res = backend_builder.execute_task(task)
                    fixed_output = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))
                    
                    if "content" in fixed_output:
                        fixed_output["path"] = rel_path 
                        write_artifacts([fixed_output], backend_dir)
                        print(f"      ✅ Procesado: {rel_path}")
                    
                except Exception as e_repair:
                    print(f"   ❌ Error procesando {err.get('file')}: {e_repair}")
            
            time.sleep(1) # Respiro para la API



        # --- OPCIONAL: Guardar la arquitectura final en el JSON para el futuro ---
        with open(spec_file, 'w', encoding='utf-8') as f:
            full_spec = {
                "domain": state.domain_model,
                "architecture": state.architecture
            }
            json.dump(full_spec, f, indent=2, ensure_ascii=False)




        # -----------------------
        # 7. CIERRE
        # -----------------------
        state.status = "COMPLETED"
        generate_report(state)
        print(f"\n✅ PROYECTO FINALIZADO CON ÉXITO")
        print(f"📂 Resultados en: {out_dir}")
        return 0

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        traceback.print_exc()
        state.status = "FAILED"
        state.errors.append(str(e))
        generate_report(state)
        return 1

    finally:
        if 'tee' in locals():
            tee.close()

if __name__ == "__main__":
    sys.exit(main())