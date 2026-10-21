import io
import zipfile

import pytest

from anagnosis import norms


def _zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()


def test_parse_spanish():
    text = "word\taverageAoA\tSD\nPerro\t2.58\t1.1\nvenganza\t8.80\t1.9\nvacía\t\t0.5\n"
    blob = _zip({"SpanishAoA.txt": text.encode("utf-16")})
    assert norms.parse_spanish(blob) == {"perro": 2.58, "venganza": 8.8}


def test_parse_english_reads_shared_strings_and_numbers():
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    shared = f'<sst {ns}><si><t>Word</t></si><si><t>Rating.Mean</t></si><si><t>aardvark</t></si><si><t>dog</t></si></sst>'
    sheet = (f'<worksheet {ns}><sheetData>'
             '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="E1" t="s"><v>1</v></c></row>'
             '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>18</v></c><c r="E2"><v>9.89</v></c></row>'
             '<row r="3"><c r="A3" t="s"><v>3</v></c><c r="E3"><v>2.5</v></c></row>'
             '<row r="4"><c r="A4" t="inlineStr"><is><t>zzz</t></is></c><c r="E4" t="s"><v>0</v></c></row>'
             '</sheetData></worksheet>')
    blob = _zip({"xl/sharedStrings.xml": shared, "xl/worksheets/sheet1.xml": sheet})
    assert norms.parse_english(blob) == {"aardvark": 9.89, "dog": 2.5}


def test_load_names_the_command_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("ANAGNOSIS_CACHE", str(tmp_path))
    norms.load.cache_clear()
    with pytest.raises(FileNotFoundError, match="anagnosis fetch-norms"):
        norms.load("es")


def test_load_reads_the_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("ANAGNOSIS_CACHE", str(tmp_path))
    norms.load.cache_clear()
    (tmp_path / "aoa-es.tsv").write_text("perro\t2.58\n")
    assert norms.load("es") == {"perro": 2.58}
    norms.load.cache_clear()
