def ask_user_questions(open_questions: list[str]) -> str:
    print("\n🔎 Additional information required:\n")

    for i, q in enumerate(open_questions, 1):
        print(f"{i}. {q}")

    print(
        "\nPlease provide the missing information below.\n"
        "You may answer in free text. Press ENTER when finished:\n"
    )

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)

    return "\n".join(lines).strip()