# ai/validation/domain_guard.py

def validate_domain(domain_output: dict, expected_keywords: list[str]) -> None:
    """
    Lanza excepción si el dominio no parece coherente con la idea original.
    """

    text = str(domain_output).lower()

    missing = [
        kw for kw in expected_keywords
        if kw.lower() not in text
    ]

    if len(missing) == len(expected_keywords):
        raise ValueError(
            f"Dominio incoherente. No se encontraron conceptos esperados: {expected_keywords}"
        )