# Literature corpus (systematic Europe PMC search)

Built by `src/literature_search.py` (search) + `src/fetch_corpus_fulltext.py` (fetch) +
`src/make_download_page.py` (download lists).

## Files
- **corpus.csv** — every unique hit from the query battery (384 papers): metadata, abstract,
  `access_route`, `relevance_score`, candidates mentioned, URL. The master index.
- **fetched_index.csv** — per paper: which ones we fetched free full text for, and how.
- **download_list.html / .md** — ranked, clickable list of papers with **no free full text**
  (for manual download). Grouped: Tier A names one of the 8 candidates, B = high relevance /
  ThT, C = other.
- **download_urls.txt** — the same list as plain URLs, one per line.
- **_search_log.json** — queries run and hit counts.
- **fulltext_xml/**, **fulltext_text/** — the fetched full texts (git-ignored; large,
  re-fetchable). Files are named by PMCID; join to titles via `corpus.csv`.

## Current numbers
- 384 relevant papers found; **149 free full texts fetched** (139 Europe PMC OA XML + 10 PMC
  HTML); **234 need manual download** (213 paywalled + 21 captcha-blocked PMC).

## Next step
Triage the 149 fetched texts for primary ThT/aggregation experiments with the 8 candidates /
related lipids, and extend the structured dataset (papers/conditions/components/measurements)
the same way as the 7 already curated — with verbatim source quotes and provenance checks.
Drop manually-downloaded PDFs into `../manual_downloads/` and run `src/ingest_manual.py`.
