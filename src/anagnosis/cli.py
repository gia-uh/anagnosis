"""Command line: anagnosis fetch-norms | measure."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys

from . import norms
from .doc import segment
from .extractors import ALL
from .features import LEVELS, table


def _quartiles(values: list[float]) -> tuple[float, float, float]:
    if len(values) == 1:
        return values[0], values[0], values[0]
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return q1, q2, q3


def summary(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Median and quartiles of every numeric feature across rows."""
    out = {}
    for k in rows[0]:
        if k in ("file", "level", "index", "start", "end", "text"):
            continue
        vals = [r[k] for r in rows if isinstance(r.get(k), (int, float))]
        if vals:
            q1, med, q3 = _quartiles(vals)
            out[k] = {"median": med, "q1": q1, "q3": q3, "n": len(vals)}
    return out


def measure(paths, lang, level, exclude) -> list[dict]:
    rows = []
    for path in paths:
        source = open(path, encoding="utf-8").read()
        for r in table(segment(source, lang, exclude), ALL, level):
            row = {"file": path, **r}
            if level != "document":
                row["text"] = " ".join(source[r["start"]:r["end"]].split())
            rows.append(row)
    return rows


def _fmt(v) -> str:
    return "" if v is None else f"{v:.3f}" if isinstance(v, float) else str(v)


def _print_table(rows, summ, out):
    keys = [k for k in rows[0] if k not in ("level", "start", "end", "text")]
    out.write("\t".join(keys) + "\n")
    for r in rows:
        out.write("\t".join(_fmt(r.get(k)) for k in keys) + "\n")
    if summ and len(rows) > 1:
        for stat in ("median", "q1", "q3"):
            out.write("\t".join([stat] + [_fmt(summ.get(k, {}).get(stat)) for k in keys[1:]]) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="anagnosis", description="Multi-dimensional reading complexity.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch-norms", help="download the age-of-acquisition norms into the cache")
    sub.add_parser("features", help="list every feature with its family, languages, levels, source and definition")
    m = sub.add_parser("measure", help="features per sentence, paragraph or document")
    m.add_argument("files", nargs="+")
    m.add_argument("--lang", required=True, choices=["es", "en"])
    m.add_argument("--level", default="document", choices=LEVELS)
    m.add_argument("--exclude-heading", action="append", default=[], metavar="REGEX",
                   help="drop the section under any heading matching REGEX (repeatable)")
    m.add_argument("--format", default="table", choices=["table", "jsonl", "csv"])
    m.add_argument("--summary", action="store_true", help="print only the median and quartiles across units, as JSON")
    a = ap.parse_args(argv)

    if a.cmd == "fetch-norms":
        for lang, n in norms.fetch().items():
            print(f"aoa-{lang}.tsv: {n} words in {norms.cache_dir()}")
        return 0

    if a.cmd == "features":
        for e in ALL:
            for f in e.features:
                print(f"{f.name}\t{f.family}\t{','.join(sorted(f.languages))}\t{','.join(f.levels)}\t{f.source}\t{f.doc}")
        return 0

    try:
        rows = measure(a.files, a.lang, a.level, a.exclude_heading)
    except FileNotFoundError as e:
        print(f"anagnosis: {e}", file=sys.stderr)
        return 2
    if not rows:
        print("anagnosis: no prose found", file=sys.stderr)
        return 1
    summ = summary(rows)
    if a.summary:
        json.dump(summ, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif a.format == "jsonl":
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
    elif a.format == "csv":
        w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    else:
        _print_table(rows, summ, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
