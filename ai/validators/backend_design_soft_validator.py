from __future__ import annotations

from typing import Any, Dict, List, Tuple


def soft_validate_backend_design(
    backend_contract: Dict[str, Any],
    backend_design: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Soft validation: turns "design deviations / ambiguities" into open_questions.

    Does NOT raise. Returns:
      - possibly enriched backend_design (open_questions appended)
      - list of questions found
    """

    questions: List[str] = []

    # Helper: safe get list
    def _list(x):
        return x if isinstance(x, list) else []

    # 1) Payments ambiguity
    entity_names = {e.get("name") for e in _list(backend_design.get("entities")) if isinstance(e, dict)}
    if "Payment" in entity_names:
        questions.append(
            "Payments: ¿los pagos son mensuales, por asistencia o por periodos configurables (mensual/trim/curso)?"
        )
        questions.append(
            "Payments: ¿se requiere estado del pago (PENDING/PAID/OVERDUE) y fechas (dueDate/paidAt)?"
        )

    # 2) Attendance ambiguity
    if "Attendance" in entity_names or "AttendanceRecord" in entity_names:
        questions.append(
            "Attendance: ¿la asistencia se registra por día completo, por franjas horarias (entrada/salida), o ambos?"
        )

    # 3) Multi-center / organization
    # If not explicitly modeled, ask
    questions.append(
        "Multi-center: ¿el sistema debe soportar múltiples guarderías bajo una misma organización (multi-tenant lógico)?"
    )

    # 4) Identity / roles ambiguity (Level 2 design only)
    questions.append(
        "Roles: ¿qué roles mínimos necesitas (ADMIN, STAFF) y qué permisos básicos por módulo?"
    )

    # 5) Data retention / soft delete
    questions.append(
        "Retención: ¿necesitas borrado lógico (soft delete) para niños/pagos/asistencias?"
    )

    # Append questions to backend_design.open_questions (dedup)
    bd = dict(backend_design)
    existing = bd.get("open_questions") if isinstance(bd.get("open_questions"), list) else []
    merged = list(dict.fromkeys(existing + questions))
    bd["open_questions"] = merged

    return bd, questions