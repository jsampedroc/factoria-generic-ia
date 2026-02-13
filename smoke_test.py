import sys
import json
from pathlib import Path

# Asegurar que Python vea las carpetas internas
sys.path.append(str(Path(__file__).parent))

try:
    from factoria.core.blueprint_engine import BlueprintManager
    from jinja2 import Environment, FileSystemLoader
    print("✅ Importaciones de módulos: OK")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

# ... (mismo inicio de smoke_test.py)

def run_smoke_test():
    print("\n" + "="*40)
    print("🔍 INICIANDO SMOKE TEST (CERO TOKENS)")
    print("="*40)

    # 1. Validar carga de Configuración
    try:
        bm = BlueprintManager("factory_config.yaml")
        print("✅ factory_config.yaml: Encontrado y cargado.")
    except Exception as e:
        print(f"❌ Error cargando factory_config.yaml: {e}")
        return

    # 2. Validar Entorno de Plantillas
    try:
        # CAMBIO: Ruta corregida a factoria/templates
        env = Environment(loader=FileSystemLoader("factoria/templates"))
        print("✅ Entorno Jinja2: Inicializado en factoria/templates")
    except Exception as e:
        print(f"❌ Error inicializando Jinja2: {e}")
        return

    # 3. Simulación de Renderizado (Prueba de Fuego)
    casos = [
        {"path": "app/service/User.java", "ext": "java"},
        {"path": "api/routes/auth.py", "ext": "python"}
    ]

    for caso in casos:
        print(f"\n--- Probando Blueprint para {caso['ext'].upper()} ---")
        t_path = bm.resolve_template(caso['path'])
        
        if not t_path:
            print(f"❌ No se encontró template definido para {caso['path']} en el YAML.")
            continue
            
        print(f"📂 Intentando cargar: {t_path}") # Debug log
        try:
            template = env.get_template(t_path)
            mock_data = {
                "class_name": "SmokeTestComponent",
                "description": "Componente de prueba de humo",
                "extra_imports": ["os", "sys"] if caso['ext'] == "python" else ["java.util.List"],
                "business_logic": "def hello_world():\n    return 'Hello from Factoria'",
                "package_name": "com.test.smoke",
                "requirements": []
            }
            
            result = template.render(**mock_data)
            print(f"✅ Template '{t_path}' renderizado correctamente.")
            
        except Exception as e:
            print(f"❌ Error renderizando {t_path}: {e}")

    # ... (final del archivo smoke_test.py)

    print("\n" + "="*40)
    print("✨ RESULTADO: Si todo es verde, tu factoría está lista.")
    print("="*40)

if __name__ == "__main__":
    run_smoke_test()