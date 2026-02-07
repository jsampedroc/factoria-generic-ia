import json
import re
from typing import Any, Dict


def normalize_llm_output(raw_output: Any) -> Dict[str, Any]:
    """
    Robust LLM output normalization.
    Never raises JSON errors.
    """

    if raw_output is None:
        return {
            "status": "NEEDS_INPUT",
            "error": "EMPTY_OUTPUT",
            "raw_output": "",
        }

    if isinstance(raw_output, dict):
        return raw_output

    text = str(raw_output).strip()

    # 1️⃣ Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2️⃣ Try extracting first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception as e:
            return {
                "status": "NEEDS_INPUT",
                "error": "INVALID_JSON",
                "message": str(e),
                "raw_output": candidate[:4000],
            }

    # 3️⃣ Fallback: no JSON at all
    return {
        "status": "NEEDS_INPUT",
        "error": "NO_JSON_FOUND",
        "raw_output": text[:4000],
    }