# First joint calibration: Spanish corpora

The same method as `2026-10-21-calibration-en` on the two Spanish corpora: `es-storyweaver` (1,383 stories, StoryWeaver level 1–5, 1,289 of them translations) and `es-cuba-grades` (23 public-domain texts, earliest Cuban school grade 3–8, with ages).

## Run

```bash
uv run anagnosis fetch-norms    # once
uv run python experiments/2026-10-21-calibration-es/run.py
```

A text without a `group` is its own group in the 5-fold split.

## Results

Rank correlation (Spearman) with the label, out of fold:

| | StoryWeaver | Cuba |
|---|---|---|
| lexical, held out | 0.34 | 0.46 |
| lexical, other corpus only | 0.32 | 0.45 |
| syntactic, held out | 0.27 | 0.35 |
| syntactic, other corpus only | 0.29 | 0.39 |
| Fernández Huerta (sign flipped) | 0.30 | 0.43 |
| Szigriszt-Pazos (sign flipped) | 0.30 | 0.43 |
| Crawford | 0.26 | 0.41 |
| text length in words, not a feature | 0.50 | 0.37 |

Age from the lexical dimension on the Cuban texts, out of fold: 1.34 years off on average, against 1.30 for a constant age. Correlation of the two dimension scores: 0.30.

Weights per standard deviation. Lexical: aoa_p90 0.48, long_word_share 0.17, syllables_per_word 0.13, aoa_mean 0.07, the rest 0. Syntactic: mean_dependency_distance 0.29, clauses_per_sentence 0.17, mean_tree_depth 0.10, words_per_sentence 0.

## What it showed

1. **StoryWeaver's levels are mostly about length.** The number of words in a story ranks the levels better (0.50) than any measure of difficulty, because the publisher's level descriptions are word-count bands. The lexical dimension still beats the classic formulas on it (0.34 against 0.30), but the corpus is a weak label for reading difficulty, and 93% of it is translated.
2. **The Cuban texts point the right way but are too few to conclude.** With 23 texts, a rank correlation of 0.46 has a 95% interval of roughly 0.06 to 0.73. They are also a strange sample: Martí's poems are read from 3rd grade to 8th.
3. **Age anchoring fails again,** for the same reason as in English: too few texts with ages and too little spread.
4. **The two dimensions are below the 0.5 the design allows (0.30),** unlike in English (0.55).
5. **What Spanish needs is our own corpus.** Neither open source gives a reading age for native children with enough texts to fit. The annotation protocol (`docs/annotation/`) and the MINED textbooks, if the permission arrives, are the two ways to get it.
