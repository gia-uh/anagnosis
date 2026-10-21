import json

from anagnosis.cli import main

FIXTURE = "tests/fixtures/easy-es.md"


def test_sentence_rows_carry_offsets_and_text(tiny_norms, capsys):
    assert main(["measure", FIXTURE, "--lang", "es", "--level", "sentence", "--format", "jsonl",
                 "--exclude-heading", "Para padres"]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [r["text"] for r in rows] == ["El perro come pan.", "La niña lee un libro.", "El gato duerme."]
    source = open(FIXTURE, encoding="utf-8").read()
    assert all(source[r["start"]:r["end"]] == r["text"] for r in rows)


def test_summary_over_documents(tiny_norms, capsys):
    assert main(["measure", FIXTURE, FIXTURE, "--lang", "es", "--summary"]) == 0
    s = json.loads(capsys.readouterr().out)
    assert s["words_per_sentence"]["n"] == 2
    assert s["words_per_sentence"]["median"] == s["words_per_sentence"]["q1"]


def test_missing_norms_exit_2(tmp_path, monkeypatch, capsys):
    from anagnosis import norms
    monkeypatch.setenv("ANAGNOSIS_CACHE", str(tmp_path))
    norms.load.cache_clear()
    assert main(["measure", FIXTURE, "--lang", "es"]) == 2
    assert "fetch-norms" in capsys.readouterr().err


def test_features_lists_the_registry(capsys):
    assert main(["features"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert any(l.startswith("crawford\tsurface\tes\t") for l in lines)
    assert len(lines) == 18
