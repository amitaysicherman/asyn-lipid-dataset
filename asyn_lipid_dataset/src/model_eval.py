#!/usr/bin/env python3
"""Honest baseline modelling + leakage-aware evaluation on the pilot dataset.

Targets the 3-class effect label {accelerate, neutral, reduce}. Because the dataset is
small (n=35), heterogeneous, and the 'reduce' class is almost entirely one paper
(Martinez 2007), the point of this script is to measure generalisation HONESTLY under
the splits that match the scientific claims, not to produce an impressive number.

Models:
  - Dummy (most-frequent)                  -> trivial baseline
  - Rule (domain heuristic)                -> interpretable, encodes the known confound
  - Nearest-neighbour (chem+conditions)    -> k=1, Gower-style via one-hot+scaled numerics
  - Multinomial logistic regression (L2)   -> regularised linear

Evaluations:
  - Stratified 5-fold (optimistic; related rows can share a paper)       [reference only]
  - Leave-One-Paper-Out (transfer between studies)                       [the honest test]
  - Leave-One-Driver-Lipid-Out (transfer to new chemistry)              [the honest test]

Preprocessing (impute + scale + one-hot) is fit on TRAIN folds only.
Writes outputs/model_report.md.
"""
import os
import warnings
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold, LeaveOneGroupOut
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

warnings.filterwarnings("ignore")
from features import build  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

NUM = ["driver_charge", "driver_mean_chain_C", "driver_total_db", "driver_is_ganglioside",
       "driver_is_natural_mix", "n_components", "pH", "temp_C"]
CAT = ["driver_class", "formulation", "agitation", "assay_paradigm"]
CLASSES = ["accelerate", "neutral", "reduce"]


def make_pre():
    return ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), NUM),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT),
    ])


def models():
    return {
        "Dummy(most_frequent)": DummyClassifier(strategy="most_frequent"),
        "NN(k=1 chem+cond)": Pipeline([("pre", make_pre()),
                                       ("clf", KNeighborsClassifier(n_neighbors=1))]),
        "Logistic(L2)": Pipeline([("pre", make_pre()),
                                  ("clf", LogisticRegression(max_iter=2000, C=1.0,
                                                             class_weight="balanced"))]),
    }


def rule_predict(df):
    """Transparent domain heuristic. Encodes: anionic/ganglioside + acidic pH -> accelerate;
    ganglioside at neutral/unknown pH -> reduce (GM1 neutral-pH inhibition); zwitterionic -> neutral."""
    out = []
    for _, r in df.iterrows():
        charge = r.driver_charge
        pH = r.pH
        is_gang = r.driver_is_ganglioside == 1
        if is_gang and (np.isnan(pH) or pH >= 7.0):
            out.append("reduce")
        elif (not np.isnan(charge)) and charge < 0 and (np.isnan(pH) or pH < 7.0):
            out.append("accelerate")
        elif (not np.isnan(charge)) and charge == 0:
            out.append("neutral")
        else:
            out.append("accelerate")
    return np.array(out)


def scores(y_true, y_pred):
    return (accuracy_score(y_true, y_pred),
            f1_score(y_true, y_pred, average="macro", labels=CLASSES, zero_division=0))


def cv_eval(df, X, y, splitter, groups=None):
    res = {}
    # model-based
    for name, mdl in models().items():
        preds = np.empty(len(y), dtype=object)
        for tr, te in splitter.split(X, y, groups):
            mdl.fit(X.iloc[tr], y.iloc[tr])
            preds[te] = mdl.predict(X.iloc[te])
        res[name] = scores(y, preds)
    # rule baseline (no fitting; evaluated on same rows)
    res["Rule(heuristic)"] = scores(y, rule_predict(df))
    return res


def main():
    df = build()
    X = df[NUM + CAT].copy()
    y = df["effect_class"].copy()
    paper = df["paper_id"]
    lip = df["driver_lipid"]

    L = ["# Baseline model evaluation (pilot)", "",
         f"- Modelling rows (conditions with a direct-aggregation effect label): **{len(df)}**",
         f"- Class balance: " + ", ".join(f"{k}={v}" for k, v in y.value_counts().items()),
         f"- Driver-lipid classes present: " + ", ".join(f"{k}={v}" for k, v in df.driver_class.value_counts().items()),
         "",
         "Each cell is **accuracy / macro-F1**. Macro-F1 weights the three classes equally, so it "
         "punishes a model that ignores the rare `reduce` class. Majority-class accuracy is "
         f"**{y.value_counts().max()/len(y):.3f}**.", ""]

    # --- Stratified 5-fold (optimistic reference) ---
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    r_sk = cv_eval(df, X, y, skf)
    # --- Leave-One-Paper-Out ---
    logo = LeaveOneGroupOut()
    r_lopo = cv_eval(df, X, y, logo, groups=paper)
    # --- Leave-One-Driver-Lipid-Out ---
    r_lolo = cv_eval(df, X, y, logo, groups=lip)

    names = ["Dummy(most_frequent)", "Rule(heuristic)", "NN(k=1 chem+cond)", "Logistic(L2)"]
    L.append("| model | Stratified-5fold (optimistic) | Leave-One-Paper-Out | Leave-One-Lipid-Out |")
    L.append("|---|---|---|---|")
    for n in names:
        def cell(r):
            a, f = r[n]
            return f"{a:.3f} / {f:.3f}"
        L.append(f"| {n} | {cell(r_sk)} | {cell(r_lopo)} | {cell(r_lolo)} |")
    L.append("")

    # Confusion under LOPO for the logistic model
    preds = np.empty(len(y), dtype=object)
    mdl = models()["Logistic(L2)"]
    for tr, te in logo.split(X, y, paper):
        mdl.fit(X.iloc[tr], y.iloc[tr]); preds[te] = mdl.predict(X.iloc[te])
    cm = confusion_matrix(y, preds, labels=CLASSES)
    L.append("## Leave-One-Paper-Out confusion (Logistic L2)")
    L.append("")
    L.append("rows = true, cols = predicted")
    L.append("")
    L.append("| true \\ pred | " + " | ".join(CLASSES) + " |")
    L.append("|" + "---|" * (len(CLASSES) + 1))
    for i, c in enumerate(CLASSES):
        L.append(f"| {c} | " + " | ".join(str(cm[i, j]) for j in range(len(CLASSES))) + " |")
    L.append("")

    # Per-paper LOPO accuracy (where does transfer fail?)
    L.append("## Per-held-out-paper accuracy (Logistic L2, LOPO)")
    L.append("")
    L.append("| held-out paper | n | accuracy | note |")
    L.append("|---|---|---|---|")
    for pid in paper.unique():
        te = paper == pid
        tr = ~te
        mdl = models()["Logistic(L2)"]
        mdl.fit(X[tr], y[tr])
        acc = accuracy_score(y[te], mdl.predict(X[te]))
        cls = ",".join(sorted(y[te].unique()))
        note = ""
        if "reduce" in y[te].unique() and "reduce" not in y[tr].unique():
            note = "reduce class absent from training -> unlearnable"
        L.append(f"| {pid} | {te.sum()} | {acc:.3f} | classes: {cls}. {note} |")
    L.append("")

    L.append("## Interpretation")
    L.append("")
    L.append(
        "- The **Rule heuristic** and models beat the majority baseline on the *optimistic* "
        "stratified split, confirming a real, learnable signal: **charged/ganglioside lipids "
        "trigger aggregation; zwitterionic PC/cholesterol do not**.\n"
        "- Under **Leave-One-Paper-Out** and **Leave-One-Lipid-Out**, performance drops toward "
        "baseline and the `reduce` (inhibition) class collapses: nearly all inhibition evidence "
        "is Martinez 2007, so when it is held out the model cannot predict inhibition at all. "
        "The direction of GM1 is set by **pH**, which is confounded with paper.\n"
        "- **Conclusion:** the pilot supports a coarse, interpretable *triggering* classifier under "
        "published conditions, but does **not** support quantitative or inhibition prediction, and "
        "must not be presented as a validated predictor of the 8 candidates or of Yuval's assay. "
        "This is a methodology demonstration and an honest sparsity diagnosis, not a deployable model.")
    open(os.path.join(OUT, "model_report.md"), "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
