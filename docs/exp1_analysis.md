# Experiment 1 (261022) — first results vs model predictions

First ThT run from Yuval: A53T α-syn (50 µM) + 8 candidates + a reference liposome ("REAAM'S
LIPO"), each at 10:1 and 50:1, pH 7.4, 72 h, with solvent & buffer controls. **Preliminary** —
Yuval plans to repeat (positive control weaker than hoped; will raise protein to 100 µM).
Analysis: `src/analyze_yuval_exp1.py` → `experiments/exp1_results.csv`, figure `outputs/exp1_curves.png`.

## What's robust (high confidence)

1. **GM1 is the strongest reducer — and it's ratio-dependent. ✅ (model's #1 call)**
   - **GM1 50:1 completely abolishes aggregation** — flat at baseline for the full 72 h
     (endpoint ≈ 88 vs ≈ 2100 for its matched isopropanol control; no growth).
   - **GM1 10:1 partially reduces** (rises to ≈ 800, well below the ~1500 control).
   - This is exactly the prediction: GM1 top reducer, and **high ratio → stronger sequestration**
     (Rule 5). Textbook match.

2. **DSPC (and the reference liposome, DPPC at 10:1) PROMOTE. ✅**
   - **DSPC 50:1** gives the highest early ThT peak (~1900, above both controls) → strong promoter.
   - **REAAM'S LIPO 50:1** and **DPPC 10:1** rise late to 3000–4400 → strong promoters.
   - Consistent with "gel / long-chain saturated lipids don't help and can promote."

3. **Solvent strongly shifts the baseline. ✅ (Rule 9 in spirit)**
   - Positive controls: buffer ≈ 1718, 10% ethanol ≈ 886, 10% isopropanol ≈ 2100 (and noisy).
   - So lipids **must** be compared within their own solvent — GM1 (isopropanol) is not directly
     comparable to the ethanol lipids. The matched-control design was the right call.

## What's ambiguous / needs the repeat (low confidence)

- **The other PCs + cholesterol + SM at 50:1 read as *lower* than the ethanol control**
  (rel. endpoint ~0.3–0.5). This is **unexpected** (model: PCs inert, cholesterol promoter) and
  I would not trust it yet, because:
  - the **positive control was weak** (Yuval's own note) → "below control" is a soft claim;
  - **"free" lipids may scatter light / form aggregates**, which can depress or distort absolute
    ThT independently of real inhibition (the assembly-state check will matter here);
  - cholesterol is contradictory across ratios (50:1 low, 10:1 high), i.e. not a clean signal.
- **The 10:1 (2% solvent) conditions have no α-syn + 2%-solvent control in this run**, so their
  relative numbers are unreliable (I compared to the 10% control as a stopgap). Add a
  protein + 2%-ethanol (and +1% isopropanol) control next time.

## Scorecard: prediction vs observed
| candidate | model said | exp 1 (50:1) | verdict |
|---|---|---|---|
| **GM1** | ↓↓ reduce | **flat — fully suppressed** | ✅ strong match |
| DSPC | ↑ mild promote | **strong promote** | ✅ match (stronger than predicted) |
| DPPC | ↑ mild promote | ~control (50:1) / promote (10:1) | ✅ roughly |
| REAAM'S LIPO | — (not scored) | strong promote | n/a reference |
| DOPC / POPC | ~ inert | apparent reduce | ⚠ unexpected, low confidence |
| DMPC | ~ / mild ↓ | apparent reduce | ~ consistent-ish |
| SM | ~ inert | apparent reduce | ⚠ unexpected |
| Cholesterol | ↑ promote | mixed (50:1 low, 10:1 high) | ⚠ unclear |

**Bottom line:** the single highest-confidence prediction (GM1 ↓↓, ratio-dependent) is strongly
confirmed, and the predicted promoters (gel/long-chain) show up. The PC "reduction" at 50:1 is the
open question — resolve it with the repeat (higher protein for a stronger positive control, the
missing 2%-solvent controls, and a light-scattering / assembly-state check).

## For the next run
1. **↑ protein to 100 µM** (stronger, cleaner positive control — Yuval already plans this).
2. Add **α-syn + 2% ethanol** and **α-syn + 1% isopropanol** controls (for the 10:1 conditions).
3. A quick **light-scattering / turbidity read** (or absorbance) per well to catch optical
   artefacts from the "free" lipids.
4. Consider adding the top **anionic** picks (GM3, DOPS, POPG, cardiolipin) to test whether the
   "anionic → reduce" branch holds beyond GM1.
