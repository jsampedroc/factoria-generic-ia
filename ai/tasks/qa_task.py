from crewai import Task

def build_qa_review_task(agent, file_path: str, code_content: str):
    description = f"""
    Review the following source code for the file: {file_path}

    CODE TO REVIEW:
    {code_content}

    INSTRUCTIONS:
    1. Check for Java syntax errors (missing semicolons, unclosed braces, etc).
    2. Ensure all necessary imports are present.
    3. Verify it follows Spring Boot 3 standards.
    4. If the code is truncated or incomplete, mark it as INVALID.

    OUTPUT FORMAT (Strict JSON):
    {{
      "is_valid": true/false,
      "feedback": "Description of errors found or 'None'",
      "suggested_fix": "Brief instruction to fix the code"
    }}
    """
    return Task(
        description=description,
        expected_output="A code quality report in JSON format.",
        agent=agent
    )