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

| Dimension | Measures | Sources |
|---|---|---|
| Surface | words per sentence, syllables per word, classic formulas | Crawford (1984), Fernández Huerta (1959), Szigriszt-Pazos (1993) with the INFLESZ scale (Barrio-Cantalejo et al., 2008), Flesch-Kincaid |
| Vocabulary | the age at which the content words of a text are learned | age-of-acquisition norms: Alonso, Fernández and Díez (2015) for 7,039 Spanish words; Kuperman, Stadthagen-Gonzalez and Brysbaert (2012) for 30,000 English words |
| Syntax | subordinate clauses per sentence, mean dependency distance, parse-tree depth | dependency parses from spaCy |
| Semantics | not started | |

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

MIT. The age-of-acquisition norms are not redistributed here. `experiments/2026-10-21-baseline/fetch_norms.py` downloads them from the publisher.
