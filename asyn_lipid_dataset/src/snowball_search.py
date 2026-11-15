#!/usr/bin/env python3
"""Citation-snowball search: find more relevant papers from the references and citing
papers of the known-good seeds (the densest pool of on-topic primary studies).

For each seed we pull its Europe PMC references + citations, dedup against the existing
corpus, batch-fetch core metadata (abstract + OA status) for the new ones, keep those that
pass the relevance gate (alpha-syn AND lipid AND aggregation), and fetch free full text for
the open-access ones.

Outputs (data/literature/):
  corpus_snowball.csv  - the new relevant papers (same columns as corpus.csv)
  adds fetched full texts to fulltext_text/ ; appends to fetched_index.csv
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from parse_articles import parse_jats
from literature_search import relevance, access_route, best_url

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIT = os.path.join(ROOT, "data", "literature")
TXT = os.path.join(LIT, "fulltext_xml")
TEXT = os.path.join(LIT, "fulltext_text")
for d in (TXT, TEXT):
    os.makedirs(d, exist_ok=True)
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = "Mozilla/5.0 (compatible; research-dataset-builder)"

# most-relevant seeds (primary lipid x alpha-syn aggregation studies)
SEEDS = ["27298346", "25580854", "29803858", "25425650", "17253773", "39469734",
         "12482878", "12859192", "14555644"]  # last 3: Fink-lab lipid/fibrillation JBC 2003 etc.


def fetch(url, binary=False, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def fetch_json(url):
    t = fetch(url)
    try:
        return json.loads(t) if t else None
    except Exception:
        return None


def linked_pmids(pmid, kind):
    """kind = 'references' or 'citations'. Return set of linked PMIDs."""
    out, page = set(), 1
    while page <= 6:
        url = f"{EPMC}/MED/{pmid}/{kind}?format=json&pageSize=1000&page={page}"
        d = fetch_json(url)
        if not d:
            break
        stem = kind[:-1]  # 'references' -> 'reference', 'citations' -> 'citation'
        items = d.get(stem + "List", {}).get(stem, [])
        if not items:
            break
        for it in items:
            pid = it.get("id") if it.get("source") == "MED" else it.get("pmid")
            if pid and str(pid).isdigit():
                out.add(str(pid))
        if len(items) < 1000:
            break
        page += 1
        time.sleep(0.3)
    return out


def core_lookup(pmids):
    """Batch EXT_ID core lookups -> list of records with abstract + OA."""
    recs = []
    pmids = list(pmids)
    for i in range(0, len(pmids), 25):
        chunk = pmids[i:i + 25]
        q = "(" + " OR ".join(f"EXT_ID:{p}" for p in chunk) + ") AND SRC:MED"
        url = f"{EPMC}/search?query={urllib.parse.quote(q)}&resultType=core&pageSize=25&format=json"
        d = fetch_json(url)
        if d:
            recs.extend(d.get("resultList", {}).get("result", []))
        time.sleep(0.4)
    return recs


def main():
    existing = set()
    for r in csv.DictReader(open(os.path.join(LIT, "corpus.csv"))):
        if r["pmid"]:
            existing.add(r["pmid"])
    print(f"corpus has {len(existing)} pmids")

    # 1. gather linked pmids from all seeds
    linked = set()
    for s in SEEDS:
        refs = linked_pmids(s, "references")
        cites = linked_pmids(s, "citations")
        print(f"  seed {s}: {len(refs)} refs, {len(cites)} citations")
        linked |= refs | cites
        time.sleep(0.3)
    new = sorted(linked - existing)
    print(f"new linked pmids (not already in corpus): {len(new)}")

    # 2. core metadata for the new ones
    recs = core_lookup(new)
    print(f"core records retrieved: {len(recs)}")

    # 3. relevance filter + build rows
    rows = []
    for rec in recs:
        abstract = rec.get("abstractText", "") or ""
        title = rec.get("title", "") or ""
        relevant, score, lh, ah, cands, tht = relevance(abstract, title)
        if not relevant:
            continue
        rows.append(dict(
            pmid=rec.get("pmid", ""), pmcid=rec.get("pmcid", ""), doi=rec.get("doi", ""),
            title=title.strip(), year=rec.get("pubYear", ""),
            journal=(rec.get("journalInfo", {}) or {}).get("journal", {}).get("title", ""),
            is_open_access=rec.get("isOpenAccess", ""), in_epmc=rec.get("inEPMC", ""),
            in_pmc=rec.get("inPMC", ""), access_route=access_route(rec), url=best_url(rec),
            relevance_score=score, candidates_mentioned=";".join(cands), has_tht=tht,
            abstract=abstract.strip().replace("\n", " "),
        ))
    rows.sort(key=lambda r: r["relevance_score"], reverse=True)
    with open(os.path.join(LIT, "corpus_snowball.csv"), "w", newline="") as f:
        cols = ["pmid", "pmcid", "doi", "title", "year", "journal", "is_open_access",
                "in_epmc", "in_pmc", "access_route", "url", "relevance_score",
                "candidates_mentioned", "has_tht", "abstract"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    # 4. fetch OA full text for the new relevant papers
    fetched = 0
    for r in rows:
        pmcid = r["pmcid"]
        if r["access_route"] == "epmc_oa_xml" and pmcid and not os.path.exists(os.path.join(TEXT, f"{pmcid}.txt")):
            raw = fetch(f"{EPMC}/{pmcid}/fullTextXML")
            if raw and "<article" in raw[:5000].lower():
                open(os.path.join(TXT, f"{pmcid}.xml"), "w").write(raw)
                try:
                    text = parse_jats(BeautifulSoup(raw, "lxml-xml"))
                except Exception:
                    text = ""
                if len(text) > 500:
                    open(os.path.join(TEXT, f"{pmcid}.txt"), "w").write(text)
                    fetched += 1
            time.sleep(0.4)

    from collections import Counter
    print(f"\nNEW relevant papers (snowball): {len(rows)}")
    print("access routes:", dict(Counter(r["access_route"] for r in rows)))
    print(f"NEW open-access full texts fetched: {fetched}")
    print("candidate-naming:", sum(1 for r in rows if r["candidates_mentioned"]))
    print("-> data/literature/corpus_snowball.csv")


if __name__ == "__main__":
    main()
