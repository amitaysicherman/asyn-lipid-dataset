#!/usr/bin/env python3
"""Rule-based (NOT machine-learned) ranking of lipids for REDUCING alpha-synuclein
fibril formation, from first-principles membrane biophysics grounded in the extracted
dataset.

The score is fully transparent: every lipid's number decomposes into named mechanistic
terms, and the ranking is recomputed for the assay conditions you give (pH and
lipid:protein ratio FLIP the answer, so a single ranking would be misleading).

Mechanistic terms (each 0-3 unless noted), per the rules in docs/chemistry_rules.md:
  B   binding strength of alpha-syn to the lipid surface
  T   triggering propensity  (promotes aggregation  -> BAD for our goal)
  Iseq sequestration-inhibition capacity (soaks up monomer -> GOOD)
  O   ordering/defect protection (raft-like packing lowers nucleation sites -> mild GOOD)
  reduction_potential = Iseq + O - T   (rescaled 0-10; higher = more likely to REDUCE fibrils)

Evidence confidence is reported separately (direct data vs pure chemical prediction).

Usage:
  python3 src/chemistry_ranking.py                 # prints two standard scenarios
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

CANDIDATES = ["GM1", "Cholesterol", "SM", "DMPC", "DPPC", "DSPC", "DOPC", "POPC"]

# evidence confidence from the pilot dataset (how much DIRECT aggregation data exists)
CONFIDENCE = {
    "GM1": "moderate (multiple papers; but pH-conflicted)",
    "DOPC": "moderate (pure DOPC tested: inert/mild retardation)",
    "Cholesterol": "low (one additive test: no initiation)",
    "DMPC": "low (only as DMPS diluent)",
    "SM": "very low (abstract: 'negligible interaction')",
    "DPPC": "none (prediction from rules only)",
    "DSPC": "none (prediction from rules only)",
    "POPC": "none (prediction from rules only)",
}


def is_fluid(lip, temp):
    tm = lip.get("tm_C", "")
    try:
        return float(tm) < temp
    except (TypeError, ValueError):
        return True  # gangliosides/sterol/unsaturated: treat as non-gel / fluid-compatible


def binding_B(lip, temp):
    charge = _f(lip["net_charge_phys"])
    cls = lip["lipid_class"]
    if cls == "ganglioside":
        return 3.0  # anionic + large, highly accessible, soluble headgroup
    if charge is not None and charge < 0:          # anionic phospholipid
        return 3.0 if is_fluid(lip, temp) else 1.0
    if cls == "sterol":
        return 0.3
    return 0.5                                      # zwitterionic PC/PE/SM: weak


def triggering_T(lip, temp, pH, ratio_high):
    """Intrinsic propensity to PROMOTE nucleation, modulated by pH and ratio."""
    charge = _f(lip["net_charge_phys"])
    cls = lip["lipid_class"]
    meanC = _f(lip["mean_chain_carbons"])
    db = _f(lip["total_double_bonds"]) or 0
    # intrinsic (acidic, low-ratio) triggering strength
    if cls == "ganglioside":
        base = 2.5
    elif charge is not None and charge < 0:
        # short + saturated anionic = high solubility = strong trigger (Galvagnion rule)
        if meanC is not None and meanC <= 14 and db == 0:
            base = 3.0
        else:
            base = 0.5          # long/unsaturated anionic: binds but does not trigger
    else:
        base = 0.0              # zwitterionic / sterol: do not trigger
    # pH: neutral strongly suppresses triggering (alpha-syn repulsion high; and gangliosides
    # flip to inhibition at neutral pH). acidic = full triggering.
    pH_factor = 1.0 if pH < 6.5 else (0.5 if pH < 7.0 else 0.15)
    # ratio: excess lipid removes free monomer -> less triggering
    ratio_factor = 0.25 if ratio_high else 1.0
    return base * pH_factor * ratio_factor


def sequestration_I(lip, temp, pH, ratio_high):
    """Capacity to inhibit by soaking monomer into a stable bound state."""
    B = binding_B(lip, temp)
    ratio_factor = 1.0 if ratio_high else 0.2     # need excess lipid to deplete monomer
    pH_factor = 1.0 if pH >= 7.0 else (0.6 if pH >= 6.5 else 0.3)  # neutral favours clean sequestration
    return B * ratio_factor * pH_factor


def ordering_O(lip, temp):
    """Raft-like, defect-poor packing lowers heterogeneous-nucleation site density.
    Mechanistic hypothesis; weighted low. Only meaningful when the lipid is a major
    membrane component."""
    cls = lip["lipid_class"]
    charge = _f(lip["net_charge_phys"])
    if cls == "sterol":
        return 1.0
    if charge is not None and charge < 0:
        return 0.0
    if cls in ("sphingolipid",) or (not is_fluid(lip, temp)):  # SM / gel saturated PC
        return 0.7
    meanC = _f(lip["mean_chain_carbons"]) or 0
    db = _f(lip["total_double_bonds"]) or 0
    if db == 0 and meanC <= 14:      # DMPC: fluid but saturated
        return 0.3
    return 0.1                        # unsaturated loose (DOPC/POPC)


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def score(lip, temp, pH, ratio_high):
    B = binding_B(lip, temp)
    T = triggering_T(lip, temp, pH, ratio_high)
    I = sequestration_I(lip, temp, pH, ratio_high)
    O = ordering_O(lip, temp)
    raw = I + O - T                 # range roughly [-3, +4]
    reduction = round(10 * (raw + 3) / 7, 1)   # rescale to 0-10
    return dict(B=round(B, 2), T=round(T, 2), Iseq=round(I, 2), O=round(O, 2),
                raw=round(raw, 2), reduction_potential=reduction)


def rank(lipids, temp, pH, ratio_high):
    rows = []
    for c in CANDIDATES:
        lip = lipids[c]
        s = score(lip, temp, pH, ratio_high)
        rows.append(dict(candidate=c, **s))
    rows.sort(key=lambda r: r["reduction_potential"], reverse=True)
    return rows


def scenario_md(title, note, rows):
    L = [f"### {title}", "", f"_{note}_", "",
         "| rank | candidate | reduction potential (0-10) | trigger risk T | sequestration Iseq | ordering O | evidence |",
         "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        L.append(f"| {i} | **{r['candidate']}** | {r['reduction_potential']} | {r['T']} | "
                 f"{r['Iseq']} | {r['O']} | {CONFIDENCE[r['candidate']]} |")
    return "\n".join(L)


def main():
    lipids = {r["lipid_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "lipids.csv")))}
    L = ["# Rule-based lipid ranking for REDUCING alpha-synuclein fibril formation", "",
         "Transparent, mechanism-driven (not ML). Scores decompose into binding (B), "
         "triggering risk (T), sequestration-inhibition (Iseq) and ordering/defect "
         "protection (O); `reduction_potential = Iseq + O - T` rescaled to 0-10. "
         "Rules & justification: `docs/chemistry_rules.md`. **The ranking changes with "
         "assay conditions** - that is the point.", ""]

    # Scenario A: the regime that FAVOURS inhibition (what to aim for)
    L.append(scenario_md(
        "Scenario A - Neutral pH (7.4), HIGH lipid:protein ratio, 37 C",
        "Inhibition-favouring regime: excess membrane sequesters monomer; neutral pH keeps "
        "secondary nucleation slow. This is where a strong binder can actively suppress fibrils.",
        rank(lipids, temp=37, pH=7.4, ratio_high=True)))
    L.append("")
    # Scenario B: the regime that FAVOURS triggering (danger regime)
    L.append(scenario_md(
        "Scenario B - Acidic pH (5.5), LOW lipid:protein ratio, 37 C",
        "Triggering-favouring regime (as in Grey/Gaspar). Here anionic/ganglioside lipids "
        "PROMOTE aggregation; only the inert neutral lipids are 'safe'.",
        rank(lipids, temp=37, pH=5.5, ratio_high=False)))
    L.append("")
    L.append("## How to read this")
    L.append(
        "- **GM1 is the only high-leverage candidate** and it is a *switch*: top of Scenario A "
        "(neutral pH, excess GM1 -> sequesters monomer, induces stable helix -> inhibits, per "
        "Martinez 2007) but a strong *promoter* in Scenario B (acidic, low ratio -> Grey/Gaspar). "
        "Its rank swings the most between scenarios.\n"
        "- **The seven neutral candidates cannot strongly inhibit** (weak alpha-syn binding), but "
        "they are *safe* (they do not trigger). Among them the protective ordering term ranks the "
        "tightly-packed, defect-poor lipids first: **cholesterol > DSPC ~ DPPC ~ sphingomyelin > "
        "DMPC > POPC > DOPC**.\n"
        "- So the practical answer depends entirely on which lever the wet lab can pull: a strong "
        "*active* inhibitor (GM1, only at neutral pH + high ratio) vs a *passive, safe* membrane "
        "(ordered raft lipids: cholesterol/SM/saturated-PC).\n"
        "- Terms marked low-confidence (DPPC/DSPC/POPC) are **predictions from the rules, not "
        "observations** - no direct ThT data exists for them yet.")
    open(os.path.join(OUT, "chemistry_ranking.md"), "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
