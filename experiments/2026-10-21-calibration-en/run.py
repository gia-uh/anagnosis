"""First joint calibration of the lexical and syntactic dimensions on the English school-reader corpora.

Run: uv run python experiments/2026-10-21-calibration-en/run.py
Writes data/features-<corpus>.jsonl (cached) and results.json, and prints the tables in README.md.
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np

from anagnosis.calibrate import fit, spearman, within_one
from anagnosis.corpora import load
from anagnosis.doc import segment
from anagnosis.extractors import ALL
from anagnosis.features import table

# The dimensions as they were when this experiment ran; anagnosis.calibrate.DIMENSIONS has moved on since.
DIMENSIONS = {
    "lexical": ["aoa_mean", "aoa_p90", "aoa_late_share", "rare_word_share",
                "letters_per_word", "syllables_per_word", "long_word_share"],
    "syntactic": ["words_per_sentence", "clauses_per_sentence", "mean_dependency_distance", "mean_tree_depth"],
}

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
CORPORA = ["en-school-readers", "en-school-years"]
FORMULAS = ["flesch_kincaid_grade", "flesch_reading_ease"]
FOLDS = 5


def features(name):
    path = HERE / "data" / f"features-{name}.jsonl"
    c = load(ROOT / "corpora" / name)
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            for d in c.docs:
                row = table(segment(d.text, c.lang, []), ALL, "document")[0]
                f.write(json.dumps({"id": d.id, **row}) + "\n")
    rows = {r["id"]: r for r in map(json.loads, open(path))}
    return c, [rows[d.id] for d in c.docs]


def matrix(rows, names):
    return np.array([[np.nan if r.get(k) is None else r[k] for k in names] for r in rows], float)


def main():
    data = {name: features(name) for name in CORPORA}
    corpus = np.array([n for n, (c, _) in data.items() for _ in c.docs])
    level = np.array([d.level for c, _ in data.values() for d in c.docs])
    group = np.array([f"{n}/{d.group}" for n, (c, _) in data.items() for d in c.docs])
    rows = [r for _, rs in data.values() for r in rs]
    n_levels = {n: len(c.levels) for n, (c, _) in data.items()}
    ages = {n: c.ages for n, (c, _) in data.items() if c.ages}
    fold = np.array([zlib.crc32(g.encode()) % FOLDS for g in group])  # whole books per fold
    out = {"n": {n: int((corpus == n).sum()) for n in CORPORA}, "books": {n: len(set(group[corpus == n])) for n in CORPORA}}

    scores = {}
    for dim, names in DIMENSIONS.items():
        X = matrix(rows, names)
        signs = [1] * len(names)
        full = fit(X, corpus, level, n_levels, signs, ages=ages)
        scores[dim] = np.array([full.score(x) for x in np.nan_to_num(X, nan=0) + np.isnan(X) * full.mean])
        res = {"weights_per_sd": dict(zip(names, map(float, full.weights * full.std))),
               "age_map": {"slope": full.age_slope, "intercept": full.age_intercept, "valid": full.age_range}}
        oof_s, oof_l, oof_age = np.zeros(len(rows)), np.zeros(len(rows), int), np.full(len(rows), np.nan)
        for k in range(FOLDS):
            tr, te = fold != k, fold == k
            m = fit(X[tr], corpus[tr], level[tr], n_levels, signs, ages=ages)
            Xt = np.where(np.isnan(X[te]), m.mean, X[te])
            oof_age[te] = [m.age(x) for x in Xt]
            oof_s[te] = [m.score(x) for x in Xt]
            oof_l[te] = [m.level(x, c) for x, c in zip(Xt, corpus[te])]
        res["held_out"] = {n: {"spearman": spearman(oof_s[corpus == n], level[corpus == n]),
                               "within_one": within_one(oof_l[corpus == n], level[corpus == n])} for n in CORPORA}
        for n, a in ages.items():
            gold = np.array(a)[level[corpus == n]]
            res["held_out"][n]["age_mae"] = float(np.mean(np.abs(oof_age[corpus == n] - gold)))
            res["held_out"][n]["age_mae_constant"] = float(np.mean(np.abs(np.median(gold) - gold)))
        res["leave_one_corpus_out"] = {}
        for n in CORPORA:
            tr = corpus != n
            m = fit(X[tr], corpus[tr], level[tr], {k: v for k, v in n_levels.items() if k != n}, signs)
            Xt = np.where(np.isnan(X[~tr]), m.mean, X[~tr])
            res["leave_one_corpus_out"][n] = spearman([m.score(x) for x in Xt], level[~tr])
        out[dim] = res

    out["majority_within_one"] = {n: within_one(np.full((corpus == n).sum(), np.bincount(level[corpus == n]).argmax()),
                                                level[corpus == n]) for n in CORPORA}
    out["formulas"] = {f: {n: spearman(matrix(rows, [f])[corpus == n, 0], level[corpus == n]) for n in CORPORA}
                       for f in FORMULAS}
    out["correlation"] = {"lexical~syntactic": float(np.corrcoef(scores["lexical"], scores["syntactic"])[0, 1])}
    for f in FORMULAS:
        v = matrix(rows, [f])[:, 0]
        ok = ~np.isnan(v)
        for dim in DIMENSIONS:
            out["correlation"][f"{dim}~{f}"] = float(np.corrcoef(scores[dim][ok], v[ok])[0, 1])
    (HERE / "results.json").write_text(json.dumps(out, indent=2))
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
