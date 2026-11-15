#!/usr/bin/env python3
"""Systematic literature search for alpha-synuclein x lipid aggregation papers.

Runs a battery of Europe PMC queries (title/abstract scoped), aggregates + dedups the
results, scores each by abstract relevance, classifies the free-full-text access route,
and writes a master corpus. Deterministic and rerunnable.

Outputs:
  data/literature/corpus.csv     - one row per unique paper (metadata + abstract + score)
  data/literature/_search_log.json

Access routes:
  epmc_oa_xml   - open access, full text via Europe PMC fullTextXML (we CAN fetch)
  pmc_html      - in PMC but not OA; HTML sometimes fetchable (may hit a captcha)
  paywalled     - no free full text here; give the user the DOI URL to download
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIT = os.path.join(ROOT, "data", "literature")
os.makedirs(LIT, exist_ok=True)
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = "Mozilla/5.0 (compatible; research-dataset-builder)"

# --- query battery (title/abstract scoped for precision) ------------------
# EPMC supports TITLE: and ABSTRACT: field tags; we OR them via a helper.
def ta(term):
    return f'(TITLE:"{term}" OR ABSTRACT:"{term}")'

SYN = ta("alpha-synuclein")  # EPMC normalises the greek alpha
AGG = '(ABSTRACT:aggregation OR ABSTRACT:fibril OR ABSTRACT:amyloid OR ABSTRACT:fibrillation OR ABSTRACT:"thioflavin")'

QUERIES = [
    f'{SYN} AND (ABSTRACT:lipid OR ABSTRACT:phospholipid OR ABSTRACT:membrane OR ABSTRACT:vesicle OR ABSTRACT:liposome) AND {AGG}',
    f'{SYN} AND (ABSTRACT:ganglioside OR ABSTRACT:GM1 OR ABSTRACT:GM3) AND {AGG}',
    f'{SYN} AND ABSTRACT:cholesterol AND {AGG}',
    f'{SYN} AND (ABSTRACT:sphingomyelin OR ABSTRACT:sphingolipid OR ABSTRACT:ceramide) AND {AGG}',
    f'{SYN} AND (ABSTRACT:phosphatidylserine OR ABSTRACT:phosphatidylcholine OR ABSTRACT:phosphatidylglycerol) AND {AGG}',
    f'{SYN} AND (ABSTRACT:DMPC OR ABSTRACT:DMPS OR ABSTRACT:POPC OR ABSTRACT:POPG OR ABSTRACT:POPS OR ABSTRACT:DOPC OR ABSTRACT:DOPS OR ABSTRACT:DPPC) AND {AGG}',
    f'{SYN} AND ABSTRACT:"thioflavin" AND (ABSTRACT:lipid OR ABSTRACT:membrane OR ABSTRACT:vesicle)',
    f'{SYN} AND {AGG} AND (ABSTRACT:inhibit OR ABSTRACT:suppress OR ABSTRACT:prevent) AND (ABSTRACT:lipid OR ABSTRACT:membrane)',
    f'{SYN} AND (ABSTRACT:"lipid membrane" OR ABSTRACT:"model membrane" OR ABSTRACT:bilayer) AND {AGG}',
    f'{SYN} AND (ABSTRACT:exosome OR ABSTRACT:"lipid raft" OR ABSTRACT:micelle OR ABSTRACT:"fatty acid") AND {AGG}',
    f'{SYN} AND (ABSTRACT:"primary nucleation" OR ABSTRACT:"secondary nucleation" OR ABSTRACT:"aggregation kinetics") AND (ABSTRACT:lipid OR ABSTRACT:membrane OR ABSTRACT:vesicle)',
    f'{SYN} AND ABSTRACT:cardiolipin',
]

# relevance lexicon
LIPID_TERMS = ["lipid", "phospholipid", "membrane", "vesicle", "liposome", "ganglioside",
               "gm1", "gm3", "cholesterol", "sphingomyelin", "sphingolipid", "ceramide",
               "phosphatidyl", "dmpc", "dmps", "popc", "popg", "pops", "dopc", "dops",
               "dppc", "dspc", "cardiolipin", "bilayer", "micelle", "fatty acid",
               "lipid raft", "exosome", "saturat"]
AGG_TERMS = ["aggregat", "fibril", "amyloid", "thioflavin", "tht", "nucleation",
             "oligomer", "fibrillation", "lag time", "half-time", "kinetics"]
CAND = ["cholesterol", "sphingomyelin", "dmpc", "dppc", "dspc", "dopc", "popc", "gm1"]


def fetch_json(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 * (i + 1))
    print("  FETCH FAIL", last)
    return None


def run_query(q, max_results=250):
    out, cursor, got = [], "*", 0
    while got < max_results:
        params = urllib.parse.urlencode({
            "query": q, "format": "json", "resultType": "core",
            "pageSize": 100, "cursorMark": cursor})
        d = fetch_json(f"{EPMC}?{params}")
        if not d:
            break
        res = d.get("resultList", {}).get("result", [])
        out.extend(res)
        got += len(res)
        nxt = d.get("nextCursorMark")
        if not nxt or nxt == cursor or not res:
            break
        cursor = nxt
        time.sleep(0.5)
    return out


def access_route(rec):
    oa = rec.get("isOpenAccess") == "Y"
    in_epmc = rec.get("inEPMC") == "Y"
    in_pmc = rec.get("inPMC") == "Y"
    if oa and in_epmc:
        return "epmc_oa_xml"
    if in_pmc or in_epmc:
        return "pmc_html"
    return "paywalled"


def best_url(rec):
    pmcid = rec.get("pmcid")
    doi = rec.get("doi")
    if pmcid:
        return f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    if doi:
        return f"https://doi.org/{doi}"
    return ""


def relevance(abstract, title):
    text = f"{title} {abstract}".lower()
    has_syn = "synuclein" in text
    lipid_hits = sum(1 for t in LIPID_TERMS if t in text)
    agg_hits = sum(1 for t in AGG_TERMS if t in text)
    cand_hits = sorted({c for c in CAND if c in text})
    tht = 1 if ("thioflavin" in text or "tht" in text) else 0
    score = (2 * has_syn + min(lipid_hits, 5) + min(agg_hits, 5) + 2 * tht + len(cand_hits))
    # gate: must be about alpha-syn AND lipids AND aggregation
    relevant = has_syn and lipid_hits >= 1 and agg_hits >= 1
    return relevant, score, lipid_hits, agg_hits, cand_hits, tht


def main():
    seen = {}  # key -> record
    log = []
    for qi, q in enumerate(QUERIES, 1):
        print(f"[Q{qi}/{len(QUERIES)}] {q[:70]}...")
        res = run_query(q)
        print(f"   {len(res)} hits")
        log.append({"query": q, "hits": len(res)})
        for rec in res:
            key = rec.get("doi") or rec.get("pmid") or rec.get("id") or rec.get("title")
            if not key:
                continue
            key = key.lower().strip()
            if key in seen:
                seen[key]["_matched_queries"].append(qi)
                continue
            rec["_matched_queries"] = [qi]
            seen[key] = rec
        time.sleep(0.5)

    rows = []
    for rec in seen.values():
        abstract = rec.get("abstractText", "") or ""
        title = rec.get("title", "") or ""
        relevant, score, lh, ah, cands, tht = relevance(abstract, title)
        rows.append(dict(
            key=(rec.get("doi") or rec.get("pmid") or rec.get("id") or "").lower(),
            pmid=rec.get("pmid", ""), pmcid=rec.get("pmcid", ""), doi=rec.get("doi", ""),
            title=re.sub(r"\s+", " ", title).strip(),
            year=rec.get("pubYear", ""),
            journal=(rec.get("journalInfo", {}) or {}).get("journal", {}).get("title", ""),
            is_open_access=rec.get("isOpenAccess", ""),
            in_epmc=rec.get("inEPMC", ""), in_pmc=rec.get("inPMC", ""),
            access_route=access_route(rec),
            url=best_url(rec),
            relevant=int(relevant), relevance_score=score,
            n_lipid_terms=lh, n_agg_terms=ah, has_tht=tht,
            candidates_mentioned=";".join(cands),
            n_queries_matched=len(rec["_matched_queries"]),
            cited_by=rec.get("citedByCount", ""),
            abstract=re.sub(r"\s+", " ", abstract).strip(),
        ))
    rows.sort(key=lambda r: (r["relevant"], r["relevance_score"], r["n_queries_matched"]),
              reverse=True)

    import csv
    fields = ["key", "pmid", "pmcid", "doi", "title", "year", "journal", "is_open_access",
              "in_epmc", "in_pmc", "access_route", "url", "relevant", "relevance_score",
              "n_lipid_terms", "n_agg_terms", "has_tht", "candidates_mentioned",
              "n_queries_matched", "cited_by", "abstract"]
    with open(os.path.join(LIT, "corpus.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(LIT, "_search_log.json"), "w") as f:
        json.dump(log, f, indent=2)

    rel = [r for r in rows if r["relevant"]]
    print(f"\nUnique papers: {len(rows)} | relevant: {len(rel)}")
    from collections import Counter
    print("Access routes (relevant):", dict(Counter(r["access_route"] for r in rel)))
    print("With a candidate named (relevant):",
          sum(1 for r in rel if r["candidates_mentioned"]))
    print("-> data/literature/corpus.csv")


if __name__ == "__main__":
    main()
