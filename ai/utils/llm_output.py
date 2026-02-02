from __future__ import annotations

import json
from typing import Any, Dict


def normalize_llm_output(output: Any) -> Dict[str, Any]:
    """
    Normalize LLM output into a dictionary.

    - If output is already a dict → return as is
    - If output is a JSON string → parse it
    - Otherwise → wrap raw output safely
    """
    if isinstance(output, dict):
        return output

    if isinstance(output, str):
        output = output.strip()
        try:
            parsed = json.loads(output)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        return {
            "raw_output": output,
            "open_questions": [],
        }

    return {
        "raw_output": str(output),
        "open_questions": [],
    }