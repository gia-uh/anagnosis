# anagnosis

anagnosis researches how to measure the reading complexity of Spanish and English text along separate dimensions (surface, vocabulary, syntax, semantics), and is the tool that applies it: a book declares its target reading band, and anagnosis reports each chapter's level, the variation within and between corpora, and the passages that fall outside the band, located for a person or a language model to rewrite.

This file changes when the goals change. Nothing in it should be made false by a commit that adds code, an experiment or a report.

## Rules

- **Every metric carries its source and its measurement.** A metric enters with the paper it comes from, or the experiment that justified it, and its values on the reference corpora.
- **Age claims are calibrated or labelled.** A number reported as a reading age is either fitted on texts of known age or marked as the formula's own mapping, with its valid range.
- **Code is MIT, corpora are CC BY 4.0.** A corpus enters only if its own license is CC BY or public domain; CC BY-SA and non-commercial sets stay out.
- **Metrics are implemented here.** Dependencies stay at the level of spaCy and similar basic tools; no readability toolkit is wrapped.
- **Third-party norms are downloaded, never committed.** Their licenses do not allow redistribution.
- **The repo is in English.** Code, comments, docs, commits and reports are English. Spanish appears only as corpus text and as the per-language data that processes it (vowel rules, subordinator lists, corpus headings), and Spanish reference titles carry an English translation in brackets.
- **Language is declared, never guessed.** Syllables, norms and parsers are per language.

## Layout

- `experiments/YYYY-MM-DD-slug/`: one experiment per directory, with its code, a README saying how to run it, the results and what they showed.
