"""Build en-school-readers and en-school-years from public-domain school readers on Project Gutenberg.

en-school-readers: readers numbered within a series (First Reader ... Seventh
Reader); the label is the number, which orders difficulty inside a series but is
not a grade (McGuffey's Sixth is high-school reading), so it carries no ages.
en-school-years: readers whose title states the school year or grade; the label
is that year and the age is year + 5.5, the middle of a US school year.

Only lesson prose is kept: the text before the first lesson (elocution
treatises in the upper readers), prefaces to teachers, transcriber's notes,
author biographies, word lists, definitions, notes, exercises and illustration
captions are dropped. Each book is cut into passages of about
PASSAGE words at paragraph boundaries, and at most PER_BOOK passages, evenly
spaced, are kept so that long books do not dominate.

Run: python corpora/build_en_readers.py [download dir]
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

PASSAGE, PER_BOOK = 200, 40
HERE = Path(__file__).parent
URL = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"

READERS = {  # Gutenberg id: (series, number)
    14640: ("McGuffey", 1), 14668: ("McGuffey", 2), 14766: ("McGuffey", 3), 14880: ("McGuffey", 4),
    15040: ("McGuffey", 5), 16751: ("McGuffey", 6), 13853: ("New National", 1), 15825: ("New National", 4),
    16936: ("Parker", 2), 15659: ("Beacon", 2), 15170: ("Child's World", 3), 6685: ("Story Hour", 3),
    18561: ("Ontario", 3), 18702: ("Ontario", 4), 10811: ("De La Salle", 5), 9106: ("Elson", 5),
    19721: ("Literary World", 7),
}
YEARS = {  # Gutenberg id: school year stated in the title
    41243: 1, 40774: 3, 10541: 4, 7425: 4, 43336: 4, 60409: 4, 53732: 5,
}
START = {16751: "I. ANECDOTE OF THE DUKE OF NEWCASTLE."}  # first selection, after a 70-page elocution treatise
ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]

LESSON = re.compile(r"^\s*(LESSON|Lesson)\s+([IVXL]+|\d+)\b", re.M)
DROP = re.compile(r"^\s*(\[Illustration|DEFINITIONS|Definitions|NOTES?\b|Notes?\.|EXERCISES?|Exercises?\b|REMARKS?|"
                  r"RULES?\b|EXAMPLES?|QUESTIONS?|Questions?\b|SPELLING|Spelling|VOCABULARY|LANGUAGE LESSON|"
                  r"[A-Z][A-Z ]+\.?\s*--|[A-Z][a-z]+\.\s*--)")
META = re.compile(r"\b(pupils?|teachers?|series|selections|lessons|exercises|edition|publishers?|readers)\b", re.I)
NOTE = re.compile(r"^\s*[\[(]|Transcriber|\(b\. \d{4}|\bb\. \d{4}|\bd\. \d{4}")
PAGE = re.compile(r"\b[A-Z][A-Z' ]*(READER|BOOK)\.? \d+\b|\b\d+ [A-Z][A-Z' ]*(READER|BOOK)\b\.?")
INSTRUCTION = re.compile(r"\b(this|the) (lesson|selection|stanza)s? (should|is|may)|\bpupils?\b|\binflect|\bemphasis\b|\bemphatic\b|\bstanzas?\b|^(Notice|Mark|Find|Tell|Point out) |[A-Z][a-z]+( [A-Z][a-z]+)?\.--")
END = re.compile(r"^\s*(INDEX|VOCABULARY|GLOSSARY|WORD LIST|PRONOUNCING)\b.*$", re.M)


def body(raw: str, gid: int) -> str:
    raw = raw.replace("\r\n", "\n")
    start, end = raw.find("*** START"), raw.find("*** END")
    text = raw[raw.index("\n", start) + 1:end if end > 0 else None]
    m = LESSON.search(text)
    if gid in START:
        text = text[text.index(START[gid]):]
    elif m and m.start() < 0.4 * len(text):
        text = text[m.start():]
    tail = [e for e in END.finditer(text) if e.start() > 0.8 * len(text)]
    return text[:tail[0].start()] if tail else text


HEADING = re.compile(r"^[ \t]*([A-Z][A-Z .,;:'-]{3,70})[ \t]*$", re.M)
TEACHER = re.compile(r"PREFACE|CONTENTS|INTRODUCT|SUGGESTION|PRONUNCIATION|VOWELS|CONSONANTS|DIPHTHONGS|DEFINITIONS|"
                     r"RULES|PHONIC|EQUIVALENTS|ACKNOWLEDG|ARTICULATION|INFLECTION|ACCENT|EMPHASIS|MODULATION|PAUSES|"
                     r"ASPIRATE|SUBSTITUTES|EXAMPLES|CORRECT|PRELIMINARY|TRANSCRIBER|NOTES?\b|ELOCUTION|SUBJECT|"
                     r"GEOGRAPHICAL|PROPER NAMES|TO THE TEACHER|ILLUSTRATIONS|INDEX|VOCABULARY|GLOSSARY|SERIES|EDITION")


def sections(text: str) -> list[str]:
    """Drop every section whose heading names teacher's matter (preface, contents, elocution rules, word lists)."""
    marks = list(HEADING.finditer(text))
    keep = [text[:marks[0].start()]] if marks else [text]
    for m, nxt in zip(marks, marks[1:] + [None]):
        if not TEACHER.search(m.group(1)):
            keep.append(text[m.end():nxt.start() if nxt else None])
    return keep


def prose(text: str) -> list[str]:
    out = []
    for para in (q for sec in sections(text) for q in re.split(r"\n\s*\n", sec)):
        p = PAGE.sub(" ", " ".join(para.split()))
        p = re.sub(r"^\d+\.\s+", "", p.strip())  # paragraph numbers
        words = p.split()
        if len(words) < 8 or DROP.match(para) or not re.search(r"[.!?][\"')\]]*$", p):
            continue
        if sum(w.isupper() and len(w) > 1 for w in words) > len(words) / 3:  # headings and title runs
            continue
        if INSTRUCTION.search(p) or NOTE.search(p) or len(set(m.lower() for m in META.findall(p))) >= 2:  # notes, biographies, prefaces
            continue
        out.append(p)
    return out


def passages(paras: list[str]) -> list[str]:
    out, cur = [], []
    for p in paras:
        cur.append(p)
        if sum(len(q.split()) for q in cur) >= PASSAGE:
            out.append("\n\n".join(cur))
            cur = []
    if len(out) > PER_BOOK:
        step = len(out) / PER_BOOK
        out = [out[int(i * step)] for i in range(PER_BOOK)]
    return out


def fetch(gid: int, cache: Path) -> str:
    path = cache / f"{gid}.txt"
    if not path.exists():
        with urllib.request.urlopen(urllib.request.Request(URL.format(id=gid), headers={"User-Agent": "anagnosis"})) as r:
            path.write_bytes(r.read())
        time.sleep(1)
    return path.read_text(encoding="utf-8")


def write(name: str, records: list[dict]) -> int:
    with open(HERE / name / "texts.jsonl", "w") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    return len(records)


def main(cache: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    readers, years = [], []
    for gid, (series, n) in READERS.items():
        for i, t in enumerate(passages(prose(body(fetch(gid, cache), gid)))):
            readers.append({"id": f"pg{gid}-{i:03d}", "text": t, "label": ORDINALS[n - 1], "group": f"pg{gid}",
                            "series": series})
    for gid, year in YEARS.items():
        for i, t in enumerate(passages(prose(body(fetch(gid, cache), gid)))):
            years.append({"id": f"pg{gid}-{i:03d}", "text": t, "label": f"year{year}", "group": f"pg{gid}"})
    print(f"en-school-readers: {write('en-school-readers', readers)} passages")
    print(f"en-school-years: {write('en-school-years', years)} passages")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "anagnosis" / "gutenberg")
