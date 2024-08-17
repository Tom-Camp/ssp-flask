def get_machine_name(name: str) -> str:
    to_replace = "~`!@#$%^&*()+=[]{}|:;\"'?/>.<,"
    for x in to_replace:
        name = name.replace(x, "")
    return name.replace(" ", "_").lower()
