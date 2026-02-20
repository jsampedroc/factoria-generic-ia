import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

def build_llm(tier="cheap") -> LLM:
    """
    Crea un LLM compatible con CrewAI basado en la configuración.
    
    Tier 'smart': Para diseño, arquitectura y razonamiento complejo.
    Tier 'cheap': Para generación masiva de código (Java verboso).
    """
    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

    if tier == "smart":
        model = os.getenv("AI_SMART_MODEL", "deepseek-chat") 
        # Aumentamos capacidad para razonar arquitectura
        max_tokens = 8000 
        temperature = 0.2
    else:
        # Tier 'cheap' (usado por backend_builder)
        model = os.getenv("AI_CHEAP_MODEL", "deepseek-chat")
        # CORRECCIÓN CRÍTICA: Subimos de 1500 a 4000. 
        # Java es verboso, 1500 corta los archivos a la mitad.
        max_tokens = 4000  
        temperature = 0.1

    return LLM(
        model=model, 
        base_url=base_url, 
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens
    )


