"""Age-of-acquisition norms: downloaded from the publisher into a local cache, never committed.

Spanish: Alonso, Fernández and Díez (2015), 7,039 words rated in years on a 1-11
scale, where 1 means before age 2 and 11 means 11 or older. CC BY-NC-ND.
English: Kuperman, Stadthagen-Gonzalez and Brysbaert (2012), about 30,000 words
rated in years. Published as supplementary material without a license.
"""
from __future__ import annotations

import io
import os
import re
import urllib.request
import zipfile
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree

_ESM = "https://media.springernature.com/original/springer-static/esm/art%3A10.3758%2F{doi}/MediaObjects/{name}"
SOURCES = {
    "es": _ESM.format(doi="s13428-014-0454-2", name="13428_2014_454_MOESM1_ESM.zip"),
    "en": _ESM.format(doi="s13428-013-0348-8", name="13428_2013_348_MOESM1_ESM.xlsx"),
}


def cache_dir() -> Path:
    return Path(os.environ.get("ANAGNOSIS_CACHE", Path.home() / ".cache" / "anagnosis"))


def parse_spanish(blob: bytes) -> dict[str, float]:
    """SpanishAoA.txt inside the zip: UTF-16, tab-separated, word then mean rating."""
    text = zipfile.ZipFile(io.BytesIO(blob)).read("SpanishAoA.txt").decode("utf-16")
    out = {}
    for line in text.splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) > 1 and cols[1].strip():
            out[cols[0].strip().lower()] = float(cols[1])
    return out


_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _xlsx_rows(blob: bytes) -> list[dict[str, str]]:
    """Rows of the first sheet as {column letter: value}, read with zipfile and xml only."""
    z = zipfile.ZipFile(io.BytesIO(blob))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ElementTree.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", _NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
    sheet = ElementTree.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.iter(f"{{{_NS['m']}}}row"):
        cells = {}
        for c in row.findall("m:c", _NS):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            if c.get("t") == "inlineStr":
                cells[col] = "".join(t.text or "" for t in c.iter(f"{{{_NS['m']}}}t"))
                continue
            v = c.find("m:v", _NS)
            if v is not None:
                cells[col] = shared[int(v.text)] if c.get("t") == "s" else v.text
        rows.append(cells)
    return rows


def parse_english(blob: bytes) -> dict[str, float]:
    """Columns Word, OccurTotal, OccurNum, Freq_pm, Rating.Mean, ...: word in A, rating in E."""
    out = {}
    for cells in _xlsx_rows(blob)[1:]:
        word, rating = cells.get("A"), cells.get("E")
        try:
            out[str(word).strip().lower()] = float(rating)
        except (TypeError, ValueError):
            continue
    return out


PARSERS = {"es": parse_spanish, "en": parse_english}


def fetch(langs=("es", "en")) -> dict[str, int]:
    """Download, parse and write aoa-{lang}.tsv into the cache. Returns words per language."""
    cache_dir().mkdir(parents=True, exist_ok=True)
    counts = {}
    for lang in langs:
        req = urllib.request.Request(SOURCES[lang], headers={"User-Agent": "anagnosis"})
        with urllib.request.urlopen(req, timeout=120) as r:
            norms = PARSERS[lang](r.read())
        with open(cache_dir() / f"aoa-{lang}.tsv", "w") as f:
            f.writelines(f"{w}\t{a:.2f}\n" for w, a in sorted(norms.items()))
        counts[lang] = len(norms)
    return counts


@lru_cache(maxsize=None)
def load(lang: str) -> dict[str, float]:
    path = cache_dir() / f"aoa-{lang}.tsv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run `anagnosis fetch-norms` first")
    return {w: float(a) for w, a in (line.rstrip("\n").split("\t") for line in open(path))}
