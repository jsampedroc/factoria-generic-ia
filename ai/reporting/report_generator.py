from pathlib import Path
import json

def generate_report(state):
    report_path = state.out_dir / "report.md"
    
    # Contar archivos por tipo
    java_files = [p for p in state.written_artifacts if p.endswith(".java")]
    infra_files = [p for p in state.written_artifacts if "infra" in p or "docker" in p]

    content = f"""# 🏭 Execution Report: Software Factory v2
    
## 💡 User Idea
{state.idea}

## 📊 Summary
- **Status:** {state.status}
- **Total Artifacts:** {len(state.written_artifacts)}
- **Java Classes:** {len(java_files)}
- **Infra/SRE Files:** {len(infra_files)}
- **QA Results:** {state.qa_stats['passed']} Passed, {state.qa_stats['fixed']} Auto-fixed

## 🏗️ Domain Model: {state.domain_model.get('domain_name', 'Generic')}
- **Entities:** {', '.join([e['name'] if isinstance(e, dict) else str(e) for e in state.domain_model.get('core_entities', [])])}

## 📐 Architecture Overview
{state.architecture.get('architecture_overview', 'Hexagonal Architecture')}

## 📂 Generated Artifacts (Inventory)
"""
    for artifact in state.written_artifacts:
        content += f"- `{artifact}`\n"

    if state.errors:
        content += "\n## ❌ Errors Encountered\n"
        for err in state.errors:
            content += f"- {err}\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)