"""What counts as a word: a spaCy token that contains a letter."""
import re

_LETTER = re.compile(r"[^\W\d_]")


def words(span) -> list:
    return [t for t in span if not t.is_space and not t.is_punct and _LETTER.search(t.text)]
