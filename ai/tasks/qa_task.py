from crewai import Task

def build_qa_review_task(agent, file_path: str, code_content: str) -> Task:
    description = f"""
    Review the following code for: {file_path}

    CODE:
    {code_content}

    STRICT CHECKLIST:
    1. Truncated code? (Check for missing closing braces '}}').
    2. Correct Layer? (Domain layer must NOT have JPA/Spring annotations).
    3. Syntax errors? (Missing semicolons, wrong imports).

    OUTPUT FORMAT (Strict JSON):
    {{
      "is_valid": true/false,
      "feedback": "Reason if invalid",
      "suggested_fix": "Brief instruction"
    }}
    """
    return Task(
        description=description,
        expected_output="Code quality report in JSON.",
        agent=agent
    )