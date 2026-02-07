# ai/tasks/architecture_task.py
from crewai import Task
from ai.prompts import load_prompt

def build_architecture_task(architect_agent):
    prompt = load_prompt("architecture.md")

    return Task(
        description=prompt,
        expected_output="JSON architecture description wrapped in <<<JSON>>> markers",
        agent=architect_agent,
    )