import json
import os
from pathlib import Path

class StateManager:
    @staticmethod
    def load_specs(spec_file: Path, state):
        """Carga el estado previo de las especificaciones si existen."""
        if spec_file.exists() and spec_file.stat().st_size > 0:
            print(f"♻️  MODO CACHÉ: Cargando diseño de {spec_file.name}")
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Soportamos el formato antiguo y el nuevo
                    state.domain_model = data.get("domain_model", data)
                    state.architecture = data.get("architecture")
                
                # Retornamos True solo si tenemos al menos el dominio
                return state.domain_model is not None
            except Exception as e:
                print(f"⚠️ Error leyendo caché: {e}")
                return False
        return False

    @staticmethod
    def save_specs(spec_file: Path, domain_model, architecture=None):
        """Guarda el estado actual asegurando que no se pierdan datos previos."""
        # Recuperamos datos existentes para no sobrescribir con Nones
        current_domain = domain_model
        current_arch = architecture

        if spec_file.exists() and spec_file.stat().st_size > 0:
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    if not current_domain:
                        current_domain = old_data.get("domain_model")
                    if not current_arch:
                        current_arch = old_data.get("architecture")
            except:
                pass

        data = {
            "domain_model": current_domain,
            "architecture": current_arch
        }
        
        # Asegurar directorio de specs
        spec_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Escritura atómica (evita que el archivo se quede vacío si falla la escritura)
        temp_file = spec_file.with_suffix(".tmp")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno()) # Asegura que se escribe en el disco físico
        
        os.replace(temp_file, spec_file) # Reemplazo seguro
        print(f"💾 Specs actualizadas en: {spec_file.name}")