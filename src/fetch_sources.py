#!/usr/bin/env python3
"""Deterministic fetcher for primary/secondary literature sources.

Pulls, for each source:
  1. Europe PMC "core" bibliographic record (JSON)  -> data/raw_meta/<key>.meta.json
  2. Full-text HTML from PMC                          -> data/raw_html/<key>.html
  3. Supplementary file listing (Europe PMC)          -> data/raw_meta/<key>.supp.json
  4. Supplementary archive if available               -> data/raw_supp/<key>.supp.zip

No interpretation happens here; this only retrieves bytes and records provenance.
Run: python3 src/fetch_sources.py
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
META = os.path.join(ROOT, "data", "raw_meta")
HTML = os.path.join(ROOT, "data", "raw_html")
SUPP = os.path.join(ROOT, "data", "raw_supp")
for d in (META, HTML, SUPP):
    os.makedirs(d, exist_ok=True)

UA = "Mozilla/5.0 (compatible; research-dataset-builder)"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

# key -> identifiers. role: primary_aggregation / primary_support / review / assay_ref
SOURCES = [
    dict(key="martinez2007", pmcid=None, doi="10.1021/bi061749a",
         title="GM1 Specifically Interacts with alpha-Synuclein and Inhibits Fibrillation",
         role="primary_aggregation"),
    dict(key="grey2015", pmcid="PMC4317028", doi="10.1074/jbc.M114.585703",
         title="Acceleration of alpha-Synuclein Aggregation by Exosomes",
         role="primary_aggregation"),
    dict(key="galvagnion2016", pmcid="PMC4932957", doi="10.1073/pnas.1601899113",
         title="Chemical properties of lipids strongly affect the kinetics of the membrane-induced aggregation of alpha-synuclein",
         role="primary_aggregation"),
    dict(key="galvagnion2015", pmcid="PMC5019199", doi="10.1038/nchembio.1750",
         title="Lipid vesicles trigger alpha-synuclein aggregation by stimulating primary nucleation",
         role="primary_aggregation"),
    dict(key="gaspar2018", pmcid="PMC6121081", doi="10.1039/c7sc04367c",
         title="Ganglioside lipids accelerate alpha-synuclein amyloid formation",
         role="primary_aggregation"),
    dict(key="tht_assay2018", pmcid="PMC6066150", doi=None,
         title="alpha-Synuclein Aggregation Monitored by Thioflavin T Fluorescence Assay",
         role="assay_ref"),
]


def fetch(url, binary=False, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa
            last = e
            time.sleep(2 * (i + 1))
    print(f"    FAILED {url}: {last}", file=sys.stderr)
    return None


def epmc_core(src):
    if src["pmcid"]:
        q = f"PMCID:{src['pmcid']}"
    elif src["doi"]:
        q = f"DOI:{src['doi']}"
    else:
        q = src["title"]
    url = f"{EPMC}/search?query={urllib.parse.quote(q)}&resultType=core&format=json"
    txt = fetch(url)
    if not txt:
        return None
    try:
        d = json.loads(txt)
        res = d.get("resultList", {}).get("result", [])
        return res[0] if res else None
    except Exception:
        return None


import urllib.parse  # noqa: E402

log = []
for src in SOURCES:
    key = src["key"]
    print(f"[{key}] {src['title'][:60]}")
    rec = epmc_core(src)
    status = {"key": key, "role": src["role"], "requested": src}
    if rec:
        pmcid = rec.get("pmcid") or src["pmcid"]
        src["pmcid"] = pmcid
        status.update(pmid=rec.get("pmid"), pmcid=pmcid,
                      isOpenAccess=rec.get("isOpenAccess"),
                      inPMC=rec.get("inPMC"), inEPMC=rec.get("inEPMC"),
                      hasPDF=rec.get("hasPDF"),
                      journal=rec.get("journalInfo", {}).get("journal", {}).get("title"),
                      year=rec.get("pubYear"))
        with open(os.path.join(META, f"{key}.meta.json"), "w") as f:
            json.dump(rec, f, indent=2)
        print(f"    meta ok  pmcid={pmcid} OA={rec.get('isOpenAccess')} inPMC={rec.get('inPMC')}")
    else:
        print("    meta MISSING")
        status["meta"] = "missing"

    pmcid = src["pmcid"]
    # Full text HTML from PMC
    if pmcid:
        html = fetch(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/")
        if html and len(html) > 2000:
            with open(os.path.join(HTML, f"{key}.html"), "w") as f:
                f.write(html)
            status["html_bytes"] = len(html)
            print(f"    html ok  {len(html)} bytes")
        else:
            status["html"] = "failed_or_tiny"
            print("    html FAILED")
        # Supplementary listing + archive
        supp = fetch(f"{EPMC}/{pmcid}/supplementaryFiles", binary=True)
        if supp and len(supp) > 200:
            with open(os.path.join(SUPP, f"{key}.supp.zip"), "wb") as f:
                f.write(supp)
            status["supp_bytes"] = len(supp)
            print(f"    supp ok  {len(supp)} bytes")
        else:
            status["supp"] = "none"
    else:
        status["html"] = "no_pmcid"
    log.append(status)
    time.sleep(1)

with open(os.path.join(META, "_fetch_log.json"), "w") as f:
    json.dump(log, f, indent=2)
print("\nDone. Log -> data/raw_meta/_fetch_log.json")
