# α-Synuclein × lipid fibril-modulation dataset (pilot)

An evidence-backed, provenance-tracked dataset of how lipids and lipid formulations modulate
**α-synuclein fibril formation** (ThT assay), built from the primary literature, plus a curated
lipid structure reference, an audit, a per-candidate evidence table, and an honestly-evaluated
baseline model.

Collaboration: Amitay Sicherman, Kira Radinsky's lab, Avi Schroeder's lab (Technion).

> **Read `docs/report.md` first.** The one critical idea: this literature mixes two *opposite*
> assay paradigms (lipid-*induced* aggregation vs *inhibition*), so "no effect" usually means
> "did not trigger," **not** "inhibited." Direction depends on pH, ratio, and formulation.

## Layout
```
data/
  papers.csv conditions.csv components.csv measurements.csv curves.csv   # linked dataset
  lipids.csv            # lipid structure reference (RDKit-validated SMILES / flagged mixtures)
  cross_refs.csv        # secondary-literature cross-references (context, not measurements)
  model_table.csv       # per-condition feature matrix + target (generated)
  raw_html/ raw_meta/ raw_supp/ extracted_text/   # fetched sources + parsed text (provenance)
src/
  fetch_sources.py      # (network) download articles + supplementary via Europe PMC / PMC
  parse_articles.py     # JATS-XML / PMC-HTML -> clean text dumps
  lipids_reference.py   # build data/lipids.csv (+ RDKit validation)
  extraction_records.py # SINGLE SOURCE OF TRUTH: curated records w/ verbatim source quotes
  build_dataset.py      # emit the linked CSVs + calculated fields
  verify_provenance.py  # check every source_quote appears in the fetched text
  audit.py              # outputs/audit_report.md + candidate_evidence_table.{md,csv}
  features.py           # build data/model_table.csv
  model_eval.py         # baselines + leave-one-paper/lipid-out eval -> outputs/model_report.md
  chemistry_ranking.py  # RULE-BASED (not ML) candidate ranker -> outputs/chemistry_ranking.md
  ingest_manual.py      # ingest user-downloaded PDFs/DOCX -> data/manual_text/
  run_all.py            # reproduce everything
docs/
  report.md             # main findings, limitations, verdict
  chemistry_rules.md    # mechanistic rules + hand-reasoned candidate ranking (deep chemistry)
  data_dictionary.md    # every table & column, evidence-type legend
  search_log.md         # retrieval & access-limitation log
  needs_from_yuval.md   # exact protocol details required to make this predictive
outputs/
  audit_report.md  candidate_evidence_table.{md,csv}  provenance_check.md
  model_report.md  chemistry_ranking.md
```

## Reproduce
```bash
pip install -r requirements.txt          # rdkit, scikit-learn, pandas, beautifulsoup4, lxml, python-docx
python3 src/run_all.py                    # offline: build + verify + audit + model
python3 src/run_all.py --fetch            # also re-download sources (needs network allowlist)
```
`run_all.py` fails loudly if any `source_quote` is not found in its source text.

## What this is / isn't
- **Is:** a trustworthy, auditable pilot dataset (5 primary papers, 43 conditions, 55 measurements),
  a structure reference, a per-candidate evidence synthesis, and a baseline model with leakage-aware
  evaluation.
- **Isn't:** a validated predictor. Under leave-one-paper-out the inhibition class is unlearnable
  from this pilot; three of the eight candidates have zero direct evidence. See `docs/report.md` §4.

## Evidence separation
Measured facts, (pending) digitized estimates, calculated quantities, model predictions and
hypotheses are kept distinct — in the CSV `evidence_type`/`quality_flag` columns and in the report's
section labels. Natural lipid mixtures are never assigned an arbitrary SMILES.
