def reverse_text(text: str) -> str:
    """Return reversed text"""
    return text[::-1]

def count_letters(text: str) -> int:
    """Return number of letters in text"""
    return sum(1 for c in text if c.isalpha())

def count_words(text: str) -> int:
    """Return number of words in text"""
    return len(text.split())
