"""Calibration on synthetic corpora whose latent scale is known."""
import numpy as np
import pytest

from anagnosis.calibrate import fit, spearman, within_one

TRUE_W = np.array([1.5, 0.8, 0.0, 0.5])
CUTS = {"a": [-2.0, 0.0, 2.0], "b": [-1.0, 1.5], "c": [0.5, 1.0, 1.5, 3.0]}


def synthetic(seed=0, n=1500):
    rng = np.random.default_rng(seed)
    X, corpus, level = [], [], []
    for name, cuts in CUTS.items():
        x = rng.normal(size=(n, len(TRUE_W)))
        s = x @ TRUE_W + rng.logistic(size=n)
        X.append(x)
        corpus += [name] * n
        level.append(np.searchsorted(cuts, s))
    return np.vstack(X), corpus, np.concatenate(level)


@pytest.fixture(scope="module")
def recovered():
    X, corpus, level = synthetic()
    return fit(X, corpus, level, n_levels={k: len(v) + 1 for k, v in CUTS.items()}, signs=[1, 1, 1, 1]), X, corpus, level


def test_weights_are_recovered(recovered):
    m, *_ = recovered
    assert np.abs(m.weights - TRUE_W).max() < 0.15


def test_cut_points_are_recovered_per_corpus(recovered):
    m, X, *_ = recovered
    shift = m.mean @ m.weights  # standardizing moves the origin of the latent scale
    for name, cuts in CUTS.items():
        assert np.abs(m.thresholds[name] + shift - np.array(cuts)).max() < 0.25


def test_predicted_levels_match_the_true_model(recovered):
    m, X, corpus, level = recovered
    pred = np.array([m.level(x, c) for x, c in zip(X, corpus)])
    oracle = np.array([np.searchsorted(CUTS[c], x @ TRUE_W) for x, c in zip(X, corpus)])  # noise sets the ceiling
    assert within_one(pred, level) > within_one(oracle, level) - 0.01


def test_sign_constraint_holds_against_the_data():
    X, corpus, level = synthetic(seed=1)
    m = fit(X, corpus, level, n_levels={k: len(v) + 1 for k, v in CUTS.items()}, signs=[1, -1, 1, 1])
    assert m.weights[1] == 0.0  # the data say positive; the constraint allows only negative or zero
    assert m.weights[0] > 1.0


def test_pairs_alone_recover_the_direction():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(800, len(TRUE_W)))
    s = X @ TRUE_W + rng.logistic(size=800)
    pairs = [(i, i + 1) if s[i] < s[i + 1] else (i + 1, i) for i in range(0, 800, 2)]  # (easier, harder)
    m = fit(X, ["p"] * 800, None, n_levels={}, signs=[1, 1, 1, 1], pairs=pairs)
    assert spearman(X @ m.weights, X @ TRUE_W) > 0.95


def test_age_mapping_is_linear_in_the_anchor_range():
    X, corpus, level = synthetic(seed=3, n=600)
    ages = {"a": [6, 8, 10, 12]}
    m = fit(X, corpus, level, n_levels={k: len(v) + 1 for k, v in CUTS.items()}, signs=[1, 1, 1, 1], ages=ages)
    lo, hi = m.age_range
    assert (lo, hi) == (6, 12)
    a = [i for i, c in enumerate(corpus) if c == "a"]
    by_level = [np.mean([m.age(X[i]) for i in a if level[i] == k]) for k in range(4)]
    assert by_level == sorted(by_level)


def test_spearman_and_within_one_by_hand():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert spearman([1, 2, 2, 3], [1, 2, 3, 4]) == pytest.approx(0.9486833, abs=1e-6)  # tied ranks averaged
    assert within_one(np.array([0, 2, 4]), np.array([1, 2, 1])) == pytest.approx(2 / 3)
