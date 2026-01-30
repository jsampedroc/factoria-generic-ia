from pathlib import Path
import yaml
from typing import Dict


def load_yaml(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"No existe el fichero: {path}")
    with path.open() as f:
        return yaml.safe_load(f)


def apply_run_config(golden_path: Dict, run_config: Dict) -> Dict:
    resolved = golden_path.copy()

    options = run_config.get("options", {})
    for section, values in options.items():
        if section in resolved and isinstance(resolved[section], dict):
            resolved[section].update(values)

    resolved["project"] = run_config.get("project", {})
    return resolved