# Baseline: three dimensions on eight books

First prototype. It measures each chapter on surface, vocabulary and syntax, and reports the median per book.

## Run

```bash
uv run --with playwright --with openpyxl python fetch_norms.py   # once: writes data/aoa-{es,en}.tsv
S="--with wordfreq --with cmudict --with spacy \
  --with https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl \
  --with https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
uv run $S python deep.py es my-book 'chapters/*.md'   # median per book
uv run $S python deep.py es - 'chapters/*.md'         # one line per file
```

`surface.py` alone (`--with wordfreq --with cmudict`) gives the formulas without spaCy.

## What each column is

| Column | Meaning |
|---|---|
| `wps` | words per sentence |
| `fh` | Fernández Huerta, 206.84 − 60 × syllables/word − 1.02 × words/sentence (es) |
| `craw` | Crawford grade, −0.205 × sentences/100 words + 0.049 × syllables/100 words − 3.407 (es, valid for grades 1–6) |
| `fkgl` | Flesch-Kincaid grade (en) |
| `unc%` | share of tokens, proper nouns excluded, with Zipf frequency below 4 (`wordfreq`) |
| `cl/s` | subordinate clauses per sentence (`advcl`, `acl`, `relcl`, `ccomp`, `csubj`, `parataxis`) |
| `mdd` | mean dependency distance, punctuation excluded |
| `depth` | mean of each sentence's parse-tree depth |
| `aoa`, `aoa90` | mean and 90th percentile age of acquisition of the content words found in the norms, in years |
| `late%` | share of those words learned at 9 or later |
| `cov%` | share of content words found in the norms |

## Results

Medians per chapter. The corpora: a Spanish anthology of myths for children aged 6 to 10; a Spanish collection of classic novels abridged for children, and six of the originals they abridge; a Spanish nonfiction book for adults; four English nonfiction books for adults.

| Corpus | n | wps | fh / fkgl | craw | cl/s | mdd | depth | aoa90 | late% | cov% |
|---|---|---|---|---|---|---|---|---|---|---|
| es, myths for children | 23 | 11.1 | 86.7 | 3.7 | 0.64 | 2.40 | 3.20 | 6.2 | 0.4 | 86 |
| es, abridged classics | 17 | 15.1 | 73.8 | 4.9 | 1.08 | 2.51 | 4.16 | 7.9 | 3.2 | 76 |
| es, the originals | 6 | 18.1 | 72.0 | 5.0 | 1.62 | 2.94 | 4.22 | 7.5 | 2.2 | 78 |
| es, adult nonfiction | 18 | 20.0 | 58.4 | 6.0 | 1.33 | 2.70 | 4.71 | 9.0 | 10.0 | 68 |
| en, philosophy for programmers | 21 | 17.2 | 12.6 | | 1.76 | 5.51 | 5.68 | 12.3 | 30.6 | 89 |
| en, science of computation | 30 | 17.4 | 10.8 | | 1.29 | 2.61 | 5.01 | 11.0 | 25.3 | 94 |
| en, AI for managers | 16 | 16.6 | 10.6 | | 1.18 | 2.66 | 4.93 | 11.1 | 27.1 | 93 |
| en, chatbots | 16 | 12.9 | 9.5 | | 0.59 | 2.52 | 3.90 | 11.1 | 34.3 | 92 |

Within the myths anthology the 23 chapters are close: Crawford 3.4 to 4.5 (σ 0.24), clauses per sentence 0.46 to 0.84. The highest is the part's frame, which is written for an older reader.

## What it showed

- **The formulas separate the Spanish corpora** in the expected order, but Crawford saturates above grade 6, so it says nothing about adult texts.
- **The abridged classics are not simpler on the surface**: their formula scores match the originals (Fernández Huerta 73.8 against 72.0). Their syntax is: a third fewer subordinate clauses per sentence (1.08 against 1.62). A surface-only measure misses this.
- **Frequency lists do not measure children's vocabulary.** `unc%` sits between 10 and 16 % in every corpus. Age-of-acquisition norms separate them (`late%` 0.4 → 3.2 → 10 in Spanish).
- **The Spanish and English norms are not on one scale.** The Spanish ratings stop at 11 ("11 or older") and come from different raters, so `aoa90` cannot be compared across languages.
- **`mdd` 5.51 for one English book is probably an artifact** (lists, tables or long parentheticals left after cleaning), not syntax. Not checked.

## Known weaknesses

- The cleaner is regex over Markdown; each corpus has its own markup.
- Sentence splitting is punctuation-based; dialogue and abbreviations split badly.
- English syllables come from CMUdict with a heuristic fallback (9 of 10 test words right); Spanish syllables from vowel-nucleus rules (24 of 24).
- One number per chapter. The worst passages, which a model would rewrite, need per-sentence and per-paragraph scores.
- No reference corpus with known reading ages, so nothing is calibrated yet: the age mapping is each formula's own.
