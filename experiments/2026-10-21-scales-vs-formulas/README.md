# Fitted scales against the classic formulas

The numbers behind `reports/2026-10-21-scales-vs-formulas`: the lexical and syntactic dimensions as they stand after `experiments/2026-10-21-orthogonality`, against the classic formulas, on the four calibration corpora, with 95% intervals that resample whole books.

## Run

```bash
uv run python experiments/2026-10-21-calibration-en/run.py   # once, to cache the English features
uv run python experiments/2026-10-21-calibration-es/run.py   # once, to cache the Spanish features
uv run python experiments/2026-10-21-scales-vs-formulas/run.py en
uv run python experiments/2026-10-21-scales-vs-formulas/run.py es
```

About a minute and a half per language. `results-en.json` and `results-es.json` have every number below.

## Method

- Fitted scores, all out of fold (5 folds, a whole book in one fold): **lexical**, **syntactic**, **both dimensions** (one fit on the features of both), and **formula inputs, refitted** (syllables per word and words per sentence, the two inputs of every formula here, fitted the same way). The last one separates what better features buy from what fitting buys.
- Unfitted scores: the classic formulas, oriented so that higher means harder, and text length in words.
- **Transfer** fits on the other corpus of the same language and ranks this one, without its cut points.
- Intervals: 2000 bootstrap resamples of books (StoryWeaver stories and Cuban texts are each their own book). **Lexical minus best formula** is the paired difference in Spearman between lexical and the formula that did best on that corpus, picked after seeing the data, which favours the formula.

## Results

Spearman with the label, out of fold, with 95% intervals by book:

| | readers (17 books) | years (7) | StoryWeaver (1373) | Cuba (23) |
|---|---|---|---|---|
| lexical | 0.66 [0.39, 0.82] | 0.56 [0.22, 0.76] | 0.34 [0.29, 0.40] | 0.46 [0.05, 0.77] |
| syntactic | 0.37 [0.03, 0.61] | 0.36 [-0.11, 0.72] | 0.28 [0.22, 0.33] | 0.36 [-0.09, 0.74] |
| both dimensions | 0.63 [0.31, 0.82] | 0.58 [0.25, 0.77] | 0.37 [0.31, 0.42] | 0.68 [0.40, 0.84] |
| formula inputs, refitted | 0.56 [0.26, 0.76] | 0.49 [0.15, 0.72] | 0.30 [0.24, 0.35] | 0.50 [0.09, 0.80] |
| Flesch-Kincaid grade | 0.53 [0.19, 0.75] | 0.49 [0.04, 0.78] | | |
| Flesch reading ease | 0.56 [0.25, 0.76] | 0.51 [0.10, 0.75] | | |
| Fernández Huerta | | | 0.30 [0.25, 0.36] | 0.43 [0.03, 0.77] |
| Szigriszt-Pazos | | | 0.30 [0.25, 0.36] | 0.43 [0.04, 0.75] |
| Crawford | | | 0.26 [0.21, 0.32] | 0.41 [-0.00, 0.77] |
| text length in words | 0.35 [0.15, 0.50] | 0.14 [-0.12, 0.36] | 0.50 [0.44, 0.56] | 0.37 [-0.12, 0.71] |

Lexical minus the best formula: readers +0.10 [0.004, 0.195] against Flesch reading ease; years +0.05 [-0.15, 0.22]; StoryWeaver +0.04 [-0.01, 0.09] and Cuba +0.03 [-0.56, 0.63], both against Fernández Huerta.

Transfer (Spearman, fitted on the other corpus only):

| | readers | years | StoryWeaver | Cuba |
|---|---|---|---|---|
| lexical | 0.65 | 0.53 | 0.32 | 0.45 |
| syntactic | 0.41 | 0.40 | 0.29 | 0.36 |
| both dimensions | 0.65 | 0.55 | 0.30 | 0.70 |
| formula inputs, refitted | 0.57 | 0.46 | 0.31 | 0.51 |

Predicted level within one of the true level, against always predicting the most frequent level:

| | readers | years | StoryWeaver | Cuba |
|---|---|---|---|---|
| lexical | 0.78 | 0.91 | 0.82 | 0.61 |
| syntactic | 0.66 | 0.85 | 0.80 | 0.61 |
| both dimensions | 0.77 | 0.91 | 0.83 | 0.74 |
| formula inputs, refitted | 0.74 | 0.91 | 0.80 | 0.61 |
| most frequent level | 0.62 | 0.93 | 0.62 | 0.52 |

Pearson correlation over all documents of a language: lexical~syntactic 0.38 (en) and 0.27 (es); lexical~refitted formula inputs 0.83 and 0.63; syntactic~Flesch-Kincaid 0.76; syntactic~Crawford 0.62. The full matrices are in the result files.

## What it showed

1. **Lexical beats the best formula clearly on one corpus only**, the English readers, by 0.10 with an interval that just excludes zero. Elsewhere the difference is positive and its interval includes zero.
2. **The gain comes from the features, not from fitting.** Refitting the two formula inputs scores like the formulas themselves (0.56 against 0.56 on the readers); the age-of-acquisition features are what lift lexical to 0.66.
3. **Spanish labels are weak.** StoryWeaver levels follow story length (0.50) more than any difficulty score, and the Cuban intervals span most of the scale.
4. **Combining the two dimensions helps only on the Cuban texts** (0.68), where 23 texts make it the least trustworthy number in the table.
