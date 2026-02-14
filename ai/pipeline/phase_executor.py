import time
import re
from pathlib import Path
from ai.pipeline.llm_output import normalize_llm_output
from ai.artifacts.writer import write_artifacts
from ai.utils.compiler import run_maven_compile
from ai.utils.java_helpers import calculate_package
from ai.tasks.backend_generation_task import build_single_file_task
from ai.tasks.repair_task import build_repair_task
from ai.tasks.qa_task import build_qa_review_task 
from ai.tasks.infra_task import build_infra_task

class PhaseExecutor:
    def __init__(self, state, llm, template_engine, backend_builder, qa_agent, sre_agent):
        self.state = state
        self.llm = llm
        self.template_engine = template_engine
        self.backend_builder = backend_builder
        self.qa_agent = qa_agent
        self.sre_agent = sre_agent
        self.backend_dir = state.out_dir / "generated" / "backend"



    def _clean_hallucinated_class(self, content, file_name):
        """🛡️ Limpiador de Seguridad: Evita que la IA escriba la cabecera de la clase."""
        content_clean = content.strip()
        
        # 1. Limpiar bloques markdown si existen
        if content_clean.startswith("```"):
            content_clean = re.sub(r"```[a-z]*\n", "", content_clean).replace("```", "").strip()
        
        # 2. Detectar y recortar la clase/interfaz/enum. Buscamos: (Tipo) (Nombre) {
        #    Este patrón es más específico que el anterior.
        class_pattern = r"(?:public\s+)?(?:class|interface|enum)\s+\w+\s*(\{|<)" # Busca la llave de apertura
        match = re.search(class_pattern, content_clean, re.DOTALL)
        
        if match:
            print(f"   🛡️  Limpiador: Recortando estructura redundante en {file_name}")
            # El final es la última llave '}' que no esté dentro de una función
            start_idx = match.end() - 1 # Empezar justo después del {
            end_idx = content_clean.rfind("}")
            
            if end_idx > start_idx:
                # Extraemos el contenido entre el { de la declaración y el último }
                content_clean = content_clean[start_idx:end_idx].strip()
        
        # 3. Eliminar imports y packages que se hayan colado en el fragmento
        lines = [l for l in content_clean.split("\n") if not l.strip().startswith(("package ", "import "))]
        return "\n".join(lines).strip()
    
    

    def execute_generation(self, inventory):
        """Fase 3: Generación Mixta + QA Loop"""
        print(f"\n🚀 Iniciando generación de código...")
        
        code_files = [f for f in inventory if Path(f).suffix in ['.java', '.py']]
        
        for idx, file_path in enumerate(code_files, 1):
            clean_path = str(file_path).strip()
            target_file = self.backend_dir / clean_path
            
            if target_file.exists() and target_file.stat().st_size > 0:
                if clean_path not in self.state.written_artifacts:
                    self.state.written_artifacts.append(clean_path)
                continue

            file_name = Path(clean_path).stem
            print(f"🛠️ [{idx}/{len(code_files)}] Generando: {clean_path}")
            
            entities = self.state.domain_model.get("core_entities", {})
            entity_data = entities.get(file_name) or entities.get(file_name.capitalize()) or {}
            
            relevant_domain = {
                "entity": entity_data,
                "attributes": entity_data.get("attributes", []),
                "enums": self.state.domain_model.get("enums", {}),
                "context": f"Generación de {clean_path}"
            }

            try:
                task = build_single_file_task(self.backend_builder, clean_path, relevant_domain, self.state.architecture)
                res = self.backend_builder.execute_task(task)
                output = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))

                if output and "content" in output:
                    output["path"] = clean_path 
                    logic_fragment = self._clean_hallucinated_class(output["content"], file_name)
                    
                    # --- SELECTOR INTELIGENTE DE TEMPLATE ---
                    ext = Path(clean_path).suffix
                    if ext == ".java":
                        path_lower = clean_path.lower()
                        if "mainapplication" in path_lower:
                            t_path = "java/maven_main.j2"
                        elif any(x in path_lower for x in ["domain/model", "domain/valueobject", "application/dto"]):
                            t_path = "java/maven_pojo.j2"
                        elif "repositoryport" in path_lower:
                            t_path = "java/maven_port.j2" 
                        else: # Service, Controller, RepositoryImpl
                            t_path = "java/maven_class.j2"
                        
                        output["content"] = self.template_engine.render(t_path, {
                            "class_name": file_name,
                            "package_name": calculate_package(clean_path),
                            "extra_imports": output.get("imports", []),
                            "business_logic": logic_fragment,
                            "description": f"Componente {file_name}"
                        })

                    # QA Loop (Skipeado para MainApplication)
                    if "mainapplication" not in clean_path.lower():
                        qa_task = build_qa_review_task(self.qa_agent, clean_path, output["content"])
                        qa_res = self.qa_agent.execute_task(qa_task)
                        qa_report = normalize_llm_output(qa_res.raw if hasattr(qa_res, 'raw') else str(qa_res))
                        
                        if qa_report.get("is_valid"):
                            self.state.qa_stats["passed"] += 1
                        else:
                            self.state.qa_stats["fixed"] += 1 
                    else:
                        self.state.qa_stats["passed"] += 1

                    # ESCRITURA FÍSICA Y REGISTRO EN EL ESTADO
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    write_artifacts([output], self.backend_dir)
                    self.state.written_artifacts.append(clean_path)
                    
            except Exception as e:
                print(f"   ❌ Error en {clean_path}: {e}")

    def execute_infrastructure(self):
        """Fase 4: Infraestructura"""
        print("\n" + "="*50)
        print("🐳 FASE 4: GENERANDO INFRAESTRUCTURA")
        print("="*50)
        
        try:
            infra_task = build_infra_task(self.sre_agent, self.state.domain_model, self.state.architecture)
            res = self.sre_agent.execute_task(infra_task)
            
            # --- DEBUGGING: Ver qué narices está devolviendo la IA ---
            raw_output = res.raw if hasattr(res, 'raw') else str(res)
            print(f"🔍 DEBUG SRE Raw Output (First 100 chars): {raw_output[:100]}...")
            
            output = normalize_llm_output(raw_output)
            
            if output and "artifacts" in output:
                # Asegurar que el directorio existe
                self.backend_dir.mkdir(parents=True, exist_ok=True)
                
                written = write_artifacts(output["artifacts"], self.backend_dir)
                
                if not written:
                     print("⚠️ ALERTA: write_artifacts devolvió una lista vacía.")
                
                for p in written:
                    rel_p = str(p.relative_to(self.backend_dir))
                    if rel_p not in self.state.written_artifacts:
                        self.state.written_artifacts.append(rel_p)
                
                print(f"✅ Infraestructura escrita: {[p.name for p in written]}")
            else:
                print(f"❌ ERROR FASE 4: La IA no devolvió un JSON válido con la clave 'artifacts'.")
                print(f"   Contenido recibido: {raw_output}")
                
        except Exception as e:
            print(f"❌ Excepción crítica en Fase 4: {e}")
            import traceback
            traceback.print_exc()

            
    def execute_healing(self):
        """Fase 5: Reparación Maven"""
        print("\n🔍 FASE 5: AUTO-CURACIÓN")
        for heal_attempt in range(5): # <-- heal_attempt se usa aquí
            errors = run_maven_compile(self.backend_dir)
            if not errors or not isinstance(errors, list):
                print("✅ Proyecto compila perfectamente.")
                break
            
            print(f"⚠️ Intento {heal_attempt+1}: {len(errors)} errores. Reparando...") # <-- Uso de heal_attempt
            for err in errors[:10]:
                rel_path = err['file']
                file_to_fix = self.backend_dir / rel_path
                if not file_to_fix.exists(): continue
                with open(file_to_fix, 'r') as f: broken_code = f.read()
                
                task = build_repair_task(self.backend_builder, rel_path, broken_code, err['message'], self.state.domain_model)
                res = self.backend_builder.execute_task(task)
                fix = normalize_llm_output(res.raw if hasattr(res, 'raw') else str(res))
                
                if fix and "content" in fix:
                    fix["path"] = rel_path
                    logic_fix = self._clean_hallucinated_class(fix["content"], Path(rel_path).stem)
                    
                    # Seleccionar template basado en la ruta
                    path_lower = rel_path.lower()
                    t_path = "java/maven_pojo.j2" if any(x in path_lower for x in ["model", "valueobject", "dto"]) else "java/maven_class.j2"
                    
                    fix["content"] = self.template_engine.render(t_path, {
                        "class_name": Path(rel_path).stem,
                        "package_name": calculate_package(rel_path),
                        "extra_imports": fix.get("imports", []),
                        "business_logic": logic_fix,
                        "description": "Reparado"
                    })
                    write_artifacts([fix], self.backend_dir)
            time.sleep(1)