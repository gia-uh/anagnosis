"""Vocabulary features: age of acquisition, frequency and lexical diversity."""
import math

from wordfreq import zipf_frequency

from .. import norms
from ..features import Feature, Pool, ratio
from .words import words

BOTH = frozenset({"es", "en"})
CONTENT = {"NOUN", "VERB", "ADJ", "ADV"}
LATE = 9.0  # years: words learned at nine or later
RARE = 4.0  # Zipf: fewer than ten occurrences per million words


def _proper(t) -> bool:
    """A proper noun is tagged PROPN and capitalized. The small spaCy models tag some
    common words PROPN in short sentences ("El perro come pan."); a lowercase PROPN
    is treated as a common word."""
    return t.pos_ == "PROPN" and not t.text.islower()
MTLD_THRESHOLD = 0.72


def _p90(p: Pool):
    ages = sorted(p.bags.get("aoa", []))
    return ages[math.ceil(0.9 * len(ages)) - 1] if ages else None  # nearest-rank percentile


def _mean(bag):
    def f(p: Pool):
        v = p.bags.get(bag, [])
        return sum(v) / len(v) if v else None
    return f


def _share(bag, test):
    def f(p: Pool):
        v = p.bags.get(bag, [])
        return sum(map(test, v)) / len(v) if v else None
    return f


def _mtld_pass(tokens):
    factors, types, n = 0.0, set(), 0
    for t in tokens:
        n += 1
        types.add(t)
        if len(types) / n <= MTLD_THRESHOLD:
            factors, types, n = factors + 1, set(), 0
    if n:
        factors += (1 - len(types) / n) / (1 - MTLD_THRESHOLD)
    return len(tokens) / factors if factors else None


def mtld(p: Pool):
    """Mean of the forward and backward passes (McCarthy and Jarvis 2010)."""
    t = p.bags.get("tokens", [])
    a, b = _mtld_pass(t), _mtld_pass(t[::-1])
    return (a + b) / 2 if a is not None and b is not None else None


class Vocabulary:
    family = "vocabulary"
    features = [
        Feature("aoa_mean", "vocabulary", BOTH, "alonso2015;kuperman2012",
                "mean age of acquisition, in years, of content words found in the norms", _mean("aoa")),
        Feature("aoa_p90", "vocabulary", BOTH, "alonso2015;kuperman2012",
                "90th percentile (nearest rank) of the same ages", _p90),
        Feature("aoa_late_share", "vocabulary", BOTH, "alonso2015;kuperman2012",
                "share of those words learned at nine or later", _share("aoa", lambda a: a >= LATE)),
        Feature("aoa_coverage", "vocabulary", BOTH, "anagnosis",
                "share of content words found in the norms", ratio("aoa_found", "content_words")),
        Feature("rare_word_share", "vocabulary", BOTH, "speer2022",
                "share of words, proper nouns excluded, with Zipf frequency below 4", _share("zipf", lambda z: z < RARE)),
        Feature("mtld", "vocabulary", BOTH, "mccarthy2010",
                "measure of textual lexical diversity, threshold 0.72", mtld, levels=("document",)),
    ]

    def measure(self, sentence, lang: str) -> Pool:
        aoa = norms.load(lang)
        ws = words(sentence.span)
        p = Pool()
        content = [t for t in ws if t.pos_ in CONTENT or (t.pos_ == "PROPN" and not _proper(t))]
        ages = [a for a in (aoa.get(t.lemma_.lower(), aoa.get(t.text.lower())) for t in content) if a is not None]
        p.counts.update(content_words=len(content), aoa_found=len(ages))
        p.bags["aoa"] = ages
        p.bags["zipf"] = [zipf_frequency(t.text.lower(), lang) for t in ws if not _proper(t)]
        p.bags["tokens"] = [t.text.lower() for t in ws]
        return p
