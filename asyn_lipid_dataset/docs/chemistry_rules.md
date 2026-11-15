# Mechanistic rules for how lipids modulate α-synuclein fibril formation

This is a **chemistry-based reading** of the extracted dataset — the rules I would use to
rank lipids by hand, independent of the ML model. Each rule gives the **mechanism**, the
**evidence** in our dataset, and **which of the 8 candidates it touches**. The rules are
encoded in `src/chemistry_ranking.py` (a transparent, condition-parameterised scorer).

Legend: **[fact]** = directly supported by an extracted measurement; **[inference]** =
mechanistic reasoning / established membrane biophysics; **[hypothesis]** = plausible,
untested here.

---

## 0. The molecule sets up two opposing effects

α-Synuclein has three parts that matter:
- **N-terminal lipid-binding region (res 1–60):** 7 imperfect KTKEGV repeats, lysine-rich
  (**cationic**); folds into an **amphipathic α-helix** on anionic membranes.
- **NAC region (61–95):** hydrophobic, the amyloid core.
- **C-terminal tail (96–140):** acidic (**anionic**), stays in solution.

Binding is driven by (i) **electrostatics** (cationic N-term ↔ anionic headgroups) and
(ii) **hydrophobic insertion** into membrane **packing defects**. A lipid surface then does
two *opposite* things to aggregation:

- **(+) Surface catalysis:** binding concentrates α-syn in 2D → high local concentration →
  **accelerates primary nucleation** at the interface. [fact: Galvagnion 2015 — nucleation
  rate ↑ >1000×]
- **(−) Sequestration:** if essentially all α-syn is locked in the stable membrane-bound
  helix (no free monomer), nucleation **stops**, and excess membrane can even **dissolve
  fibrils** (the bound state is thermodynamically more stable than the fibril).
  [fact: Galvagnion 2015 — ratio >40 gives no aggregation; 2–8 mM DMPS dissolves fibrils]

**Everything below is about which of these two wins.** That is why the same lipid can
accelerate *or* inhibit.

---

## Rule 1 — Headgroup charge is the gate for strong binding
**Mechanism:** the cationic N-terminus needs anionic headgroups (PS, PG, PA, PI, cardiolipin,
gangliosides) for tight binding. Zwitterionic PC/PE (net-neutral) and cholesterol bind only
weakly. [inference, standard]
**Evidence:** α-syn binds all *fluid anionic* lipids with similar KD ≈ 0.2–0.5 µM
[fact: Galvagnion 2016 Table 1]; **pure DOPC shows no binding and no aggregation**
[fact: Gaspar 2018]; cholesterol in a mixed membrane does not initiate [fact: Galvagnion 2016].
**Touches the candidates:** **only GM1 is anionic.** DMPC, DPPC, DSPC, DOPC, POPC (all PC) +
SM (phosphocholine head) + cholesterol are **neutral → weak binders → low leverage** either
way.

## Rule 2 — Binding is necessary but NOT sufficient to trigger; acyl-chain *solubility* decides
**Mechanism:** the rate-limiting nucleation step requires **extracting a lipid from the
bilayer** into the growing nucleus. Short, saturated chains → higher aqueous solubility →
lower extraction cost → **triggers**. Long/unsaturated chains bind but **do not** trigger.
[inference from the data below]
**Evidence [fact: Galvagnion 2016]:** among anionic PS lipids that all bind similarly,
**only the most soluble trigger**: DLPS (12:0) > DMPS (14:0) ≫ DPPS (16:0, none); DOPS (18:1),
POPS (16:0/18:1) bind but do **not** trigger. Aggregation rate ∝ 1/ΔG°(water→bilayer).
DPPS kept at 50 °C (now fluid) still does not trigger → **chemistry, not phase, sets the
magnitude.**
**Touches the candidates:** explains why the long/unsaturated PCs would be non-triggering even
if they were charged; and why **GM1** (large, highly soluble headgroup, 1–30 µM) is an
effective trigger when charge is "on".

## Rule 3 — Gangliosides are a special high-leverage class
**Mechanism:** large sialylated oligosaccharide headgroup = **anionic + very soluble + charge
presented far from the bilayer** → strong, accessible binding and efficient catalysis.
[inference] Even *uncharged* large heads (asialo-GM1, Cer-PEG) weakly trigger → headgroup
bulk/entropy contributes, but **charge dominates**. [fact: Gaspar 2018]
**Touches the candidates:** **GM1.** This is the one candidate that can both strongly trigger
*and* strongly inhibit, depending on conditions (Rules 4–5).

## Rule 4 — pH flips the sign (this is the master switch)
**Mechanism:** at **neutral pH** the acidic C-terminus is fully charged → strong monomer–
monomer repulsion, **secondary nucleation is slow**; a strong binder then mostly
**sequesters** monomer in the helix → **inhibits**. At **mildly acidic pH (~5.5)** α-syn net
charge ≈ 0 (pI ≈ 4.7) → repulsion screened, **secondary nucleation dramatically faster**,
membrane catalysis dominates → **accelerates**. [inference, strongly supported]
**Evidence [fact]:** **GM1 inhibits/eliminates fibrillation at neutral pH** (Martinez 2007)
but **accelerates at pH 5.5** (Grey 2015, Gaspar 2018) — and both acidic-pH papers explicitly
cite the neutral-pH inhibition result. Same lipid, opposite sign.
**Touches the candidates:** decisive for **GM1**. Also means the whole ranking must be given
*per pH* (see `chemistry_ranking.py` Scenarios A vs B).

## Rule 5 — Lipid:protein ratio is biphasic (the dose switch)
**Mechanism:** the catalytic (+) effect needs **free monomer** present; the sequestration (−)
effect needs **excess lipid**. [inference]
**Evidence [fact: Galvagnion 2015]:** DMPS at **low** ratio (2–15, max rate ~8) strongly
accelerates; at **high** ratio (>40) gives **no** aggregation and **dissolves preformed
fibrils**. Also DMPC dilution of DMPS: >25 % DMPC → no triggering [fact: Galvagnion 2016].
**Implication for our goal:** to *reduce* fibrils with any binding lipid, you want a **high
lipid:protein ratio**. "Stronger binding ≠ stronger inhibition" — strength of binding only
helps inhibition in the high-ratio / neutral-pH regime.

## Rule 6 — Membrane phase controls *binding efficiency* (not triggering magnitude)
**Mechanism:** **fluid** bilayers expose more hydrophobic area + allow lateral diffusion →
bind α-syn ~10× better (stoichiometry ~30 lipids/protein) than **gel** bilayers (~250).
[fact: Galvagnion 2016 Table 1 — DPPS gel L≈251 vs fluid ~30]
**Touches the candidates:** at a 37 °C assay, **DSPC (Tm 55 °C) and DPPC (Tm 41 °C) are gel**
(bind α-syn least), **DMPC (24 °C), POPC (−2 °C), DOPC (−17 °C) are fluid**, **SM (~39 °C)
near/above** → **ordered**. Gel/ordered neutral lipids are the *most inert* (least interaction
of all).

## Rule 7 — Zwitterionic lipids act as charge diluents (passive protection)
**Mechanism:** mixing neutral PC into an anionic membrane lowers surface charge density →
weakens α-syn binding → less catalysis. [inference]
**Evidence [fact: Galvagnion 2016]:** DMPC:DMPS — binding falls as DMPC rises; >25 % DMPC
abolishes triggering.
**Touches the candidates:** the PC candidates can *blunt* an anionic trigger, but this is a
dilution effect, not intrinsic inhibition.

## Rule 8 — Ordered/raft lipids lower the density of nucleation-competent defects
**Mechanism [hypothesis]:** α-syn inserts at **packing defects**. Cholesterol condenses
bilayers and, with sphingomyelin and saturated PC, forms tightly-packed **liquid-ordered /
raft** phases with few defects → fewer heterogeneous-nucleation sites → mildly protective.
**Evidence:** cholesterol added to a synaptic-mimic membrane did not initiate aggregation
[fact: Galvagnion 2016]; the rest is established raft biophysics [hypothesis for α-syn].
**Touches the candidates:** ranks the neutral candidates among themselves:
**cholesterol > DSPC ≈ DPPC ≈ SM (ordered, defect-poor) > DMPC > POPC > DOPC (loose, defect-rich).**

---

## Synthesis: what determines accelerate vs. inhibit

```
            charged & soluble?          pH / ratio
 lipid ──► (anionic + short-sat         ──► acidic + low ratio ─► ACCELERATE (surface catalysis)
            or ganglioside)             ──► neutral + high ratio ─► INHIBIT  (sequestration)
       └─► neutral (PC/SM/chol) ─► weak binding ─► INERT ─► at most mild, passive protection
                                                   (ordered/raft lipids a little more protective)
```

The single most useful sentence: **only an anionic, soluble binder (among the 8, just GM1)
can *actively* suppress α-syn — and only at neutral pH with excess lipid; otherwise it does the
opposite. The seven neutral candidates cannot actively inhibit, but they are safe and the
tightly-packed ones are mildly protective.**

---

## Ranking the 8 candidates (and why)

Produced quantitatively by `src/chemistry_ranking.py`; the summary:

**If the wet-lab assay can be run at NEUTRAL pH with EXCESS lipid (the inhibition-favouring
regime):**
1. **GM1** — the only candidate that can *actively* inhibit (binds strongly, sequesters
   monomer, induces stable helix). [fact at neutral pH: Martinez 2007]
2. **Cholesterol** — best "passive" protector (condenses membranes, removes defects).
3–4. **Sphingomyelin ≈ DSPC ≈ DPPC** — ordered/gel, defect-poor, most inert.
5. **DMPC** — fluid but saturated; inert, slightly less ordered.
6–7. **DOPC ≈ POPC** — fluid, unsaturated, defect-rich; inert but least protective (DOPC's
   mild retardation is the only *measured* hint of protection here).

**If the assay is ACIDIC / low ratio (the triggering regime, as in Grey/Gaspar):** GM1 drops
to **last** (it becomes a strong promoter); the neutral lipids keep the same order and are the
only safe choices.

**Candidates with zero direct evidence (DPPC, DSPC, POPC):** their positions are **predictions
from the rules, not observations** — they should be the first dedicated wet-lab experiments.

---

## Testable predictions for the wet lab (to validate these rules)
1. **GM1 pH-switch:** titrate GM1:α-syn at pH 5.5 vs 7.4 — predict acceleration at acidic/low
   ratio, inhibition at neutral/high ratio, with a crossover. This single experiment validates
   Rules 3–5 and pins down GM1's usable window.
2. **Cholesterol dose in an *aggregating* system:** cholesterol (0–40 %) in a membrane that
   otherwise triggers (e.g. with DMPS) — predict monotonic *reduction* of triggering (Rule 8).
3. **Saturation/length series of neutral PC:** DOPC vs POPC vs DMPC vs DPPC vs DSPC at fixed
   conditions — predict all inert, with the ordered (DPPC/DSPC) giving the largest mild
   retardation (Rules 6, 8). Fills the DPPC/DSPC/POPC evidence gap.
4. **Raft mimic:** cholesterol + sphingomyelin + saturated PC vs a loose DOPC membrane —
   predict the raft mimic is the more protective (Rule 8).

## Honest caveats
- Rules 1–7 are well-supported by the extracted data; **Rule 8 (ordering protection) is the
  main hypothesis** and is what separates the otherwise-tied neutral candidates — treat that
  sub-ranking as a prediction to test, not a finding.
- All of this is **in-vitro ThT chemistry**. Brain targeting / BBB transport are out of scope
  and would re-order candidates for a therapeutic (e.g. cholesterol/SM behave very differently
  in vivo).
- The scorer's weights are chosen to reflect the mechanisms transparently, not fitted to data;
  they are meant to be read and argued with, not treated as calibrated probabilities.
