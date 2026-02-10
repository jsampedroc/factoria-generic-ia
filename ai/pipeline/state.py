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