#!/usr/bin/env python3
"""Fetch free full text for the relevant corpus and list paywalled URLs for the user.

Reads data/literature/corpus.csv (from literature_search.py). For each RELEVANT paper not
already in the extracted dataset:
  - epmc_oa_xml : download Europe PMC fullTextXML -> data/literature/fulltext_xml/<id>.xml,
                  parse to text -> data/literature/fulltext_text/<id>.txt
  - pmc_html    : attempt the PMC HTML (often behind a captcha); keep if it yields real text
  - paywalled / failed : add to the ranked download list for manual retrieval

Outputs:
  data/literature/fetched_index.csv     - per paper: id, route, status, chars, url
  data/literature/download_list.md      - ranked paywalled/failed papers with URLs
Full-text files are git-ignored (large, re-fetchable); the index + list are kept.

Run: python3 src/fetch_corpus_fulltext.py [max_oa]
"""
import csv
import os
import sys
import time
import urllib.request
from bs4 import BeautifulSoup
from parse_articles import parse_jats, parse_pmchtml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIT = os.path.join(ROOT, "data", "literature")
XML = os.path.join(LIT, "fulltext_xml")
TXT = os.path.join(LIT, "fulltext_text")
for d in (XML, TXT):
    os.makedirs(d, exist_ok=True)
UA = "Mozilla/5.0 (compatible; research-dataset-builder)"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

# papers already extracted into the main dataset (skip re-fetch)
ALREADY = {"PMC4317028", "PMC6121081", "PMC4932957", "PMC5019199", "PMC6066150",
           "PMC11587506", "17253773"}  # pmcids + martinez pmid


def fetch(url, binary=False, tries=2):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 * (i + 1))
    return None


def is_review(r):
    t = (r["title"] + " " + r["journal"]).lower()
    return any(w in t for w in ["review", "perspective", "minireview"])


def main():
    max_oa = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rows = [r for r in csv.DictReader(open(os.path.join(LIT, "corpus.csv"))) if r["relevant"] == "1"]
    rows.sort(key=lambda r: (int(r["relevance_score"]), int(r["n_queries_matched"])), reverse=True)

    index, download = [], []
    oa_done = 0
    for r in rows:
        pmcid, pmid, doi = r["pmcid"], r["pmid"], r["doi"]
        rid = pmcid or pmid or (doi or "").replace("/", "_")
        if pmcid in ALREADY or pmid in ALREADY:
            index.append(dict(id=rid, route="already_in_dataset", status="skip", chars=0, url=r["url"]))
            continue
        route, status, chars = r["access_route"], "", 0
        # resume: if we already have the parsed text on disk, don't re-fetch
        existing = os.path.join(TXT, f"{pmcid}.txt") if pmcid else ""
        if existing and os.path.exists(existing):
            index.append(dict(id=rid, route=route, status="fetched",
                              chars=os.path.getsize(existing), url=r["url"]))
            continue
        if route == "epmc_oa_xml" and oa_done < max_oa and pmcid:
            raw = fetch(f"{EPMC}/{pmcid}/fullTextXML")
            if raw and len(raw) > 2000 and "<article" in raw[:5000].lower():
                open(os.path.join(XML, f"{pmcid}.xml"), "w").write(raw)
                try:
                    text = parse_jats(BeautifulSoup(raw, "lxml-xml"))
                except Exception:
                    text = ""
                if len(text) > 500:
                    open(os.path.join(TXT, f"{pmcid}.txt"), "w").write(text)
                    status, chars = "fetched", len(text)
                else:
                    status = "parsed_empty"
            else:
                status = "oa_xml_failed"
            oa_done += 1
            time.sleep(0.4)
        elif route == "pmc_html" and pmcid:
            html = fetch(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/")
            if html and "recaptcha" not in html.lower() and html.count("synuclein") > 5:
                try:
                    text = parse_pmchtml(BeautifulSoup(html, "lxml"))
                except Exception:
                    text = ""
                if len(text) > 500:
                    open(os.path.join(TXT, f"{pmcid}.txt"), "w").write(text)
                    status, chars = "fetched_html", len(text)
                else:
                    status = "html_empty"
            else:
                status = "pmc_html_blocked"
            time.sleep(0.4)
        else:
            status = "paywalled"

        index.append(dict(id=rid, route=route, status=status, chars=chars, url=r["url"]))
        if status not in ("fetched", "fetched_html", "skip"):
            download.append(r)

    # write index
    with open(os.path.join(LIT, "fetched_index.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "route", "status", "chars", "url"])
        w.writeheader(); w.writerows(index)

    # ranked download list for the user (paywalled + any failed)
    dl = sorted(download, key=lambda r: (int(r["relevance_score"]), int(r["n_queries_matched"])),
                reverse=True)
    L = ["# Papers to download manually (ranked by relevance)", "",
         f"{len(dl)} papers have no free full text reachable from this session. Download the "
         "PDF (+ SI) and drop it in `data/manual_downloads/<folder>/`, then run "
         "`python3 src/ingest_manual.py`. Open-access papers were fetched automatically "
         "(see `fetched_index.csv`).", "",
         "| # | year | score | cand | title | URL |",
         "|---|---|---|---|---|---|"]
    for i, r in enumerate(dl[:150], 1):
        cand = r["candidates_mentioned"][:18] or "-"
        title = r["title"][:70].replace("|", "/")
        L.append(f"| {i} | {r['year']} | {r['relevance_score']} | {cand} | {title} | {r['url']} |")
    open(os.path.join(LIT, "download_list.md"), "w").write("\n".join(L))

    from collections import Counter
    print("fetched full text:", sum(1 for i in index if i["status"] in ("fetched", "fetched_html")))
    print("status breakdown:", dict(Counter(i["status"] for i in index)))
    print(f"download list: {len(dl)} papers -> data/literature/download_list.md")
    print("fetched text dir: data/literature/fulltext_text/")


if __name__ == "__main__":
    main()
