#!/usr/bin/env python3
"""Curated lipid structure reference for the alpha-synuclein/lipid dataset.

Each lipid has: abbrev, full_name, class, headgroup, net_charge_phys (approx net
charge of the molecule at neutral pH ~7), acyl chains (as (n_carbons, n_double_bonds)
tuples), a SMILES string where a single well-defined molecular species exists, and
flags for natural mixtures.

Design rules honoured here:
  * Diacyl glycerophospholipid SMILES are BUILT from backbone + headgroup + acyl
    chains so they are internally consistent, then validated/canonicalised by RDKit.
  * Gangliosides (GM1/GM2/GM3/asialo-GM1) and other NATURAL-SOURCE mixtures are NOT
    given an arbitrary SMILES: `natural_mixture=True` and smiles="" with a note.
    (Task rule: do not assign one arbitrary molecular structure to a natural mixture.)
  * Descriptor columns (headgroup class, charge, chain length, unsaturation) are the
    primary machine-readable features; SMILES is the optional structure identifier.

Run `python3 src/lipids_reference.py` to validate SMILES and write data/lipids.csv.
"""
import csv
import os
from rdkit import Chem

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")


def acyl(n_c, n_db):
    """SMILES fragment for an sn ester acyl chain of n_c carbons (incl. carbonyl).

    Saturated only is built explicitly. For mono-unsaturated we place a single cis
    double bond near the middle (position is approximate; used only so the SMILES is
    chemically a mono-unsaturated chain of the right length/ unsaturation count).
    """
    # carbons after the carbonyl carbon:
    tail = n_c - 1
    if n_db == 0:
        return "C(=O)" + "C" * tail
    if n_db == 1:
        # put one C=C roughly mid-chain (e.g. oleoyl 18:1 delta-9)
        left = tail // 2
        right = tail - left - 2  # two carbons consumed by /C=C\
        left = max(left, 1)
        right = max(right, 1)
        return "C(=O)" + "C" * left + "/C=C\\" + "C" * right
    if n_db == 2:
        a = max(tail // 3, 1)
        b = max(tail // 3, 1)
        c = max(tail - a - b - 4, 1)
        return "C(=O)" + "C" * a + "/C=C\\" + "C" * b + "/C=C\\" + "C" * c
    raise ValueError(n_db)


HEADGROUPS = {
    # name: (smiles fragment attached at phosphate O, net charge of whole lipid ~pH7)
    "PC": ("OP(=O)([O-])OCC[N+](C)(C)C", 0),
    "PS": ("OP(=O)([O-])OC[C@@H](N)C(=O)O", -1),
    "PE": ("OP(=O)([O-])OCCN", 0),
    "PG": ("OP(=O)([O-])OCC(O)CO", -1),
    "PA": ("OP(=O)([O-])O", -1),
}


def build_diacyl(headgroup, sn1, sn2):
    head_smiles, charge = HEADGROUPS[headgroup]
    sn1_s = acyl(*sn1)
    sn2_s = acyl(*sn2)
    # sn-glycerol: C1(sn1 ester)-C2(sn2 ester)-C3(phosphate-head)
    smi = f"{sn1_s}OC[C@H](O{sn2_s})CO{head_smiles}"
    return smi, charge


# -------- lipid catalogue --------
# fields: abbrev, name, lclass, headgroup, chains(list of (C,db)), smiles(or None=build),
#         natural_mixture, is_candidate, note
LIPIDS = [
    # ---- the 8 wet-lab candidates ----
    ("DMPC", "1,2-dimyristoyl-sn-glycero-3-phosphocholine", "PC", "PC",
     [(14, 0), (14, 0)], None, False, True, ""),
    ("DPPC", "1,2-dipalmitoyl-sn-glycero-3-phosphocholine", "PC", "PC",
     [(16, 0), (16, 0)], None, False, True, ""),
    ("DSPC", "1,2-distearoyl-sn-glycero-3-phosphocholine", "PC", "PC",
     [(18, 0), (18, 0)], None, False, True, ""),
    ("DOPC", "1,2-dioleoyl-sn-glycero-3-phosphocholine", "PC", "PC",
     [(18, 1), (18, 1)], None, False, True, ""),
    ("POPC", "1-palmitoyl-2-oleoyl-sn-glycero-3-phosphocholine", "PC", "PC",
     [(16, 0), (18, 1)], None, False, True, ""),
    ("Cholesterol", "cholesterol", "sterol", "OH", [],
     "C[C@H](CCCC(C)C)[C@H]1CC[C@H]2[C@@H]3CC=C4C[C@H](O)CC[C@]4(C)[C@H]3CC[C@]12C",
     False, True, "sterol; modulator, not a bilayer-forming phospholipid"),
    ("SM", "sphingomyelin (N-acyl, phosphocholine headgroup)", "sphingolipid", "PC",
     [(18, 0)], None, True, True,
     "brain/egg SM is a natural mixture of N-acyl chain lengths; headgroup=phosphocholine; SMILES omitted"),
    ("GM1", "monosialotetrahexosylganglioside GM1", "ganglioside", "ganglioside-GM1",
     [(18, 0)], None, True, True,
     "anionic glycosphingolipid; defined oligosaccharide+1 sialic acid; natural ceramide acyl heterogeneity; SMILES omitted"),
    # ---- lipids appearing in the pilot studies (not candidates) ----
    ("DMPS", "1,2-dimyristoyl-sn-glycero-3-phospho-L-serine", "PS", "PS",
     [(14, 0), (14, 0)], None, False, False, ""),
    ("DLPS", "1,2-dilauroyl-sn-glycero-3-phospho-L-serine", "PS", "PS",
     [(12, 0), (12, 0)], None, False, False, ""),
    ("DPPS", "1,2-dipalmitoyl-sn-glycero-3-phospho-L-serine", "PS", "PS",
     [(16, 0), (16, 0)], None, False, False, ""),
    ("DOPS", "1,2-dioleoyl-sn-glycero-3-phospho-L-serine", "PS", "PS",
     [(18, 1), (18, 1)], None, False, False, ""),
    ("POPS", "1-palmitoyl-2-oleoyl-sn-glycero-3-phospho-L-serine", "PS", "PS",
     [(16, 0), (18, 1)], None, False, False, ""),
    ("DOPE", "1,2-dioleoyl-sn-glycero-3-phosphoethanolamine", "PE", "PE",
     [(18, 1), (18, 1)], None, False, False, ""),
    ("CL", "cardiolipin (1',3'-bis(1,2-dioleoyl-sn-glycero-3-phospho)-sn-glycerol)",
     "cardiolipin", "diphosphatidylglycerol", [(18, 1), (18, 1), (18, 1), (18, 1)],
     None, False, False, "net charge -2; four acyl chains; SMILES omitted (built separately if needed)"),
    ("Sphingosine", "D-erythro-sphingosine", "sphingolipid", "amino-OH", [(18, 1)],
     "CCCCCCCCCCCCC/C=C/[C@@H](O)[C@@H](N)CO", False, False,
     "cationic (+1) at neutral pH; NOT sphingomyelin"),
    ("GM3", "monosialodihexosylganglioside GM3", "ganglioside", "ganglioside-GM3",
     [(18, 0)], None, True, False,
     "anionic glycosphingolipid; natural source; SMILES omitted"),
    ("GM2", "ganglioside GM2", "ganglioside", "ganglioside-GM2", [(18, 0)], None, True,
     False, "anionic glycosphingolipid; natural source; SMILES omitted"),
    ("AsialoGM1", "asialo-GM1 (GM1 lacking sialic acid)", "glycosphingolipid",
     "neutral-glycan", [(18, 0)], None, True, False,
     "uncharged large headgroup; natural source; SMILES omitted"),
    ("PE-PEG750", "1,2-distearoyl-sn-glycero-3-phosphoethanolamine-N-[methoxy(PEG)-750]",
     "PEG-lipid", "PE-PEG", [(18, 0), (18, 0)], None, False, False,
     "anionic PEGylated PE; polymer headgroup; SMILES omitted"),
    ("Cer-PEG750", "N-palmitoyl-sphingosine-1-succinyl[methoxy(PEG)750]", "PEG-lipid",
     "Cer-PEG", [(16, 0)], None, False, False,
     "uncharged PEGylated ceramide; SMILES omitted"),
    ("BrainGangliosides", "total brain gangliosides (mixture)", "ganglioside",
     "ganglioside-mixture", [], None, True, False,
     "undefined natural mixture of ganglioside species; SMILES omitted"),
]

HEADGROUP_CHARGE = {"PC": 0, "PE": 0, "PS": -1, "PG": -1, "PA": -1,
                    "ganglioside-GM1": -1, "ganglioside-GM3": -1, "ganglioside-GM2": -1,
                    "ganglioside-mixture": -1, "neutral-glycan": 0, "PE-PEG": -1,
                    "Cer-PEG": 0, "amino-OH": 1, "OH": 0, "diphosphatidylglycerol": -2}


def chain_summary(chains):
    if not chains:
        return "", "", ""
    carbons = [c for c, _ in chains]
    dbs = [d for _, d in chains]
    desc = "/".join(f"{c}:{d}" for c, d in chains)
    return desc, sum(carbons) / len(carbons), sum(dbs)


def main():
    rows = []
    problems = []
    for (abbrev, name, lclass, headgroup, chains, smiles, natmix, cand, note) in LIPIDS:
        built_from = ""
        if smiles is None and headgroup in HEADGROUPS and len(chains) == 2:
            smiles, _ = build_diacyl(headgroup, chains[0], chains[1])
            built_from = "built_diacyl"
        canon = ""
        valid = ""
        if smiles:
            m = Chem.MolFromSmiles(smiles)
            if m is None:
                valid = "INVALID"
                problems.append((abbrev, smiles))
            else:
                canon = Chem.MolToSmiles(m)
                valid = "ok"
        chain_desc, mean_c, tot_db = chain_summary(chains)
        rows.append(dict(
            lipid_id=abbrev, abbrev=abbrev, name=name, lipid_class=lclass,
            headgroup=headgroup,
            net_charge_phys=HEADGROUP_CHARGE.get(headgroup, ""),
            acyl_chains=chain_desc,
            mean_chain_carbons=round(mean_c, 1) if mean_c != "" else "",
            total_double_bonds=tot_db,
            n_chains=len(chains),
            smiles=canon, smiles_input=smiles or "", smiles_valid=valid,
            smiles_source=built_from or ("curated" if smiles else "omitted"),
            natural_mixture=int(bool(natmix)),
            is_candidate=int(bool(cand)),
            note=note,
        ))
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "lipids.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} lipids -> data/lipids.csv")
    print("SMILES valid:", sum(1 for r in rows if r["smiles_valid"] == "ok"),
          "| omitted:", sum(1 for r in rows if r["smiles_source"] == "omitted"))
    if problems:
        print("INVALID SMILES:", problems)


if __name__ == "__main__":
    main()
