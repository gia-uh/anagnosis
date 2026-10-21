import pytest

from anagnosis.doc import segment
from anagnosis.extractors import ALL
from anagnosis.extractors.vocabulary import mtld
from anagnosis.features import Pool, table


def doc_row(text, lang, level="document"):
    return table(segment(text, lang), ALL, level)[0]


# Hand-computed: "El perro come pan." has 4 words, 1+2+2+1 = 6 syllables, 14 letters, no long word.
def test_surface_spanish_by_hand(tiny_norms):
    r = doc_row("El perro come pan.", "es")
    assert r["words_per_sentence"] == 4
    assert r["syllables_per_word"] == 1.5
    assert r["letters_per_word"] == 3.5
    assert r["long_word_share"] == 0
    assert r["fernandez_huerta"] == pytest.approx(206.84 - 60 * 1.5 - 1.02 * 4)  # 112.76
    assert r["szigriszt_pazos"] == pytest.approx(206.835 - 62.3 * 1.5 - 4)  # 109.385
    assert r["crawford"] == pytest.approx(-0.205 * 25 + 0.049 * 150 - 3.407)  # -1.182
    assert "flesch_kincaid_grade" not in r


# "The dog eats bread." has 4 words and 1+1+1+1 = 4 syllables in CMUdict.
def test_surface_english_by_hand(tiny_norms):
    r = doc_row("The dog eats bread.", "en")
    assert r["syllables_per_word"] == 1.0
    assert r["flesch_reading_ease"] == pytest.approx(206.835 - 1.015 * 4 - 84.6 * 1.0)
    assert r["flesch_kincaid_grade"] == pytest.approx(0.39 * 4 + 11.8 * 1.0 - 15.59)
    assert "crawford" not in r


# Content words niña, lee (lemma leer), libro: ages 2.0, 4.5, 3.0.
def test_vocabulary_spanish_by_hand(tiny_norms):
    r = doc_row("La niña lee un libro.", "es")
    assert r["aoa_mean"] == pytest.approx((2.0 + 4.5 + 3.0) / 3)
    assert r["aoa_p90"] == 4.5  # nearest rank: ceil(0.9 * 3) = 3rd of [2.0, 3.0, 4.5]
    assert r["aoa_late_share"] == 0
    assert r["aoa_coverage"] == 1.0


def test_mtld_by_hand():
    # forward a b a b: TTR falls to 2/3 at the third token -> one factor, then "b" leaves a remainder of TTR 1 -> 0 more.
    assert mtld(Pool(bags={"tokens": list("abab")})) == 4.0


# El -> perro -> come <- pan: distances 1, 1, 1; the longest path to the root is El -> perro -> come.
def test_syntax_by_hand(tiny_norms):
    r = doc_row("El perro come pan.", "es")
    assert r["mean_dependency_distance"] == 1.0
    assert r["mean_tree_depth"] == 2
    assert r["clauses_per_sentence"] == 0


def test_clauses_counted(tiny_norms):
    r = doc_row("Cuando Odiseo volvió a casa, los pretendientes que comían su pan no lo reconocieron.", "es")
    assert r["clauses_per_sentence"] == 2  # advcl "volvió", acl "comían"


EASY = {
    "es": "El perro come pan. El perro juega. Luego el perro duerme en casa.",
    "en": "The dog eats bread. The dog plays. Then the dog sleeps at home.",
}
HARD = {
    "es": ("La jurisprudencia que los tribunales superiores consolidaron durante décadas obliga a interpretar "
           "cada norma conforme a principios constitucionales que, aunque no siempre resultan explícitos, "
           "condicionan su aplicación administrativa."),
    "en": ("The jurisprudence that appellate courts consolidated over decades obliges practitioners to interpret "
           "each statute according to constitutional principles which, although they are not always explicit, "
           "constrain its administrative application."),
}
HARDER = ["words_per_sentence", "syllables_per_word", "letters_per_word", "long_word_share", "aoa_mean",
          "aoa_p90", "clauses_per_sentence", "mean_dependency_distance", "mean_tree_depth", "rare_word_share"]


@pytest.mark.parametrize("lang", ["es", "en"])
@pytest.mark.parametrize("name", HARDER)
def test_discrimination_harder_is_higher(tiny_norms, lang, name):
    assert doc_row(HARD[lang], lang)[name] > doc_row(EASY[lang], lang)[name]


@pytest.mark.parametrize("lang,name", [("es", "fernandez_huerta"), ("es", "szigriszt_pazos"), ("en", "flesch_reading_ease")])
def test_discrimination_ease_scores_are_lower_for_harder(tiny_norms, lang, name):
    assert doc_row(HARD[lang], lang)[name] < doc_row(EASY[lang], lang)[name]


@pytest.mark.parametrize("lang,name", [("es", "crawford"), ("en", "flesch_kincaid_grade")])
def test_discrimination_grades_are_higher_for_harder(tiny_norms, lang, name):
    assert doc_row(HARD[lang], lang)[name] > doc_row(EASY[lang], lang)[name]


def test_levels(tiny_norms):
    d = segment("El perro come pan. El gato duerme.\n\nLa casa es grande.", "es")
    assert len(table(d, ALL, "sentence")) == 3
    assert len(table(d, ALL, "paragraph")) == 2
    doc = table(d, ALL, "document")
    assert len(doc) == 1 and doc[0]["mtld"] is not None
    assert "mtld" not in table(d, ALL, "sentence")[0]
