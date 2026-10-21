"""Syntactic features from the dependency parse."""
from ..features import Feature, Pool, ratio

BOTH = frozenset({"es", "en"})
# Dependency labels that open a subordinate or paratactic clause in the spaCy
# models for Spanish (UD) and English (ClearNLP). xcomp is left out: "quiso volver"
# is one clause for a reader.
CLAUSE = {"advcl", "acl", "acl:relcl", "relcl", "ccomp", "csubj", "csubj:pass", "csubjpass", "parataxis"}


def _depth(tok) -> int:
    d = 0
    while tok.head.i != tok.i:
        tok, d = tok.head, d + 1
    return d


class Syntax:
    family = "syntax"
    features = [
        Feature("clauses_per_sentence", "syntax", BOTH, "anagnosis",
                "subordinate and paratactic clauses per sentence", ratio("clauses", "parsed_sentences")),
        Feature("mean_dependency_distance", "syntax", BOTH, "liu2008",
                "mean distance in words between a word and its head, punctuation excluded", ratio("dep_distance", "dependencies")),
        Feature("mean_tree_depth", "syntax", BOTH, "anagnosis",
                "mean over sentences of the longest path from a word to the root", ratio("depth", "parsed_sentences")),
    ]

    def measure(self, sentence, lang: str) -> Pool:
        toks = [t for t in sentence.span if not t.is_punct and not t.is_space]
        p = Pool()
        if len(toks) < 2:
            return p
        index = {t.i: n for n, t in enumerate(toks)}  # positions with punctuation removed
        deps = [(index[t.i], index[t.head.i]) for t in toks if t.head.i != t.i and t.head.i in index]
        p.counts.update(
            parsed_sentences=1,
            clauses=sum(t.dep_ in CLAUSE for t in toks),
            dep_distance=sum(abs(a - b) for a, b in deps),
            dependencies=len(deps),
            depth=max(_depth(t) for t in toks),
        )
        return p
