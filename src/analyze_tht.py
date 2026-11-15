#!/usr/bin/env python3
"""Turn Yuval's raw ThT kinetic export into model-ready endpoints + a reduction ranking.

Inputs (in experiments/):
  plate_layout.csv   - from design_experiment.py (well -> condition)
  raw_kinetics.csv   - the plate-reader export: a 'time_min' (or 'time_h') column plus one
                       column per well header (A1, A2, ... H12). Wide format.
                       (If Yuval's export differs, this is the one place to adapt the reader.)

For each well it computes: lag time, t1/2, endpoint RFU, AUC (all on buffer-subtracted signal).
Replicates are averaged per condition. For each LIPID condition it reports, versus its
**solvent-matched control**:
  relative_reduction_AUC = 1 - AUC_lipid / AUC_solventctrl   (fibril-load proxy; + = less fibril)
  delta_t_half_h         = t_half_lipid - t_half_solventctrl (+ = delayed = inhibitory)
Censored ('no growth within 72 h') is handled explicitly, not as infinite.

Outputs: experiments/results.csv  and  experiments/ranking.md
Run: python3 src/analyze_tht.py
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXP = os.path.join(ROOT, "experiments")


def load_layout():
    well2cond, cond_info = {}, {}
    for r in csv.DictReader(open(os.path.join(EXP, "plate_layout.csv"))):
        well2cond[r["well"]] = r["cond_id"]
        cond_info.setdefault(r["cond_id"], r)
    return well2cond, cond_info


def load_kinetics():
    path = os.path.join(EXP, "raw_kinetics.csv")
    if not os.path.exists(path):
        return None, None
    rows = list(csv.DictReader(open(path)))
    cols = rows[0].keys()
    tkey = "time_h" if "time_h" in cols else ("time_min" if "time_min" in cols else None)
    if not tkey:
        raise SystemExit("raw_kinetics.csv needs a 'time_h' or 'time_min' column")
    scale = 1.0 if tkey == "time_h" else 1 / 60.0
    times = [float(r[tkey]) * scale for r in rows]
    wells = [c for c in cols if c != tkey]
    series = {w: [float(r[w]) if r[w] not in ("", "NA") else float("nan") for r in rows]
              for w in wells}
    return times, series


def endpoints(times, y, baseline):
    y = [v - baseline for v in y]
    ymax = max(y)
    plateau = sum(sorted(y)[-3:]) / 3.0  # mean of top-3 reads
    thr10 = 0.10 * plateau
    thr50 = 0.50 * plateau
    # growth detection: require a real rise over noise
    grew = plateau > max(5 * abs(baseline), 0.05 * (max(y) + 1e-9)) and ymax > 3 * (abs(min(y)) + 1e-9)
    def crossing(thr):
        for i in range(1, len(y)):
            if y[i] >= thr:
                # linear interp
                if y[i] == y[i-1]:
                    return times[i]
                f = (thr - y[i-1]) / (y[i] - y[i-1])
                return times[i-1] + f * (times[i] - times[i-1])
        return None
    lag = crossing(thr10) if grew else None
    thalf = crossing(thr50) if grew else None
    auc = 0.0
    for i in range(1, len(times)):
        auc += 0.5 * (y[i] + y[i-1]) * (times[i] - times[i-1])
    return dict(lag_h=lag, t_half_h=thalf, endpoint_RFU=round(plateau, 1),
                auc=round(auc, 1), grew=grew)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def main():
    well2cond, cond_info = load_layout()
    times, series = load_kinetics()
    if series is None:
        print("No experiments/raw_kinetics.csv yet. Fill plate_layout.csv wells, run the assay, "
              "export the kinetics as raw_kinetics.csv (time_min/time_h + one column per well), "
              "then rerun. results_template.csv shows the endpoints that will be computed.")
        return
    # buffer baseline
    buf_wells = [w for w, c in well2cond.items() if c == "CTRL_buffer" and w in series]
    baseline = 0.0
    if buf_wells:
        import statistics
        baseline = statistics.mean(series[w][0] for w in buf_wells)  # use t0 of buffer wells

    # per-well endpoints -> per-condition averages
    per_cond = {}
    for w, vals in series.items():
        cond = well2cond.get(w)
        if not cond:
            continue
        e = endpoints(times, vals, baseline)
        per_cond.setdefault(cond, []).append(e)
    agg = {}
    for cond, es in per_cond.items():
        agg[cond] = dict(
            lag_h=mean([e["lag_h"] for e in es]),
            t_half_h=mean([e["t_half_h"] for e in es]),
            endpoint_RFU=mean([e["endpoint_RFU"] for e in es]),
            auc=mean([e["auc"] for e in es]),
            n=len(es), n_grew=sum(e["grew"] for e in es))

    # results.csv with reduction vs matched control
    out, ranking = [], []
    for cond, info in cond_info.items():
        a = agg.get(cond, {})
        row = dict(cond_id=cond, lipid=info["lipid"], ratio=info["ratio"],
                   solvent=info["solvent"], solvent_pct=info["solvent_pct"],
                   role=info["role"], n=a.get("n", 0), n_grew=a.get("n_grew", 0),
                   lag_h=a.get("lag_h"), t_half_h=a.get("t_half_h"),
                   endpoint_RFU=a.get("endpoint_RFU"), auc=a.get("auc"))
        if info["role"] == "lipid":
            pct = info["solvent_pct"]
            ctrl = (f"CTRL_iPrOH_{float(pct):g}pct" if info["lipid"] == "GM1"
                    else f"CTRL_EtOH_{float(pct):g}pct")
            ca = agg.get(ctrl, {})
            row["matched_control"] = ctrl
            if a.get("auc") and ca.get("auc"):
                row["relative_reduction_AUC"] = round(1 - a["auc"] / ca["auc"], 3)
            if a.get("t_half_h") is not None and ca.get("t_half_h") is not None:
                row["delta_t_half_h"] = round(a["t_half_h"] - ca["t_half_h"], 2)
            if a.get("n_grew", 0) == 0 and ca.get("n_grew", 1) > 0:
                row["flag"] = "no_growth_with_lipid (strong inhibition or interference)"
            ranking.append(row)
        out.append(row)

    fields = ["cond_id", "role", "lipid", "ratio", "solvent", "solvent_pct", "n", "n_grew",
              "lag_h", "t_half_h", "endpoint_RFU", "auc", "matched_control",
              "relative_reduction_AUC", "delta_t_half_h", "flag"]
    with open(os.path.join(EXP, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(out)

    ranking.sort(key=lambda r: (r.get("relative_reduction_AUC") is None,
                                -(r.get("relative_reduction_AUC") or -9)))
    L = ["# Candidate ranking by fibril reduction (Yuval's assay)", "",
         "`relative_reduction_AUC` > 0 means less ThT signal than the solvent-matched control "
         "(more inhibition). `delta_t_half_h` > 0 means delayed aggregation.", "",
         "| lipid | ratio | rel_reduction_AUC | Δt½ (h) | flag |", "|---|---|---|---|---|"]
    for r in ranking:
        L.append(f"| {r['lipid']} | {r['ratio']}:1 | {r.get('relative_reduction_AUC','—')} | "
                 f"{r.get('delta_t_half_h','—')} | {r.get('flag','')} |")
    open(os.path.join(EXP, "ranking.md"), "w").write("\n".join(L))
    print(f"wrote experiments/results.csv and ranking.md ({len(ranking)} lipid conditions)")


if __name__ == "__main__":
    main()
