from crewai import Task

def build_self_check_task(verifier_agent):
    return Task(
        description=(
            "Verifica que la salida anterior contiene SOLO afirmaciones soportadas por el CONTEXTO. "
            "Lista cualquier afirmación no verificable, issues y cómo corregirlo."
        ),
        expected_output="""JSON with:
- pass (boolean)
- unverified_claims (array of strings)
- issues (array of strings)
- fix_instructions (array of strings)
""",
        agent=verifier_agent,
    )
