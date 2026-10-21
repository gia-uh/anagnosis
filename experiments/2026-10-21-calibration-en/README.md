# First joint calibration: English school readers

The first fit of the lexical and syntactic dimensions (`anagnosis.calibrate`) on the two public-domain English corpora, `en-school-readers` (642 passages, 17 books, labelled by the reader's number in its series) and `en-school-years` (258 passages, 7 books, labelled by the school year in the title, which anchors ages).

## Run

```bash
uv run anagnosis fetch-norms    # once
uv run python experiments/2026-10-21-calibration-en/run.py
```

Features are cached in `data/features-<corpus>.jsonl`; delete them to re-measure (about two minutes). `results.json` has every number below.

## Method

- One passage is one document; its features are pooled over the passage.
- Lexical uses the age-of-acquisition, rare-word and word-length features; syntactic uses words per sentence, clauses per sentence, dependency distance and tree depth. All weights are held non-negative.
- Held-out numbers come from 5-fold cross-validation in which a whole book falls in one fold, so no book has passages on both sides.
- Leave-one-corpus-out fits on the other corpus and ranks the left-out one, without its cut points.
- The classic formulas are not fitted; their rank correlation with the label is reported as is.

## Results

Rank correlation (Spearman) with the label, out of fold:

| | readers | years |
|---|---|---|
| lexical, held out | 0.66 | 0.56 |
| lexical, other corpus only | 0.65 | 0.53 |
| syntactic, held out | 0.44 | 0.41 |
| syntactic, other corpus only | 0.47 | 0.45 |
| Flesch-Kincaid grade | 0.53 | 0.49 |
| Flesch reading ease (sign flipped) | 0.56 | 0.51 |

Predicted level within one of the true level, out of fold, against always predicting the most frequent level:

| | readers | years |
|---|---|---|
| lexical | 0.78 | 0.91 |
| syntactic | 0.67 | 0.88 |
| most frequent level | 0.62 | 0.93 |

Fitted weights, per standard deviation of the feature:

| lexical | | syntactic | |
|---|---|---|---|
| aoa_p90 | 0.82 | mean_tree_depth | 0.58 |
| aoa_mean | 0.46 | mean_dependency_distance | 0.44 |
| long_word_share | 0.30 | words_per_sentence | 0 |
| syllables_per_word | 0.20 | clauses_per_sentence | 0 |
| aoa_late_share, rare_word_share, letters_per_word | 0 | | |

Correlation of the two dimension scores over all 900 passages: 0.55.

## What it showed

1. **The lexical dimension ranks these texts better than the formulas, and transfers.** 0.66 against 0.53 for Flesch-Kincaid on the readers, and fitting on the other corpus alone loses almost nothing (0.65), so the weights are not tied to one corpus's cut points. Age of acquisition carries most of it.
2. **The syntactic dimension ranks worse than the formulas.** Flesch-Kincaid mixes word length with sentence length, and word length is the stronger signal here, so a syntax-only score loses to it. Sentence length gets weight 0 because tree depth already grows with it. Verse also inflates syntax: a stanza with no final period is parsed as one long sentence.
3. **Age anchoring fails on this data.** Out of fold, the age predicted by the lexical dimension is 0.84 years off on average, while a constant age is 0.52 years off. The years corpus has 7 books and 62% of its passages are fourth-year, which is too little spread to fit a slope. Ages need an age-anchored corpus with several books per age, which is what our own corpus is for.
4. **The two dimensions are not yet orthogonal.** Their correlation (0.55) is above the 0.5 the design allows. Part of it is real (texts for older readers are harder on both counts); part is shared features of length. The next fit should residualize syntax on lexical, or test whether dropping the length-sensitive features from one side brings it below 0.5.
5. **"Within one level" is not informative on the years corpus**, where predicting fourth year always scores 0.93. On the readers corpus the lexical fit adds 16 points over that baseline.
