import re


def to_pascal_case(string: str) -> str:
    """Converts a string to PascalCase."""
    # Split on common delimiters and filter empty strings
    words = re.split(r"[-_\s]+", string.strip())
    # Capitalize first letter of each word and join
    return "".join(word.capitalize() for word in words if word)
