from pathlib import Path
from typing import Any


def _write_section(f, title: str, content: Any):
    f.write(f"\n## {title}\n\n")
    if content is None:
        f.write("_No data available_\n")
        return

    if isinstance(content, (dict, list)):
        import json
        f.write("```json\n")
        f.write(json.dumps(content, indent=2, ensure_ascii=False))
        f.write("\n```\n")
    else:
        f.write(str(content) + "\n")


def generate_report(state) -> None:
    """
    Generates outputs/run_xxx/report.md
    This function must NEVER crash the pipeline.
    """
    try:
        out_dir = Path(state.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        report_path = out_dir / "report.md"

        with report_path.open("w", encoding="utf-8") as f:
            f.write("# Execution Report\n\n")

            # --- IDEA ---
            _write_section(f, "Idea", getattr(state, "idea", None))

            # --- DOMAIN ---
            _write_section(f, "Domain Model", getattr(state, "domain_model", None))

            # --- ARCHITECTURE ---
            _write_section(f, "Architecture", getattr(state, "architecture", None))

            # --- BACKEND (summary only) ---
            backend = getattr(state, "backend", None)
            if isinstance(backend, dict):
                summary = {
                    k: backend.get(k)
                    for k in ("stack", "modules", "notes")
                    if k in backend
                }
                _write_section(f, "Backend (Summary)", summary)
            else:
                _write_section(f, "Backend (Summary)", backend)

            # --- STATUS ---
            status = getattr(state, "status", None)
            if status == "NEEDS_INPUT":
                _write_section(
                    f,
                    "Execution Status",
                    {
                        "status": "NEEDS_INPUT",
                        "open_questions": getattr(state, "open_questions", []),
                    },
                )
            else:
                _write_section(
                    f,
                    "Execution Status",
                    {"status": "COMPLETED"},
                )

    except Exception as e:
        # Report generation must NEVER break execution
        print(f"⚠️ Failed to generate report.md: {e}")