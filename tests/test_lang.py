import pytest

from anagnosis.lang import SYLLABLES

ES = {
    "perrito": 3, "cariño": 3, "guerra": 2, "queso": 2, "país": 2, "ciudad": 2, "rey": 1,
    "poeta": 3, "aéreo": 4, "huevo": 2, "y": 1, "Troya": 2, "hoy": 1, "muy": 1,
    "pingüino": 3, "Perséfone": 4, "Odiseo": 4, "maíz": 2, "leía": 3, "construir": 2,
    "océano": 4, "Zeus": 1, "héroe": 3, "guitarra": 3, "averigüéis": 4, "buey": 1,
}
EN = {"the": 1, "water": 2, "beautiful": 3, "computation": 4, "machine": 2, "elephant": 3,
      "language": 2, "simple": 2, "created": 3, "a": 1}


@pytest.mark.parametrize("word,n", ES.items())
def test_spanish(word, n):
    assert SYLLABLES["es"](word) == n


@pytest.mark.parametrize("word,n", EN.items())
def test_english(word, n):
    assert SYLLABLES["en"](word) == n


def test_english_fallback_for_unknown_word():
    assert SYLLABLES["en"]("blorptastic") == 3
