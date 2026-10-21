"""Vocabulary (age of acquisition) and syntax metrics from spaCy parses, plus the surface formulas."""
import sys, glob, statistics as st
import spacy, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from surface import clean, measure

AOA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CONTENT = {"NOUN", "VERB", "ADJ", "ADV"}
CLAUSE = {"advcl", "acl", "acl:relcl", "relcl", "ccomp", "csubj", "csubj:pass", "parataxis"}

def load_aoa(lang):
    return {w: float(a) for w, a in (l.rstrip("\n").split("\t") for l in open(f"{AOA_DIR}/aoa-{lang}.tsv"))}

def depth(tok):
    d = 0
    while tok.head.i != tok.i:
        tok, d = tok.head, d + 1
    return d

def syntax_vocab(text, nlp, aoa):
    doc = nlp(text)
    clauses, dists, depths, sents = [], [], [], 0
    ages, content = [], 0
    for s in doc.sents:
        toks = [t for t in s if not t.is_punct and not t.is_space]
        if len(toks) < 2:
            continue
        sents += 1
        clauses.append(sum(t.dep_ in CLAUSE for t in toks))
        dists += [abs(t.i - t.head.i) for t in toks if t.head.i != t.i]
        depths.append(max(depth(t) for t in toks))
        for t in toks:
            if t.pos_ in CONTENT:
                content += 1
                a = aoa.get(t.lemma_.lower()) or aoa.get(t.text.lower())
                if a is not None:
                    ages.append(a)
    ages.sort()
    return {
        "cl/s": st.mean(clauses),
        "mdd": st.mean(dists),
        "depth": st.mean(depths),
        "aoa": st.mean(ages),
        "aoa90": ages[int(0.9 * len(ages))],
        "late%": 100 * sum(a >= 9 for a in ages) / len(ages),
        "cov%": 100 * len(ages) / content,
    }

if __name__ == "__main__":
    lang, label, pats = sys.argv[1], sys.argv[2], sys.argv[3:]
    nlp = spacy.load({"es": "es_core_news_sm", "en": "en_core_web_sm"}[lang], disable=["ner"])
    nlp.max_length = 3_000_000
    aoa = load_aoa(lang)
    files = sorted(f for p in pats for f in glob.glob(p))
    rows = []
    for f in files:
        t = clean(open(f).read(), lang)
        words = t.split()
        if len(words) < 300:
            continue
        t = " ".join(words[:40000]) if len(words) > 40000 else t
        r = {k: v for k, v in measure(t, lang).items() if k in ("wps", "fh", "craw", "fkgl", "unc%")}
        r.update(syntax_vocab(t, nlp, aoa))
        rows.append((f, r))
    keys = list(rows[0][1])
    if label == "-":
        for f, r in rows:
            print(f"{f.split('/')[-1][:22]:22} " + " ".join(f"{k}={r[k]:.2f}" for k in keys))
    else:
        print(f"{label:16} n={len(rows):3} " + " ".join(f"{k}={st.median(r[k] for _, r in rows):.2f}" for k in keys))
