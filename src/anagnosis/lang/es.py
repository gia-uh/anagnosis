"""Spanish orthographic rules."""
import re

_STRONG = set("aeoáéóíú")  # accented i/u form a hiatus, so they count as strong
_VOWELS = re.compile(r"[aeiouáéíóúü]+")


def syllables(word: str) -> int:
    """Count syllables by vowel nuclei.

    A run of vowels is one nucleus (a diphthong or triphthong) except where two
    strong vowels meet, which is a hiatus. The u of que/qui/gue/gui is silent, and
    a final y after a vowel is part of the nucleus (rey, muy); y elsewhere is a
    consonant, and the word "y" alone is one syllable.
    """
    w = word.lower()
    if w == "y":
        return 1
    w = re.sub(r"(?<=[qg])u(?=[eiéí])", "", w)
    w = re.sub(r"y$", "i", w).replace("y", "")
    n = 0
    for run in _VOWELS.findall(w):
        n += 1 + sum(a in _STRONG and b in _STRONG for a, b in zip(run, run[1:]))
    return max(n, 1)
