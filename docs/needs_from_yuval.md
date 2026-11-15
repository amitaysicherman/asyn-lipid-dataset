# Exact experimental details needed from Yuval's wet-lab protocol

The accessible literature shows that α-synuclein's response to a lipid **flips or scales** with
nearly every assay parameter (pH flips GM1 between inhibition and acceleration; lipid:protein ratio
makes DMPS switch between triggering and fibril dissolution; plate surface and agitation change the
dominant nucleation route). So a model can only be tied to Yuval's assay once these are known.
Each item below lists *why it matters* with the evidence from the dataset.

## Assay chemistry & conditions
1. **Buffer and pH.** Decisive. GM1 inhibits at neutral pH (Martinez 2007) but accelerates at
   pH 5.5 (Grey 2015, Gaspar 2018). Which regime is Yuval's?
2. **Agitation** (quiescent vs shaking, and rpm/bead/geometry). Determines whether secondary
   nucleation/fragmentation is active; Grey shows shaking vs quiescent changes rates and which
   effects are even detectable.
3. **Plate / surface** (binding polystyrene vs non-binding PEGylated; well geometry). Non-binding
   plates suppress surface nucleation so that *only* lipid effects show (Grey, Galvagnion); binding
   plates can nucleate on their own.
4. **Temperature.**
5. **ThT concentration** and **read settings** (ex/em, top/bottom read).
6. **Salt / ionic strength.** Screens the electrostatic lipid–protein interaction (Galvagnion 2015:
   added NaCl slows DMPS-driven aggregation).

## Protein
7. **α-synuclein variant** (WT vs A53T/A30P/E46K) and any tags/modifications. A30P barely binds GM1
   (Martinez); variant changes behaviour.
8. **Preparation** (monomer isolation / gel-filtration, freshness) — strongly affects reproducibility.
9. **Protein concentration.**
10. **Seeding status** (unseeded vs % preformed seeds). Changes the kinetics and the meaning of a
    "reduction."

## Lipid / formulation
11. **Formulation** (SUV/LUV/micelle/free lipid), **vesicle size**, **prep method**.
12. **Total lipid concentration, per-component concentration, and lipid:protein molar ratio** — and
    for mixtures, **mol fractions on a molar (not mass) basis**. The ratio alone can flip the sign
    (Galvagnion 2015).
13. For the candidates: exact species (e.g. brain vs egg **sphingomyelin**; ganglioside source),
    supplier/catalog, and purity.

## Readout / labelling
14. **How "effect" is scored** — endpoint fluorescence, AUC, lag time, half-time, or independently
    measured fibril mass (e.g. pelleting/sedimentation, TEM). This decides which target the model
    should predict and whether amplitudes are comparable.
15. **Matched controls** run in the same plate/batch (lipid-free, and ideally a buffer-only ThT blank).
16. **Replicates** and batch structure (so replicate wells aren't mistaken for independent experiments).

## The key scientific question to pin down with Yuval
Is the goal to **prevent** fibril formation from monomer (lipid present from t=0) or to **treat**
existing fibrils? These are different experiments (Galvagnion 2015 shows excess DMPS can dissolve
preformed fibrils — a *treatment* effect distinct from *prevention*). The dataset separates these;
the protocol should state which one the project targets.
