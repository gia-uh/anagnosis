# Corpora

Each corpus is a directory with `corpus.yaml` (source, license, citation, language, label scale) and `texts.jsonl` (one document per line: `id`, `text`, `label`, optional `group` and source-specific fields). `anagnosis.corpora.load` refuses any corpus whose license is not CC BY or public domain. No corpus that is not CC BY or public domain is used, not even fetched for evaluation, so that no result depends on non-commercial data. Corpora are released under CC BY 4.0 (`LICENSE`); public-domain texts stay public domain.

Each corpus is rebuilt by a script in this directory, which downloads its sources into `~/.cache/anagnosis/`.

## In the repo

| corpus | lang | labels | source | build |
|---|---|---|---|---|
| `en-school-readers` | en | reader number in its series, 1–7 | US, Canadian and British school readers, 1857–1925, Project Gutenberg | `build_en_readers.py` |
| `en-school-years` | en | school year stated in the title, with ages | US school readers, 1900–1925, Project Gutenberg | `build_en_readers.py` |
| `es-storyweaver` | es | StoryWeaver level 1–5 | StoryWeaver (Pratham Books), CC BY 4.0 per story; 1,289 of 1,384 are translations | `build_storyweaver.py` (needs a free account) |
| `es-cuba-grades` | es | earliest Cuban school grade that reads the text, 3–8, with ages | public-domain texts (Martí, Darío, Quiroga, Lorca, Bécquer, Lope de Vega) from Wikisource, listed from the MINED textbooks | `build_es_cuba_grades.py` |

## Checked and excluded (2026-10-21)

| source | why |
|---|---|
| HablaCultura, Kwiziq, CAES | not CC BY at the source: HablaCultura forbids commercial use; Kwiziq and CAES grant no license. Hugging Face cards that say CC BY 4.0 are the uploader's claim. |
| UniversalCEFR | one license per source set; no Spanish or English set is CC BY |
| OneStopEnglish, Coh-Metrix-Esp, Vikidia | CC BY-SA |
| CLEAR, LengClaro2023 | CC BY-NC-SA |
| Cuban primary and secondary textbooks (MINED, Editorial Pueblo y Educación, biblioteca.cubaeduca.cu) | © Ministerio de Educación and Editorial Pueblo y Educación, 2025: reproduction and "incorporation into a computer system" are forbidden without written authorization. **Pending:** an express permission is being requested from MINED. Until it arrives, the books are used only as a reference for which public-domain texts are read in each grade; those texts are taken from public-domain sources, never from the textbooks. |
