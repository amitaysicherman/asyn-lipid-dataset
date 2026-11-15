#!/usr/bin/env python3
"""Parse fetched JATS-XML and PMC-HTML articles into clean structured text.

Outputs one readable text dump per paper to data/extracted_text/<key>.txt with:
  - title, abstract
  - body sections (heading + paragraphs)
  - figure captions (labelled [FIGURE ...])
  - tables rendered as text (labelled [TABLE ...])

This is a deterministic extraction aid for human/LLM reading. It does NOT
interpret or compute anything.
"""
import os
import re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML = os.path.join(ROOT, "data", "raw_html")
OUT = os.path.join(ROOT, "data", "extracted_text")
os.makedirs(OUT, exist_ok=True)

# key -> (filename, format)
ARTICLES = {
    "grey2015": ("PMC4317028.xml", "jats"),
    "gaspar2018": ("PMC6121081.xml", "jats"),
    "galvagnion2016": ("galvagnion2016.html", "pmchtml"),
    "galvagnion2015": ("galvagnion2015.html", "pmchtml"),
    "tht_assay2018": ("tht_assay2018.html", "pmchtml"),
}


def clean(s):
    return re.sub(r"[ \t]+", " ", re.sub(r"\s*\n\s*", " ", (s or "").strip()))


def table_to_text(tbl):
    rows = []
    for tr in tbl.find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in tr.find_all(["td", "th"])]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def parse_jats(soup):
    out = []
    title = soup.find("article-title")
    out.append("TITLE: " + clean(title.get_text(" ")) if title else "TITLE: ?")
    abs_ = soup.find("abstract")
    if abs_:
        out.append("\nABSTRACT:\n" + clean(abs_.get_text(" ")))
    body = soup.find("body")
    if body:
        out.append("\n==== BODY ====")
        for el in body.find_all(["sec", "p"], recursive=True):
            if el.name == "sec":
                t = el.find("title", recursive=False)
                if t:
                    out.append("\n## " + clean(t.get_text(" ")))
        # paragraphs in document order (excluding those inside fig/table captions)
        for p in body.find_all("p"):
            if p.find_parent(["fig", "table-wrap", "caption"]):
                continue
            txt = clean(p.get_text(" "))
            if txt:
                out.append(txt)
    # figures
    for fig in soup.find_all("fig"):
        label = clean((fig.find("label").get_text(" ") if fig.find("label") else ""))
        cap = fig.find("caption")
        out.append(f"\n[FIGURE {label}] " + (clean(cap.get_text(" ")) if cap else ""))
    # tables
    for tw in soup.find_all("table-wrap"):
        label = clean((tw.find("label").get_text(" ") if tw.find("label") else ""))
        cap = tw.find("caption")
        out.append(f"\n[TABLE {label}] " + (clean(cap.get_text(" ")) if cap else ""))
        t = tw.find("table")
        if t:
            out.append(table_to_text(t))
    return "\n".join(out)


def parse_pmchtml(soup):
    out = []
    # title
    h1 = soup.find("h1")
    out.append("TITLE: " + clean(h1.get_text(" ")) if h1 else "TITLE: ?")
    # abstract
    abs_ = soup.find(attrs={"id": re.compile("^abstract", re.I)}) or soup.find("section", class_=re.compile("abstract", re.I))
    if abs_:
        out.append("\nABSTRACT:\n" + clean(abs_.get_text(" ")))
    # main article body: PMC wraps in <section class="body main-article-body"> or article
    body = (soup.find("section", class_=re.compile("main-article-body", re.I))
            or soup.find("div", class_=re.compile("article|tsec", re.I))
            or soup.find("article"))
    out.append("\n==== BODY ====")
    if body:
        for el in body.find_all(["h2", "h3", "h4", "p"]):
            if el.find_parent("figure") or el.find_parent(attrs={"class": re.compile("fig|table", re.I)}):
                continue
            txt = clean(el.get_text(" "))
            if not txt:
                continue
            if el.name in ("h2", "h3", "h4"):
                out.append("\n## " + txt)
            else:
                out.append(txt)
    # figures (PMC html uses <figure> with <figcaption>)
    for fig in soup.find_all("figure"):
        cap = fig.find("figcaption") or fig
        label = ""
        lab = fig.find(class_=re.compile("fig-label|label", re.I))
        if lab:
            label = clean(lab.get_text(" "))
        out.append(f"\n[FIGURE {label}] " + clean(cap.get_text(" ")))
    # tables
    for tbl in soup.find_all("table"):
        wrap = tbl.find_parent(class_=re.compile("table", re.I))
        cap = None
        if wrap:
            cap = wrap.find("caption") or wrap.find(class_=re.compile("caption", re.I))
        out.append(f"\n[TABLE] " + (clean(cap.get_text(' ')) if cap else ""))
        out.append(table_to_text(tbl))
    return "\n".join(out)


for key, (fn, fmt) in ARTICLES.items():
    path = os.path.join(HTML, fn)
    if not os.path.exists(path):
        print(f"skip {key}: {fn} missing")
        continue
    raw = open(path, encoding="utf-8", errors="replace").read()
    soup = BeautifulSoup(raw, "lxml-xml" if fmt == "jats" else "lxml")
    text = parse_jats(soup) if fmt == "jats" else parse_pmchtml(soup)
    with open(os.path.join(OUT, f"{key}.txt"), "w") as f:
        f.write(text)
    print(f"{key}: {len(text)} chars -> data/extracted_text/{key}.txt")
