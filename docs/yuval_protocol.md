# Yuval's assay protocol — captured + analysis

Source: WhatsApp + `Experimental_Procedure.docx` (Yuval, 2026-11-15). Marked "method so far;
some details may still change" — notably whether the lipids stay free or self-assemble.

## Fixed parameters (the regime to pin the model to)
| field | value |
|---|---|
| objective | do lipids **inhibit** fibril formation when added at the **start** (prevention, not treatment) |
| protein | **A53T** α-synuclein (mutant), recombinant E. coli, anion-exchange purified |
| protein conc | 50 µM (done) → **100 µM** (next) |
| seeding | **none** (de novo) |
| buffer | 20 mM K₂HPO₄ + 5 mM KH₂PO₄ + 100 mM KCl, **pH 7.4** |
| ThT | 20 µM, 100 µL/well, bottom read, ex 448 / em 482 |
| lipid addition | **"free" from solvent — NO SUV/LUV**; ethanol stock (GM1: 80% isopropanol/20% water) |
| lipid:protein ratio | **10:1 or 50:1** (lipid in large excess) |
| lipid conc | 10:1 → 0.5 mM (50 µM prot) / 1 mM (100 µM); 50:1 → 2.5 mM / 5 mM |
| final solvent | 10:1 → **2% EtOH** (GM1 1.6% iPrOH); 50:1 → **10% EtOH** (GM1 8% iPrOH) |
| plate | black flat-bottom polystyrene µClear, Greiner 655090 (**binding** surface) |
| incubation | 37 °C, 72 h; 25-min cycles = 5 min orbital shake (2 mm, ~281 rpm) + read |

## How this regime maps to what we know (good news + caveats)

**Good — this is an inhibition-favouring regime, which is exactly the goal:**
- **Neutral pH 7.4** = the regime where lipids tend to **inhibit** (Martinez 2007: GM1 inhibits
  at neutral pH; Nanoscale 2018: cholesterol liposomes retard). Opposite of the acidic pH-5.5
  papers where everything accelerates.
- **High lipid:protein ratio (10:1, 50:1)** = the **sequestration/inhibition** regime
  (Galvagnion 2015: excess lipid → no aggregation, even dissolves fibrils). The right side of
  the dose switch for finding reducers.
- **Shaking + binding plate** = α-syn **will aggregate on its own** → there is a real baseline
  to suppress, so "reduction" is measurable (unlike the quiescent lipid-induced assays where
  the control is flat).

So the literature subset that transfers as a **prior** is the neutral-pH / high-ratio /
aggregating-baseline set (Martinez 2007, Nanoscale 2018, Matveyenka 2024, the JBC-2003
"lipid binding inhibits"). The acidic quiescent vesicle papers (Galvagnion, Gaspar, Grey) are
**mechanism context, not quantitative priors** for this assay.

**⚠ Caveat 1 — the ethanol co-solvent is a confound that must be controlled.**
At 50:1 the wells contain **10% ethanol** (2% at 10:1). Alcohols are known to modulate α-syn
folding/aggregation on their own. **Every lipid must be compared to a solvent-matched,
lipid-free control at the same % ethanol (and % isopropanol for GM1).** Otherwise a lipid effect
and an ethanol effect are indistinguishable, and 10:1 vs 50:1 isn't comparable (different % EtOH).
This is the single most important design point.

**⚠ Caveat 2 — "free" lipids ≠ the bilayers in the literature.**
Every literature study uses SUV/LUV vesicles; here lipids are spiked from ethanol and their
assembly state is unknown (Yuval is checking this week — likely micelles/aggregates/precipitate,
differing per lipid by solubility). So quantitative transfer from vesicle literature is weak; the
**chemistry rules (charge, chain solubility, headgroup) are directional priors, not numbers.**
The model's "formulation" feature should be encoded as `free_from_ethanol (assembly TBD)`, a new
category distinct from SUV/LUV.

**⚠ Caveat 3 — A53T, not WT.** Most literature is WT. A53T aggregates faster and is the right
disease variant; GM1 interacted with A53T like WT (Martinez 2007), but note the variant when
borrowing WT priors.

## Consequences for the model / decision tree
Because pH, ratio, plate, agitation, variant are now **fixed**, the model collapses to the
**lipid-feature → effect** tree you pictured. The only non-lipid axes he varies are
**ratio (10:1 vs 50:1)** and **protein conc (50 vs 100 µM)** — small extra branches. Everything
else is constant, so the lipid descriptors (headgroup charge, chain length, saturation, Tm,
headgroup size) are the features.

## Open items to confirm with Yuval
- Lipid assembly-state result (this week) → sets the `formulation` encoding and maybe the stock
  solvent/concentration.
- Which candidates already run at 50 µM, and the raw curves (to calibrate the endpoint + see the
  ethanol baseline).
- Preferred endpoint: lag time / t½ / endpoint / AUC (we'll compute all; pick the primary).
