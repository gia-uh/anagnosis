from anagnosis.doc import mask, segment

SOURCE = """---
title: Prueba
---

# El viaje

Odiseo **volvió** a [Ítaca](https://example.org) después de veinte años. Nadie lo reconoció.

![Un barco](barco.png)

Su perro Argos sí lo reconoció{~argos}. Movió la cola y murió.

```python
print("no es prosa")
```

| a | b |
|---|---|

## Para padres

Este texto no es para niños.

## Después

Penélope esperaba.
"""


def test_mask_keeps_length_and_lines():
    out = mask(SOURCE)
    assert len(out) == len(SOURCE)
    assert out.count("\n") == SOURCE.count("\n")


def test_mask_removes_markup_and_keeps_words():
    out = mask(SOURCE)
    for gone in ["title", "**", "https", "](", "barco.png", "{~argos}", "print", "| a |", "# El viaje"]:
        assert gone not in out
    for kept in ["volvió", "Ítaca", "Argos", "Penélope"]:
        assert kept in out


def test_exclude_masks_the_section_up_to_the_next_heading_of_same_level():
    out = mask(SOURCE, exclude=["Para padres"])
    assert "no es para niños" not in out
    assert "Penélope esperaba" in out


def test_offsets_point_into_the_source():
    doc = segment(SOURCE, "es")
    for s in doc.sentences:
        assert doc.masked[s.start:s.end] == s.span.text.strip()


def test_paragraphs_and_sentences():
    doc = segment(SOURCE, "es", exclude=["Para padres"])
    texts = [[SOURCE[s.start:s.end] for s in p.sentences] for p in doc.paragraphs]
    assert texts[0][0].startswith("Odiseo **volvió**")
    assert texts[0][1] == "Nadie lo reconoció."
    assert texts[1][1] == "Movió la cola y murió."
    assert texts[-1] == ["Penélope esperaba."]
    assert len(doc.paragraphs) == 3


def test_text_without_words_yields_no_paragraphs():
    assert segment("---\n\n***\n", "es").paragraphs == []
