"""English orthographic rules."""
import re
from functools import lru_cache

import cmudict


@lru_cache(maxsize=1)
def _cmu() -> dict:
    return cmudict.dict()


def syllables(word: str) -> int:
    """Count syllables from CMUdict stress marks, or by vowel groups when the word is absent."""
    w = word.lower()
    prons = _cmu().get(w)
    if prons:
        return sum(ph[-1].isdigit() for ph in prons[0])
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(len(re.findall(r"[aeiouy]{1,2}", w)), 1)
