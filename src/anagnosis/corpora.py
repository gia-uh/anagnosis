"""Calibration corpora: a directory with corpus.yaml and texts.jsonl.

corpus.yaml declares name, source, license, citation, lang and the label scale
(type, ordered levels, and optionally the reading age of each level). Each line
of texts.jsonl is one document: id, text, label (one of the levels) and an
optional group (the book or series it comes from, so a split never puts parts
of one book on both sides).

Only CC BY and public-domain corpora load: everything in corpora/ must be
redistributable under CC BY 4.0, and no result may depend on a corpus that is
not.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

OPEN_LICENSES = frozenset({"CC-BY-4.0", "CC-BY-3.0", "CC-BY-2.0", "CC0-1.0", "public-domain"})


class LicenseError(ValueError):
    pass


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    level: int
    group: str | None = None


@dataclass
class Corpus:
    name: str
    source: str
    license: str
    citation: str
    lang: str
    label_type: str
    levels: list[str]
    ages: list[float] | None = None
    docs: list[Document] = field(default_factory=list)

    def age_of(self, level: int) -> float | None:
        return self.ages[level] if self.ages else None


def load(path) -> Corpus:
    path = Path(path)
    meta = yaml.safe_load((path / "corpus.yaml").read_text())
    if meta["license"] not in OPEN_LICENSES:
        raise LicenseError(f"{meta['name']}: license {meta['license']} is not CC BY or public domain")
    label = meta["label"]
    levels = list(label["levels"])
    c = Corpus(name=meta["name"], source=meta["source"], license=meta["license"], citation=meta["citation"],
               lang=meta["lang"], label_type=label["type"], levels=levels, ages=label.get("ages"))
    index = {lv: i for i, lv in enumerate(levels)}
    for line in (path / "texts.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["label"] not in index:
            raise ValueError(f"{c.name}/{r['id']}: label {r['label']} is not one of {levels}")
        c.docs.append(Document(r["id"], r["text"], index[r["label"]], r.get("group")))
    return c
