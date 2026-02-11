from pathlib import Path
from typing import List, Dict, Any

class PipelineState:
    def __init__(self, idea: str, out_dir: Path):
        self.idea = idea
        self.out_dir = out_dir
        self.status = "STARTING"
        self.domain_model: Dict[str, Any] = {}
        self.architecture: Dict[str, Any] = {}
        self.backend: Dict[str, Any] = {"artifacts": []}
        self.infrastructure: Dict[str, Any] = {"artifacts": []}
        self.qa_stats = {"passed": 0, "fixed": 0, "failed": 0} # Importante para main.py
        self.written_artifacts: List[str] = []
        self.errors: List[str] = []
        self.open_questions: List[str] = []


stats = {
    "cache_hits": 0,
    "static_qa_fixes": 0,
    "tokens_saved_estimate": 0
}

def display_business_metrics(state):
    print("\n" + "💰" * 20)
    print("📊 DASHBOARD DE RENTABILIDAD")
    print(f" Archivos recuperados de Caché: {state.stats['cache_hits']}")
    print(f" Errores evitados por QA Estático: {state.stats['static_qa_fixes']}")
    
    # Estimación: Ahorras ~500 tokens por caché y ~300 por QA estático
    total_saved = (state.stats['cache_hits'] * 500) + (state.stats['static_qa_fixes'] * 300)
    print(f"Tokens de DeepSeek ahorrados: {total_saved}")
    print(f"Costo de producción estimado: ${(total_saved / 1000000) * 0.20:.4f}") 
    print("💰" * 20)