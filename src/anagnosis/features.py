"""Feature registry and pooling.

An extractor turns each sentence into a Pool: additive counts and ordered bags.
A paragraph or a document pools its sentences, then every feature is computed
from the pool. A ratio at paragraph level is therefore a pooled ratio (total
syllables over total words), never a mean of sentence ratios.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Protocol

from .doc import Doc

LEVELS = ("sentence", "paragraph", "document")


@dataclass
class Pool:
    counts: Counter = field(default_factory=Counter)
    bags: dict[str, list] = field(default_factory=dict)


def pool(pools: list[Pool]) -> Pool:
    out = Pool()
    for p in pools:
        out.counts.update(p.counts)
        for k, v in p.bags.items():
            out.bags.setdefault(k, []).extend(v)
    return out


@dataclass(frozen=True)
class Feature:
    name: str
    family: str
    languages: frozenset[str]
    source: str  # key in research/references.bib, or "anagnosis" for our own definitions
    doc: str
    compute: Callable[[Pool], float | None]
    levels: tuple[str, ...] = LEVELS


class Extractor(Protocol):
    family: str
    features: list[Feature]

    def measure(self, sentence, lang: str) -> Pool: ...


def ratio(num: str, den: str, scale: float = 1.0) -> Callable[[Pool], float | None]:
    def f(p: Pool) -> float | None:
        return scale * p.counts[num] / p.counts[den] if p.counts[den] else None
    return f


def table(doc: Doc, extractors: list[Extractor], level: str) -> list[dict]:
    """One row per unit at the given level, with its source offsets and every feature that applies."""
    feats = [f for e in extractors for f in e.features if doc.lang in f.languages and level in f.levels]
    sent_pools = {id(s): pool([e.measure(s, doc.lang) for e in extractors]) for s in doc.sentences}
    if level == "sentence":
        units = [(s.start, s.end, sent_pools[id(s)]) for s in doc.sentences]
    elif level == "paragraph":
        units = [(p.start, p.end, pool([sent_pools[id(s)] for s in p.sentences])) for p in doc.paragraphs]
    elif level == "document":
        sents = doc.sentences
        units = [(sents[0].start, sents[-1].end, pool(list(sent_pools.values())))] if sents else []
    else:
        raise ValueError(f"level must be one of {LEVELS}")
    return [{"level": level, "index": i, "start": a, "end": b, **{f.name: f.compute(p) for f in feats}}
            for i, (a, b, p) in enumerate(units)]
