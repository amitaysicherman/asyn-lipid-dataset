#!/usr/bin/env python3
"""Build the per-condition modelling table from the CSV dataset.

One row per experimental condition that carries a direct-aggregation effect label.
Features are split into:
  - driver-lipid chemistry (the studied/active lipid, not the inert matrix)
  - formulation / mixture composition
  - assay conditions
Target:
  - effect_class in {accelerate, neutral, reduce}
  - effect_score ordinal (+2 strong accel ... -1.5 fibril dissolution)

No outcome information leaks into features. Missing numeric values are left as NaN
(imputation, if any, is done inside CV folds by the modelling script).

Writes data/model_table.csv and returns a DataFrame via build().
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

DRIVER_ROLES = {"anionic", "cationic", "sterol_additive", "neutral_large_head",
                "natural_extract", "exosome"}
ANIONIC_ROLES = {"anionic", "natural_extract", "exosome"}

EFFECT_SCORE = {
    "strong_acceleration": 2.0, "acceleration": 1.0, "weak_acceleration": 0.5,
    "no_detectable_effect": 0.0, "retardation": -0.5, "inhibition": -1.0,
    "fibril_dissolution": -1.5,
}
EFFECT_CLASS = {
    "strong_acceleration": "accelerate", "acceleration": "accelerate",
    "weak_acceleration": "accelerate", "no_detectable_effect": "neutral",
    "retardation": "neutral", "inhibition": "reduce", "fibril_dissolution": "reduce",
}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def build():
    conds = pd.read_csv(os.path.join(DATA, "conditions.csv"))
    comps = pd.read_csv(os.path.join(DATA, "components.csv"))
    meas = pd.read_csv(os.path.join(DATA, "measurements.csv"))
    lipids = pd.read_csv(os.path.join(DATA, "lipids.csv")).set_index("lipid_id")

    # one effect label per condition: take the first direct_aggregation effect_direction
    # that is an actual effect (not 'not_applicable')
    eff = meas[(meas.evidence_category == "direct_aggregation") &
               (~meas.effect_direction.isin(["", "not_applicable"])) &
               (meas.endpoint == "effect_direction")].copy()
    # pick one row per condition (priority: strongest-magnitude label)
    eff["score"] = eff.effect_direction.map(EFFECT_SCORE)
    eff["absscore"] = eff.score.abs()
    eff = eff.sort_values("absscore", ascending=False).drop_duplicates("condition_id")

    rows = []
    for _, cond in conds.iterrows():
        cid = cond.condition_id
        e = eff[eff.condition_id == cid]
        if e.empty:
            continue
        direction = e.iloc[0].effect_direction
        ccomps = comps[comps.condition_id == cid]
        if ccomps.empty:
            continue  # controls / no lipid
        # pick driver lipid: a component with a driver role, else sole component, else 'main'
        driver = None
        drv = ccomps[ccomps.role.isin(DRIVER_ROLES)]
        if len(drv):
            driver = drv.iloc[0]
        elif len(ccomps) == 1:
            driver = ccomps.iloc[0]
        else:
            m = ccomps[ccomps.role == "main"]
            driver = m.iloc[0] if len(m) else ccomps.iloc[0]
        dl = driver.lipid_id
        if not isinstance(dl, str) or not dl.strip():
            # natural mixture with no catalogued lipid id (e.g. exosome, lipid extract)
            dl = f"natural_{driver.role}"
        li = lipids.loc[dl] if dl in lipids.index else None

        # anionic fraction (numeric mol_fractions only)
        fr = ccomps.copy()
        fr["mf"] = fr.mol_fraction.map(_num)
        anion_frac = fr.loc[fr.role.isin(ANIONIC_ROLES), "mf"].sum(min_count=1)

        def lp(attr, default=np.nan):
            if li is None:
                return default
            v = li.get(attr, default)
            return _num(v) if attr in ("net_charge_phys", "mean_chain_carbons",
                                       "total_double_bonds", "n_chains") else v

        rows.append(dict(
            condition_id=cid, paper_id=cond.paper_id, label=cond.label,
            driver_lipid=dl,
            driver_class=(li.lipid_class if li is not None else "unknown"),
            driver_charge=lp("net_charge_phys"),
            driver_mean_chain_C=lp("mean_chain_carbons"),
            driver_total_db=lp("total_double_bonds"),
            driver_is_ganglioside=int((li is not None) and li.lipid_class == "ganglioside"),
            driver_is_natural_mix=int((li is not None) and str(li.natural_mixture) == "1"),
            anionic_mol_fraction=anion_frac,
            n_components=len(ccomps),
            formulation=cond.formulation,
            pH=_num(cond.pH),
            temp_C=_num(cond.temp_C),
            agitation=("shaking" if str(cond.agitation).strip() and "rpm" in str(cond.agitation)
                       else ("quiescent" if str(cond.agitation).strip() == "quiescent" else "unknown")),
            protein_conc_uM=_num(cond.protein_conc_uM),
            lipid_to_protein_ratio=_num(cond.lipid_to_protein_molar_ratio),
            assay_paradigm=cond.assay_paradigm,
            effect_direction=direction,
            effect_score=EFFECT_SCORE[direction],
            effect_class=EFFECT_CLASS[direction],
        ))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA, "model_table.csv"), index=False)
    return df


if __name__ == "__main__":
    df = build()
    pd.set_option("display.width", 200, "display.max_columns", 40)
    print(f"model rows: {len(df)}")
    print("\neffect_class distribution:\n", df.effect_class.value_counts())
    print("\nby paper:\n", df.groupby("paper_id").effect_class.value_counts())
    print("\ndriver_class distribution:\n", df.driver_class.value_counts())
    print("\nmissingness:\n", df[["pH","temp_C","driver_charge","driver_mean_chain_C",
          "anionic_mol_fraction","lipid_to_protein_ratio"]].isna().sum())
