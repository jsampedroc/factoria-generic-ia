from __future__ import annotations

import os
from pathlib import Path


def output_path(filename: str) -> str:
    """Devuelve ruta de outputs configurable vía FACTORIA_OUTPUT_DIR."""
    base = Path(os.getenv("FACTORIA_OUTPUT_DIR", "outputs"))
    return str(base / filename)
