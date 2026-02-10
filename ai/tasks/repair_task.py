from crewai import Task

def build_repair_task(agent, file_path: str, error_msg: str, current_code: str, domain_model: dict) -> Task:
    # Extraemos info de la entidad si el nombre del archivo coincide
    description = f"""
    CRITICAL REPAIR MISSION:
    The file {file_path} is BROKEN or INCOMPLETE.
    
    COMPILER ERROR: {error_msg}
    
    CURRENT CODE STATE:
    "{current_code}"

    INSTRUCTIONS:
    1. If the current code is nearly empty or truncated, you MUST regenerate the logic from scratch.
    2. Reference the Domain Model to identify the necessary fields and logic for this specific file.
    3. Ensure a complete, valid Java class that solves the compilation error.
    4. Do not just fix the error; ensure the file is functional and consistent with the rest of the app.

    OUTPUT FORMAT:
    {{
      "path": "{file_path}",
      "content": "... (the full, fixed, and complete source code) ..."
    }}
    """
    return Task(description=description, agent=agent, expected_output="Full fixed Java file.")