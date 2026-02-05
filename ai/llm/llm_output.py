import json


def normalize_llm_output(output):
    """
    CrewAI returns LLM outputs as strings.
    This helper ensures we always work with dicts when JSON is expected.
    """
    if isinstance(output, dict):
        return output

    if isinstance(output, str):
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                "LLM output is not valid JSON"
            ) from e

    raise RuntimeError(f"Unsupported LLM output type: {type(output)}")