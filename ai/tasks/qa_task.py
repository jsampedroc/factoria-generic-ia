from crewai import Task

def build_qa_review_task(agent, file_path: str, code_content: str) -> Task:
    description = f"""
    Review the following code for: {file_path}
    NOTE: This code was generated using a MIXED FACTORY (Templates + IA).

    CODE TO REVIEW:
    {code_content}

    STRICT CHECKLIST:
    1. Truncated code?
    2. **Layer Correctness**: Domain/VO must be POJO. Service must NOT have @RestController. Controller must NOT have business logic.
    3. **No Redundant Structure**: If the code contains `public class ... {{` or `public interface ... {{`, mark as invalid. The structure is provided by templates.
    4. Syntax errors?

    STRICT QUALITY CHECKLIST:
    1. **DDD Consistency**: Does it use Value Objects (e.g., new ChildId(id)) instead of primitives (Long/String) for IDs? (CRITICAL).
    2. **Hexagonal Integrity**: Does the logic respect the layers? (e.g., Application services should not leak JPA details).
    3. **Logic Completeness**: Are all business requirements for this component implemented or is it just a placeholder?
    4. **Safety**: Check for potential NullPointerExceptions in the injected logic.

    IGNORE: Boilerplate, imports, and class declarations (handled by templates).

    OUTPUT FORMAT (Strict JSON):
    {{
      "is_valid": true/false,
      "feedback": "Reason if invalid (focus on DDD and logic)",
      "suggested_fix": "Brief instruction to fix the logic"
    }}
    """
    return Task(
        description=description,
        expected_output="Quality report focusing on DDD logic and Hexagonal consistency.",
        agent=agent
    )