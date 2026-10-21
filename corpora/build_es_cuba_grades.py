"""Build es-cuba-grades: public-domain texts read in Cuban primary and lower-secondary school, labelled by grade.

es-cuba-grades/readings.jsonl lists the readings by public-domain authors (died
before 1946, original Spanish) found in the Lengua Española and Español-
Literatura textbooks of grades 2 to 9 published by MINED (biblioteca.cubaeduca.cu),
with the grade, title, credited author and first words. The list is a
reference: the textbooks are not redistributable, so no text is taken from
them. Each text is fetched from Spanish Wikisource, found by a phrase search on
its first words, and kept only if those words appear in the fetched page.

The same text is often read in several grades ("Los zapaticos de rosa" in 3rd,
5th, 6th and 7th); its label is the earliest grade, the one where the school
first expects children to read it.

Run: python corpora/build_es_cuba_grades.py [cache dir]
"""
import html
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent / "es-cuba-grades"
API = "https://es.wikisource.org/w/api.php"
UA = {"User-Agent": "anagnosis-research/0.1 (https://github.com/gia-uh/anagnosis)"}
MAX_WORDS, MIN_WORDS = 600, 40


def api(cache: Path, **params) -> dict:
    params["format"] = "json"
    key = cache / (re.sub(r"[^\w]+", "_", json.dumps(params, sort_keys=True))[:180] + ".json")
    if not key.exists():
        time.sleep(0.5)
        with urllib.request.urlopen(urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA),
                                    timeout=60) as r:
            key.write_bytes(r.read())
    return json.loads(key.read_text())


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return " ".join(re.sub(r"[^a-zñ ]+", " ", "".join(c for c in s if not unicodedata.combining(c))).split())


def page_text(cache: Path, title: str) -> str:
    raw = api(cache, action="parse", page=title, prop="text", redirects=1)["parse"]["text"]["*"]
    raw = re.sub(r'<(div|table|span) [^>]*class="[^"]*(header|noprint|ws-noexport|reference|pagenum|mw-editsection)'
                 r'[^"]*"[^>]*>.*?</\1>', "", raw, flags=re.S)
    raw = re.sub(r"<sup.*?</sup>|<style.*?</style>", "", raw, flags=re.S)
    raw = re.sub(r"<br\s*/?>", "\n", raw)
    raw = re.sub(r"</(p|div|h\d|li|dd|tr)>", "\n\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", "", raw))
    return "\n\n".join(" ".join(p.split()) if "\n" not in p.strip() else "\n".join(l.strip() for l in p.strip().splitlines())
                       for p in re.split(r"\n\s*\n", text) if p.strip())


def by(cache: Path, title: str, author: str) -> bool:
    """The page is credited to the author: their surname is in its header template or its categories."""
    p = api(cache, action="parse", page=title, prop="wikitext|categories", redirects=1)["parse"]
    head = fold(p["wikitext"]["*"][:800] + " " + " ".join(c["*"].replace("_", " ") for c in p["categories"]))
    names = [w for w in fold(author).split() if len(w) > 3 and w not in ("jose", "maria", "miguel", "juan")]
    return any(w in head.split() for w in names)


def find(cache: Path, first_words: str, author: str) -> tuple[str, str] | None:
    """(page title, passage) by the author whose text contains the reading's first words."""
    words = fold(first_words).split()
    target = " ".join(words[:5])
    for n, start in ((6, 0), (4, 0), (4, 1), (4, 2)):
        phrase = " ".join(first_words.replace("\n", " ").split()[start:start + n]).strip("“”\"'¡¿—-–…[]() ")
        if len(phrase.split()) < 3:
            continue
        hits = api(cache, action="query", list="search", srsearch=f'"{phrase}"', srnamespace="0", srlimit=5)
        for hit in hits.get("query", {}).get("search", []):
            text = page_text(cache, hit["title"])
            folded = fold(text)
            if target in folded and by(cache, hit["title"], author):
                return hit["title"], passage(text, target)
    return None


def passage(text: str, target: str) -> str:
    """The whole text if short; otherwise MAX_WORDS words from the paragraph where the reading starts."""
    paras = text.split("\n\n")
    start = next(i for i, p in enumerate(paras) if target.split()[0] in fold(p) and target in fold(" ".join(paras[i:i + 3])))
    out, n = [], 0
    for p in paras[start:]:
        out.append(p)
        n += len(p.split())
        if n >= MAX_WORDS:
            break
    return "\n\n".join(out)


def main(cache: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    readings = [json.loads(l) for l in open(HERE / "readings.jsonl")]
    found, missing = {}, []
    for r in readings:
        hit = find(cache, r["first_words"], r["author"])
        if hit is None or len(hit[1].split()) < MIN_WORDS:
            missing.append(r)
            continue
        title, text = hit
        doc = found.setdefault(title, {"text": text, "grades": set(), "readings": r})
        doc["grades"].add(r["grade"])
    with open(HERE / "texts.jsonl", "w") as f:
        for title, d in sorted(found.items()):
            f.write(json.dumps({"id": title, "text": d["text"], "label": f"grade{min(d['grades'])}",
                                "grades": sorted(d["grades"]), "author": d["readings"]["author"],
                                "source": "https://es.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))},
                               ensure_ascii=False) + "\n")
    print(f"es-cuba-grades: {len(found)} texts from {len(readings) - len(missing)} of {len(readings)} readings")
    for r in missing:
        print(f"  not found: grade {r['grade']} · {r['author']} · {r['title']}", file=sys.stderr)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "anagnosis" / "wikisource")
