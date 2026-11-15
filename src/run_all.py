#!/usr/bin/env python3
"""Reproduce the whole dataset + analysis pipeline from the curated records.

Steps 2-6 are fully deterministic and offline (they only read files already in data/).
Step 1 (fetch) needs network + the allowlisted hosts and is OPTIONAL once raw files exist.

Usage:
  python3 src/run_all.py            # build dataset + audit + verify + model (offline)
  python3 src/run_all.py --fetch    # also re-download sources first (needs network)
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def run(mod):
    print(f"\n=== {mod} ===")
    subprocess.run([sys.executable, os.path.join(HERE, mod)], check=True)


def main():
    if "--fetch" in sys.argv:
        run("fetch_sources.py")
        run("parse_articles.py")
    run("lipids_reference.py")   # data/lipids.csv
    run("build_dataset.py")      # papers/conditions/components/measurements/curves CSVs
    run("verify_provenance.py")  # outputs/provenance_check.md (exits !=0 on failure)
    run("audit.py")              # outputs/audit_report.md + candidate_evidence_table
    run("features.py")           # data/model_table.csv
    run("model_eval.py")         # outputs/model_report.md
    run("chemistry_ranking.py")  # outputs/chemistry_ranking.md (rule-based, not ML)
    print("\nAll steps completed. See outputs/ and docs/.")


if __name__ == "__main__":
    main()
