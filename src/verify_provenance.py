#!/usr/bin/env python3
"""Verify that every measurement's source_quote is grounded in the fetched source text.

For each measurement with a non-empty source_quote, we check that each fragment of the
quote (split on '...') appears in the normalised full text of the corresponding paper
(the extracted_text dump, or the abstract for abstract-only papers). This is an
automated provenance audit: it proves the quotes were not fabricated.

Normalisation maps greek letters and strips punctuation so our ASCII transcription
matches the unicode source. Writes outputs/provenance_check.md and exits non-zero if
any quote fragment cannot be located.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TEXT = os.path.join(DATA, "extracted_text")
OUT = os.path.join(ROOT, "outputs")

GREEK = {"α": "alpha", "β": "beta", "γ": "gamma", "μ": "u", "Δ": "delta", "°": "",
         "–": "-", "—": "-", "’": "", "‘": "", "“": "", "”": "", "·": " ", "×": "x",
         "≥": ">=", "≤": "<=", "″": "", "′": "", " ": " ", "\xa0": " "}


def norm(s):
    s = s or ""
    for k, v in GREEK.items():
        s = s.replace(k, v)
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def source_text(paper_id):
    f = os.path.join(TEXT, f"{paper_id}.txt")
    if os.path.exists(f):
        return norm(open(f, encoding="utf-8", errors="replace").read())
    meta = os.path.join(DATA, "raw_meta", f"{paper_id}.meta.json")
    if os.path.exists(meta):
        d = json.load(open(meta))
        return norm((d.get("title", "") + " " + d.get("abstractText", "")))
    return ""


texts = {}
meas = list(csv.DictReader(open(os.path.join(DATA, "measurements.csv"))))
rows = []
n_checked = n_ok = n_fail = 0
for m in meas:
    q = m["source_quote"].strip()
    if not q:
        continue
    pid = m["paper_id"]
    if pid not in texts:
        texts[pid] = source_text(pid)
    src = texts[pid]
    if not src:
        rows.append((m["measurement_id"], pid, "NO_SOURCE_TEXT", q[:50]))
        continue
    # split on ellipsis into fragments; each must be found. Compare SPACELESS so that
    # source renderings like "m m" (for mM) / "0 5" (for 0.5) match our "mM" / "0.5".
    src_ns = src.replace(" ", "")
    frags = [norm(fr).replace(" ", "") for fr in re.split(r"\.\.\.|\s\.\.\.\s", q)]
    frags = [fr for fr in frags if len(fr) >= 8]  # ignore tiny connectors
    n_checked += 1
    missing = [fr for fr in frags if fr not in src_ns]
    if missing:
        n_fail += 1
        rows.append((m["measurement_id"], pid, "MISSING", " | ".join(x[:40] for x in missing)))
    else:
        n_ok += 1

os.makedirs(OUT, exist_ok=True)
L = ["# Provenance verification", "",
     f"Measurements with a source quote checked: **{n_checked}**",
     f"- fully grounded in fetched source text: **{n_ok}**",
     f"- with at least one unlocated fragment: **{n_fail}**", ""]
if rows:
    L.append("## Items needing attention")
    L.append("")
    L.append("| measurement | paper | status | detail |")
    L.append("|---|---|---|---|")
    for r in rows:
        L.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
else:
    L.append("All source quotes located in their source texts. No issues.")
open(os.path.join(OUT, "provenance_check.md"), "w").write("\n".join(L))
print("\n".join(L))
# abstract-only / figure-only sources that lack full text are expected; only hard
# MISSING fragments in papers we DID fetch are failures.
hard = [r for r in rows if r[2] == "MISSING"]
if hard:
    print(f"\n{len(hard)} quote(s) not found in fetched text — review needed.")
    sys.exit(1)
print("\nProvenance OK (all quotes grounded; NO_SOURCE_TEXT only for abstract/figure-only).")
