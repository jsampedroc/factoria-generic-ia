from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime


class TeeStdout:
    """
    Duplica stdout y stderr:
    - imprime en consola
    - escribe exactamente lo mismo en un fichero
    """

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self._file = open(self.log_file, "a", encoding="utf-8")
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def write(self, message: str):
        self._stdout.write(message)
        self._file.write(message)

    def flush(self):
        self._stdout.flush()
        self._file.flush()

    def close(self):
        self._file.close()


def tee_to_file(log_dir: Path, prefix: str = "run") -> TeeStdout:
    """
    Redirige stdout + stderr a consola y a fichero log
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = log_dir / f"{prefix}-{timestamp}.log"

    tee = TeeStdout(log_file)

    sys.stdout = tee
    sys.stderr = tee

    print(f"📝 Logging activado → {log_file}")

    return tee