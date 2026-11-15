#!/usr/bin/env python3
"""Stricter re-ranking of the corpus to find PRIMARY in-vitro lipid x aggregation studies.

The first pass (literature_search.py) scored on loose keyword presence, so reviews,
lipidomics surveys and animal-model papers that merely *mention* a lipid ranked high.
This pass reads data/literature/corpus.csv and scores each abstract for the specific
thing we want: an in-vitro experiment where a LIPID modulates alpha-synuclein aggregation,
measured by a kinetic/ThT readout. It flags and down-ranks reviews / lipidomics / purely
cellular or in-vivo papers.

Outputs (data/literature/):
  shortlist.csv            - all papers with the refined score + priority_class + flags
  shortlist_priority.html  - clickable, grouped by priority (A1 best -> C)
  shortlist_priority.md
"""
import csv
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIT = os.path.join(ROOT, "data", "literature")

INVITRO = ["thioflavin", "tht ", "aggregation kinetic", "fibril formation", "fibrillation",
           "nucleation", "lag time", "lag-time", "half-time", "half time", "t1/2",
           "aggregation rate", "amyloid formation", "aggregation assay"]
MEMBRANE = ["vesicle", "liposome", "suv", "luv", "guv", "micelle", "bilayer",
            "lipid membrane", "model membrane", "phospholipid", "lipid vesicle"]
MODULATE = ["accelerat", "inhibit", "promot", "trigger", "suppress", "retard", "modulat",
            "catalyi", "catalyz", "catalys", "enhance", "affect", "slow", "prevent", "delay"]
SPECIFIC_LIPID = ["cholesterol", "sphingomyelin", "ganglioside", "gm1", "gm3", "dmpc",
                  "dppc", "dspc", "dopc", "popc", "dmps", "dops", "pops", "popg", "dopg",
                  "cardiolipin", "phosphatidylserine", "phosphatidylglycerol", "ceramide",
                  "phosphatidylcholine", "fatty acid", "oleic", "palmitic"]
CAND = ["cholesterol", "sphingomyelin", "gm1", "dmpc", "dppc", "dspc", "dopc", "popc"]
EXCLUDE_REVIEW = ["review", "perspective", "minireview", "we review", "this review",
                  "overview of", "current understanding", "recent advances"]
EXCLUDE_OMICS = ["lipidomic", "lipidomics", "mass spectrometry imaging", "untargeted lipid"]
EXCLUDE_INVIVO = ["caenorhabditis", "c. elegans", "drosophila", "mouse model", "mice were",
                  "rat model", "zebrafish", "transgenic", "clinical", "cerebrospinal",
                  "patients", "epidemiolog"]


def has_any(text, terms):
    return sum(1 for t in terms if t in text)


def classify(r):
    text = (r["title"] + " . " + r["abstract"]).lower()
    invitro = has_any(text, INVITRO)
    membrane = has_any(text, MEMBRANE)
    modulate = has_any(text, MODULATE)
    specific = sorted({t for t in SPECIFIC_LIPID if t in text})
    cands = sorted({c for c in CAND if c in text})
    is_review = has_any(text, EXCLUDE_REVIEW) > 0 or has_any((r["journal"] or "").lower(), ["review"])
    is_omics = has_any(text, EXCLUDE_OMICS) > 0 and invitro == 0
    is_invivo = has_any(text, EXCLUDE_INVIVO) >= 2 and membrane == 0

    # refined score: reward the specific in-vitro lipid-modulation signal
    score = (min(invitro, 3) * 2 + min(membrane, 3) * 2 + min(modulate, 2) +
             min(len(specific), 3) + 2 * len(cands))
    if is_review:
        score -= 4
    if is_omics:
        score -= 5
    if is_invivo:
        score -= 3

    # priority class
    core = invitro >= 1 and membrane >= 1 and not is_review and not is_omics
    if core and cands and modulate >= 1:
        pc = "A1 - tests a candidate's effect on aggregation in vitro"
    elif core and (specific and modulate >= 1):
        pc = "A2 - tests a (non-candidate) lipid's effect on aggregation in vitro"
    elif core:
        pc = "B - in-vitro lipid + aggregation, modulation unclear"
    elif is_review:
        pc = "D - review / perspective (reference-mining only)"
    elif is_omics:
        pc = "D - lipidomics / observational (separate evidence category)"
    elif is_invivo:
        pc = "D - cellular / in-vivo model (separate evidence category)"
    else:
        pc = "C - tangential"
    return dict(refined_score=score, invitro=invitro, membrane=membrane, modulate=modulate,
                specific_lipids=";".join(specific), candidates=";".join(cands),
                is_review=int(is_review), is_omics=int(is_omics), is_invivo=int(is_invivo),
                priority_class=pc)


ORDER = ["A1 - tests a candidate's effect on aggregation in vitro",
         "A2 - tests a (non-candidate) lipid's effect on aggregation in vitro",
         "B - in-vitro lipid + aggregation, modulation unclear",
         "C - tangential",
         "D - review / perspective (reference-mining only)",
         "D - lipidomics / observational (separate evidence category)",
         "D - cellular / in-vivo model (separate evidence category)"]


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(LIT, "corpus.csv"))) if r["relevant"] == "1"]
    for r in rows:
        r.update(classify(r))
    rows.sort(key=lambda r: (ORDER.index(r["priority_class"]) if r["priority_class"] in ORDER else 9,
                             -int(r["refined_score"])))

    with open(os.path.join(LIT, "shortlist.csv"), "w", newline="") as f:
        cols = ["priority_class", "refined_score", "candidates", "specific_lipids", "year",
                "journal", "title", "access_route", "url", "pmcid", "doi",
                "invitro", "membrane", "modulate", "is_review", "is_omics", "is_invivo"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    # grouped HTML (prioritise A1/A2/B; list D/C compactly)
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        groups[r["priority_class"]].append(r)

    H = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width, initial-scale=1'><title>a-Syn lipid: priority papers</title>",
         "<style>:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#e5e5e5;--link:#1a56db;--chip:#eef2ff;--good:#dcfce7;}",
         "@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#111;--fg:#e8e8e8;--mut:#9aa;--line:#2a2a2a;--link:#8ab4f8;--chip:#1e293b;--good:#14532d;}}",
         "body{background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px}.wrap{max-width:62em;margin:0 auto}",
         "h1{font-size:1.4rem}h2{font-size:1.02rem;margin-top:1.5em;border-bottom:1px solid var(--line);padding-bottom:4px}",
         ".p{padding:7px 0;border-bottom:1px solid var(--line)}.t{font-weight:600}.m{color:var(--mut);font-size:.84rem}",
         "a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}.chip{background:var(--chip);border-radius:10px;padding:1px 7px;font-size:.73rem;margin-left:6px}",
         ".free{background:var(--good)}.num{color:var(--mut);margin-right:5px}</style></head><body><div class='wrap'>",
         "<h1>&alpha;-Synuclein &times; lipid: priority papers (refined)</h1>",
         "<p class='m'>Re-ranked for <b>primary in-vitro experiments where a lipid modulates aggregation</b>. "
         "Start with <b>A1</b> (tests one of the 8 candidates). A green <span class='chip free'>free</span> chip = full text "
         "already fetched (no need to download). Others: click to open the publisher/PMC page.</p>"]
    for pc in ORDER:
        items = groups.get(pc, [])
        if not items:
            continue
        H.append(f"<h2>{html.escape(pc)} &middot; {len(items)}</h2>")
        for i, r in enumerate(items, 1):
            free = "<span class='chip free'>free</span>" if r["access_route"] == "epmc_oa_xml" else ""
            cand = f"<span class='chip'>{html.escape(r['candidates'])}</span>" if r["candidates"] else ""
            url = html.escape(r["url"])
            H.append(f"<div class='p'><div class='t'><span class='num'>{i}.</span>"
                     f"<a href='{url}' target='_blank' rel='noopener'>{html.escape(r['title'])}</a>{cand}{free}</div>"
                     f"<div class='m'>{html.escape(r['journal'] or '')} &middot; {r['year']} &middot; score {r['refined_score']} "
                     f"&middot; lipids: {html.escape(r['specific_lipids'][:60] or '-')}</div></div>")
    H.append("</div></body></html>")
    open(os.path.join(LIT, "shortlist_priority.html"), "w").write("\n".join(H))

    # markdown of the A-tier only (the ones worth downloading)
    A = [r for r in rows if r["priority_class"].startswith(("A1", "A2"))]
    M = ["# Priority download shortlist (A-tier: primary in-vitro lipid x aggregation)", "",
         f"{len(A)} papers. `free` = already fetched here (skip). Download the rest.", "",
         "| priority | yr | cand | lipids | title | link | free? |", "|--|--|--|--|--|--|--|"]
    for r in A:
        free = "FREE" if r["access_route"] == "epmc_oa_xml" else ""
        M.append(f"| {r['priority_class'][:2]} | {r['year']} | {r['candidates'] or '-'} | "
                 f"{r['specific_lipids'][:30]} | {r['title'][:60].replace('|','/')} | {r['url']} | {free} |")
    open(os.path.join(LIT, "shortlist_priority.md"), "w").write("\n".join(M))

    from collections import Counter
    print("priority classes:", dict(Counter(r["priority_class"][:2] for r in rows)))
    print(f"A-tier (worth downloading): {len(A)}  | of which already free: "
          f"{sum(1 for r in A if r['access_route']=='epmc_oa_xml')}")
    print("-> data/literature/shortlist_priority.html / .md, shortlist.csv")


if __name__ == "__main__":
    main()
