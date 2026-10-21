"""Surface metrics and classic readability formulas for Spanish and English book chapters."""
import re, sys, glob, statistics as st
from wordfreq import zipf_frequency

WORD = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*")

def clean(md: str, lang: str) -> str:
    if md.startswith("---\n"):
        md = md.split("\n---\n", 1)[1]
    md = md.split("\n## Para padres")[0].split("\n## For parents")[0]
    md = re.sub(r"(?s)```.*?```", "", md)
    md = re.sub(r"(?m)^\s*(#.*|!\[.*|<.*>|\|.*|---+|:::.*|\$\$.*)$", "", md)
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"\{[^}]*\}|\[\^[^\]]*\]|[*_`>]", "", md)
    return md

def sentences(text):
    parts = re.split(r"(?<=[.!?…])[\"”»)]*\s+|\n\s*\n", text)
    return [s for s in parts if WORD.search(s)]

STRONG = set("aeoáéóíú")
def syl_es(w):
    w = w.lower()
    w = re.sub(r"(?<=[qg])u(?=[eiéí])", "", w)
    w = re.sub(r"y$", "i", w) if len(w) > 1 else "i"
    w = w.replace("y", "")  # consonantal y elsewhere
    n = 0
    for run in re.findall(r"[aeiouáéíóúü]+", w):
        k = 1
        for a, b in zip(run, run[1:]):
            if a in STRONG and b in STRONG:
                k += 1
        n += k
    return max(n, 1)

import cmudict
CMU = cmudict.dict()
def syl_en(w):
    w = w.lower()
    if w in CMU:
        return sum(ph[-1].isdigit() for ph in CMU[w][0])
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(len(re.findall(r"[aeiouy]{1,2}", w)), 1)

SUB = {
    "es": "que porque cuando aunque mientras si donde como cuyo cuya quien quienes cual cuales pues hasta".split(),
    "en": "that which who whom whose because although though when while if where since unless until whereas".split(),
}

def mtld_pass(toks, thr=0.72):
    factors, types, count = 0.0, set(), 0
    for t in toks:
        count += 1; types.add(t)
        if len(types) / count <= thr:
            factors += 1; types, count = set(), 0
    if count:
        factors += (1 - len(types) / count) / (1 - thr)
    return len(toks) / factors if factors else len(toks)

def measure(text, lang):
    sents = sentences(text)
    raw = WORD.findall(text)
    lower_seen = {w for w in raw if w.islower()}
    proper = {w.lower() for w in raw if w[0].isupper() and w.lower() not in lower_seen}
    words = [w.lower() for w in raw]
    common = [w for w in words if w not in proper]
    W, S = len(words), len(sents)
    syl = syl_es if lang == "es" else syl_en
    sy = sum(syl(w) for w in words)
    letters = sum(len(w) for w in words)
    wps, spw = W / S, sy / W
    zipfs = [zipf_frequency(w, lang) for w in words]
    m = {
        "words": W,
        "wps": wps,
        "spw": spw,
        "long%": 100 * sum(len(w) > 6 for w in words) / W,
        "lix": wps + 100 * sum(len(w) > 6 for w in words) / W,
        "rare%": 100 * sum(zipf_frequency(w, lang) < 3.0 for w in common) / len(common),
        "unc%": 100 * sum(zipf_frequency(w, lang) < 4.0 for w in common) / len(common),
        "prop%": 100 * (W - len(common)) / W,
        "zipf": st.mean(zipfs),
        "mtld": (mtld_pass(words) + mtld_pass(words[::-1])) / 2,
        "sub/s": sum(w in SUB[lang] for w in words) / S,
    }
    if lang == "es":
        m["fh"] = 206.84 - 60 * spw - 1.02 * wps
        m["szig"] = 206.835 - 62.3 * spw - wps
        m["polini"] = 95.2 - 9.7 * letters / W - 0.35 * wps
        m["craw"] = -0.205 * 100 * S / W + 0.049 * 100 * spw - 3.407
    else:
        m["fre"] = 206.835 - 1.015 * wps - 84.6 * spw
        m["fkgl"] = 0.39 * wps + 11.8 * spw - 15.59
        m["cli"] = 0.0588 * 100 * letters / W - 0.296 * 100 * S / W - 15.8
    return m

if __name__ == "__main__":
    lang, label, pats = sys.argv[1], sys.argv[2], sys.argv[3:]
    files = sorted(f for p in pats for f in glob.glob(p, recursive=True))
    texts = [clean(open(f).read(), lang) for f in files]
    rows = [measure(t, lang) for t in texts if len(WORD.findall(t)) > 300]
    rows = [r for r in rows if r["words"] > 300]
    keys = list(rows[0])
    if label == "-":
        for f, r in zip(files, rows):
            print(f"{f.split('/')[-1][:22]:22} " + " ".join(f"{k}={r[k]:.1f}" for k in keys[1:]))
        sys.exit()
    print(f"{label:22} n={len(rows):3} " + " ".join(f"{k}={st.median(r[k] for r in rows):.1f}" for k in keys[1:]))
