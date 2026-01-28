from __future__ import annotations

DEFAULTS = {
    # Generic defaults for the factory (not tied to any specific domain).
    "output_dir": "output",
    "kpi": {
        "must_compile": True,
        "must_have_tests": True,
        "must_have_docker": True,
    },
}
