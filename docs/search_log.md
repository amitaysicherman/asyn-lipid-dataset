# Search & access log

Chronological record of literature retrieval, access status, and limitations.
Date: 2026-11-15. Network access in this environment is restricted; hosts were allowlisted
on request (NCBI/PMC, Europe PMC, DOI resolver). WebSearch is available.

## Access method
- Full text retrieved via **Europe PMC full-text XML** (open-access subset) or the **PMC HTML
  article page** (free but non-OA). Both parsed deterministically (`src/fetch_sources.py`,
  `src/parse_articles.py`).
- PMC gates direct supplementary-file (`/bin/...`) downloads behind a proof-of-work challenge;
  supplementary **figures/tables** were obtained via the Europe PMC `supplementaryFiles` endpoint
  for the open-access papers (Grey 2015, Gaspar 2018). For the non-OA papers the supplementary PDFs
  (Galvagnion 2015/2016 SI) were **not** retrieved; their key SI results are captured from the
  main-text descriptions and flagged.

## Seed papers (as specified in the brief)

| key | citation | status | notes |
|---|---|---|---|
| martinez2007 | Martinez et al. 2007, GM1 inhibits fibrillation (Biochemistry) | **abstract only** | Subscription-only (ACS); no PMC. Abstract captured; no ThT numbers accessible. |
| grey2015 | Grey et al. 2015, Acceleration by Exosomes (JBC) | full text + SI figs | PMC4317028, open access. Figs 6–8 (lipid/ganglioside) prioritised. |
| galvagnion2016 | Galvagnion et al. 2016, Chemical properties of lipids (PNAS) | full text | PMC4932957 (free, non-OA). Table 1 + all figure captions extracted. SI PDF (DMPC:DMPS, Fig S2) behind PoW gate; captured from main-text description. |
| galvagnion2015 | Galvagnion et al. 2015, Primary nucleation (Nat Chem Biol) | full text | PMC5019199 (free, non-OA). DMPS-only; mechanistic/supporting. |
| gaspar2018 | Gaspar et al. 2018, Gangliosides accelerate (BBA Proteins Proteom.) | full text + SI | PMC6121081, open access. |
| tht_assay2018 | ThT fluorescence assay (Bio-protocol) | full text | PMC6066150. Methodological reference only. |

## Background reviews (not supplied as PDFs; used only to locate primary studies)
The four background PDFs named in the brief were **not present** in the environment. They are
reviews / a lipidomics study (cells-10-02452; Fabelo 2011; Hussain 2019; "Lipids and Lipid raft
Alterations"). Review-level and disease-abundance (lipidomics) claims are **excluded** from the
aggregation dataset by design (observational, not direct aggregation measurements). WebSearch was
used to confirm identities/DOIs of the primary studies above.

## Access limitations recorded
1. **Martinez 2007** — full text inaccessible (paywall). Only qualitative, direction-level evidence
   from the abstract; exact assay conditions (pH, temperature, agitation, concentrations) are not in
   the accessible text and are left blank (not imputed). Secondary citations in Grey 2015 (ref 57)
   and Gaspar 2018 (ref 67) place GM1 inhibition at neutral pH — recorded in `cross_refs.csv` as
   supporting context, not a primary measurement.
2. **Galvagnion 2015 / 2016 supplementary PDFs** — behind PMC proof-of-work download gate; not
   retrieved. Affected results (Galvagnion 2016 DMPC:DMPS mixtures, Fig S2) are captured from the
   main-text statements and flagged; the underlying SI curves are a documented gap.
3. **Numeric half-times** for individual lipids in Grey 2015 and Gaspar 2018 appear only in figures
   (no tables); they are marked `digitization_pending` rather than invented.

## Expansion status
Pilot = the first three primary studies (Martinez 2007, Grey 2015, Galvagnion 2016), extended with
Galvagnion 2015 and Gaspar 2018 (also in the seed list, already read). Broader citation/forward-search
expansion is the documented next step (see report §Next steps); it was deprioritised until the pilot
was validated, per the brief.
