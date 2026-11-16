#!/usr/bin/env python3
"""Build two Google-Docs-ready .docx deliverables from the summaries + scored library.

  outputs/Lipid_rules_summary.docx        - the decision tree (as text) + rules->paper table
  outputs/Lipid_candidates_ranked.docx    - the 8-candidate verdicts + FULL 107-lipid ranked table

Drag either into Google Drive -> opens as a native Google Doc.
"""
import csv
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "outputs")


def h(doc, text, size=16, color=(20, 40, 80), space_before=10):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(*color)
    return p


def body(doc, text, size=11, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(size); r.italic = italic
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.add_run(text).font.size = Pt(11)


def table(doc, headers, rows, widths=None, header_fill="1F3A5F"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    for i, hd in enumerate(headers):
        c = t.rows[0].cells[i]
        c.paragraphs[0].add_run(hd).bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(9)
    return t


# ---------------- DOC 1: rules ----------------
def build_rules():
    d = Document()
    ti = d.add_paragraph(); r = ti.add_run("How the model scores a lipid"); r.bold = True
    r.font.size = Pt(20); r.font.color.rgb = RGBColor(20, 40, 80)
    body(d, "Goal: predict whether a lipid REDUCES alpha-synuclein fibrils, to prioritise "
            "experiments. A rule-based prior from ~10 papers, pinned to Yuval's assay "
            "(A53T, pH 7.4, high lipid:protein). A starting guess - the ThT data re-fits it.",
         italic=True)

    h(d, "The decision tree")
    tree = [
        "lipid",
        "  |- anionic headgroup (PS / PG / PA / ganglioside)",
        "  |     |- big sugar head (ganglioside)      -> REDUCER (strong)   e.g. GM1, GM3",
        "  |     |- single-chain (fatty acid / lyso)  -> PROMOTER (detergent/micelle)",
        "  |     \\- bilayer-former                    -> REDUCER           e.g. DOPS, POPG, cardiolipin",
        "  |- sterol (cholesterol)                    -> PROMOTER at high %",
        "  \\- zwitterionic (PC / PE / sphingomyelin)",
        "        |- fluid at 37C & short saturated    -> mild reduce        e.g. DMPC",
        "        \\- gel / long (DPPC, DSPC)            -> inert -> mild promote",
    ]
    for line in tree:
        p = d.add_paragraph(); run = p.add_run(line); run.font.name = "Consolas"; run.font.size = Pt(9.5)

    h(d, "In words")
    bullet(d, "Anionic lipids (PS, PG, PA, gangliosides) bind alpha-syn; at high ratio + neutral pH "
              "they sequester it and REDUCE fibrils. Gangliosides strongest.")
    bullet(d, "Zwitterionic PC/PE and sphingomyelin are weak binders -> mostly inert; fluid short "
              "DMPC mildly helps, gel DPPC/DSPC do not.")
    bullet(d, "Cholesterol PROMOTES at high % (raises membrane hydrophobicity).")
    bullet(d, "Free fatty acids / single-chain are detergent-like -> PROMOTE.")

    h(d, "4 things fixed by Yuval's setup (they flip the answer)")
    bullet(d, "pH 7.4 (neutral) -> pushes binders toward inhibition.")
    bullet(d, "High ratio (10:1, 50:1) -> sequestration regime -> favours reduction.")
    bullet(d, "Ethanol vehicle itself speeds aggregation -> compare each lipid to its SAME-% "
              "control; do not compare 10:1 vs 50:1.")
    bullet(d, "A53T binds membranes more than WT -> effects likely stronger.")

    h(d, "Where each rule comes from")
    table(d, ["Rule", "Source paper(s)", "Takeaway"], [
        ["Charge gate", "Galvagnion 2016; Gaspar 2018", "binds anionic, not pure PC"],
        ["Gangliosides strongest", "Grey 2015; Gaspar 2018; Martinez 2007", "big sugar head = biggest effect"],
        ["pH flips the sign", "Martinez 2007 vs Gaspar/Grey", "GM1 inhibits at pH 7.4, accelerates at 5.5"],
        ["High ratio -> reduce", "Galvagnion 2015", "excess lipid stops / dissolves fibrils"],
        ["Cholesterol promotes; DMPC suppresses, DPPC doesn't", "Matveyenka 2024; Dou 2023", "14:0->16:0 flips a PC"],
        ["Fatty acids promote", "JBC 2003", "anionic micelles accelerate"],
        ["Ethanol not inert", "Chem Sci 2021", "alcohol speeds aggregation at 100uM / pH 7"],
        ["A53T binds more", "Jo 2000", "effects amplified vs WT"],
    ])
    body(d, "Prior from ~10 papers (mostly WT + vesicles); Yuval uses A53T + free lipids, so treat "
            "as a hypothesis to test. Full version with quotes & DOIs in the repo "
            "(DOC1_lipid_decision_tree.md).", italic=True, size=9)
    d.save(os.path.join(OUT, "Lipid_rules_summary.docx"))


# ---------------- DOC 2: candidates ----------------
def build_candidates():
    d = Document()
    ti = d.add_paragraph(); r = ti.add_run("Lipid candidates, ranked"); r.bold = True
    r.font.size = Pt(20); r.font.color.rgb = RGBColor(20, 40, 80)
    body(d, "Model prediction (literature prior) for Yuval's assay. DOWN = reduce fibrils (good), "
            "~ = no effect, UP = may increase. First guess - your data decides.", italic=True)

    h(d, "Your 8 candidates - what the model expects")
    table(d, ["Lipid", "Prediction", "Why"], [
        ["GM1", "DOWN DOWN (reduce)", "anionic + big sugar head; inhibits at neutral pH"],
        ["DMPC", "~ / mild DOWN", "fluid short PC, binds a little"],
        ["Sphingomyelin", "~ no effect", "zwitterionic, weak binder"],
        ["DOPC", "~ no effect", "zwitterionic matrix lipid"],
        ["POPC", "~ no effect", "zwitterionic"],
        ["DPPC", "UP mild promote", "gel, doesn't bind/sequester"],
        ["DSPC", "UP mild promote", "gel, long saturated"],
        ["Cholesterol", "UP promote", "raises membrane hydrophobicity at high %"],
    ])
    body(d, "Bottom line: of the 8, only GM1 is a strong reducer bet; the rest are mostly inert and "
            "a few may speed things up.")

    h(d, "Best bets to add (anionic - predicted reducers)")
    bullet(d, "Gangliosides: GM1, GM3 (GD1a, GT1b later)")
    bullet(d, "Phosphatidylserine: DOPS, DMPS")
    bullet(d, "Phosphatidylglycerol: POPG")
    bullet(d, "Cardiolipin")
    body(d, "GM3, DOPS, POPG and cardiolipin were added to the proposed plate to test this directly.")

    h(d, "Full ranked library (107 lipids)")
    rows = list(csv.DictReader(open(os.path.join(OUT, "lipid_library_scored.csv"))))
    trows = []
    for r in rows:
        trows.append([r["rank"], r["lipid"], r["score"], r["predicted"], r["lipid_class"],
                      r["net_charge"], r["acyl"] or "-", "yes" if r["fluid_37C"] == "1" else "no",
                      r["rationale"]])
    table(d, ["#", "Lipid", "Score", "Predicted", "Class", "Charge", "Chains", "Fluid@37", "Why"], trows)
    body(d, "Score >= 2 likely reducer; 0-1 inert/mild; < 0 likely promoter. Prior only - re-fit on "
            "Yuval's ThT data. Source: src/lipid_library.py.", italic=True, size=9)
    d.save(os.path.join(OUT, "Lipid_candidates_ranked.docx"))


if __name__ == "__main__":
    build_rules()
    build_candidates()
    print("wrote outputs/Lipid_rules_summary.docx and outputs/Lipid_candidates_ranked.docx")
