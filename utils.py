import re


def clean_title(title: str) -> str:
    """Remove leading numbers/dots and extra whitespace from a heading title.
    '3 ارتباط الحل' → 'ارتباط الحل'
    '4.  المنهجية' → 'المنهجية'
    """
    cleaned = re.sub(r"^\d+[\.\-\s]*\s*", "", title.strip())
    return cleaned.strip()


def normalize_arabic(text: str) -> str:
    """Normalize common Arabic character variations for matching.
    ة → ه, أ/إ/آ → ا, ى → ي, etc.
    """
    text = text.replace("ة", "ه")
    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalized_filename(title: str) -> str:
    """Clean + normalize a title for use as a stable filename."""
    name = normalize_arabic(clean_title(title))
    name = name.replace("/", "_").replace("\\", "_")
    return name
