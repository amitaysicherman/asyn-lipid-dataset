#!/usr/bin/env python3
"""Analyse Yuval's first experiment (261022) from the 'Final' sheet (mean kinetic curves).

Computes per condition: endpoint (plateau), max, AUC, t1/2; then compares each lipid to its
solvent-matched POSITIVE control (alpha-syn + same solvent, no lipid):
  - 10%-solvent (50:1) ethanol lipids -> 'Control+ 10% ethanol'
  - GM1 (isopropanol) 50:1            -> 'Control+ 10% ISO+ddw'
  - buffer-only positive control       -> 'Control+ phosphate buffer'
Reports relative_endpoint = endpoint_lipid / endpoint_control  (<1 = REDUCES, >1 = promotes).

Writes experiments/exp1_curves.csv (tidy) and experiments/exp1_results.csv + prints a summary
and a predicted-vs-observed check. The 10:1 (2% solvent) conditions lack a protein+2%-solvent
control in this run, so they are flagged.
"""
import csv
import os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXP = os.path.join(ROOT, "experiments")
XLSX = os.environ.get("YUVAL_XLSX",
    "/root/.claude/uploads/4a60ad49-28f2-515d-9ffe-1a5f16bf82c1/593af1ad-261022_Lipid_with_AS_first_exp_results.xlsx")


def load_final():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Final"]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h).strip() if h is not None else "" for h in rows[0]]
    times, series = [], {h: [] for h in header[1:] if h}
    colmap = [(i, h) for i, h in enumerate(header) if i > 0 and h]
    for r in rows[1:]:
        if r[0] is None or not isinstance(r[0], (int, float)):
            continue
        times.append(float(r[0]))
        for i, h in colmap:
            v = r[i]
            series[h].append(float(v) if isinstance(v, (int, float)) else float("nan"))
    return times, series


def metrics(times, y):
    yy = [v for v in y if v == v]
    if len(yy) < 5:
        return {}
    base = sum(y[:3]) / 3.0
    plateau = sum(sorted(yy)[-5:]) / 5.0            # mean of top-5 (endpoint)
    ymax = max(yy)
    rise = plateau - base
    # AUC over baseline-subtracted
    auc = 0.0
    for i in range(1, len(times)):
        a, b = y[i-1] - base, y[i] - base
        if a == a and b == b:
            auc += 0.5 * (a + b) * (times[i] - times[i-1])
    # t1/2: first time crossing base + 0.5*rise
    thalf = None
    thr = base + 0.5 * rise
    if rise > 5:
        for i in range(1, len(times)):
            if y[i] >= thr:
                thalf = round(times[i], 1); break
    grew = rise > max(8, 0.2 * base)
    return dict(baseline=round(base, 1), endpoint=round(plateau, 1), max=round(ymax, 1),
                rise=round(rise, 1), auc=round(auc, 0), t_half_h=thalf, grew=int(grew))


MATCH = {  # lipid-condition suffix / solvent -> control column name
    "iso": "Control+ 10% ISO+ddw",
    "etoh": "Control+ 10% ethanol",
    "buffer": "Control+ phosphate buffer",
}


def control_for(cond):
    if cond.startswith("GM1"):
        return MATCH["iso"]
    return MATCH["etoh"]


def main():
    times, series = load_final()
    M = {h: metrics(times, y) for h, y in series.items()}

    # tidy curves
    os.makedirs(EXP, exist_ok=True)
    with open(os.path.join(EXP, "exp1_curves.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["time_h"] + list(series.keys()))
        for i, t in enumerate(times):
            w.writerow([t] + [series[h][i] if i < len(series[h]) else "" for h in series])

    lipids = [h for h in series if any(h.startswith(p) for p in
              ("GM1", "CHOL", "SM", "DMPC", "DPPC", "DSPC", "DOPC", "POPC", "REAAM"))
              and not h.startswith("C:")]
    out = []
    for cond in lipids:
        m = M.get(cond, {})
        ctrl = control_for(cond)
        cm = M.get(ctrl, {})
        rel_end = round(m.get("endpoint", 0) / cm["endpoint"], 2) if cm.get("endpoint") else ""
        rel_auc = round((m.get("auc") or 0) / cm["auc"], 2) if cm.get("auc") else ""
        out.append(dict(condition=cond, matched_control=ctrl, endpoint=m.get("endpoint"),
                        control_endpoint=cm.get("endpoint"), rel_endpoint=rel_end,
                        rel_auc=rel_auc, max=m.get("max"), t_half_h=m.get("t_half_h"),
                        grew=m.get("grew")))
    with open(os.path.join(EXP, "exp1_results.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(out[0].keys())); wr.writeheader(); wr.writerows(out)

    # ---- print summary ----
    def g(name): return M.get(name, {})
    print(f"Timepoints: {len(times)} over {times[-1]:.0f} h\n")
    print("CONTROLS (endpoint / max / grew):")
    for c in ["Control+ phosphate buffer", "Control- phosphate buffer",
              "Control+ 10% ethanol", "Control- 10% ethanol",
              "Control+ 10% ISO+ddw", "Control- 10% ISO+ddw", "Control- 2% ethanol"]:
        m = g(c)
        if m: print(f"  {c:28} end={m['endpoint']:>6}  max={m['max']:>6}  rise={m['rise']:>6}  grew={m['grew']}")
    print("\nLIPIDS vs matched +control  (rel_endpoint <1 = REDUCES, >1 = promotes):")
    print(f"  {'condition':22} {'end':>6} {'ctrl':>6} {'rel_end':>8} {'rel_auc':>8} {'t1/2':>6} grew")
    for r in sorted(out, key=lambda r: (r['rel_endpoint'] == "", r['rel_endpoint'] or 9)):
        print(f"  {r['condition']:22} {str(r['endpoint']):>6} {str(r['control_endpoint']):>6} "
              f"{str(r['rel_endpoint']):>8} {str(r['rel_auc']):>8} {str(r['t_half_h']):>6} {r['grew']}")
    print("\n-> experiments/exp1_curves.csv, exp1_results.csv")


if __name__ == "__main__":
    main()
