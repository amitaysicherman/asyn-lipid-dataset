#!/usr/bin/env python3
"""Design the first ThT screen for Yuval's assay, and emit a plate layout + data template.

Implements Yuval's protocol (docs/yuval_protocol.md): A53T alpha-syn, pH 7.4, lipids added
'free' from ethanol (GM1 from isopropanol) at 10:1 and 50:1 lipid:protein, shaking, 72 h.

The design's whole point is CLEAN comparison: every lipid is paired with a **solvent-matched,
lipid-free control at the same % solvent**, because 2% vs 10% ethanol is itself a variable.

Outputs to experiments/:
  plate_layout.csv        - one row per well (what to pipette where), with a plate grid
  results_template.csv    - the sheet Yuval fills (endpoints per condition), ingest-ready
Run: python3 src/design_experiment.py [protein_uM]   (default 100)
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "experiments")
os.makedirs(OUT, exist_ok=True)

CANDIDATES = ["Cholesterol", "SM", "DMPC", "DPPC", "DSPC", "DOPC", "POPC", "GM1"]
# Top rule-predicted anionic REDUCERS added to test the prior's key prediction
# (anionic lipids reduce; the PC/cholesterol set does not), at Yuval's regime.
EXTRA_ANIONIC = ["GM3", "DOPS", "POPG", "Cardiolipin"]
TEST_LIPIDS = CANDIDATES + EXTRA_ANIONIC
# gangliosides go in isopropanol (like GM1); everything else in ethanol
GANGLIOSIDES = {"GM1", "GM3"}
RATIOS = [10, 50]
REPLICATES = 3
# solvent % by ratio, from the protocol tables
ETHANOL_PCT = {10: 2.0, 50: 10.0}
GM1_IPA_PCT = {10: 1.6, 50: 8.0}


def is_gang(lipid):
    return lipid in GANGLIOSIDES


def solvent_for(lipid, ratio):
    if is_gang(lipid):
        return "isopropanol", GM1_IPA_PCT[ratio]
    return "ethanol", ETHANOL_PCT[ratio]


def build(protein_uM):
    conditions = []  # dict per condition (before replicating)
    # ---- controls (critical) ----
    conditions.append(dict(cond_id="CTRL_buffer", role="control", lipid="", ratio="",
                           lipid_mM="", solvent="none", solvent_pct=0, protein_uM=0,
                           note="buffer + ThT only; instrument/ThT baseline (no protein)"))
    conditions.append(dict(cond_id="CTRL_protein_only", role="control", lipid="", ratio="",
                           lipid_mM="", solvent="none", solvent_pct=0, protein_uM=protein_uM,
                           note="alpha-syn alone; aggregation baseline (no lipid, no added solvent)"))
    for r in RATIOS:
        conditions.append(dict(cond_id=f"CTRL_EtOH_{ETHANOL_PCT[r]:g}pct", role="control",
                               lipid="", ratio=r, lipid_mM="", solvent="ethanol",
                               solvent_pct=ETHANOL_PCT[r], protein_uM=protein_uM,
                               note=f"solvent control for ethanol lipids at {r}:1 ratio"))
    for r in RATIOS:
        conditions.append(dict(cond_id=f"CTRL_iPrOH_{GM1_IPA_PCT[r]:g}pct", role="control",
                               lipid="", ratio=r, lipid_mM="", solvent="isopropanol",
                               solvent_pct=GM1_IPA_PCT[r], protein_uM=protein_uM,
                               note=f"solvent control for GM1 at {r}:1 ratio"))
    # ---- lipid conditions ----
    for lipid in TEST_LIPIDS:
        for r in RATIOS:
            solv, pct = solvent_for(lipid, r)
            lipid_mM = round(r * protein_uM / 1000.0, 3)  # ratio * [prot]; uM->mM
            conditions.append(dict(cond_id=f"{lipid}_{r}to1", role="lipid", lipid=lipid,
                                   ratio=r, lipid_mM=lipid_mM, solvent=solv, solvent_pct=pct,
                                   protein_uM=protein_uM,
                                   note=f"match to CTRL_{'iPrOH' if lipid=='GM1' else 'EtOH'}_"
                                        f"{pct:g}pct"))
    # ---- replicate into wells + assign to a 96-well grid ----
    rows_letters = "ABCDEFGH"
    wells = [f"{r}{c}" for c in range(1, 13) for r in rows_letters]  # column-major fill
    layout, i = [], 0
    for cond in conditions:
        for rep in range(1, REPLICATES + 1):
            w = wells[i]; i += 1
            layout.append(dict(well=w, replicate=rep, **cond))
    n_wells = len(layout)
    return conditions, layout, n_wells


def main():
    protein_uM = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    conditions, layout, n_wells = build(protein_uM)

    # plate_layout.csv
    fields = ["well", "cond_id", "role", "lipid", "ratio", "lipid_mM", "solvent",
              "solvent_pct", "protein_uM", "replicate", "note"]
    with open(os.path.join(OUT, "plate_layout.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(layout)

    # results_template.csv — one row per condition for Yuval to fill (or auto-filled from curves)
    tfields = ["cond_id", "lipid", "ratio", "protein_uM", "solvent", "solvent_pct",
               "matched_control_cond_id",
               "lag_time_h", "t_half_h", "endpoint_RFU", "auc",
               "relative_reduction_vs_solvent_ctrl", "n_replicates", "notes"]
    trows = []
    for c in conditions:
        if c["role"] != "lipid":
            matched = ""
        else:
            matched = (f"CTRL_iPrOH_{c['solvent_pct']:g}pct" if is_gang(c["lipid"])
                       else f"CTRL_EtOH_{c['solvent_pct']:g}pct")
        trows.append(dict(cond_id=c["cond_id"], lipid=c["lipid"], ratio=c["ratio"],
                          protein_uM=c["protein_uM"], solvent=c["solvent"],
                          solvent_pct=c["solvent_pct"], matched_control_cond_id=matched,
                          n_replicates=REPLICATES))
    with open(os.path.join(OUT, "results_template.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=tfields, extrasaction="ignore")
        w.writeheader(); w.writerows(trows)

    # a human-readable plate grid
    grid = {row: {col: "" for col in range(1, 13)} for row in "ABCDEFGH"}
    for L in layout:
        row, col = L["well"][0], int(L["well"][1:])
        tag = (L["cond_id"].replace("CTRL_", "·") + f".{L['replicate']}")
        grid[row][col] = tag
    with open(os.path.join(OUT, "plate_grid.txt"), "w") as f:
        f.write(f"96-well plate layout — A53T a-syn {protein_uM} uM, pH 7.4 (Greiner 655090)\n")
        f.write(f"{len(conditions)} conditions x {REPLICATES} reps = {n_wells} wells\n\n")
        header = "    " + "".join(f"{c:>16}" for c in range(1, 13))
        f.write(header + "\n")
        for row in "ABCDEFGH":
            f.write(f"{row}  " + "".join(f"{grid[row][c]:>16}" for c in range(1, 13)) + "\n")

    print(f"protein {protein_uM} uM | conditions={len(conditions)} "
          f"({len(TEST_LIPIDS)} lipids x 2 ratios + {len(conditions)-2*len(TEST_LIPIDS)} controls) | wells={n_wells}/96")
    print("wrote experiments/plate_layout.csv, results_template.csv, plate_grid.txt")
    print("\nController pairings (lipid -> solvent-matched control):")
    for c in conditions:
        if c["role"] == "lipid":
            m = (f"CTRL_iPrOH_{c['solvent_pct']:g}pct" if is_gang(c["lipid"])
                 else f"CTRL_EtOH_{c['solvent_pct']:g}pct")
            print(f"  {c['cond_id']:16} {c['lipid_mM']} mM, {c['solvent_pct']:g}% {c['solvent']:11} -> {m}")


if __name__ == "__main__":
    main()
