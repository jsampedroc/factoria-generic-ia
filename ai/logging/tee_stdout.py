# ai/logging/tee_stdout.py

import sys
from pathlib import Path


class TeeStdout:
    def __init__(self, file_path: Path):
        self.file = open(file_path, "w", encoding="utf-8")
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def write(self, data):
        self.file.write(data)
        self.file.flush()
        self._stdout.write(data)

    def flush(self):
        self.file.flush()
        self._stdout.flush()

    def close(self):
        # 🔒 restaurar primero
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        self.file.close()


def tee_to_file(file_path: Path) -> TeeStdout:
    tee = TeeStdout(file_path)
    sys.stdout = tee
    sys.stderr = tee
    return tee