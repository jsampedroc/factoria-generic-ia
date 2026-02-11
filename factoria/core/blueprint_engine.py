import os
from pathlib import Path
import yaml

class BlueprintManager:
    def __init__(self, config_name="factory_config.yaml"):
        # Esto busca el archivo en la raíz del proyecto, sin importar desde dónde lances el comando
        root_dir = Path(__file__).parent.parent.parent
        config_path = root_dir / config_name
        
        if not config_path.exists():
            raise FileNotFoundError(f"❌ No se encontró el archivo de configuración en: {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)