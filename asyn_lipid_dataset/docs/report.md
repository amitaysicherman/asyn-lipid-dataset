# α-Synuclein × lipid fibril-modulation dataset — pilot report

**Goal (from the brief):** identify lipids / lipid formulations that *reduce* α-synuclein
fibril formation (measured by Thioflavin-T, ThT), starting from eight candidates
(Cholesterol, Sphingomyelin, DMPC, DPPC, DSPC, DOPC, POPC, GM1), and build an
evidence-backed dataset + an initial model *if the data supports one*.

**Status:** pilot dataset built and validated from 5 primary studies (the 3 required
pilot papers + 2 more from the seed list); every record is provenance-checked; a baseline
model was implemented and evaluated honestly. This is the "trustworthy dataset" milestone;
predictive performance is demonstrated but shown to be **not yet deployable**.

This report separates, explicitly: **measured facts**, **digitized estimates** (none yet),
**calculated quantities**, **model predictions**, and **hypotheses**.

---

## 1. The single most important finding (read this first)

There are **two opposite assay paradigms** in this literature, and conflating them would
corrupt everything downstream:

- **Lipid-induced aggregation** (Grey 2015, Gaspar 2018, Galvagnion 2015/2016): under
  quiescent conditions α-synuclein alone **does not aggregate**. A lipid can only *trigger /
  accelerate* nucleation. Here, **"no detectable effect" is NOT inhibition** — the no-lipid
  control is also flat. Most of the accessible primary data is of this type.
- **Inhibition of aggregation** (Martinez 2007): the protein *is* made to aggregate and the
  lipid is tested for its ability to *reduce* fibrils. This is the paradigm that matches the
  wet-lab goal — and it is the **scarcest** evidence we have (one, abstract-only, paper).

Consequences the model and the candidate table reflect:
- The effect of a lipid is **not a fixed property**. **GM1 accelerates** aggregation at mildly
  acidic pH (5.5; Grey, Gaspar) but **inhibits/eliminates** it at neutral pH (Martinez; and
  Grey/Gaspar both explicitly cite the neutral-pH inhibition result). Same lipid, opposite sign.
- **The same lipid is biphasic in concentration/ratio.** DMPS at high lipid:protein ratio (>40)
  gives *no* aggregation and even **dissolves preformed fibrils**; at low ratio (~8) it strongly
  accelerates (Galvagnion 2015). "Stronger binding" ≠ "stronger inhibition."
- Therefore we do **not** collapse everything into one number, and we do **not** claim to predict
  the wet-lab (Yuval's) assay, whose pH/agitation/ratio are not yet known.

---

## 2. Dataset coverage (see `outputs/audit_report.md` for the full audit)

- **Papers:** 6 (5 primary + 1 assay reference). 5 full-text; **Martinez 2007 abstract-only**
  (paywalled).
- **Lipids catalogued:** 22 (13 with RDKit-validated SMILES; 9 natural mixtures/gangliosides
  deliberately left without a SMILES — no arbitrary structure assigned to a natural mixture).
- **Experimental conditions:** 43. **Measurement records:** 55 (46 direct-aggregation,
  9 binding/structural). **Distinct formulations:** 26.
- **Independent-experiment counting is conservative:** 1 condition = 1 experiment; replicate
  wells and time points are *not* counted as independent.
- **Raw vs digitized:** all numeric values are text/table-reported; **0 digitized** so far
  (15 figure-only curves flagged `digitization_pending`).
- **Matched controls:** 28/46 direct-aggregation measurements name a matched control, all present.
- **Missingness** is explicit, never imputed (e.g. Martinez conditions blank; mixture ratios
  reported as ranges).

### Coverage of the 8 candidates (primary = candidate is the studied driver, not inert matrix)
| candidate | primary conds | direction(s) | quantitative? |
|---|---|---|---|
| **GM1** | 7 | inhibition (neutral pH) **vs** acceleration (pH 5.5) — conflict by pH | no (curves/abstract) |
| **DOPC** | 2 (pure) | no effect / mild retardation | no |
| **Cholesterol** | 1 | no effect (does not initiate; tested only as additive in a non-triggering mix) | no |
| **Sphingomyelin** | 1 | "negligible interaction" (Martinez, abstract; thin) | no |
| **DMPC** | (mixture) | reduces DMPS-driven aggregation as its fraction rises (dilution of charge) | ordinal threshold only |
| **DPPC** | 0 | — no primary evidence found | no |
| **DSPC** | 0 | — no primary evidence found | no |
| **POPC** | 0 | — no primary evidence found (POPS ≠ POPC) | no |

Full prose per candidate: `outputs/candidate_evidence_table.md` / `.csv`.

**Bottom line on candidates:** the dataset is *rich on anionic/ganglioside triggering chemistry*
but *poor on the 8 candidates themselves* — three of eight (DPPC, DSPC, POPC) have **zero** direct
records, and the biologically wanted *inhibition* direction has essentially one (abstract-only) source.

---

## 3. Prediction target choice

Inspecting the data (§1–2) rules out a single continuous cross-paper target:
- Absolute ThT half-times are mostly figure-only and **not comparable across papers** (different
  pH, plate surface, agitation, protein conc).
- Many conditions are **censored** ("no aggregation within 50 h / 140 h").
- Normalisation to own-max curves means amplitudes can't be compared for fibril *quantity*.

The one endpoint that is **explicitly stated and comparable** across papers is the **ordinal
effect direction** relative to the matched control. We therefore model
`effect_class ∈ {accelerate, neutral, reduce}` (and keep an ordinal `effect_score`).
The `relative_ThT_reduction = 1 − AUC_treat/AUC_control` score from the brief is **not** computed
yet because it needs digitized, background-corrected, shared-window curves with matched controls —
a documented next step, valid only *within* a paper.

## 4. Baseline model & honest evaluation (`outputs/model_report.md`)

35 conditions carry an effect label (accelerate=16, neutral=13, reduce=6). Majority-class
accuracy = 0.457. Cells below are **accuracy / macro-F1**.

| model | Stratified-5fold (optimistic) | Leave-One-Paper-Out | Leave-One-Lipid-Out |
|---|---|---|---|
| Dummy (most frequent) | 0.457 / 0.209 | 0.314 / 0.185 | 0.343 / 0.174 |
| Rule (domain heuristic) | 0.600 / 0.600 | 0.600 / 0.600 | 0.600 / 0.600 |
| Nearest-neighbour (chem+cond) | 0.743 / 0.712 | 0.371 / 0.262 | 0.771 / 0.752 |
| Logistic regression (L2) | 0.714 / 0.686 | **0.457 / 0.324** | 0.800 / 0.772 |

**Interpretation (this is a *prediction*/methodology result, not a measured fact):**
- A real, learnable signal exists — *charged/ganglioside lipids trigger aggregation; zwitterionic
  PC and cholesterol do not* — so models beat the trivial baseline on random splits.
- Under **leave-one-paper-out** the gain largely **disappears** and the `reduce` (inhibition)
  class **collapses to 0 correct** (confusion: 6 true reduce → 0 predicted): nearly all inhibition
  evidence is one paper, and GM1's direction is set by pH, which is confounded with paper. Holding
  out Martinez → 0.00 accuracy; holding out Galvagnion 2016 → 0.10 (the chain-length subtlety that
  only short-chain PS triggers is paper-specific).
- The transparent **rule** is the most robust (0.60 everywhere) precisely because it encodes the
  known confound without overfitting.

**Verdict:** enough data to demonstrate the pipeline and a coarse *triggering* classifier under
published conditions; **not** enough to predict *inhibition*, to rank the 8 candidates, or to
claim anything about Yuval's assay. We deliberately did **not** manufacture a split that looks
confident.

---

## 5. What we would need from Yuval to make this predictive (see `docs/needs_from_yuval.md`)

Short version: the assay's **pH, agitation, plate surface, protein & lipid concentrations and
lipid:protein ratio, seeding status, protein variant, and how "effect" is scored** — because every
one of these is a factor that *flips or scales* the outcome in the data above.

## 6. Next steps (to move from "trustworthy dataset" to "useful predictor")
1. **Digitize** the flagged figure curves (Grey Figs 3/6/7/8, Gaspar Fig 2, Galvagnion Fig 3/5)
   into `curves.csv`, compute within-paper `relative_ThT_reduction` and lag/half-time deltas.
2. **Retrieve the gated SI** (Galvagnion 2015/2016 SI PDFs) and Martinez full text to recover the
   DMPC:DMPS curves and the GM1 inhibition numbers + exact neutral-pH conditions.
3. **Expand** to the specific candidates with zero coverage (DPPC, DSPC, POPC) and to dedicated
   neutral-pH inhibition studies; prioritise controlled concentration/formulation series.
4. Only then revisit regularised regression / GP with proper leave-lipid-out evaluation.

---

### Provenance & integrity
Every measurement's `source_quote` is verbatim and auto-verified against the fetched article text
(`outputs/provenance_check.md`: 55/55 grounded). All SMILES validated by RDKit. The whole pipeline
is reproducible offline via `python3 src/run_all.py`.
