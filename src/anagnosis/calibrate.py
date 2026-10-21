"""Joint ordinal calibration: one latent scale per dimension, cut points per corpus.

A dimension's score is a weighted sum of its standardized features. Every
corpus with ordered levels gets its own cut points on that scale (cumulative
logit), pairwise judgements add a ranking term (the harder text must score
higher), and all corpora are fitted together. Each weight is held to the sign
the literature predicts, so a feature can only push the score the way it is
supposed to, or not at all. Corpora that give a reading age per level turn the
scale into years with a linear map, valid only between their lowest and highest
age.

Fitted with Adam on the exact gradient, projected onto the sign constraints.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

DIMENSIONS = {
    "lexical": ["aoa_mean", "aoa_p90", "aoa_late_share", "rare_word_share",
                "letters_per_word", "syllables_per_word", "long_word_share"],
    # Sentence length and tree depth stay out: they share the length signal with the lexical side and pushed
    # the two scores to 0.51 (experiments/2026-10-21-orthogonality).
    "syntactic": ["clauses_per_sentence", "mean_dependency_distance"],
}


def _sig(z):
    return 1.0 / (1.0 + np.exp(-z))


def _dsig(z):
    s = _sig(z)
    return s * (1.0 - s)


@dataclass
class Fit:
    mean: np.ndarray
    std: np.ndarray
    weights: np.ndarray  # on the raw feature scale: score(x) = (x - mean) @ weights
    thresholds: dict[str, np.ndarray] = field(default_factory=dict)
    age_slope: float | None = None
    age_intercept: float | None = None
    age_range: tuple[float, float] | None = None

    def score(self, x) -> float:
        return float((np.asarray(x, float) - self.mean) @ self.weights)

    def level(self, x, corpus: str) -> int:
        return int(np.searchsorted(self.thresholds[corpus], self.score(x)))

    def age(self, x) -> float:
        return self.age_intercept + self.age_slope * self.score(x)


def _thresholds(a, b):
    return a + np.concatenate([[0.0], np.cumsum(np.exp(b))])


def fit(X, corpus, level, n_levels: dict[str, int], signs, pairs=(), ages: dict[str, list[float]] | None = None,
        l2: float = 1e-3, steps: int = 3000, lr: float = 0.05) -> Fit:
    """X: documents by features (NaN where a feature is undefined). corpus: one name per row.
    level: ordinal level per row (ignored for corpora not in n_levels). pairs: (easier, harder) row indices."""
    X = np.asarray(X, float)
    mean, std = np.nanmean(X, axis=0), np.nanstd(X, axis=0)
    std[std == 0] = 1.0
    Z = np.nan_to_num((X - mean) / std)
    signs = np.asarray(signs, float)
    corpus = np.asarray(corpus)
    groups = {c: np.flatnonzero(corpus == c) for c in n_levels}
    ys = {c: np.asarray(level)[idx] for c, idx in groups.items()}
    easy, hard = (np.array([p[i] for p in pairs], int) for i in (0, 1)) if len(pairs) else (np.array([], int),) * 2

    params = {"w": 0.1 * signs}
    for c, k in n_levels.items():
        params[f"a:{c}"] = np.array(-1.0)
        params[f"b:{c}"] = np.zeros(k - 2)
    m = {k: np.zeros_like(v) for k, v in params.items()}
    v = {k: np.zeros_like(p) for k, p in params.items()}
    n = len(Z)

    for t in range(1, steps + 1):
        w = params["w"]
        s = Z @ w
        g = {k: np.zeros_like(p) for k, p in params.items()}
        g["w"] = 2 * l2 * w
        for c, idx in groups.items():
            th = _thresholds(params[f"a:{c}"], params[f"b:{c}"])
            y, sc = ys[c], s[idx]
            upper = np.where(y < len(th), th[np.minimum(y, len(th) - 1)], np.inf)
            lower = np.where(y > 0, th[np.maximum(y - 1, 0)], -np.inf)
            p = np.maximum(_sig(upper - sc) - _sig(lower - sc), 1e-12)
            du = np.where(np.isfinite(upper), _dsig(np.where(np.isfinite(upper), upper - sc, 0)), 0) / p
            dl = np.where(np.isfinite(lower), _dsig(np.where(np.isfinite(lower), lower - sc, 0)), 0) / p
            g["w"] += Z[idx].T @ (du - dl) / n  # d(-log p)/ds = du - dl
            dth = np.zeros(len(th))
            np.add.at(dth, np.minimum(y, len(th) - 1)[y < len(th)], -du[y < len(th)])
            np.add.at(dth, np.maximum(y - 1, 0)[y > 0], dl[y > 0])
            dth /= n
            g[f"a:{c}"] = np.array(dth.sum())
            g[f"b:{c}"] = np.exp(params[f"b:{c}"]) * np.cumsum(dth[::-1])[::-1][1:]
        if len(easy):
            d = s[hard] - s[easy]
            r = 1.0 - _sig(d)  # d(-log sig(d))/dd = -(1 - sig(d))
            g["w"] -= (Z[hard] - Z[easy]).T @ r / max(n, 1)
        for k in params:
            m[k] = 0.9 * m[k] + 0.1 * g[k]
            v[k] = 0.999 * v[k] + 0.001 * g[k] ** 2
            params[k] = params[k] - lr * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v[k] / (1 - 0.999 ** t)) + 1e-8)
        params["w"] = np.where(params["w"] * signs > 0, params["w"], 0.0)

    weights = params["w"] / std
    out = Fit(mean=mean, std=std, weights=weights,
              thresholds={c: _thresholds(params[f"a:{c}"], params[f"b:{c}"]) for c in n_levels})
    ages = {c: a for c, a in (ages or {}).items() if c in groups and len(groups[c])}
    if ages:
        idx = np.concatenate([groups[c] for c in ages])
        yrs = np.concatenate([np.asarray(ages[c], float)[ys[c]] for c in ages])
        out.age_slope, out.age_intercept = np.polyfit(Z[idx] @ params["w"], yrs, 1)
        out.age_range = (min(min(a) for a in ages.values()), max(max(a) for a in ages.values()))
    return out


def _ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(1, len(x) + 1)
    for val in np.unique(x):
        tie = x == val
        r[tie] = r[tie].mean()
    return r


def spearman(a, b) -> float:
    return float(np.corrcoef(_ranks(a), _ranks(b))[0, 1])


def within_one(pred, gold) -> float:
    return float(np.mean(np.abs(np.asarray(pred) - np.asarray(gold)) <= 1))
