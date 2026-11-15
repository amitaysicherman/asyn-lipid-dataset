# The scoring rules, with the paper behind each one

**How many papers?** The rules rest on **7 primary studies read & extracted in full** (P1–P4, P6,
P9, and partially P10), plus **3 read at abstract level** (P5, P7, P8) = **~10 papers**. The
640-paper literature corpus is a *search pool*, not the basis — only these were actually used to
write the rules. (P9–P10 were added from 3 targeted reads specific to Yuval's assay.)
Each rule below is tagged **[full-text]** (I extracted the data) or **[abstract]** (direction
only), and **[fact]** (stated in the paper) or **[inference]** (mechanistic reasoning).

## The 8 grounding papers
- **P1 Galvagnion 2016** — Chemical properties of lipids strongly affect the kinetics of the
  membrane-induced aggregation of α-synuclein. *PNAS* 113:7065. doi:10.1073/pnas.1601899113. [full-text]
- **P2 Galvagnion 2015** — Lipid vesicles trigger α-synuclein aggregation by stimulating primary
  nucleation. *Nat Chem Biol* 11:229. doi:10.1038/nchembio.1750. [full-text]
- **P3 Gaspar 2018** — Ganglioside lipids accelerate α-synuclein amyloid formation. *BBA Proteins
  Proteom* 1866:1062. doi:10.1016/j.bbapap.2018.05.005. [full-text]
- **P4 Grey 2015** — Acceleration of α-synuclein aggregation by exosomes. *JBC* 290:2969.
  doi:10.1074/jbc.M114.585703. [full-text]
- **P5 Martinez 2007** — GM1 specifically interacts with α-synuclein and inhibits fibrillation.
  *Biochemistry* 46:1868. doi:10.1021/bi061749a. [abstract — paywalled]
- **P6 Matveyenka 2024** — Cholesterol accelerates aggregation of α-synuclein… *ACS Chem Neurosci*
  15:4215. doi:10.1021/acschemneuro.4c00501. [full-text]
- **P7 Dou 2023** — …in the presence of phosphatidylcholine and phosphatidylserine. *ACS Chem
  Neurosci* 14:3183. doi:10.1021/acschemneuro.3c00314. [abstract / via P6 — DMPC suppression]
- **P8 "Rapid anionic micelle-mediated α-synuclein fibrillization in vitro."** *JBC* 2003.
  doi:10.1074/jbc.m308231200. [abstract — for the detergent/fatty-acid correction]
- **P9 "The extent of protein hydration dictates… α-synuclein aggregates."** *Chem Sci* 2021.
  doi:10.1039/d0sc05297c. [full-text — ethanol/alcohol co-solvent accelerates at 100 µM/PBS/pH 7]
- **P10 Jo et al. — α-synuclein membrane interactions and lipid specificity.** *JBC* 2000.
  doi:10.1074/jbc.M004345200. [A53T↑ / A30P↓ membrane binding vs WT]

---

## Rule → score → paper(s)

**Rule 1 — Headgroup charge is the binding gate.** Anionic lipids bind α-syn strongly; zwitterionic
PC/PE and cholesterol bind weakly. → *anionic +2, zwitterionic 0, sterol −1.*
Source: **P1** (α-syn binds all fluid anionic with similar K_D ≈ 0.2–0.5 µM) [fact]; **P3, P4**
(pure DOPC shows no binding / no effect) [fact].

**Rule 2 — Among anionic lipids, only short, soluble, saturated chains trigger (bilayer case).**
DLPS > DMPS ≫ DPPS; DOPS/POPS bind but don't trigger. → underlies why chain length/fluidity matter.
Source: **P1** (rate ∝ 1/ΔG_transfer; DPPS fluid at 50 °C still inert) [fact].

**Rule 3 — Gangliosides are the high-leverage class (big, soluble, anionic head).** → *+1 for a big
soluble anionic headgroup* (puts GM1/GM3/GD/GT on top).
Source: **P3** (GM1/GM3 accelerate at pH 5.5; even uncharged large heads weakly trigger) [fact];
**P4** (GM1/GM3 vesicles accelerate) [fact]; **P5** (GM1 the standout at neutral pH) [abstract].

**Rule 4 — pH sets the SIGN.** Neutral pH → lipids tend to *inhibit*; acidic pH → *accelerate*.
This is why the score's direction is fixed for Yuval's pH 7.4.
Source: **P5** (GM1 inhibits/eliminates fibrillation at neutral pH) [abstract] **vs** **P3 + P4**
(same GM1 accelerates at pH 5.5, both papers explicitly cite the neutral-pH inhibition) [fact].

**Rule 5 — Lipid:protein ratio is biphasic; HIGH ratio → sequestration → reduce.** This is why
anionic binders score as *reducers* at Yuval's 10:1 and 50:1.
Source: **P2** (DMPS at ratio >40 → no aggregation, even dissolves preformed fibrils; max rate at
ratio ~8) [fact].

**Rule 6 — Phase/fluidity controls how much it binds.** Fluid membranes bind ~10× better than gel.
→ *fluid short-saturated zwitterionic PC +1; gel/very-long −0.5.*
Source: **P1** (stoichiometry ~30 lipids/protein fluid vs ~250 gel, Table 1) [fact].

**Rule 7 — Zwitterionic lipids dilute anionic charge (passive).** Background for why neutral PCs are
mostly inert. Source: **P1** (DMPC:DMPS — binding & triggering fall as DMPC rises; >25 % DMPC → none) [fact].

**Rule 8 — Among neutral lipids, protection comes from fluidity-enabled sequestration, NOT ordering;
cholesterol promotes at high %.** → *cholesterol −1; DMPC-like fluid short PC +1; gel DPPC/DSPC 0/−0.5.*
Source: **P6** (cholesterol *accelerates* at 60 %; gel DPPC does *not* suppress, shortens lag) [fact];
**P7** (DMPC strongly *suppresses*; a 14:0→16:0 change flips it) [abstract]. *This rule was revised —
my first "ordered lipids are protective" guess was wrong and P6 overturned it.*

**Correction rule — single-chain anionic amphiphiles (free fatty acids, lyso) are detergent-like →
micelle catalysis → ACCELERATE.** → *single-chain anionic −2* (keeps FFAs out of the "reducer" top).
Source: **P8** (fatty acids / anionic detergents greatly accelerate fibrillization, lag as short as
11 min, via micelles) [abstract].

---

## Rules added from the 3 targeted reads (specific to Yuval's assay)

**Rule 9 — The ethanol vehicle is NOT inert: it accelerates α-syn aggregation (and can shift the
fibril polymorph) at Yuval's exact conditions.** Consequence for scoring/analysis, not the lipid
score itself: the aggregation **baseline rises with % ethanol**, so (a) every lipid must be judged
against its **solvent-matched control at the same %**, (b) **10:1 (2% EtOH) and 50:1 (10% EtOH) are
NOT directly comparable**, and (c) at 50:1 the ethanol effect may dominate / change the aggregate
type. This is now evidence-backed, not just caution.
Source: **P9 — "The extent of protein hydration dictates… α-synuclein aggregates", Chem Sci 2021,
doi:10.1039/d0sc05297c** [full-text]: low-to-mild alcohols "increased significantly the rate of αS
aggregation (100 µM αS, PBS, pH 7)" concentration-dependently; higher alcohol shifts parallel→
antiparallel β-sheet polymorph. [fact] (Directly matches Yuval's 100 µM / PBS / pH 7.4.)

**Rule 10 — A53T binds membranes MORE strongly than WT, so lipid effects are likely amplified**
relative to the (mostly-WT) rules above — stronger binders may sequester/inhibit more, and any
membrane-driven effect is enhanced. Treat the WT-derived scores as a conservative floor for A53T.
Source: **P10 — Jo et al., α-synuclein membrane interactions & lipid specificity, *JBC* 2000,
doi:10.1074/jbc.M004345200** (and A53T↑ / A30P↓ membrane binding in the familial-mutant literature),
corroborated in fetched full texts (e.g. PMC9209734 tested A53T vs WT with DOPC/Mimic membranes). [fact]

**Free-lipid assembly state — a genuine GAP, not a rule.** Beyond the single-chain→micelle case
(P8), there is no clean literature on how *bilayer-forming* lipids behave when added "free" from
ethanol (Yuval's method). This is exactly what Yuval is checking this week; until then the
`formulation = free_from_ethanol (assembly TBD)` feature carries real uncertainty.

---

## Honest limits of this evidence base
- **Small & indirect.** 6 full + 2 abstract papers, almost all **WT** α-syn in **SUV/LUV vesicles** —
  Yuval uses **A53T** with **free (non-vesicle)** lipids, so these are *priors*, not measurements.
- **Direction is pH/ratio-dependent.** Rules 4–5 mean the same lipid flips sign; the score is only
  valid pinned to Yuval's regime (pH 7.4, high ratio).
- **Thin on the actual candidates.** Only GM1 (P5), cholesterol/DPPC (P6/P7), DOPC (P3/P4) have direct
  data; DSPC/POPC/SM are pure rule extrapolation.
- **This is why batch 1 matters:** Yuval's data replaces these 8 papers as the basis, and the weights
  get re-fit from his measurements.
