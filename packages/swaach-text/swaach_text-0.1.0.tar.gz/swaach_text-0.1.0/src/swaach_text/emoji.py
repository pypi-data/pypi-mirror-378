def emoji_to_text(s: str, mapping: dict[str, str]) -> str:
    # Map emoji characters to text tags; unknowns pass through unchanged.
    return "".join(mapping.get(ch, ch) for ch in s)
