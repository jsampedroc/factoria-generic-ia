from crewai import Task
from ai.prompts import load_prompt


def build_backend_generation_task(backend_builder):
    """
    Backend Generation – Nivel 2
    Contract-first, artifacts-only, disk-writable
    """

    prompt = load_prompt("backend_springboot.md")

    return Task(
        description=prompt,
        expected_output="""
A SINGLE valid JSON object with the following structure:

{
  "artifacts": [
    {
      "path": "relative/path/from/backend/root",
      "content": "file content as plain text"
    }
  ]
}

Rules:
- artifacts MUST be a list
- path MUST be relative (no absolute paths)
- content MUST be valid source code or config
- DO NOT include explanations
- DO NOT include markdown
- DO NOT include comments outside code
""",
        agent=backend_builder,
    )