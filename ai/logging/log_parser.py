import re
from pathlib import Path


STEP_RE = re.compile(r"🔹 Ejecutando paso: (.+)")
ERROR_RE = re.compile(r"⚠️ Error en (.+): (.+)")


def parse_log(log_file: Path) -> dict:
    events = []

    for line in log_file.read_text(encoding="utf-8").splitlines():
        if m := STEP_RE.search(line):
            events.append({"type": "step_start", "step": m.group(1)})
        elif m := ERROR_RE.search(line):
            events.append({
                "type": "error",
                "step": m.group(1),
                "message": m.group(2),
            })

    return {"events": events}