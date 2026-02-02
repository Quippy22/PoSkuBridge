def extract_keywords(text: str) -> str:
    """Takes a raw string, splits it into words, and returns a clean list"""

    if not text:
        return ""

    # Normalize: lowercase and strip
    text = text.lower().strip()
    # Split
    words = text.split()
    # Remove duplicates and keep the words in a list
    keywords = sorted(list(set(words)))

    return " ".join(keywords)
