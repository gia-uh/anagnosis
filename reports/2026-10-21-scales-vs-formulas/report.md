---
theme: article
title: Fitted Lexical and Syntactic Scales against the Classic Readability Formulas
authors:
  - name: The anagnosis project
date: October 2026
abstract: >
  We fit two reading-difficulty scales, lexical and syntactic, on four openly licensed
  corpora of graded texts in English and Spanish, and compare their held-out rank
  correlation with the corpus labels against Flesch-Kincaid, Flesch reading ease,
  Fernández Huerta, Szigriszt-Pazos and Crawford. The lexical scale, driven by
  age-of-acquisition norms, ranks English school readers at 0.66 against 0.56 for the
  best formula, a gain of 0.10 whose 95% interval by book is 0.004 to 0.195. On the
  other three corpora it is ahead by 0.03 to 0.05 with intervals that include zero.
  Refitting the formulas' own inputs gains nothing, so the improvement comes from the
  features. Separating the two scales required removing sentence length and tree depth
  from the syntactic one, which brought their correlation from 0.51 to 0.38. Mapping
  the scales to reading ages fails on these corpora, and the Spanish labels are too
  weak to rank difficulty well; both point to an age-anchored corpus of our own.
keywords: readability, reading age, age of acquisition, ordinal regression, Spanish, English
references-label: References
footnotes-label: Notes
bibliography:
  flesch1948: "Flesch, R. *A new readability yardstick.* Journal of Applied Psychology 32(3), 221–233, 1948. [doi:10.1037/h0057532](https://doi.org/10.1037/h0057532)."
  kincaid1975: "Kincaid, J. P., Fishburne, R. P., Rogers, R. L. and Chissom, B. S. *Derivation of New Readability Formulas for Navy Enlisted Personnel.* Report 8-75, Naval Technical Training Command, 1975."
  fernandezhuerta1959: "Fernández Huerta, J. *Medidas sencillas de lecturabilidad* [Simple measures of readability]. Consigna, 29–32, 1959."
  szigriszt1993: "Szigriszt Pazos, F. *Sistemas predictivos de legibilidad del mensaje escrito: fórmula de perspicuidad* [Predictive systems for the legibility of the written message: the perspicuity formula]. PhD thesis, Universidad Complutense de Madrid, 1993."
  crawford1984: "Crawford, A. N. *A Spanish Language Fry-Type Readability Procedure: Elementary Level.* Bilingual Education Paper Series 7(8), California State University, Los Angeles, 1984. ERIC ED273119."
  kuperman2012: "Kuperman, V., Stadthagen-Gonzalez, H. and Brysbaert, M. *Age-of-acquisition ratings for 30,000 English words.* Behavior Research Methods 44, 978–990, 2012. [doi:10.3758/s13428-012-0210-4](https://doi.org/10.3758/s13428-012-0210-4)."
  alonso2015: "Alonso, M. Á., Fernández, Á. and Díez, E. *Subjective age-of-acquisition norms for 7,039 Spanish words.* Behavior Research Methods 47, 268–274, 2015. [doi:10.3758/s13428-014-0454-2](https://doi.org/10.3758/s13428-014-0454-2)."
  speer2022: "Speer, R. *wordfreq*, version 3.0, 2022. [github.com/rspeer/wordfreq](https://github.com/rspeer/wordfreq)."
  liu2008: "Liu, H. *Dependency distance as a metric of language comprehension difficulty.* Journal of Cognitive Science 9(2), 159–191, 2008."
  gutenberg: "Project Gutenberg. [gutenberg.org](https://www.gutenberg.org)."
  storyweaver: "StoryWeaver, Pratham Books. Spanish stories under CC BY 4.0. [storyweaver.org.in](https://storyweaver.org.in)."
  wikisource: "Wikisource in Spanish. [es.wikisource.org](https://es.wikisource.org)."
---

::: titleblock
:::

# Question

Classic readability formulas combine two surface counts, word length in syllables and sentence length in words, with weights fitted decades ago on other texts: Flesch reading ease and Flesch-Kincaid in English,[@flesch1948; @kincaid1975] Fernández Huerta, Szigriszt-Pazos and Crawford in Spanish.[@fernandezhuerta1959; @szigriszt1993; @crawford1984] anagnosis replaces the single number with separate dimensions, each fitted on corpora whose difficulty is known, so that a text can be hard for one reason and easy for another. This report asks whether the first two dimensions, lexical and syntactic, rank graded texts better than the formulas, and whether they can be kept apart.

Every number here comes from three experiments in the repository: `experiments/2026-10-21-calibration-en` and `-es` (the first fit), `experiments/2026-10-21-orthogonality` (separating the dimensions) and `experiments/2026-10-21-scales-vs-formulas` (the comparison). Each has a README with the command that reproduces it.

# Data

Only corpora whose license is CC BY or public domain enter the repository, which rules out most published readability sets.[^licenses]

**Table 1.** The four calibration corpora.

| Corpus | Language | Documents | Books | Label |
|---|---|---|---|---|
| en-school-readers | English | 642 passages | 17 | reader number in its series, first to seventh |
| en-school-years | English | 258 passages | 7 | school year in the title (1, 3, 4, 5), mapped to ages 6.5–10.5 |
| es-storyweaver | Spanish | 1383 stories | 1373 | publisher level, 1 to 5 |
| es-cuba-grades | Spanish | 23 texts | 23 | first grade (3 to 8) whose Cuban school textbook includes it, mapped to ages 8.5–13.5 |

The English corpora are US, Canadian and British school readers from 1857 to 1925, taken from Project Gutenberg.[@gutenberg] The Spanish stories come from StoryWeaver under CC BY 4.0,[@storyweaver] and 93% of them are translations. The Cuban texts are public-domain works, mostly by José Martí, taken from Wikisource;[@wikisource] only the reading lists of the textbooks were used, never their text.

[^licenses]: HablaCultura, Kwiziq and CAES, distributed as CC BY 4.0 on some dataset cards, are non-commercial or unlicensed at their source, and no Spanish or English UniversalCEFR set is CC BY. The checks are recorded in `corpora/README.md`.

# Method

**Features.** The lexical dimension reads the mean and 90th percentile of word age of acquisition, the share of words learned late, the share of rare words, letters and syllables per word, and the share of long words. Age-of-acquisition norms come from Kuperman et al. for English and Alonso et al. for Spanish,[@kuperman2012; @alonso2015] word frequency from wordfreq.[@speer2022] The syntactic dimension reads clauses per sentence and mean dependency distance.[@liu2008] All features are pooled over the document.

**Fit.** Each dimension is a weighted sum of its standardized features, with every weight held to the sign the literature predicts (here, non-negative). Each corpus gets its own cut points on that scale, through a cumulative logit, and all corpora of a language are fitted together. Corpora with ages map the scale to years with a linear fit.

**Evaluation.** All fitted numbers are out of fold: five folds, each book entirely in one fold. Transfer fits on the other corpus of the same language alone and ranks the held-out one. The formulas are not fitted; each is oriented so that higher means harder and ranked as is. Intervals are 95% bootstrap intervals over 2000 resamples of books.

**Controls.** Two fitted scores test where any gain comes from. *Formula inputs, refitted* fits syllables per word and words per sentence, the inputs every formula here is built from, the same way as the dimensions; if it matched lexical, the gain would come from fitting to these corpora. *Both dimensions* fits all features at once. Text length in words is reported as a score that measures no difficulty at all.

# Results

## The lexical scale against the formulas

**Table 2.** Spearman correlation with the corpus label, out of fold, with 95% intervals by book.

| | readers | years | StoryWeaver | Cuba |
|---|---|---|---|---|
| lexical | **0.66** [0.39, 0.82] | 0.56 [0.22, 0.76] | 0.34 [0.29, 0.40] | 0.46 [0.05, 0.77] |
| syntactic | 0.37 [0.03, 0.61] | 0.36 [−0.11, 0.72] | 0.28 [0.22, 0.33] | 0.36 [−0.09, 0.74] |
| both dimensions | 0.63 [0.31, 0.82] | 0.58 [0.25, 0.77] | 0.37 [0.31, 0.42] | 0.68 [0.40, 0.84] |
| formula inputs, refitted | 0.56 [0.26, 0.76] | 0.49 [0.15, 0.72] | 0.30 [0.24, 0.35] | 0.50 [0.09, 0.80] |
| Flesch-Kincaid grade | 0.53 [0.19, 0.75] | 0.49 [0.04, 0.78] | | |
| Flesch reading ease | 0.56 [0.25, 0.76] | 0.51 [0.10, 0.75] | | |
| Fernández Huerta | | | 0.30 [0.25, 0.36] | 0.43 [0.03, 0.77] |
| Szigriszt-Pazos | | | 0.30 [0.25, 0.36] | 0.43 [0.04, 0.75] |
| Crawford | | | 0.26 [0.21, 0.32] | 0.41 [−0.00, 0.77] |
| text length in words | 0.35 [0.15, 0.50] | 0.14 [−0.12, 0.36] | **0.50** [0.44, 0.56] | 0.37 [−0.12, 0.71] |

The paired difference between lexical and the best formula on each corpus, chosen after seeing the data so that the comparison favours the formula, is +0.10 [0.004, 0.195] on the readers, +0.05 [−0.15, 0.22] on the years corpus, +0.04 [−0.01, 0.09] on StoryWeaver and +0.03 [−0.56, 0.63] on the Cuban texts. The lexical scale is ahead everywhere, and the lead is distinguishable from zero only on the readers.

The lexical scale also transfers: fitted on the other English corpus alone it ranks the readers at 0.65 and the years at 0.53, close to its held-out values, so its weights are not tied to one corpus's cut points. The Spanish transfer numbers, 0.32 and 0.45, tell the same story.

## Where the gain comes from

Refitting the formula inputs on these corpora gives 0.56 on the readers, the same as Flesch reading ease, and 0.30 on StoryWeaver, the same as Fernández Huerta. Fitting alone buys nothing; the lexical scale's lead comes from the age-of-acquisition features, which carry most of its weight (the 90th percentile at 0.82 per standard deviation and the mean at 0.46 in English). Over all documents, lexical correlates 0.83 with the refitted formula inputs in English and 0.63 in Spanish: the formulas measure much of the same thing, less precisely.

## Keeping the dimensions apart

The design allows two dimensions to correlate at most 0.5. The first fit put lexical and syntactic at 0.51 out of fold. Dropping word-length features from lexical changed nothing, because word length already correlates 0.7 to 0.8 with age of acquisition. Dropping sentence length and tree depth from syntactic brought the correlation to 0.38 in English and 0.27 in Spanish, and the correlation within a level, which removes what both share through the label, from 0.34 to 0.21. Residualizing syntactic on lexical would make them uncorrelated by construction but leaves syntax ranking the readers at 0.05: on these corpora nearly everything syntax says about level, vocabulary already says. The adopted syntactic scale costs 0.07 of ranking in English and nothing in Spanish.

The narrower syntactic scale still correlates 0.76 with Flesch-Kincaid and 0.62 with Crawford, the two formulas that weigh sentence length most.

## Reading ages

On the two corpora that carry ages, the age predicted by the lexical scale is further from the truth than a constant: 0.84 years off against 0.52 on the English years corpus, 1.34 against 1.30 on the Cuban texts. Seven books, 62% of them in one year, and 23 texts are too little spread to fit a slope. No age claim in this report is calibrated.

# Limitations

- **The Spanish labels are weak.** StoryWeaver levels follow story length (0.50) better than any difficulty score, so they are as much a length grade as a difficulty grade; and 23 Cuban texts give intervals that span most of the scale. The 0.68 of the combined score on them is the least reliable number in the report.
- **The English books are old.** Readers from 1857 to 1925 use vocabulary and syntax a present-day child does not meet, and the age-of-acquisition norms come from adults today.
- **Within one level is uninformative on skewed corpora.** On the years corpus, always predicting the fourth year is within one level 93% of the time, more than any fitted score; the full table is in the experiment.
- **Few books.** The English intervals are wide because 17 and 7 books are all there are to resample.

# What follows

The lexical scale is worth keeping and the syntactic one needs a corpus where syntax varies independently of vocabulary. Both needs lead to the same place: an age-anchored corpus of our own, read by children of known age in both languages, with several books per age. The annotation protocol for it is drafted in `docs/annotation/2026-10-21-protocol-draft.html`.

::: references
:::
