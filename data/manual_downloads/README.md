# Drop downloaded papers & supplementary here

Put the PDFs (and any `.docx` supplementary) you download into these folders, then run:

```bash
python3 src/ingest_manual.py
```

The tool extracts text **and tables** from every PDF/DOCX it finds (recursively) and
writes clean, readable `.txt` dumps to `data/manual_text/`, plus a summary at
`data/manual_text/_ingest_log.md`. It flags any scanned/image PDF that has no extractable
text (those would need OCR).

## Where to put what

One folder per paper. Folders already created for the known gaps:

| folder | what to drop in it | why it's needed |
|---|---|---|
| `martinez2007/` | **Martinez et al. 2007** main PDF (+ any SI) — *GM1 inhibits fibrillation*, Biochemistry, doi:10.1021/bi061749a | full text was paywalled; this is our only *inhibition* paper and has no ThT numbers yet |
| `galvagnion2016/` | **Galvagnion 2016 SI PDF** (`pnas.1601899113.sapp.pdf`) — the DMPC:DMPS mixture curves (Fig S2) | SI was behind the PMC download gate |
| `galvagnion2015/` | **Galvagnion 2015 SI PDF** (NIHMS supplement) | SI was behind the PMC download gate |
| `other/` | any additional paper you want ingested (e.g. a neutral-pH inhibition study, or a DPPC/DSPC/POPC paper) | expands candidate coverage |

To add a brand-new paper, just make a new folder named after it (e.g. `fink2003/`) and drop
the files in — the tool picks up any folder automatically.

## Naming (optional but helpful)
Filenames can be anything. If you include `main` / `SI` / `supp` in the name
(e.g. `martinez2007_main.pdf`, `martinez2007_SI.pdf`) the log labels them for you.

## Note
Downloaded files stay **local** and are git-ignored (not pushed). Only the extracted
`.txt` dumps are kept as provenance. After ingesting, tell me and I'll read the new text
and extend the dataset (new conditions/measurements with provenance), then re-run the audit
and model.
