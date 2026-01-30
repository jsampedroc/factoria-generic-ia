from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json


def generate_reports(state):
    out_dir = Path(state.output_dir)
    reports_dir = out_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    # JSON
    json_path = reports_dir / f"execution-{ts}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)

    # MARKDOWN
    md_path = reports_dir / f"execution-{ts}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📄 Execution Report\n\n")
        f.write(f"- Idea: {state.idea}\n")
        f.write(f"- Status: {state.status}\n\n")

        for step, info in state.steps.items():
            f.write(f"## 🔹 {step}\n")
            f.write(f"- Status: {info['status']}\n")
            f.write(f"- Retries: {info['retries']}\n\n")

    print(f"📊 Reportes generados en {reports_dir}")