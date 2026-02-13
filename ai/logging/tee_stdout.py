import sys
import os

class Tee:
    def __init__(self, filename):
        self.terminal = sys.stdout
        # Aseguramos que el directorio existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush() # CRITICO: Escribe al disco inmediatamente

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def tee_to_file(filename):
    tee = Tee(filename)
    sys.stdout = tee
    sys.stderr = tee # También capturamos errores para el log
    return tee