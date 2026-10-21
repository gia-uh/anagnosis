# anagnosis

*ἀνάγνωσις*, "reading" in Greek.

anagnosis measures how hard a text is to read, along several separate dimensions, for Spanish and English. It reports three things:

- **The level:** the reading age or school grade a text sits at, per dimension.
- **The variation:** how much that level moves between the chapters of one book (intra-corpus) and between books (inter-corpus).
- **The worst passages:** the sentences and paragraphs that pull a text above its target, located precisely enough for a person or a language model to rewrite them.

A book declares its target band, for example "readable alone between 8 and 10 years", and anagnosis says which chapters and passages fall outside it.

## Status

This is a research project in its first week. There is no package yet. `experiments/2026-10-21-baseline/` holds the first prototype and its measurements on eight books.

## Dimensions

Six dimensions, kept orthogonal, and an age range derived from them. The design is in `docs/superpowers/specs/2026-10-21-anagnosis-design.html`.

| Dimension | Reads as | Built from |
|---|---|---|
| Lexical difficulty | age by which a reader knows the words | age-of-acquisition norms (Alonso, Fernández and Díez, 2015, for Spanish; Kuperman, Stadthagen-Gonzalez and Brysbaert, 2012, for English), frequency, concreteness |
| Syntactic difficulty | age by which a reader parses the sentences | clauses per sentence, dependency distance, tree depth, sentence length; classic formulas as baselines (Crawford, Fernández Huerta, Szigriszt-Pazos with INFLESZ, Flesch-Kincaid) |
| Specificity | share of the text that needs domain vocabulary | terms and entities extracted with GLiNER |
| Background knowledge | concepts per 100 words assumed and not explained | GLiNER candidates, decided by Laya or an LLM judge |
| Structure | how much the reader must track per scene: characters, viewpoints, time order, parallel threads, nested mental states; organization in expository text | GLiNER, rules over the parse, Laya, an LLM judge |
| Implicit meaning (candidate) | how much meaning is left to infer: theme, irony, figurative language, ambiguity | Laya and an LLM judge |

The age range is the 10th to 90th percentile of per-sentence ages. Only the first two dimensions exist so far, as features in the baseline experiment, and nothing is calibrated yet.

## References

- Crawford, A. N. (1984). *A Spanish Language Fry-Type Readability Procedure: Elementary Level.* Bilingual Education Paper Series 7(8). ERIC ED273119.
- Fernández Huerta, J. (1959). Medidas sencillas de lecturabilidad [Simple measures of readability]. *Consigna*, 29–32.
- Szigriszt Pazos, F. (1993). *Sistemas predictivos de legibilidad del mensaje escrito: fórmula de perspicuidad* [Predictive systems for the legibility of the written message: the perspicuity formula]. Doctoral thesis, Universidad Complutense de Madrid.
- Barrio-Cantalejo, I. M. et al. (2008). Validación de la Escala INFLESZ para evaluar la legibilidad de los textos dirigidos a pacientes [Validation of the INFLESZ scale to evaluate the readability of texts aimed at patients]. *Anales del Sistema Sanitario de Navarra*, 31(2), 135–152.
- Alonso, M. A., Fernández, A., & Díez, E. (2015). Subjective age-of-acquisition norms for 7,039 Spanish words. *Behavior Research Methods*, 47, 268–274.
- Kuperman, V., Stadthagen-Gonzalez, H., & Brysbaert, M. (2012). Age-of-acquisition ratings for 30,000 English words. *Behavior Research Methods*, 44, 978–990.
- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42, 381–392.
- Fernández Vivanco, A., & Sanfilippo, V. (2025). La lecturabilidad de textos escritos en lengua española: revisión crítica de métricas y propuesta de nuevas variables [The readability of texts written in Spanish: a critical review of metrics and a proposal of new variables]. *ELUA*, 44, 29–56.

## License

Code under MIT. Corpora under CC BY 4.0; a corpus enters the repo only if its own license is CC BY or public domain. The age-of-acquisition norms are not redistributed here. `experiments/2026-10-21-baseline/fetch_norms.py` downloads them from the publisher.
