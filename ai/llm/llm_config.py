import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

def build_llm(tier="cheap") -> LLM:
    """
    Tier 'smart': Para diseño y arquitectura (necesita más razonamiento).
    Tier 'cheap': Para generar fragmentos de código (necesita velocidad y bajo coste).
    """
    # Puedes usar deepseek-reasoner (R1) para smart y deepseek-chat (V3) para cheap
    if tier == "smart":
        model = os.getenv("AI_SMART_MODEL", "deepseek-chat") 
        max_tokens = 4000
        temperature = 0.2
    else:
        model = os.getenv("AI_CHEAP_MODEL", "deepseek-chat")
        max_tokens = 1500  # Los fragmentos de código no necesitan más
        temperature = 0.1

    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing API Key para DeepSeek/OpenAI.")

    return LLM(
        model=model, 
        base_url=base_url, 
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens
    )