from pathlib import Path
from datetime import datetime
import sys
import json
import traceback
import re
import time 

# --- IMPORTACIONES DE TU PROYECTO ---
from factoria.core.template_builder import TemplateBuilder
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


import subprocess

# --- COMPONENTES DE LA FACTORÍA MIXTA ---
from factoria.core.blueprint_engine import BlueprintManager
from jinja2 import Environment, FileSystemLoader

# Inicialización Global
blueprint_mgr = BlueprintManager("factory_config.yaml")
# Usamos un nombre claro para evitar colisiones: jinja_env
jinja_env = Environment(loader=FileSystemLoader("templates"))



def polish_code_locally(file_path: str):
    """Aplica formato profesional sin usar la IA."""
    path = Path(file_path)
    try:
        if path.suffix == ".py":
            # Black es el estándar de oro en la industria Python
            subprocess.run(["black", "-q", str(path)], check=False)
        elif path.suffix == ".java":
            # Aquí podrías usar un formateador de Java si lo tienes instalado
            pass 
    except Exception as e:
        print(f"   ⚠️ No se pudo formatear {path.name}: {e}")


# limpia lo que se envía a DeepSeek.
def get_slim_context(full_domain: dict, target_file: str) -> dict:
    """
    Extrae solo las entidades relevantes para el archivo actual.
    Si el archivo es 'PedidoService', busca la entidad 'Pedido' y relacionadas.
    """
    file_name_lower = Path(target_file).stem.lower()
    slim_domain = {
        "project_name": full_domain.get("project_name"),
        "core_entities": []
    }
    
    # Buscamos la entidad principal que coincida con el nombre del archivo
    for entity in full_domain.get("core_entities", []):
        entity_name = entity.get("name", "").lower()
        # Si el nombre de la entidad está contenido en el nombre del archivo (ej: 'User' en 'UserService')
        if entity_name in file_name_lower or file_name_lower in entity_name:
            slim_domain["core_entities"].append(entity)
            
    # Si no encontramos nada específico, enviamos solo lo básico para no romper la IA
    if not slim_domain["core_entities"]:
        slim_domain["core_entities"] = full_domain.get("core_entities", [])[:2]
        
    return slim_domain

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[áéíóúñ]', 'a', text)
    return re.sub(r'[\W_]+', '_', text).strip('_')[:50]

def get_java_package(clean_path: str) -> str:
    """Extrae el package name de una ruta Java estándar."""
    path_parts = list(Path(clean_path).parts)
    if "java" in path_parts:
        idx = path_parts.index("java")
        return ".".join(path_parts[idx+1:-1])
    return ""

def main() -> int:
    input_value = " ".join(sys.argv[1:]).strip()
    if not input_value:
        print("❌ Error: Proporciona una idea de aplicación.")
        return 1

    # Directorios de salida
    out_dir = (Path("outputs") / "run_20260209_193933").resolve()
    spec_dir = Path("specs").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    tee = tee_to_file(out_dir / f"execution.log")
    state = PipelineState(input_value, out_dir)
    llm = build_llm()

    # Si necesitas TemplateBuilder para otras funciones, úsalo con otro nombre
    t_builder = TemplateBuilder() 
    spec_file = spec_dir / f"{slugify(input_value)}.json"

    try:
        # FASE 1: DOMINIO
        if spec_file.exists():
            print(f"\n♻️ Cargando diseño de negocio existente: {spec_file}")
            with open(spec_file, 'r', encoding='utf-8') as f:
                state.domain_model = json.load(f)
        else:
            print("\n" + "="*50 + "\n🔹 FASE 1: MODELADO DE DOMINIO\n" + "="*50)
            domain_agent = build_domain_reasoner(llm)
            res_domain = domain_agent.execute_task(build_domain_model_task(domain_agent, idea=input_value))
            state.domain_model = normalize_llm_output(res_domain.raw if hasattr(res_domain, 'raw') else str(res_domain))
            if state.domain_model and "core_entities" in state.domain_model:
                with open(spec_file, 'w', encoding='utf-8') as f:
                    json.dump(state.domain_model, f, indent=2, ensure_ascii=False)

        # FASE 2: ARQUITECTURA
        print("\n" + "="*50 + "\n🔹 FASE 2: DEFINICIÓN DE ARQUITECTURA\n" + "="*50)
        architect = build_software_architect(llm)
        res_arch = architect.execute_task(build_architecture_task(architect, state.domain_model))
        state.architecture = normalize_llm_output(res_arch.raw if hasattr(res_arch, 'raw') else str(res_arch))
        inventory = state.architecture.get("file_inventory", [])

        # FASE 3: GENERACIÓN MIXTA
        print("\n" + "="*50 + f"\n🔹 FASE 3: GENERACIÓN MIXTA ({len(inventory)} archivos)\n" + "="*50)
        backend_builder = build_backend_builder(llm)
        qa_agent = build_qa_agent(llm)
        all_artifacts = []
        backend_dir = out_dir / "generated" / "backend"

        for idx, file_path in enumerate(inventory, 1):
            clean_path = str(file_path).strip()
            target_file = backend_dir / clean_path
            
            if target_file.exists() and target_file.stat().st_size > 0:
                print(f"⏩ [{idx}/{len(inventory)}] Saltando: {clean_path}")
                state.written_artifacts.append(str(target_file.relative_to(out_dir)))
                continue

            print(f"🚀 [{idx}/{len(inventory)}] Procesando: {clean_path}")
            time.sleep(1)

            try:
                slim_context = get_slim_context(state.domain_model, clean_path)
                task = build_single_file_task(backend_builder, clean_path, slim_context, state.architecture)
                res_file = backend_builder.execute_task(task)
                file_output = normalize_llm_output(res_file.raw if hasattr(res_file, 'raw') else str(res_file))

                if "content" in file_output:
                    # --- APLICACIÓN DE PLANTILLA PROFESIONAL ---
                    ext = Path(clean_path).suffix
                    template_path = blueprint_mgr.resolve_template(clean_path)
                    
                    if template_path:
                        print(f"   🎨 Aplicando Blueprint: {template_path}")
                        template_data = {
                            "class_name": Path(clean_path).stem,
                            "description": f"Componente industrial para {clean_path}",
                            "extra_imports": file_output.get("imports", []),
                            "business_logic": file_output["content"],
                            "package_name": get_java_package(clean_path) if ext == ".java" else ""
                        }
                        try:
                            template = jinja_env.get_template(template_path)
                            file_output["content"] = template.render(**template_data)
                        except Exception as te:
                            print(f"   ⚠️ Error renderizando template: {te}. Usando raw output.")

                    # --- QA LOOP ---
                    print(f"   🔍 QA analizando código...")
                    qa_task = build_qa_review_task(qa_agent, clean_path, file_output["content"])
                    res_qa = qa_agent.execute_task(qa_task)
                    qa_report = normalize_llm_output(res_qa.raw if hasattr(res_qa, 'raw') else str(res_qa))

                    if qa_report.get("is_valid") is False:
                        print(f"   ⚠️ QA detectó errores. Reintentando...")
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
                print(f"   ❌ Error en archivo {clean_path}: {e}")

        state.backend = {"artifacts": all_artifacts}

        # FASE 4: INFRAESTRUCTURA
        print("\n" + "="*50 + "\n🔹 FASE 4: INFRAESTRUCTURA\n" + "="*50)
        sre_agent = build_sre_agent(llm)
        infra_task = build_infra_task(sre_agent, state.domain_model, state.architecture)
        res_infra = sre_agent.execute_task(infra_task)
        infra_output = normalize_llm_output(res_infra.raw if hasattr(res_infra, 'raw') else str(res_infra))
        
        if "artifacts" in infra_output:
            written_infra = write_artifacts(infra_output["artifacts"], backend_dir)
            for p in written_infra:
                state.written_artifacts.append(str(p.relative_to(out_dir)))

        # FASE 5: AUTO-CURACIÓN
        print("\n" + "="*50 + "\n🔹 FASE 5: AUTO-CURACIÓN (MAVEN/HYBRID)\n" + "="*50)
        for heal_attempt in range(5): 
            errors = run_maven_compile(backend_dir)
            if not errors:
                print(f"✅ ¡Compilación correcta!")
                break
            
            for err in errors[:10]:
                rel_path = err['file']
                file_to_fix = backend_dir / rel_path
                print(f"   🔧 Reparando: {rel_path}")
                
                if file_to_fix.exists():
                    with open(file_to_fix, 'r', encoding='utf-8') as f:
                        broken_code = f.read()
                    task = build_repair_task(backend_builder, rel_path, broken_code, err['message'], state.domain_model)
                else:
                    slim_context = get_slim_context(state.domain_model, clean_path)
                    task = build_single_file_task(backend_builder, clean_path, slim_context, state.architecture)
                
                res = backend_builder.execute_task(task)
                fixed_output = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))
                
                if "content" in fixed_output:
                    template_path = blueprint_mgr.resolve_template(rel_path)
                    if template_path:
                        print(f"      🎨 Re-encuadrando reparación en {template_path}...")
                        template_data = {
                            "class_name": Path(rel_path).stem,
                            "description": "Componente auto-curado",
                            "extra_imports": fixed_output.get("imports", []),
                            "business_logic": fixed_output["content"],
                            "package_name": get_java_package(rel_path) if rel_path.endswith(".java") else ""
                        }
                        try:
                            fixed_output["content"] = jinja_env.get_template(template_path).render(**template_data)
                        except Exception as te:
                            print(f"      ❌ Error en template: {te}")
                    
                    fixed_output["path"] = rel_path 
                    write_artifacts([fixed_output], backend_dir)

        state.status = "COMPLETED"
        generate_report(state)
        print(f"\n✅ PROYECTO FINALIZADO EN: {out_dir}")
        return 0

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        traceback.print_exc()
        state.status = "FAILED"
        generate_report(state)
        return 1
    finally:
        if 'tee' in locals(): tee.close()

if __name__ == "__main__":
    sys.exit(main())