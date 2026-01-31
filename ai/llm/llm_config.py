import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

def build_llm() -> LLM:
    """Create a CrewAI-compatible LLM from environment configuration."""
    model = os.getenv("AI_MODEL", "deepseek-chat")
    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

    return LLM(model=model, base_url=base_url, api_key=api_key)
