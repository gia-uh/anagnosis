# Orthogonality of the lexical and syntactic dimensions

The first English calibration (`experiments/2026-10-21-calibration-en`) left the lexical and syntactic scores correlated at 0.55, above the 0.5 the design allows. The design names two remedies: residualize one dimension on the other, or change what feeds them. This experiment measures both, in English and Spanish, before `anagnosis.calibrate.DIMENSIONS` changes.

## Run

```bash
uv run python experiments/2026-10-21-calibration-en/run.py   # once, to cache the English features
uv run python experiments/2026-10-21-calibration-es/run.py   # once, to cache the Spanish features
uv run python experiments/2026-10-21-orthogonality/run.py en
uv run python experiments/2026-10-21-orthogonality/run.py es
```

About two minutes per language. `results-en.json` and `results-es.json` have every number below.

## Method

- Same corpora, features, sign constraints and 5-fold split by whole book as the calibration experiments.
- Every number is out of fold: each fold fits both dimensions on the other four folds and scores the held-out one. The calibration experiments reported the correlation of the full-data fit (0.55 in English); out of fold the same baseline gives 0.51.
- Variants:
  - **baseline**: the dimensions of the calibration experiments.
  - **lexical without word length**: lexical drops letters per word, syllables per word and long-word share, keeping age of acquisition and rare words.
  - **syntactic without sentence length**: syntactic drops words per sentence and tree depth, keeping clauses per sentence and dependency distance.
  - **both dropped**: the two together.
  - **residualized**: syntactic minus its linear fit on lexical, the slope taken from the training folds.
- **Within level** is the correlation after subtracting each (corpus, level) mean from both scores: what the two dimensions share beyond the label they are both fitted to.

## Results

Correlation of the two scores, and their rank correlation (Spearman) with the label. English columns are readers / years; Spanish are StoryWeaver / Cuban grades.

| English | lexical~syntactic | within level | lexical | syntactic |
|---|---|---|---|---|
| baseline | 0.51 | 0.34 | 0.66 / 0.56 | 0.44 / 0.41 |
| lexical without word length | 0.51 | 0.34 | 0.66 / 0.56 | 0.44 / 0.41 |
| syntactic without sentence length | **0.38** | 0.21 | 0.66 / 0.56 | 0.37 / 0.36 |
| both dropped | 0.40 | 0.23 | 0.66 / 0.56 | 0.37 / 0.36 |
| residualized | -0.03 | -0.13 | 0.66 / 0.56 | 0.05 / 0.17 |

| Spanish | lexical~syntactic | within level | lexical | syntactic |
|---|---|---|---|---|
| baseline | 0.29 | 0.19 | 0.34 / 0.46 | 0.27 / 0.35 |
| lexical without word length | 0.34 | 0.24 | 0.34 / 0.40 | 0.27 / 0.35 |
| syntactic without sentence length | **0.27** | 0.17 | 0.34 / 0.46 | 0.28 / 0.36 |
| both dropped | 0.32 | 0.22 | 0.34 / 0.40 | 0.28 / 0.36 |
| residualized | -0.00 | -0.10 | 0.34 / 0.46 | 0.16 / 0.23 |

## What it showed

1. **The shared signal comes from sentence length, not word length.** Dropping words per sentence and tree depth from syntax brings English from 0.51 to 0.38 and the within-level correlation from 0.34 to 0.21. Dropping word length from lexical changes nothing in English, because word length correlates 0.7 to 0.8 with age of acquisition and the fit already leaned on the latter; in Spanish it raises the correlation and costs the Cuban texts 0.06.
2. **The cost is 0.07 of syntactic ranking in English and nothing in Spanish.** Clauses per sentence and dependency distance rank the English readers at 0.37 instead of 0.44, and the Spanish corpora slightly better than before. The lexical side is untouched in both.
3. **Residualizing empties the syntactic dimension.** Its correlation with the label falls to 0.05 on the English readers: on these corpora, almost everything syntax says about level, vocabulary already says. A residualized score would be orthogonal by construction and close to useless for ranking, so it is not adopted. It stays the remedy for a pair of dimensions that cannot be separated by their features.
4. **Part of the remaining 0.38 is real.** Within a level it falls to 0.21, so about half of what the two scores share is that books for older readers are harder on both counts, which orthogonal dimensions should still show.

## Decision

`DIMENSIONS["syntactic"]` becomes clauses per sentence and mean dependency distance. Sentence length and tree depth are still measured and reported as features; they no longer feed the syntactic score. The calibration experiments pin the old lists, so they still reproduce their own numbers.
