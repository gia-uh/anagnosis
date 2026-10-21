"""The fitted lexical and syntactic scales against the classic readability formulas, with intervals by book.

Run: uv run python experiments/2026-10-21-scales-vs-formulas/run.py en|es
Reads the feature cache of experiments/2026-10-21-calibration-<lang> (run that first) and writes results-<lang>.json.
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np

from anagnosis.calibrate import fit, within_one
from anagnosis.corpora import load

# The dimensions as they were when this experiment ran.
DIMENSIONS = {
    "lexical": ["aoa_mean", "aoa_p90", "aoa_late_share", "rare_word_share",
                "letters_per_word", "syllables_per_word", "long_word_share"],
    "syntactic": ["clauses_per_sentence", "mean_dependency_distance"],
}

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
CORPORA = {"en": ["en-school-readers", "en-school-years"], "es": ["es-storyweaver", "es-cuba-grades"]}
# Each formula oriented so that a higher value means a harder text.
FORMULAS = {"en": {"flesch_kincaid_grade": 1, "flesch_reading_ease": -1},
            "es": {"fernandez_huerta": -1, "szigriszt_pazos": -1, "crawford": 1}}
FITTED = {
    **DIMENSIONS,
    "both dimensions": DIMENSIONS["lexical"] + DIMENSIONS["syntactic"],
    # The two inputs every classic formula here is built from, refitted: separates better features from fitting.
    "formula inputs, refitted": ["syllables_per_word", "words_per_sentence"],
}
FOLDS = 5
BOOT = 2000


def matrix(rows, names):
    return np.array([[np.nan if r.get(k) is None else r[k] for k in names] for r in rows], float)


def ranks(x):
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    upper = np.cumsum(counts)
    return ((upper - counts + 1 + upper) / 2)[inv]


def spearman(a, b):
    ok = ~(np.isnan(a) | np.isnan(b))
    return float(np.corrcoef(ranks(a[ok]), ranks(b[ok]))[0, 1])


def interval(stat, groups, rng):
    """95% bootstrap interval of stat(idx), resampling whole books."""
    books = np.unique(groups)
    members = {g: np.flatnonzero(groups == g) for g in books}
    vals = [stat(np.concatenate([members[g] for g in rng.choice(books, len(books))])) for _ in range(BOOT)]
    return [float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))]


def scores(m, X):
    return np.array([m.score(x) for x in np.where(np.isnan(X), m.mean, X)])


def main(lang):
    cache = ROOT / "experiments" / f"2026-10-21-calibration-{lang}" / "data"
    data = {}
    for name in CORPORA[lang]:
        c = load(ROOT / "corpora" / name)
        rows = {r["id"]: r for r in map(json.loads, open(cache / f"features-{name}.jsonl"))}
        data[name] = (c, [rows[d.id] for d in c.docs])
    names = list(data)
    corpus = np.array([n for n, (c, _) in data.items() for _ in c.docs])
    level = np.array([d.level for c, _ in data.values() for d in c.docs])
    group = np.array([f"{n}/{d.group or d.id}" for n, (c, _) in data.items() for d in c.docs])
    rows = [r for _, rs in data.values() for r in rs]
    n_levels = {n: len(c.levels) for n, (c, _) in data.items()}
    fold = np.array([zlib.crc32(g.encode()) % FOLDS for g in group])

    held, transfer, close = {}, {}, {}
    for score, feats in FITTED.items():
        X = matrix(rows, feats)
        signs = [1] * len(feats)
        s, lv = np.zeros(len(rows)), np.zeros(len(rows), int)
        for k in range(FOLDS):
            tr, te = fold != k, fold == k
            m = fit(X[tr], corpus[tr], level[tr], n_levels, signs)
            s[te] = scores(m, X[te])
            lv[te] = [m.level(x, c) for x, c in zip(np.where(np.isnan(X[te]), m.mean, X[te]), corpus[te])]
        held[score], close[score] = s, lv
        transfer[score] = {}
        for n in names:
            tr = corpus != n
            m = fit(X[tr], corpus[tr], level[tr], {k: v for k, v in n_levels.items() if k != n}, signs)
            transfer[score][n] = spearman(scores(m, X[~tr]), level[~tr].astype(float))
    for f, sign in FORMULAS[lang].items():
        held[f] = sign * matrix(rows, [f])[:, 0]
    held["text length in words"] = np.array([len(d.text.split()) for c, _ in data.values() for d in c.docs], float)

    rng = np.random.default_rng(0)
    best = {n: max(FORMULAS[lang], key=lambda f: spearman(held[f][corpus == n], level[corpus == n].astype(float)))
            for n in names}
    out = {"n": {n: int((corpus == n).sum()) for n in names}, "books": {n: len(set(group[corpus == n])) for n in names},
           "spearman": {}, "lexical_minus_best_formula": {}, "within_one": {}, "transfer": transfer}
    for score, v in held.items():
        out["spearman"][score] = {}
        for n in names:
            idx = np.flatnonzero(corpus == n)
            y = level[idx].astype(float)
            stat = lambda i, v=v[idx], y=y: spearman(v[i], y[i])
            out["spearman"][score][n] = {"value": stat(np.arange(len(idx))), "ci95": interval(stat, group[idx], rng)}
    for n in names:
        idx = np.flatnonzero(corpus == n)
        y, a, b = level[idx].astype(float), held["lexical"][idx], held[best[n]][idx]
        stat = lambda i: spearman(a[i], y[i]) - spearman(b[i], y[i])
        out["lexical_minus_best_formula"][n] = {"formula": best[n], "value": stat(np.arange(len(idx))),
                                                "ci95": interval(stat, group[idx], rng)}
        out["within_one"][n] = {s: within_one(close[s][idx], level[idx]) for s in FITTED}
        out["within_one"][n]["most frequent level"] = within_one(np.full(len(idx), np.bincount(level[idx]).argmax()),
                                                                 level[idx])
    keys = list(held)
    M = np.column_stack([held[k] for k in keys])
    ok = ~np.isnan(M).any(axis=1)
    out["correlation"] = {"order": keys, "matrix": np.round(np.corrcoef(M[ok].T), 3).tolist()}
    (HERE / f"results-{lang}.json").write_text(json.dumps(out, indent=2))
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main(sys.argv[1])
