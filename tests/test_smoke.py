import subprocess
from pathlib import Path


def test_pipeline_generates_report(tmp_path):
    result = subprocess.run(
        [
            "python",
            "-m",
            "ai.main",
            "Simple task management app with users and tasks",
        ],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    outputs = Path("outputs")
    assert outputs.exists()

    report = outputs / "report.md"
    assert report.exists()