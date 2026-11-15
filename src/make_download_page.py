#!/usr/bin/env python3
"""Build easy-to-use download lists for papers with no free full text.

Reads data/literature/corpus.csv and, if present, data/literature/fetched_index.csv
(so already-fetched OA papers are excluded). Emits, into data/literature/:
  download_urls.txt   - one URL per line, ranked (feed to a browser/downloader)
  download_list.md    - ranked table (title / journal / year / candidate / URL)
  download_list.html  - clickable page grouped by priority

A paper is "to download" if it is RELEVANT and was not successfully fetched here:
access_route is paywalled or pmc_html (HTML is often captcha-blocked), OR fetched_index
marks it not fetched. DOI links go to the publisher; PMC links to the free reader.
"""
import csv
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIT = os.path.join(ROOT, "data", "literature")


def load_fetched_ok():
    path = os.path.join(LIT, "fetched_index.csv")
    ok = set()
    if os.path.exists(path):
        for r in csv.DictReader(open(path)):
            if r["status"] in ("fetched", "fetched_html", "skip"):
                ok.add(r["id"])
    return ok


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(LIT, "corpus.csv"))) if r["relevant"] == "1"]
    fetched_ok = load_fetched_ok()

    def already(r):
        rid = r["pmcid"] or r["pmid"] or (r["doi"] or "").replace("/", "_")
        return rid in fetched_ok or (r["access_route"] == "epmc_oa_xml" and not fetched_ok)

    # to-download = relevant, not successfully fetched, and not a clean OA we can still get
    todo = []
    for r in rows:
        if r["pmcid"] in fetched_ok or r["pmid"] in fetched_ok:
            continue
        if r["access_route"] == "epmc_oa_xml" and not fetched_ok:
            # OA but fetch not yet run/finished -> we will fetch it ourselves; skip from list
            continue
        if r["access_route"] == "epmc_oa_xml" and fetched_ok:
            # OA that failed to fetch -> include
            rid = r["pmcid"] or r["pmid"]
            if rid in fetched_ok:
                continue
        todo.append(r)
    todo.sort(key=lambda r: (int(r["relevance_score"]), int(r["n_queries_matched"])), reverse=True)

    # urls.txt
    with open(os.path.join(LIT, "download_urls.txt"), "w") as f:
        for r in todo:
            if r["url"]:
                f.write(r["url"] + "\n")

    # markdown
    M = [f"# Download list — {len(todo)} papers with no free full text", "",
         "Ranked by relevance. DOI links go to the publisher (use your institutional access); "
         "PMC links open the free reader. After downloading, drop PDFs in "
         "`data/manual_downloads/<folder>/` and run `python3 src/ingest_manual.py`.", "",
         "| # | yr | score | cand | title | link |", "|--|--|--|--|--|--|"]
    for i, r in enumerate(todo, 1):
        M.append(f"| {i} | {r['year']} | {r['relevance_score']} | {r['candidates_mentioned'][:16] or '-'} "
                 f"| {r['title'][:75].replace('|','/')} | {r['url']} |")
    open(os.path.join(LIT, "download_list.md"), "w").write("\n".join(M))

    # clickable HTML, grouped by priority tier
    def tier(r):
        if r["candidates_mentioned"]:
            return "A - names one of the 8 candidates"
        if int(r["relevance_score"]) >= 9 or r["has_tht"] == "1":
            return "B - high relevance / ThT in abstract"
        return "C - other relevant"
    groups = {}
    for r in todo:
        groups.setdefault(tier(r), []).append(r)

    H = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width, initial-scale=1'>",
         "<title>a-Syn x lipid papers to download</title>",
         "<style>",
         ":root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#e5e5e5;--link:#1a56db;--chip:#eef2ff;}",
         "@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#111;--fg:#e8e8e8;--mut:#9aa;--line:#2a2a2a;--link:#8ab4f8;--chip:#1e293b;}}",
         "body{background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px;}",
         ".wrap{max-width:60em;margin:0 auto;}h1{font-size:1.4rem;}h2{font-size:1.05rem;margin-top:1.6em;border-bottom:1px solid var(--line);padding-bottom:4px;}",
         ".p{padding:8px 0;border-bottom:1px solid var(--line);}",
         ".t{font-weight:600;} .m{color:var(--mut);font-size:.86rem;} a{color:var(--link);text-decoration:none;} a:hover{text-decoration:underline;}",
         ".chip{background:var(--chip);border-radius:10px;padding:1px 7px;font-size:.75rem;margin-left:6px;}",
         ".num{color:var(--mut);margin-right:6px;}",
         "</style></head><body><div class='wrap'>",
         f"<h1>Papers to download — {len(todo)} total</h1>",
         "<p class='m'>Ranked by relevance to &alpha;-synuclein &times; lipid aggregation. "
         "Click a title to open the publisher / PMC page. Use your institutional access to grab the PDF (+ SI), "
         "then drop files in <code>data/manual_downloads/</code> and run <code>src/ingest_manual.py</code>.</p>"]
    for g in ["A - names one of the 8 candidates", "B - high relevance / ThT in abstract", "C - other relevant"]:
        items = groups.get(g, [])
        if not items:
            continue
        H.append(f"<h2>{html.escape(g)} &middot; {len(items)}</h2>")
        for i, r in enumerate(items, 1):
            cand = f"<span class='chip'>{html.escape(r['candidates_mentioned'])}</span>" if r["candidates_mentioned"] else ""
            tht = "<span class='chip'>ThT</span>" if r["has_tht"] == "1" else ""
            url = html.escape(r["url"])
            H.append(f"<div class='p'><div class='t'><span class='num'>{i}.</span>"
                     f"<a href='{url}' target='_blank' rel='noopener'>{html.escape(r['title'])}</a>{cand}{tht}</div>"
                     f"<div class='m'>{html.escape(r['journal'] or '')} &middot; {r['year']} &middot; "
                     f"score {r['relevance_score']} &middot; <a href='{url}' target='_blank' rel='noopener'>{url}</a></div></div>")
    H.append("</div></body></html>")
    open(os.path.join(LIT, "download_list.html"), "w").write("\n".join(H))

    print(f"to-download: {len(todo)}")
    from collections import Counter
    print("by tier:", {k: len(v) for k, v in groups.items()})
    print("-> data/literature/download_list.html / .md / download_urls.txt")


if __name__ == "__main__":
    main()
