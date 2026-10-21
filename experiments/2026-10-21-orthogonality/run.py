"""Bring the lexical~syntactic correlation below 0.5: drop shared features, or residualize.

Run: uv run python experiments/2026-10-21-orthogonality/run.py en|es
Reads the feature cache of experiments/2026-10-21-calibration-<lang> (run that first) and writes results-<lang>.json.
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np

from anagnosis.calibrate import fit, spearman
from anagnosis.corpora import load

# The dimensions as they were when this experiment ran; anagnosis.calibrate.DIMENSIONS has moved on since.
DIMENSIONS = {
    "lexical": ["aoa_mean", "aoa_p90", "aoa_late_share", "rare_word_share",
                "letters_per_word", "syllables_per_word", "long_word_share"],
    "syntactic": ["words_per_sentence", "clauses_per_sentence", "mean_dependency_distance", "mean_tree_depth"],
}

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
CORPORA = {"en": ["en-school-readers", "en-school-years"], "es": ["es-storyweaver", "es-cuba-grades"]}
FOLDS = 5
LEX, SYN = DIMENSIONS["lexical"], DIMENSIONS["syntactic"]
WORD_LENGTH = ["letters_per_word", "syllables_per_word", "long_word_share"]
SENTENCE_LENGTH = ["words_per_sentence", "mean_tree_depth"]
VARIANTS = {
    "baseline": (LEX, SYN, False),
    "lexical without word length": ([f for f in LEX if f not in WORD_LENGTH], SYN, False),
    "syntactic without sentence length": (LEX, [f for f in SYN if f not in SENTENCE_LENGTH], False),
    "both dropped": ([f for f in LEX if f not in WORD_LENGTH], [f for f in SYN if f not in SENTENCE_LENGTH], False),
    "syntactic residualized on lexical": (LEX, SYN, True),
}


def matrix(rows, names):
    return np.array([[np.nan if r.get(k) is None else r[k] for k in names] for r in rows], float)


def scores(m, X):
    return np.array([m.score(x) for x in np.where(np.isnan(X), m.mean, X)])


def within_level(a, b, corpus, level):
    """Correlation of a and b after removing each (corpus, level) mean: what they share beyond the label."""
    a, b = a.copy(), b.copy()
    for key in set(zip(corpus, level)):
        idx = (corpus == key[0]) & (level == key[1])
        a[idx] -= a[idx].mean()
        b[idx] -= b[idx].mean()
    return float(np.corrcoef(a, b)[0, 1])


def main(lang):
    cache = ROOT / "experiments" / f"2026-10-21-calibration-{lang}" / "data"
    data = {}
    for name in CORPORA[lang]:
        c = load(ROOT / "corpora" / name)
        rows = {r["id"]: r for r in map(json.loads, open(cache / f"features-{name}.jsonl"))}
        data[name] = (c, [rows[d.id] for d in c.docs])
    corpus = np.array([n for n, (c, _) in data.items() for _ in c.docs])
    level = np.array([d.level for c, _ in data.values() for d in c.docs])
    group = np.array([f"{n}/{d.group or d.id}" for n, (c, _) in data.items() for d in c.docs])
    rows = [r for _, rs in data.values() for r in rs]
    n_levels = {n: len(c.levels) for n, (c, _) in data.items()}
    fold = np.array([zlib.crc32(g.encode()) % FOLDS for g in group])

    out = {}
    for variant, (lex, syn, resid) in VARIANTS.items():
        XL, XS = matrix(rows, lex), matrix(rows, syn)
        oof = {"lexical": np.zeros(len(rows)), "syntactic": np.zeros(len(rows))}
        for k in range(FOLDS):
            tr, te = fold != k, fold == k
            ml = fit(XL[tr], corpus[tr], level[tr], n_levels, [1] * len(lex))
            ms = fit(XS[tr], corpus[tr], level[tr], n_levels, [1] * len(syn))
            sl, ss = scores(ml, XL), scores(ms, XS)
            if resid:  # slope and intercept come from the training fold only
                b, a = np.polyfit(sl[tr], ss[tr], 1)
                ss = ss - (a + b * sl)
            oof["lexical"][te], oof["syntactic"][te] = sl[te], ss[te]
        res = {"correlation": float(np.corrcoef(oof["lexical"], oof["syntactic"])[0, 1]),
               "correlation_within_level": within_level(oof["lexical"], oof["syntactic"], corpus, level)}
        for dim in oof:
            res[dim] = {n: spearman(oof[dim][corpus == n], level[corpus == n]) for n in data}
        out[variant] = res
    (HERE / f"results-{lang}.json").write_text(json.dumps(out, indent=2))
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main(sys.argv[1])
