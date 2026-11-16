# Lipid → α-synuclein fibril effect: decision tree & evidence

**Purpose.** A rule-based prior that scores any lipid for its likely effect on α-synuclein
fibril formation, built to prioritise experiments for **Yuval's assay** (A53T α-syn, pH 7.4,
lipids added "free" from ethanol at 10:1 & 50:1 lipid:protein, shaking, 37 °C, ThT).

**Status.** This is a *prior from the literature* (~10 papers), not a fitted model. It sets the
starting ranking; it is **re-fit on Yuval's own ThT data** after the first batch. Direction is
pinned to Yuval's regime (neutral pH + high ratio → binders tend to **reduce**).

---

## The decision tree

```mermaid
flowchart TD
  A([New lipid]) --> B{Headgroup charge?}

  B -- "Anionic<br/>(PS · PG · PA · ganglioside)" --> C{Big soluble sugar head?<br/>(ganglioside)}
  C -- "yes" --> R1["score +3<br/>strong REDUCER (prior)"]
  C -- "no" --> D{Single-chain / detergent-like?<br/>(free fatty acid, lyso)}
  D -- "yes" --> P1["detergent → micelle catalysis<br/>PROMOTER (prior)"]
  D -- "no (bilayer-former)" --> R2["score +2<br/>REDUCER (prior)"]

  B -- "Sterol<br/>(cholesterol)" --> P2["score −1<br/>PROMOTER at high mol% (prior)"]

  B -- "Zwitterionic<br/>(PC · PE · SM)" --> E{Fluid at 37°C<br/>AND short saturated ≤14C?}
  E -- "yes (DMPC-like)" --> M1["score +1<br/>mild REDUCER"]
  E -- "no (gel/long:<br/>DPPC · DSPC)" --> M2["score 0 / −0.5<br/>inert → mild promoter"]
```

**Global modifiers (set by Yuval's fixed conditions, not by the lipid):**
- **pH 7.4 (neutral)** → flips binders toward *inhibition* (at acidic pH the same lipids accelerate).
- **High ratio (10:1, 50:1)** → *sequestration* regime → favours reduction by binders.
- **Ethanol vehicle** (2% at 10:1, 10% at 50:1) → *itself accelerates* → judge each lipid vs its
  **same-% solvent control**; do **not** compare 10:1 vs 50:1 directly.
- **A53T** (not WT) → binds membranes *more* → lipid effects likely *amplified*.

**Features used:** headgroup charge · headgroup size (ganglioside?) · acyl chain length ·
saturation · gel/fluid at 37 °C (Tm) · single-chain vs bilayer-former.

---

## The rules, the papers, and what we take from each

Tags: **[full-text]** extracted / **[abstract]** direction only; **[fact]** stated in paper /
**[inference]** our reasoning.

### R1 — Headgroup charge is the binding gate
**We take:** α-syn binds **anionic** lipids strongly and **zwitterionic PC/PE / cholesterol**
weakly → charge is the first split (anionic +2, zwitterionic 0, sterol −1).
- **Galvagnion 2016** (*PNAS*, doi:10.1073/pnas.1601899113) [full-text, fact] — anionic PS lipids
  all bind with similar K_D ≈ 0.2–0.5 µM.
- **Gaspar 2018** (*BBA*, doi:10.1016/j.bbapap.2018.05.005) [full-text, fact]: *"In the presence of
  pure DOPC lipid membranes, no aggregation and no conformational change of α-syn were detected."*

### R2 — Among anionic lipids, chain solubility/length tunes the effect (bilayer case)
**We take:** short, soluble, saturated anionic chains engage most; very long/insoluble less so.
- **Galvagnion 2016** [full-text, fact]: *"the presence of DMPS was found to promote the formation
  of amyloid fibrils"*; and DLPS (12:0) > DMPS (14:0) ≫ DPPS (16:0) — rate tracks lipid solubility.
  (Direction of this *promotion* is at their acidic/low-ratio regime; see global modifiers.)

### R3 — Gangliosides are the high-leverage class (big soluble anionic head)
**We take:** large sialylated sugar headgroup = strongest, most accessible engagement → +1 on top
of anionic → gangliosides top the list.
- **Grey 2015** (*JBC*, doi:10.1074/jbc.M114.585703) [full-text, fact]: *"vesicles composed of GM1
  promote aggregation of α-syn also in nonbinding plates … where α-syn alone does not aggregate."*
- **Gaspar 2018** [full-text, fact] — gangliosides give the *"strong accelerating effect."*

### R4 — pH sets the SIGN of the effect (why the tree is pinned to pH 7.4)
**We take:** at **neutral pH** lipids tend to **inhibit**; at **acidic pH** they accelerate. Yuval
is at pH 7.4 → the inhibition branch.
- **Martinez 2007** (*Biochemistry*, doi:10.1021/bi061749a) [abstract, fact]: *"induction of
  substantial α-helical structure and **inhibition or elimination** of α-synuclein fibril
  formation, depending on the amount of GM1 present"* (neutral pH).
- **vs Gaspar 2018 / Grey 2015** — the same GM1 **accelerates** at pH 5.5.

### R5 — Lipid:protein ratio is biphasic; HIGH ratio → sequestration → reduce
**We take:** Yuval's 10:1 and 50:1 (lipid excess) sit on the **inhibition** side of the dose curve.
- **Galvagnion 2015** (*Nat Chem Biol*, doi:10.1038/nchembio.1750) [full-text, fact]: *"no increases
  in ThT fluorescence were detected when α-syn (50 µM) was incubated in the presence of an excess of
  DMPS SUVs (DMPS:α-syn > 40)"*; and excess SUVs even **dissolve** preformed fibrils.

### R6 — Fluidity controls how much a lipid binds (gel vs fluid at 37 °C)
**We take:** fluid membranes bind ~10× more than gel → a fluid, short, saturated PC can engage
enough to mildly sequester; gel PCs (DPPC/DSPC at 37 °C) barely engage.
- **Galvagnion 2016** [full-text, fact] — stoichiometry ~30 lipids/protein (fluid) vs ~250 (gel).

### R7 — Zwitterionic lipids dilute anionic charge (why pure PCs are mostly inert)
- **Galvagnion 2016** [full-text, fact]: *"DMPC:DMPS model membranes did not detectably stimulate
  the aggregation of α-synuclein for DMPC:DMPS ratios above 25:75."*

### R8 — Among neutral lipids, protection is fluidity-enabled sequestration, NOT ordering; cholesterol promotes at high %  ⚠ (this corrected our first guess)
**We take:** cholesterol −1 (promoter at high %); fluid short PC (DMPC-like) +1; gel DPPC/DSPC ~0.
- **Matveyenka 2024** (*ACS Chem Neurosci*, doi:10.1021/acschemneuro.4c00501) [full-text, fact]:
  cholesterol at 60 % **accelerates** (t½ 61 h vs 82 h); *"100% DPPC (t_lag = 12.3 h) drastically
  shortened t_lag"* — i.e. DPPC does **not** suppress.
- **Dou 2023** (*ACS Chem Neurosci*, doi:10.1021/acschemneuro.3c00314) [abstract, via Matveyenka]:
  *"LUVs composed of C14:0 PC (DMPC) strongly suppressed α-syn aggregation … not observed for DPPC."*

### R-correction — single-chain anionic amphiphiles are detergent-like → micelles → ACCELERATE
**We take:** free fatty acids / lyso-lipids score as **promoters**, not reducers.
- **JBC 2003** (doi:10.1074/jbc.m308231200) [abstract, fact] — fatty acids & anionic detergents
  *greatly accelerate* fibrillization via micelles (lag as short as 11 min).

### R9 — The ethanol vehicle is NOT inert (specific to Yuval's method)
**We take:** the aggregation baseline rises with % ethanol → solvent-matched controls mandatory,
10:1 vs 50:1 not directly comparable.
- **Chem Sci 2021** (doi:10.1039/d0sc05297c) [full-text, fact]: alcohols *"increased significantly
  the rate of αS aggregation (100 µM αS, PBS, pH 7)"* and shift the fibril polymorph at higher %.
  (Matches Yuval's 100 µM / PBS / pH 7.4.)

### R10 — A53T binds membranes more strongly than WT
**We take:** lipid effects are likely **amplified** vs the (mostly-WT) rules above; treat WT scores
as a conservative floor.
- **Jo et al. 2000** (*JBC*, doi:10.1074/jbc.M004345200) [fact] — A53T ↑ / A30P ↓ membrane binding
  vs WT; corroborated in fetched A53T-vs-WT membrane studies.

---

## Honest limits
- Built on **~10 papers** (7 full-text + 3 abstract), almost all **WT α-syn in SUV/LUV vesicles** —
  Yuval uses **A53T** with **free, non-vesicle** lipids, so these are **priors, not measurements**.
- Direction is only valid **pinned to Yuval's regime** (pH 7.4, high ratio).
- **Free-lipid assembly state** is a genuine literature gap — the biggest unknown, which Yuval is
  measuring directly.
- The **job of batch 1** is to replace these priors with Yuval's data and re-fit the tree.
