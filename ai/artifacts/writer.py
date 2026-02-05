from pathlib import Path
from typing import Iterable, Dict, List


def write_artifacts(
    artifacts: Iterable[Dict[str, str]],
    base_dir: Path,
) -> List[Path]:
    """
    Writes backend artifacts to disk.

    Each artifact must have:
      - path: relative file path
      - content: file content

    Files are written under base_dir.
    Existing files are overwritten.
    """

    written: List[Path] = []

    base_dir.mkdir(parents=True, exist_ok=True)

    for artifact in artifacts:
        rel_path = artifact.get("path")
        content = artifact.get("content")

        if not rel_path or content is None:
            # Skip invalid artifact silently
            continue

        file_path = base_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")
        written.append(file_path)

    return written