import pytest

from anagnosis import norms

# Ages chosen by hand for the fixtures; not the published norms.
TINY = {
    "es": {"niña": 2.0, "leer": 4.5, "libro": 3.0, "perro": 2.58, "comer": 3.0, "pan": 2.0, "jurisprudencia": 11.0, "interpretar": 9.5, "norma": 8.0},
    "en": {"dog": 2.5, "eat": 2.2, "bread": 3.1, "jurisprudence": 13.0, "interpret": 10.5, "statute": 12.0},
}


@pytest.fixture
def tiny_norms(tmp_path, monkeypatch):
    monkeypatch.setenv("ANAGNOSIS_CACHE", str(tmp_path))
    for lang, d in TINY.items():
        (tmp_path / f"aoa-{lang}.tsv").write_text("".join(f"{w}\t{a}\n" for w, a in d.items()))
    norms.load.cache_clear()
    yield
    norms.load.cache_clear()
