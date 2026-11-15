#!/usr/bin/env python3
"""Score a ~100-lipid library with the rule-based prior, to prioritise NEW lipids for Yuval.

Applies the decision-tree score (docs/chemistry_rules.md / the TLDR table) for Yuval's regime
(A53T, pH 7.4, high lipid:protein, aggregation baseline -> binders tend to REDUCE):

  charge:  anionic +2 | zwitterionic 0 | sterol -1 | cationic 0
  + big soluble anionic headgroup (ganglioside) : +1
  + fluid@37C AND short-saturated (<=14C) zwitterionic PC (DMPC-like weak sequestration): +1
  - gel@37C OR very long (>=20C mean) OR fully-saturated-insoluble: -0.5
  + single-chain / lyso (disperses better when added 'free' from ethanol): +0.5

  score >= 2 -> likely REDUCER ; 0..1 -> inert/mild ; < 0 -> likely promoter.

Tm is estimated from chain length/unsaturation (flagged); it only feeds the fluid@37 test.
THIS IS A PRIOR: direction set for Yuval's regime, unvalidated for his 'free-lipid' addition;
it is re-fit once his ThT data arrives. Output: outputs/lipid_library_scored.csv + top list.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

# headgroup -> (class, net charge at pH7.4, big_soluble_anionic_head)
HEADS = {
    "PS": ("glycerophospholipid", -1, False), "PG": ("glycerophospholipid", -1, False),
    "PA": ("glycerophospholipid", -1, False), "PI": ("glycerophospholipid", -1, False),
    "PC": ("glycerophospholipid", 0, False),  "PE": ("glycerophospholipid", 0, False),
}
# chain sets: (label, [(C,db),...], single_chain)
CHAINS = [
    ("DL", [(12, 0), (12, 0)], False), ("DM", [(14, 0), (14, 0)], False),
    ("DP", [(16, 0), (16, 0)], False), ("DS", [(18, 0), (18, 0)], False),
    ("DA", [(20, 0), (20, 0)], False), ("DB", [(22, 0), (22, 0)], False),
    ("DO", [(18, 1), (18, 1)], False), ("DArachidonoyl", [(20, 4), (20, 4)], False),
    ("PO", [(16, 0), (18, 1)], False), ("SO", [(18, 0), (18, 1)], False),
    ("Lyso16", [(16, 0)], True), ("Lyso18:1", [(18, 1)], True),
]

TM_ANCHOR = {12: -1, 14: 24, 16: 41, 18: 55, 20: 66, 22: 75, 24: 80}


def est_tm(chains, headgroup):
    mean_c = sum(c for c, _ in chains) / len(chains)
    tot_db = sum(d for _, d in chains)
    if tot_db > 0:                       # any unsaturation -> fluid
        tm = -5 - 10 * (tot_db - 1)
    else:                                # saturated: interpolate anchors
        lo = max(k for k in TM_ANCHOR if k <= mean_c) if mean_c >= 12 else 12
        hi = min(k for k in TM_ANCHOR if k >= mean_c) if mean_c <= 24 else 24
        tm = TM_ANCHOR[lo] if lo == hi else TM_ANCHOR[lo] + (TM_ANCHOR[hi] - TM_ANCHOR[lo]) * (mean_c - lo) / (hi - lo)
    if headgroup in ("PS", "PA"):
        tm += 4
    if len(chains) == 1:                 # lyso ~ lower / disperses
        tm -= 20
    return round(tm, 1), round(mean_c, 1), tot_db


def score_lipid(lclass, charge, chains, headgroup, big_head, single_chain):
    mean_c = sum(c for c, _ in chains) / len(chains) if chains else 0
    tot_db = sum(d for _, d in chains)
    tm, _, _ = est_tm(chains, headgroup) if chains else (999, 0, 0)
    fluid = tm < 37
    s = 0.0
    why = []
    if charge < 0:
        s += 2; why.append("anionic(+2)")
    elif lclass == "sterol":
        s -= 1; why.append("sterol(-1)")
    elif charge > 0:
        why.append("cationic(0)")
    else:
        why.append("zwitterionic(0)")
    if big_head:
        s += 1; why.append("big soluble head(+1)")
    if charge == 0 and lclass != "sterol" and fluid and tot_db == 0 and mean_c <= 14:
        s += 1; why.append("fluid short-sat PC(+1)")
    if chains and (not fluid or mean_c >= 20):
        s -= 0.5; why.append("gel/very-long(-0.5)")
    # single-chain amphiphiles: anionic ones are detergent-like -> MICELLE CATALYSIS -> accelerate
    # (JBC 2003, anionic-micelle-mediated fibrillization); neutral lyso just disperses.
    if single_chain and charge < 0:
        s -= 2; why.append("single-chain anionic=detergent/micelle->accelerates(-2)")
    elif single_chain:
        s += 0.5; why.append("neutral single-chain/lyso disperses(+0.5)")
    cls = "likely reducer" if s >= 2 else ("inert/mild" if s >= 0 else "likely promoter")
    return round(s, 2), cls, tm, round(mean_c, 1), tot_db, fluid, "; ".join(why)


def row(name, lclass, charge, chains, headgroup, big_head, single, note="", cand=0):
    s, cls, tm, mc, db, fluid, why = score_lipid(lclass, charge, chains, headgroup, big_head, single)
    acyl = "/".join(f"{c}:{d}" for c, d in chains) if chains else ""
    return dict(lipid=name, lipid_class=lclass, headgroup=headgroup, net_charge=charge,
                acyl=acyl, mean_C=mc, double_bonds=db, est_Tm_C=tm, fluid_37C=int(fluid),
                score=s, predicted=cls, is_candidate8=cand, rationale=why, note=note)


def build():
    rows = []
    # glycerophospholipids: headgroup x chains
    for hg, (lclass, charge, big) in HEADS.items():
        for label, chains, single in CHAINS:
            name = f"{label}{hg}"
            rows.append(row(name, lclass, charge, chains, hg, big, single))
    # gangliosides & complex glycosphingolipids (anionic, big soluble head) / neutral GSL
    gsl = [("GM1", -1, True), ("GM2", -1, True), ("GM3", -1, True), ("GD1a", -2, True),
           ("GD1b", -2, True), ("GT1b", -3, True), ("GQ1b", -4, True),
           ("Asialo-GM1", 0, True), ("Sulfatide", -1, False), ("GalCer", 0, False),
           ("LacCer", 0, False), ("GlcCer", 0, False)]
    for name, ch, big in gsl:
        lclass = "ganglioside" if name.startswith(("GM", "GD", "GT", "GQ")) else "glycosphingolipid"
        rows.append(row(name, lclass, ch, [(18, 0)], "glycan", big, False,
                        note="natural source; big head; added 'free' -> likely micellar"))
    # sphingolipids
    sph = [("SM(16:0)", "sphingolipid", 0, [(16, 0)]), ("SM(18:0)", "sphingolipid", 0, [(18, 0)]),
           ("SM(24:1)", "sphingolipid", 0, [(24, 1)]), ("egg-SM", "sphingolipid", 0, [(16, 0)]),
           ("Ceramide(16:0)", "sphingolipid", 0, [(16, 0)]), ("Ceramide(18:1)", "sphingolipid", 0, [(18, 1)]),
           ("Sphingosine", "sphingolipid", 1, [(18, 1)]), ("Sphinganine", "sphingolipid", 1, [(18, 0)]),
           ("S1P", "sphingolipid", -1, [(18, 1)])]
    for name, lclass, ch, chains in sph:
        rows.append(row(name, lclass, ch, chains, "sphingoid", False, len(chains) == 1))
    # sterols
    for name, ch in [("Cholesterol", 0), ("7-ketocholesterol", 0), ("25-OH-cholesterol", 0),
                     ("Cholesteryl-hemisuccinate", -1), ("Ergosterol", 0), ("Desmosterol", 0),
                     ("24-OH-cholesterol", 0)]:
        rows.append(row(name, "sterol", ch, [], "sterol", False, False,
                        note="sterol; condenses membrane / ↑hydrophobicity"))
    # free fatty acids (carboxylate, anionic at pH7.4) + a couple extras
    for name, chains in [("Oleic acid", [(18, 1)]), ("Palmitic acid", [(16, 0)]),
                         ("Arachidonic acid", [(20, 4)]), ("DHA", [(22, 6)]),
                         ("Lauric acid", [(12, 0)]), ("Myristic acid", [(14, 0)])]:
        rows.append(row(name, "fatty_acid", -1, chains, "carboxylate", False, True,
                        note="FFA: anionic at pH7.4; micellar when added free"))
    rows.append(row("Cardiolipin(18:1)", "cardiolipin", -2, [(18, 1), (18, 1), (18, 1), (18, 1)],
                    "diphosphatidylglycerol", False, False, note="net -2; 4 chains"))
    # mark the 8 candidates
    cand_map = {"DMPC": 1, "DPPC": 1, "DSPC": 1, "DOPC": 1, "POPC": 1, "GM1": 1}
    for r in rows:
        if r["lipid"] in cand_map:
            r["is_candidate8"] = 1
    for r in rows:
        if r["lipid"] in ("Cholesterol", "SM(16:0)", "egg-SM"):
            pass
    # cholesterol + sphingomyelin are candidates too
    for r in rows:
        if r["lipid"] == "Cholesterol" or r["lipid"].startswith("SM("):
            r["is_candidate8"] = 1
    return rows


def main():
    rows = build()
    rows.sort(key=lambda r: (-r["score"], r["lipid_class"]))
    fields = ["rank", "lipid", "score", "predicted", "lipid_class", "headgroup", "net_charge",
              "acyl", "mean_C", "double_bonds", "est_Tm_C", "fluid_37C", "is_candidate8",
              "rationale", "note"]
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    with open(os.path.join(OUT, "lipid_library_scored.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    # top list markdown
    L = [f"# Rule-scored lipid library ({len(rows)} lipids) — prioritised for Yuval's assay", "",
         "Score = literature-prior decision tree for Yuval's regime (A53T, pH 7.4, high "
         "lipid:protein). **>=2 likely reducer, 0–1 inert/mild, <0 likely promoter.** "
         "Prior only — re-fit on Yuval's ThT data; 'free' addition may change it.", "",
         "## Top 25", "", "| # | lipid | score | predicted | class | charge | chains | fluid@37 | why |",
         "|--|--|--|--|--|--|--|--|--|"]
    for r in rows[:25]:
        L.append(f"| {r['rank']} | {r['lipid']} | {r['score']} | {r['predicted']} | "
                 f"{r['lipid_class']} | {r['net_charge']} | {r['acyl'] or '—'} | "
                 f"{'yes' if r['fluid_37C'] else 'no'} | {r['rationale']} |")
    L += ["", "## Bottom 10 (predicted promoters / unhelpful)", "",
          "| lipid | score | predicted | why |", "|--|--|--|--|"]
    for r in rows[-10:]:
        L.append(f"| {r['lipid']} | {r['score']} | {r['predicted']} | {r['rationale']} |")
    open(os.path.join(OUT, "lipid_library_top.md"), "w").write("\n".join(L))

    from collections import Counter
    print(f"{len(rows)} lipids scored -> outputs/lipid_library_scored.csv + lipid_library_top.md")
    print("predicted:", dict(Counter(r["predicted"] for r in rows)))
    print("\nTop 12:")
    for r in rows[:12]:
        print(f"  {r['rank']:>2}. {r['lipid']:22} {r['score']:>4}  {r['predicted']:14} ({r['acyl'] or 'sterol'})")


if __name__ == "__main__":
    main()
