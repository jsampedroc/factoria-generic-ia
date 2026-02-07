# ai/pipeline/state.py

from typing import Any, List, Optional


from pathlib import Path

class PipelineState:
    def __init__(self, idea: str, output_dir: Path):
        self.idea = idea
        self.output_dir = output_dir

        self.domain_model = None
        self.architecture = None
        self.backend = None

        self.status = None
        self.open_questions = []
        self.errors = []

    # Helpers explícitos (evitan bugs silenciosos)
    def set_status(self, status: str):
        self.status = status

    def add_open_questions(self, questions: List[str]):
        self.open_questions.extend(questions)

    def add_error(self, error: str):
        self.errors.append(error)