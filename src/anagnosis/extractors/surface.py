"""Surface features: lengths of words and sentences, and the classic readability formulas."""
from ..features import Feature, Pool, ratio
from ..lang import SYLLABLES
from .words import words

ES, EN, BOTH = frozenset({"es"}), frozenset({"en"}), frozenset({"es", "en"})
LONG = 6  # a long word has more than six letters (Björnsson's LIX threshold)


def _wps(p: Pool):
    return p.counts["words"] / p.counts["sentences"] if p.counts["sentences"] else None


def _spw(p: Pool):
    return p.counts["syllables"] / p.counts["words"] if p.counts["words"] else None


def _formula(f):
    def g(p: Pool):
        if not p.counts["words"] or not p.counts["sentences"]:
            return None
        return f(_wps(p), _spw(p), p)
    return g


class Surface:
    family = "surface"
    features = [
        Feature("words_per_sentence", "surface", BOTH, "anagnosis", "words over sentences", ratio("words", "sentences")),
        Feature("syllables_per_word", "surface", BOTH, "anagnosis", "syllables over words", ratio("syllables", "words")),
        Feature("letters_per_word", "surface", BOTH, "anagnosis", "letters over words", ratio("letters", "words")),
        Feature("long_word_share", "surface", BOTH, "bjornsson1968", "share of words with more than six letters", ratio("long_words", "words")),
        Feature("fernandez_huerta", "surface", ES, "fernandezhuerta1959",
                "206.84 - 60 x syllables/word - 1.02 x words/sentence; higher is easier",
                _formula(lambda wps, spw, p: 206.84 - 60 * spw - 1.02 * wps)),
        Feature("szigriszt_pazos", "surface", ES, "szigriszt1993",
                "perspicuity, 206.835 - 62.3 x syllables/word - words/sentence; read on the INFLESZ scale",
                _formula(lambda wps, spw, p: 206.835 - 62.3 * spw - wps)),
        Feature("crawford", "surface", ES, "crawford1984",
                "school grade, -0.205 x sentences/100 words + 0.049 x syllables/100 words - 3.407; valid for grades 1-6",
                _formula(lambda wps, spw, p: -0.205 * 100 / wps + 0.049 * 100 * spw - 3.407)),
        Feature("flesch_reading_ease", "surface", EN, "flesch1948",
                "206.835 - 1.015 x words/sentence - 84.6 x syllables/word; higher is easier",
                _formula(lambda wps, spw, p: 206.835 - 1.015 * wps - 84.6 * spw)),
        Feature("flesch_kincaid_grade", "surface", EN, "kincaid1975",
                "US grade, 0.39 x words/sentence + 11.8 x syllables/word - 15.59",
                _formula(lambda wps, spw, p: 0.39 * wps + 11.8 * spw - 15.59)),
    ]

    def measure(self, sentence, lang: str) -> Pool:
        ws = [t.text for t in words(sentence.span)]
        syl = SYLLABLES[lang]
        p = Pool()
        p.counts.update(
            sentences=1,
            words=len(ws),
            syllables=sum(syl(w) for w in ws),
            letters=sum(len(w) for w in ws),
            long_words=sum(len(w) > LONG for w in ws),
        )
        return p
