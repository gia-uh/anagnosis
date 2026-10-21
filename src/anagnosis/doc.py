"""Segmentation: a source text becomes a Doc of paragraphs of sentences.

Markup is masked, never deleted: every markup character becomes a space, so an
offset into the masked text is an offset into the source file.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

import spacy

MODELS = {"es": "es_core_news_sm", "en": "en_core_web_sm"}

# Whole matches that are not prose.
_DROP = [
    r"(?s)\A---\n.*?\n---[ \t]*(?:\n|\Z)",  # front matter
    r"(?ms)^(```|~~~).*?^\1[^\n]*$",  # fenced code
    r"(?s)<!--.*?-->",  # HTML comments
    r"(?s)\$\$.*?\$\$",  # display math
    r"(?m)^[ \t]{0,3}#{1,6}[ \t].*$",  # headings
    r"(?m)^[ \t]*!\[.*$",  # image lines
    r"(?m)^[ \t]*\|.*$",  # table rows
    r"(?m)^[ \t]*:::.*$",  # pandoc fenced divs
    r"(?m)^[ \t]*(?:-[ \t]*){3,}$|^[ \t]*(?:\*[ \t]*){3,}$",  # horizontal rules
    r"(?m)^\[\^[^\]]+\]:.*$",  # footnote definitions
    r"\[\^[^\]]+\]",  # footnote references
    r"\{[~>][^}]*\}",  # scriptorium markers {~key} {>caption}
    r"\[>[^\]]*\]",  # scriptorium markers [>note]
    r"<[^>\n]+>",  # HTML tags
    r"`[^`\n]+`",  # inline code
    r"!\[[^\]]*\]\([^)]*\)",  # inline images
    r"\]\([^)\s]*\)",  # link targets: the "](url)" part
    r"https?://[^\s)\]>]*[^\s)\]>.,;:!?]",  # bare URLs, without trailing punctuation
    r"(?m)^[ \t]*>[ \t]?",  # blockquote markers
    r"(?m)^[ \t]*(?:[-*+]|\d+[.)])[ \t]+",  # list markers
    r"\*+",  # emphasis
    r"(?<!\w)_+|_+(?!\w)",  # emphasis with underscores
    r"\[",  # link openers
]
_DROP_RE = [re.compile(p) for p in _DROP]
_HEADING = re.compile(r"(?m)^[ \t]{0,3}(#{1,6})[ \t]+(.*)$")


def _blank(text: str, start: int, end: int) -> str:
    return text[:start] + re.sub(r"[^\n]", " ", text[start:end]) + text[end:]


def mask(text: str, exclude: list[str] | None = None) -> str:
    """Return text of the same length with Markdown markup replaced by spaces.

    exclude: patterns matched against heading titles; a matching heading masks its
    whole section, up to the next heading of the same or a higher level.
    """
    out = text
    if exclude:
        pats = [re.compile(p) for p in exclude]
        heads = list(_HEADING.finditer(text))
        for i, h in enumerate(heads):
            if any(p.search(h.group(2)) for p in pats):
                level = len(h.group(1))
                end = next((n.start() for n in heads[i + 1:] if len(n.group(1)) <= level), len(text))
                out = _blank(out, h.start(), end)
    for rx in _DROP_RE:
        for m in reversed(list(rx.finditer(out))):
            out = _blank(out, m.start(), m.end())
    return out


@lru_cache(maxsize=None)
def nlp(lang: str):
    model = spacy.load(MODELS[lang], disable=["ner"])
    model.max_length = 5_000_000
    return model


@dataclass
class Sentence:
    start: int
    end: int
    span: spacy.tokens.Span


@dataclass
class Paragraph:
    start: int
    end: int
    sentences: list[Sentence] = field(default_factory=list)


@dataclass
class Doc:
    source: str
    masked: str
    lang: str
    paragraphs: list[Paragraph]

    @property
    def sentences(self) -> list[Sentence]:
        return [s for p in self.paragraphs for s in p.sentences]


_BLOCK = re.compile(r"\S(?:.*?\S)?(?=\n[ \t]*\n|\s*\Z)", re.S)
_ITEM = re.compile(r"(?m)^[ \t]*(?:[-*+]|\d+[.)])[ \t]+")


def _blocks(source: str, masked: str) -> list[tuple[int, int]]:
    """Paragraphs are separated by blank lines; a list item always starts a new block."""
    cuts = sorted({m.end() for m in _ITEM.finditer(source)})
    out = []
    for m in _BLOCK.finditer(masked):
        edges = [m.start()] + [c for c in cuts if m.start() < c < m.end()] + [m.end()]
        for a, b in zip(edges, edges[1:]):
            seg = masked[a:b]
            if _WORD.search(seg):
                lead, trail = len(seg) - len(seg.lstrip()), len(seg) - len(seg.rstrip())
                out.append((a + lead, b - trail))
    return out
_WORD = re.compile(r"[^\W\d_]")


def segment(source: str, lang: str, exclude: list[str] | None = None) -> Doc:
    """Split source into paragraphs (blank-line separated) and sentences (spaCy)."""
    masked = mask(source, exclude)
    blocks = _blocks(source, masked)
    paragraphs = []
    for (start, end), parsed in zip(blocks, nlp(lang).pipe(masked[s:e] for s, e in blocks)):
        para = Paragraph(start, end)
        for sent in parsed.sents:
            if not _WORD.search(sent.text):
                continue
            text = sent.text
            lead = len(text) - len(text.lstrip())
            para.sentences.append(Sentence(start + sent.start_char + lead, start + sent.start_char + len(text.rstrip()), sent))
        if para.sentences:
            paragraphs.append(para)
    return Doc(source, masked, lang, paragraphs)
