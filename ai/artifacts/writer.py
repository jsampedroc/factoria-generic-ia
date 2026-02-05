from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict, Any


class ArtifactWriteError(RuntimeError):
    pass


def _safe_join(root: Path, rel_path: str) -> Path:
    rel = rel_path.replace("\\", "/").strip()

    if rel.startswith("/"):
        raise ArtifactWriteError(f"Artifact path must be relative, got: {rel_path}")
    if ".." in rel.split("/"):
        raise ArtifactWriteError(f"Artifact path must not contain '..', got: {rel_path}")

    target = (root / rel).resolve()
    root_resolved = root.resolve()

    if root_resolved not in target.parents and target != root_resolved:
        raise ArtifactWriteError(f"Artifact path escapes root: {rel_path}")

    return target


def write_artifacts(artifacts: Iterable[Dict[str, Any]], target_dir: Path) -> List[Path]:
    """
    Writes artifacts to target_dir safely.
    Each artifact must be: {"path": str, "content": str}
    Returns list of written file paths.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    written: List[Path] = []

    for a in artifacts:
        if not isinstance(a, dict):
            continue

        rel_path = a.get("path")
        content = a.get("content")

        if not isinstance(rel_path, str) or not isinstance(content, str):
            continue

        file_path = _safe_join(target_dir, rel_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        written.append(file_path)

    return written