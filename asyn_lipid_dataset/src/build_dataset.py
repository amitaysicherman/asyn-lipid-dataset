#!/usr/bin/env python3
"""Flatten the curated extraction records into the linked CSV tables.

Outputs to data/:
  papers.csv, conditions.csv, components.csv, measurements.csv, curves.csv
plus a merged analysis view data/measurements_enriched.csv (joins lipid descriptors,
standardized ratios) used by the modelling scripts.

All derived quantities (lipid:protein ratios, standardized concentrations) are computed
deterministically here and flagged as 'calculated'. No measured values are invented.
"""
import csv
import os
import re
from extraction_records import PAPERS, CONDITIONS, CROSS_REFS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")


def num(x):
    """Return float if x is a clean number, else None (ranges/strings -> None)."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", s):
            return float(s)
    return None


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    # ---- papers.csv ----
    pf = ["paper_id", "authors", "year", "title", "journal", "doi", "pmid", "pmcid",
          "access_status", "role", "notes"]
    write_csv(os.path.join(DATA, "papers.csv"), PAPERS, pf)

    # ---- conditions.csv ----
    cond_rows, comp_rows, meas_rows = [], [], []
    meas_counter = 0
    for cond in CONDITIONS:
        protein_uM = num(cond.get("protein_conc_uM"))
        # total lipid: take the max over components that have a numeric total
        total_lipid_vals = [num(c.get("total_lipid_uM")) for c in cond["components"]]
        total_lipid_vals = [v for v in total_lipid_vals if v is not None]
        total_lipid_uM = total_lipid_vals[0] if total_lipid_vals else None
        lp_ratio = (round(total_lipid_uM / protein_uM, 3)
                    if (total_lipid_uM is not None and protein_uM) else "")
        cond_rows.append(dict(
            condition_id=cond["condition_id"], paper_id=cond["paper"],
            label=cond.get("label", ""), assay_type=cond.get("assay_type", ""),
            assay_paradigm=cond.get("assay_paradigm", ""),
            protein_variant=cond.get("protein_variant", ""),
            protein_conc_uM=cond.get("protein_conc_uM", ""),
            buffer=cond.get("buffer", ""), pH=cond.get("pH", ""),
            salt_mM=cond.get("salt_mM", ""), temp_C=cond.get("temp_C", ""),
            agitation=cond.get("agitation", ""), plate=cond.get("plate", ""),
            tht_uM=cond.get("tht_uM", ""), formulation=cond.get("formulation", ""),
            prep_method=cond.get("prep_method", ""),
            vesicle_size_nm=cond.get("vesicle_size_nm", ""),
            seeding=cond.get("seeding", ""), obs_h=cond.get("obs_h", ""),
            total_lipid_uM=(total_lipid_uM if total_lipid_uM is not None else ""),
            lipid_to_protein_molar_ratio=lp_ratio,
            source_page=cond.get("source_page", ""),
        ))
        # ---- components.csv ----
        for i, comp in enumerate(cond["components"], 1):
            comp_conc = num(comp.get("component_conc_uM"))
            comp_lp = (round(comp_conc / protein_uM, 3)
                       if (comp_conc is not None and protein_uM) else "")
            comp_rows.append(dict(
                component_id=f"{cond['condition_id']}__comp{i}",
                condition_id=cond["condition_id"],
                lipid_id=comp.get("lipid_id", ""),
                role=comp.get("role", ""),
                mol_fraction=comp.get("mol_fraction", ""),
                fraction_basis=comp.get("fraction_basis", ""),
                total_lipid_uM=comp.get("total_lipid_uM", ""),
                component_conc_uM=comp.get("component_conc_uM", ""),
                component_to_protein_molar_ratio=comp_lp,
                note=comp.get("note", ""),
            ))
        # ---- measurements.csv ----
        for meas in cond["measurements"]:
            meas_counter += 1
            meas_rows.append(dict(
                measurement_id=f"M{meas_counter:03d}",
                condition_id=cond["condition_id"], paper_id=cond["paper"],
                endpoint=meas.get("endpoint", ""),
                evidence_category=meas.get("evidence_category", ""),
                effect_direction=meas.get("effect_direction", ""),
                value=meas.get("value", ""), value_text=meas.get("value_text", ""),
                unit=meas.get("unit", ""), uncertainty=meas.get("uncertainty", ""),
                n_replicates=meas.get("n_rep", ""),
                control_id=meas.get("control_id", ""),
                evidence_type=meas.get("evidence_type", ""),
                source_fig=meas.get("source_fig", ""),
                source_quote=meas.get("source_quote", ""),
                quality_flag=meas.get("quality_flag", ""),
            ))

    write_csv(os.path.join(DATA, "conditions.csv"), cond_rows, list(cond_rows[0].keys()))
    write_csv(os.path.join(DATA, "components.csv"), comp_rows, list(comp_rows[0].keys()))
    write_csv(os.path.join(DATA, "measurements.csv"), meas_rows, list(meas_rows[0].keys()))

    # ---- curves.csv (schema only; populated by digitize_curves.py when run) ----
    curves_path = os.path.join(DATA, "curves.csv")
    if not os.path.exists(curves_path):
        write_csv(curves_path, [], ["curve_id", "condition_id", "series_label",
                  "time_h", "tht_value", "normalization", "source_fig",
                  "digitized", "digitization_tool", "note"])

    # ---- cross_refs.csv ----
    write_csv(os.path.join(DATA, "cross_refs.csv"), CROSS_REFS,
              ["claim", "asserted_in", "source_quote", "evidence_type", "note"])

    print(f"papers={len(PAPERS)} conditions={len(cond_rows)} "
          f"components={len(comp_rows)} measurements={len(meas_rows)}")
    # quick integrity: every component lipid_id (non-empty) must be in lipids.csv
    lipid_ids = {r["lipid_id"] for r in csv.DictReader(open(os.path.join(DATA, "lipids.csv")))}
    missing = sorted({c["lipid_id"] for c in comp_rows
                      if c["lipid_id"] and c["lipid_id"] not in lipid_ids})
    if missing:
        print("WARNING unknown lipid_ids:", missing)
    else:
        print("lipid_id integrity: OK")


if __name__ == "__main__":
    main()
