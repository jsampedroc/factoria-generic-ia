from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import re


class Decision(Enum):
    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    ABORT = "ABORT"
    NEEDS_INPUT = "NEEDS_INPUT"


@dataclass
class DecisionContext:
    step: str
    success: bool
    retries: int
    error: Optional[Exception] = None
    open_questions: Optional[List[str]] = None
    idea: Optional[str] = None


class DecisionEngine:
    """
    ADL Decision Engine (Enterprise-grade)

    Responsibilities:
    - Retry/abort decisions
    - NEEDS_INPUT decisions
    - Answer Resolution: do NOT re-ask questions already answered in the idea
    """

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self.last_unresolved_questions: List[str] = []
        self.last_resolved_questions: List[str] = []

    # -----------------------------
    # Answer Resolution (ADL)
    # -----------------------------
    def resolve_open_questions(self, open_questions: List[str], idea: str) -> Tuple[List[str], List[str]]:
        """
        Resolve (close) open questions if answers already exist in the provided idea.

        Strategy (generic, domain-agnostic):
        1) Parse "key: value" lines (e.g. "- Roles: ADMIN y STAFF")
        2) If question contains that key (or similar), treat it as answered
        3) Otherwise, keyword-based match (non-trivial tokens) against idea text

        Returns:
          (resolved_questions, unresolved_questions)
        """
        if not open_questions:
            return [], []
        if not idea:
            return [], list(open_questions)

        idea_lc = idea.lower()

        # 1) Parse explicit "Key: Value" answers from idea (supports bullets)
        # Examples:
        # - Multi-center: Sí, soportar múltiples guarderías...
        # Roles: ADMIN y STAFF...
        kv_answers = {}
        for line in idea.splitlines():
            line_stripped = line.strip().lstrip("-").strip()
            if ":" in line_stripped:
                k, v = line_stripped.split(":", 1)
                k = k.strip().lower()
                v = v.strip().lower()
                if k and v:
                    kv_answers[k] = v

        # Helper: normalize key for fuzzy matching
        def _norm(s: str) -> str:
            s = s.lower().strip()
            s = re.sub(r"[^a-z0-9áéíóúñü\s\-]", "", s)
            s = re.sub(r"\s+", " ", s)
            return s

        kv_keys = [_norm(k) for k in kv_answers.keys()]

        resolved: List[str] = []
        unresolved: List[str] = []

        for q in open_questions:
            q_norm = _norm(q)

            # 2) Try key-based resolution: if any explicit key appears in question
            answered_by_key = False
            for key in kv_keys:
                # require non-trivial key length
                if len(key) >= 4 and key in q_norm:
                    answered_by_key = True
                    break

            if answered_by_key:
                resolved.append(q)
                continue

            # 3) Keyword match fallback (generic)
            # Extract non-trivial tokens from question
            tokens = [t for t in re.split(r"\W+", q_norm) if len(t) >= 5]
            # Reduce noise tokens that are too generic
            stop = {"sistema", "debe", "soportar", "necesitas", "minimos", "permisos", "basicos", "modulo"}
            tokens = [t for t in tokens if t not in stop]

            if tokens and any(t in idea_lc for t in tokens):
                resolved.append(q)
            else:
                unresolved.append(q)

        return resolved, unresolved

    # -----------------------------
    # Main Decision function
    # -----------------------------
    def decide(
        self,
        step: str,
        success: bool,
        retries: int,
        error: Optional[Exception] = None,
        open_questions: Optional[List[str]] = None,
        idea: Optional[str] = None,
    ) -> Decision:
        """
        Returns a Decision for the pipeline.

        - If open_questions exist:
            - resolve already-answered questions using idea
            - if any unresolved -> NEEDS_INPUT
            - else -> CONTINUE

        - If failure:
            - RETRY if retries < max_retries else ABORT

        - If success and no questions:
            - CONTINUE
        """
        # Reset memory
        self.last_unresolved_questions = []
        self.last_resolved_questions = []

        # 1) NEEDS_INPUT logic with Answer Resolution
        if open_questions:
            resolved, unresolved = self.resolve_open_questions(open_questions, idea or "")
            self.last_resolved_questions = resolved
            self.last_unresolved_questions = unresolved

            if unresolved:
                return Decision.NEEDS_INPUT
            return Decision.CONTINUE

        # 2) Retry/Abort logic
        if not success:
            if retries < self.max_retries:
                return Decision.RETRY
            return Decision.ABORT

        # 3) Default
        return Decision.CONTINUE