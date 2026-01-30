from __future__ import annotations
import sys
from pathlib import Path
from typing import TextIO


class TeeStdout(TextIO):
    """
    Duplica stdout/stderr:
    - consola (colores, cajas, etc)
    - fichero de log (texto crudo)
    """

    def __init__(self, logfile: Path, stream: TextIO):
        self.stream = stream
        self.logfile = logfile
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self._file = logfile.open("a", encoding="utf-8")

    def write(self, text: str):
        self.stream.write(text)
        self.stream.flush()
        self._file.write(text)
        self._file.flush()

    def flush(self):
        self.stream.flush()
        self._file.flush()

    def close(self):
        self._file.close()