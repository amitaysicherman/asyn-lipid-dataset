#!/usr/bin/env python3
"""Ingest manually-downloaded papers / supplementary (PDF, DOCX) into readable text.

Scans data/manual_downloads/ recursively, extracts text AND tables from each file, and
writes a clean dump per file to data/manual_text/<relative_path>.txt, plus a summary at
data/manual_text/_ingest_log.md.

Scanned/image-only PDFs (no extractable text) are flagged as needing OCR.

Downloaded files are treated as untrusted data: this script only PARSES them (never
executes), keeps itself outside the drop directory, and takes the drop dir as an argument.

Usage:
  python3 src/ingest_manual.py                 # default drop dir
  python3 src/ingest_manual.py <some/dir>      # custom dir
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DROP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "manual_downloads")
OUT = os.path.join(ROOT, "data", "manual_text")
os.makedirs(OUT, exist_ok=True)

# Chat attachments land in these upload dirs in the cloud container; copy any PDF/DOCX
# from there into manual_downloads/_uploaded/ so they get ingested too.
UPLOAD_DIRS = ["/mnt/user-data/uploads", "/mnt/attach"]


def collect_uploads():
    import shutil
    dst = os.path.join(DROP, "_uploaded")
    found = 0
    for ud in UPLOAD_DIRS:
        if not os.path.isdir(ud):
            continue
        for dp, _, files in os.walk(ud):
            for fn in files:
                if os.path.splitext(fn)[1].lower() in (".pdf", ".docx"):
                    os.makedirs(dst, exist_ok=True)
                    out = os.path.join(dst, fn)
                    if not os.path.exists(out):
                        try:
                            shutil.copy2(os.path.join(dp, fn), out)
                            found += 1
                        except Exception as e:  # noqa
                            print(f"  could not copy {fn}: {e}")
    if found:
        print(f"Collected {found} attachment(s) from uploads into manual_downloads/_uploaded/")


def extract_pdf(path):
    """Return (text, n_pages, n_tables, note). Tries pdfplumber, falls back to pdftotext."""
    text_parts, n_tables, n_pages, note = [], 0, 0, ""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            n_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                t = page.extract_text() or ""
                text_parts.append(f"\n----- page {i} -----\n{t}")
                for tbl in (page.extract_tables() or []):
                    n_tables += 1
                    rows = [" | ".join((c or "").strip() for c in r) for r in tbl]
                    text_parts.append(f"\n[TABLE p{i}]\n" + "\n".join(rows))
    except Exception as e:  # noqa
        note = f"pdfplumber failed ({e}); "
    text = "\n".join(text_parts).strip()
    if len(text) < 200:  # likely scanned or pdfplumber failed -> try pdftotext
        try:
            r = subprocess.run(["pdftotext", "-layout", path, "-"],
                               capture_output=True, text=True, timeout=120)
            if len(r.stdout.strip()) > len(text):
                text = r.stdout.strip()
                note += "used pdftotext; "
        except Exception as e:  # noqa
            note += f"pdftotext failed ({e}); "
    if len(text) < 200:
        note += "LIKELY SCANNED / no extractable text -> needs OCR"
    return text, n_pages, n_tables, note.strip()


def extract_docx(path):
    import docx
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs if p.text.strip()]
    n_tables = len(d.tables)
    for ti, tb in enumerate(d.tables):
        parts.append(f"\n[TABLE {ti}]")
        for r in tb.rows:
            parts.append(" | ".join(c.text.strip() for c in r.cells))
    return "\n".join(parts).strip(), 0, n_tables, ""


def main():
    if not os.path.isdir(DROP):
        print(f"Drop dir not found: {DROP}")
        return
    collect_uploads()  # pull in any chat attachments first
    found = []
    for dirpath, _, files in os.walk(DROP):
        for fn in sorted(files):
            ext = os.path.splitext(fn)[1].lower()
            if ext in (".pdf", ".docx"):
                found.append(os.path.join(dirpath, fn))
    log = ["# Manual ingest log", "",
           f"Scanned: `{os.path.relpath(DROP, ROOT)}`  —  files found: **{len(found)}**", ""]
    if not found:
        log.append("_No PDF/DOCX files yet. Drop files into the per-paper folders and re-run._")
        print("\n".join(log))
        open(os.path.join(OUT, "_ingest_log.md"), "w").write("\n".join(log))
        return
    log.append("| file | pages | tables | chars | status |")
    log.append("|---|---|---|---|---|")
    for path in found:
        rel = os.path.relpath(path, DROP)
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".pdf":
                text, npg, ntab, note = extract_pdf(path)
            else:
                text, npg, ntab, note = extract_docx(path)
        except Exception as e:  # noqa
            log.append(f"| {rel} | ? | ? | 0 | ERROR: {e} |")
            continue
        safe = rel.replace(os.sep, "__")
        outp = os.path.join(OUT, safe + ".txt")
        open(outp, "w").write(text)
        status = note or "ok"
        log.append(f"| {rel} | {npg or '-'} | {ntab} | {len(text)} | {status} |")
        print(f"[{rel}] pages={npg} tables={ntab} chars={len(text)} {('<- '+note) if note else ''}")
    log += ["", f"Text dumps written to `data/manual_text/`. "
            "Tell Claude which files you added and it will extend the dataset from them."]
    open(os.path.join(OUT, "_ingest_log.md"), "w").write("\n".join(log))
    print(f"\nSummary -> data/manual_text/_ingest_log.md")


if __name__ == "__main__":
    main()
