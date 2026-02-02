from pathlib import Path


_PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """
    Load a prompt file from the prompts directory.
    """
    prompt_path = _PROMPTS_DIR / name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {name}")

    return prompt_path.read_text(encoding="utf-8")