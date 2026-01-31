def build_grounded_prompt(
    *,
    system_rules: str,
    context_blocks: list[str],
    task_prompt: str,
    output_contract: str,
) -> str:
    """Build a grounded prompt enforcing context-only reasoning."""

    context_text = "\n\n".join(
        f"- {str(block).strip()}" for block in context_blocks if block and str(block).strip()
    )

    return f"""[SYSTEM]
{system_rules}

[CONTEXT]
{context_text}

[TASK]
{task_prompt}

[OUTPUT CONTRACT]
{output_contract}
""".strip()
