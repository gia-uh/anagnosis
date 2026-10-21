"""Per-language rules, keyed by ISO 639-1 code."""
from . import en, es

SYLLABLES = {"es": es.syllables, "en": en.syllables}
