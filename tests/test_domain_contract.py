from ai.utils.llm_output import normalize_llm_output


def test_domain_output_contract():
    fake_output = {
        "domain_name": "Task Management",
        "core_entities": ["Task", "User"],
        "key_use_cases": ["Create task", "Assign task"],
        "assumptions": [],
        "open_questions": [],
    }

    normalized = normalize_llm_output(fake_output)

    for key in [
        "domain_name",
        "core_entities",
        "key_use_cases",
        "assumptions",
        "open_questions",
    ]:
        assert key in normalized