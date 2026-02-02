from pathlib import Path
from typing import Iterable, Dict, List


def write_artifacts(
    artifacts: Iterable[Dict[str, str]],
    base_dir: Path,
) -> List[Path]:
    """
    Write generated artifacts to disk.

    Each artifact must have:
      - path: relative file path
      - content: full file content as string

    Returns a list of written file paths.
    """

    written_files: List[Path] = []

    if not artifacts:
        return written_files

    for artifact in artifacts:
        path = artifact.get("path")
        content = artifact.get("content")

        if not isinstance(path, str) or not path.strip():
            continue
        if not isinstance(content, str):
            continue

        target_path = base_dir / path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path.write_text(content, encoding="utf-8")
        written_files.append(target_path)

    return written_files