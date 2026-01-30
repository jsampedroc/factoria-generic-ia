from __future__ import annotations
from enum import Enum
from typing import Optional


class Decision(Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    ABORT = "abort"


class DecisionEngine:
    """
    Decide qué hacer tras ejecutar un paso del pipeline.
    """

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries

    def decide(
        self,
        step: str,
        success: bool,
        retries: int,
        error: Optional[Exception] = None,
    ) -> Decision:

        if success:
            return Decision.CONTINUE

        if retries < self.max_retries and self._is_recoverable(error):
            return Decision.RETRY

        return Decision.ABORT

    def _is_recoverable(self, error: Optional[Exception]) -> bool:
        if error is None:
            return False

        return isinstance(error, (ValueError, TimeoutError))