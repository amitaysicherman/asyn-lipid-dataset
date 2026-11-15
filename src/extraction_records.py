#!/usr/bin/env python3
"""Hand-curated experimental records extracted from the primary studies.

This module is the SINGLE SOURCE OF TRUTH for the dataset. Every condition and
measurement carries its provenance (figure/table/page + a short verbatim quote) and
an evidence classification. `build_dataset.py` flattens these into the CSV tables.

CONTROLLED VOCABULARIES
-----------------------
evidence_category:
  direct_aggregation  - ThT kinetics / lag / half-time / endpoint / fibril quantity
  binding_structural  - KD, stoichiometry, CD helicity, DSC, NMR
  cellular            - toxicity / cellular aggregation (none in this pilot)
  observational       - lipidomic abundance (none here; reviews excluded)

effect_direction (direct_aggregation only); defined relative to the matched
no-lipid control IN THE SAME ASSAY:
  strong_acceleration | acceleration | weak_acceleration |
  no_detectable_effect | retardation | inhibition | fibril_dissolution |
  not_applicable

assay_paradigm:
  lipid_induced   - protein alone does NOT aggregate under the assay conditions;
                    lipid can only trigger/accelerate (so "no effect" != inhibition)
  aggregating_baseline - protein DOES aggregate on its own (e.g. agitation / neutral pH);
                    a lipid can either reduce OR further accelerate it (both are informative)
  (This distinction is essential: a "no_detectable_effect" in a lipid_induced assay is
   NOT evidence of inhibition, because the control also shows no aggregation.)

evidence_type (per measurement):
  measured_text   - a numeric value stated in article text/table
  relative_text   - a relative numeric statement in text (e.g. "< 1/3 of control")
  qualitative_text- a described direction with no number
  digitized       - read off a plotted curve (marked estimate)
  calculated      - computed deterministically from other measured values

quality_flag: ok | abstract_only | conditions_unreported | censored |
              natural_mixture | digitization_pending
"""

# ---------------------------------------------------------------------------
# PAPERS
# ---------------------------------------------------------------------------
PAPERS = [
    dict(paper_id="martinez2007", authors="Martinez Z, Zhu M, Han S, Fink AL",
         year=2007, title="GM1 specifically interacts with alpha-synuclein and inhibits fibrillation",
         journal="Biochemistry", doi="10.1021/bi061749a", pmid="17253773", pmcid="",
         access_status="abstract_only",
         role="primary_aggregation",
         notes="Full text subscription-only; only the abstract was accessible. Assay paradigm is "
               "inhibition (Fink lab ThT fibrillation), but exact conditions (pH, temp, agitation, "
               "concentrations) are NOT in the accessible abstract. Secondary citations in Grey 2015 "
               "(ref 57) and Gaspar 2018 (ref 67) describe GM1 ganglioside inhibition of alpha-syn "
               "aggregation as occurring at neutral pH (~7.5)."),
    dict(paper_id="grey2015", authors="Grey M, Dunning CJ, Gaspar R, et al.",
         year=2015, title="Acceleration of alpha-Synuclein Aggregation by Exosomes",
         journal="Journal of Biological Chemistry", doi="10.1074/jbc.M114.585703",
         pmid="25425650", pmcid="PMC4317028", access_status="full_text",
         role="primary_aggregation",
         notes="Lipid-induced / membrane-catalysis paradigm at mildly acidic pH 5.5. Numeric "
               "half-times for individual lipids are shown only in figures (not tabulated); text "
               "gives relative statements. Candidate-relevant: DOPC (no accel/retard), GM1 (accel)."),
    dict(paper_id="galvagnion2016", authors="Galvagnion C, Brown JWP, Ouberai MM, et al.",
         year=2016, title="Chemical properties of lipids strongly affect the kinetics of the membrane-induced aggregation of alpha-synuclein",
         journal="PNAS", doi="10.1073/pnas.1601899113", pmid="27298346", pmcid="PMC4932957",
         access_status="full_text", role="primary_aggregation",
         notes="Lipid-induced paradigm, quiescent, pH 6.5, 30C. Anionic PS lipids of varying chain "
               "length. Candidate-relevant: cholesterol (no initiation in synaptic-mimic mix), DOPC "
               "and DMPC appear only within mixtures. Half-times plotted in Fig 5; non-aggregating "
               "systems are censored at the 50 h incubation time."),
    dict(paper_id="galvagnion2015", authors="Galvagnion C, Buell AK, Meisl G, et al.",
         year=2015, title="Lipid vesicles trigger alpha-synuclein aggregation by stimulating primary nucleation",
         journal="Nature Chemical Biology", doi="10.1038/nchembio.1750", pmid="25580854",
         pmcid="PMC5019199", access_status="full_text", role="primary_support",
         notes="DMPS-only mechanistic study (DMPS is NOT one of the 8 candidates). Important "
               "conceptual evidence: the SAME lipid is biphasic - excess lipid (ratio>40) gives NO "
               "aggregation and even DISSOLVES preformed fibrils, while low ratio accelerates "
               "(max rate ~ratio 8). Supports 'formulation/ratio changes direction'."),
    dict(paper_id="gaspar2018", authors="Gaspar R, Pallbo J, Weininger U, Linse S, Sparr E",
         year=2018, title="Ganglioside lipids accelerate alpha-synuclein amyloid formation",
         journal="Biochimica et Biophysica Acta - Proteins and Proteomics",
         doi="10.1016/j.bbapap.2018.05.005", pmid="29803858", pmcid="PMC6121081",
         access_status="full_text", role="primary_aggregation",
         notes="Lipid-induced paradigm at pH 5.5. Candidate-relevant: DOPC (no aggregation), GM1 "
               "(acceleration). Explicitly notes GM1 vesicles INHIBIT at neutral pH (ref 67), i.e. "
               "opposite direction - the key condition-dependence for GM1."),
    dict(paper_id="matveyenka2024", authors="Matveyenka M, Ali A, Mitchell CL, Brown HC, Kurouski D",
         year=2024, title="Cholesterol Accelerates Aggregation of alpha-Synuclein Simultaneously Increasing the Toxicity of Amyloid Fibrils",
         journal="ACS Chemical Neuroscience", doi="10.1021/acschemneuro.4c00501", pmid="39469734",
         pmcid="PMC11587506", access_status="full_text", role="primary_aggregation",
         notes="AGGREGATING-BASELINE paradigm: 40 uM alpha-syn in PBS pH 7.4, 37 C, 510 rpm SHAKING, "
               "1:1 lipid:protein, LUVs, 2 mM ThT - protein aggregates alone (t1/2~82 h) and lipids modulate. "
               "FIRST paper here with explicit numeric t_lag and t1/2. Directly tests CHOLESTEROL and DPPC "
               "(both candidates). Key results: pure DPPC and 60% cholesterol ACCELERATE (shorten lag/t1/2); "
               "15-30% cholesterol no effect. Cites Dou et al. that DMPC strongly SUPPRESSES but DPPC does not "
               "(a 14->16 carbon change flips the effect). NOTE: this CONTRADICTS a naive 'ordered lipids are "
               "protective' expectation - see docs/chemistry_rules.md Rule 8 revision."),
    dict(paper_id="tht_assay2018", authors="Mahls A, et al. (Bio-protocol)",
         year=2018, title="alpha-Synuclein Aggregation Monitored by Thioflavin T Fluorescence Assay",
         journal="Bio-protocol", doi="", pmid="", pmcid="PMC6066150",
         access_status="full_text", role="assay_reference",
         notes="Methodological reference for ThT assay interpretation; no lipid aggregation records "
               "extracted for the dataset."),
]

# ---------------------------------------------------------------------------
# CONDITIONS + nested COMPONENTS + nested MEASUREMENTS
# Concentrations in micromolar (uM) unless stated; total_lipid in uM for consistency.
# component: lipid_id (-> lipids.csv), mol_fraction (of total lipid; '' if pure/na),
#            fraction_basis, role
# A measurement: endpoint, value, value_text, unit, uncertainty, n_rep, evidence_category,
#   effect_direction, evidence_type, source_fig, source_quote, quality_flag, control_id
# ---------------------------------------------------------------------------

def C(**kw):
    kw.setdefault("components", [])
    kw.setdefault("measurements", [])
    return kw

def M(**kw):
    kw.setdefault("value", "")
    kw.setdefault("value_text", "")
    kw.setdefault("unit", "")
    kw.setdefault("uncertainty", "")
    kw.setdefault("n_rep", "")
    kw.setdefault("control_id", "")
    kw.setdefault("quality_flag", "ok")
    return kw

CONDITIONS = []

# ============================= MARTINEZ 2007 (abstract only) =================
_m_common = dict(paper="martinez2007", assay_type="ThT_fibrillation",
                 protein_variant="WT", protein_conc_uM="", buffer="",
                 pH="", salt_mM="", temp_C="", agitation="", plate="",
                 tht_uM="", formulation="SUV", prep_method="", vesicle_size_nm="",
                 seeding="unseeded", obs_h="", assay_paradigm="aggregating_baseline",
                 source_page="abstract")
CONDITIONS += [
    C(condition_id="martinez2007_c01", **_m_common,
      label="GM1 SUVs + WT alpha-syn",
      components=[dict(lipid_id="GM1", mol_fraction="", fraction_basis="",
                       total_lipid_uM="", component_conc_uM="", role="main",
                       note="GM1-containing SUVs; GM1 fraction not in abstract")],
      measurements=[
          M(endpoint="effect_direction", value_text="inhibition_or_elimination",
            evidence_category="direct_aggregation", effect_direction="inhibition",
            evidence_type="qualitative_text", source_fig="abstract",
            source_quote="induction of substantial alpha-helical structure and inhibition or "
                         "elimination of alpha-synuclein fibril formation, depending on the amount of GM1 present",
            quality_flag="abstract_only"),
          M(endpoint="concentration_dependence", value_text="stronger_inhibition_with_more_GM1",
            evidence_category="direct_aggregation", effect_direction="inhibition",
            evidence_type="qualitative_text", source_fig="abstract",
            source_quote="depending on the amount of GM1 present", quality_flag="abstract_only"),
          M(endpoint="helicity_induction", value_text="substantial_alpha_helix",
            evidence_category="binding_structural", effect_direction="not_applicable",
            evidence_type="qualitative_text", source_fig="abstract",
            source_quote="specifically binds to ganglioside GM1-containing small unilamellar vesicles ... "
                         "induction of substantial alpha-helical structure", quality_flag="abstract_only"),
      ]),
    C(condition_id="martinez2007_c02", **_m_common, label="GM2 SUVs + WT",
      components=[dict(lipid_id="GM2", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="weak_inhibition",
          evidence_category="direct_aggregation", effect_direction="inhibition",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="SUVs containing total brain gangliosides, gangliosides GM2 or GM3, or asialo-GM1 "
                       "had weak inhibitory effects on alpha-synuclein fibrillation", quality_flag="abstract_only")]),
    C(condition_id="martinez2007_c03", **_m_common, label="GM3 SUVs + WT",
      components=[dict(lipid_id="GM3", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="weak_inhibition",
          evidence_category="direct_aggregation", effect_direction="inhibition",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="gangliosides GM2 or GM3, or asialo-GM1 had weak inhibitory effects", quality_flag="abstract_only")]),
    C(condition_id="martinez2007_c04", **_m_common, label="asialo-GM1 SUVs + WT",
      components=[dict(lipid_id="AsialoGM1", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="weak_inhibition",
          evidence_category="direct_aggregation", effect_direction="inhibition",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="asialo-GM1 had weak inhibitory effects on alpha-synuclein fibrillation", quality_flag="abstract_only")]),
    C(condition_id="martinez2007_c05", **_m_common, label="total brain gangliosides SUVs + WT",
      components=[dict(lipid_id="BrainGangliosides", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main", note="undefined natural mixture")],
      measurements=[M(endpoint="effect_direction", value_text="weak_inhibition",
          evidence_category="direct_aggregation", effect_direction="inhibition",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="SUVs containing total brain gangliosides ... had weak inhibitory effects",
          quality_flag="natural_mixture")]),
    C(condition_id="martinez2007_c06", **_m_common,
      label="other sphingolipids + WT",
      components=[dict(lipid_id="SM", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main",
                       note="'all other sphingolipids studied' - identities not enumerated in abstract; "
                            "mapped to SM as representative but see quality_flag")],
      measurements=[M(endpoint="effect_direction", value_text="negligible_interaction",
          evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="all other sphingolipids studied showed negligible interaction with alpha-synuclein",
          quality_flag="abstract_only")]),
    C(condition_id="martinez2007_c07", **{**_m_common, "protein_variant": "A53T"},
      label="GM1 SUVs + A53T mutant",
      components=[dict(lipid_id="GM1", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="interaction", value_text="interacts_like_WT",
          evidence_category="binding_structural", effect_direction="not_applicable",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="The familial mutant A53T alpha-synuclein interacted with GM1-containing SUVs in an "
                       "analogous manner to wild type", quality_flag="abstract_only")]),
    C(condition_id="martinez2007_c08", **{**_m_common, "protein_variant": "A30P"},
      label="GM1 SUVs + A30P mutant",
      components=[dict(lipid_id="GM1", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="interaction", value_text="minimal_interaction",
          evidence_category="binding_structural", effect_direction="not_applicable",
          evidence_type="qualitative_text", source_fig="abstract",
          source_quote="the A30P mutant showed minimal interaction", quality_flag="abstract_only")]),
]

# ============================= GREY 2015 ====================================
# common: 30 uM aSyn WT, 10 mM MES pH 5.5, 140 mM NaCl, 20 uM ThT, 37C, up to 144h
_g = dict(paper="grey2015", assay_type="ThT_kinetics", protein_variant="WT",
          protein_conc_uM=30, buffer="10 mM MES", pH=5.5, salt_mM=140, temp_C=37,
          tht_uM=20, seeding="unseeded", obs_h=144, assay_paradigm="lipid_induced",
          source_page="")

def grey_control(cid, plate, agit, fig):
    return C(condition_id=cid, **_g, label="alpha-syn alone (control)", formulation="none",
             prep_method="", vesicle_size_nm="", plate=plate, agitation=agit,
             components=[], measurements=[M(endpoint="effect_direction", value_text="reference_control",
                 evidence_category="direct_aggregation", effect_direction="not_applicable",
                 evidence_type="qualitative_text", source_fig=fig,
                 source_quote="alpha-syn alone", quality_flag="ok")])

CONDITIONS += [
    grey_control("grey2015_ctrl_shake", "Costar 3631 nontreated PS full-vol", "100 rpm", "Fig 3A"),
    grey_control("grey2015_ctrl_quiet_nb", "Corning 3881 nonbinding half-area", "quiescent", "Fig 8B"),

    C(condition_id="grey2015_c_exo_wtOE", **_g, label="exosomes (N2a WT-OE) 0.25 mg/ml, shaking",
      formulation="exosome", prep_method="ultracentrifugation from N2a medium",
      vesicle_size_nm="~100", plate="Costar 3631 nontreated PS full-vol", agitation="100 rpm",
      components=[dict(lipid_id="", mol_fraction="", fraction_basis="",
                       total_lipid_uM="~150 (est. phosphorus assay)", component_conc_uM="",
                       role="exosome", note="exosome 0.25 mg/ml protein-content; mixed natural lipids+protein")],
      measurements=[
        M(endpoint="half_time_relative", value_text="<1/3 of control", unit="relative",
          evidence_category="direct_aggregation", effect_direction="strong_acceleration",
          evidence_type="relative_text", source_fig="Fig 3A",
          control_id="grey2015_ctrl_shake",
          source_quote="the half-time for the alpha-syn aggregation ... in the presence of exosomes is "
                       "less than one-third", n_rep="4-8"),
      ]),
    C(condition_id="grey2015_c_exo_naive", **_g, label="exosomes (naive N2a) 0.25 mg/ml, shaking",
      formulation="exosome", prep_method="ultracentrifugation", vesicle_size_nm="~100",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="exosome", note="naive N2a exosomes")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration",
        evidence_category="direct_aggregation", effect_direction="strong_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 3A", control_id="grey2015_ctrl_shake",
        source_quote="There is no significant difference between exosomes isolated from naive N2a cells or "
                     "those overexpressing alpha-syn", n_rep="4-8")]),
    C(condition_id="grey2015_c_dopc", **_g, label="DOPC SUV 0.2 mM",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="DOPC", mol_fraction=1.0, fraction_basis="molar",
                       total_lipid_uM=200, component_conc_uM=200, role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="no_acceleration_or_retardation",
        evidence_category="direct_aggregation", effect_direction="retardation",
        evidence_type="qualitative_text", source_fig="Fig 6A", control_id="grey2015_ctrl_shake",
        source_quote="alpha-syn aggregation is not accelerated by any of these lipid systems, and in some "
                     "cases we instead observe a minor retardation", n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_dopc_dops30", **_g, label="DOPC + 30% DOPS SUV 0.2 mM",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="DOPC", mol_fraction=0.70, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=140, role="main", note=""),
                  dict(lipid_id="DOPS", mol_fraction=0.30, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=60, role="anionic", note="")],
      measurements=[M(endpoint="effect_direction", value_text="no_acceleration_or_retardation",
        evidence_category="direct_aggregation", effect_direction="retardation",
        evidence_type="qualitative_text", source_fig="Fig 6B", control_id="grey2015_ctrl_shake",
        source_quote="charge alone does not explain the acceleration ... not accelerated by any of these "
                     "lipid systems", n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_dopc_cl6", **_g, label="DOPC + 6% cardiolipin SUV 0.2 mM",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="DOPC", mol_fraction=0.94, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=188, role="main", note=""),
                  dict(lipid_id="CL", mol_fraction=0.06, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=12, role="anionic", note="net charge -2")],
      measurements=[M(endpoint="effect_direction", value_text="no_acceleration_or_retardation",
        evidence_category="direct_aggregation", effect_direction="retardation",
        evidence_type="qualitative_text", source_fig="Fig 6B", control_id="grey2015_ctrl_shake",
        source_quote="not accelerated by any of these lipid systems, and in some cases we instead observe a "
                     "minor retardation", n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_dopc_sph15", **_g, label="DOPC + 15% sphingosine SUV 0.2 mM",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="DOPC", mol_fraction=0.85, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=170, role="main", note=""),
                  dict(lipid_id="Sphingosine", mol_fraction=0.15, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=30, role="cationic", note="net +1; NOT sphingomyelin")],
      measurements=[M(endpoint="effect_direction", value_text="no_acceleration_or_retardation",
        evidence_category="direct_aggregation", effect_direction="retardation",
        evidence_type="qualitative_text", source_fig="Fig 6C", control_id="grey2015_ctrl_shake",
        source_quote="aggregation is retarded or shows no significant change in lag time when the lipid "
                     "vesicles are added", n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_gm1_02", **_g, label="DOPC + 10% GM1 SUV 0.2 mM, shaking",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=180, role="main", note=""),
                  dict(lipid_id="GM1", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=20, role="anionic", note="GM1 conc = 20 uM, NOT 200 uM")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 8A", control_id="grey2015_ctrl_shake",
        source_quote="the addition of these vesicles ... was found to accelerate the aggregation process in "
                     "a concentration-dependent manner", n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_gm1_05", **_g, label="DOPC + 10% GM1 SUV 0.5 mM, shaking",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM=500,
                       component_conc_uM=450, role="main", note=""),
                  dict(lipid_id="GM1", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM=500,
                       component_conc_uM=50, role="anionic", note="GM1 conc = 50 uM")],
      measurements=[M(endpoint="effect_direction", value_text="stronger_acceleration_than_0.2mM",
        evidence_category="direct_aggregation", effect_direction="strong_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 8A", control_id="grey2015_ctrl_shake",
        source_quote="All samples containing vesicles at 0.5 mM total lipid concentration exhibited faster "
                     "aggregation than the samples containing vesicles at 0.2 mM", n_rep="8",
        quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_gm1_01_quiet", **_g, label="DOPC + 10% GM1 SUV 0.1 mM, quiescent nonbinding",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Corning 3881 nonbinding half-area", agitation="quiescent",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=90, role="main", note=""),
                  dict(lipid_id="GM1", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=10, role="anionic", note="GM1 conc = 10 uM")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration_where_control_flat",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 8B", control_id="grey2015_ctrl_quiet_nb",
        source_quote="vesicles composed of GM1 promote aggregation of alpha-syn also in nonbinding pegylated "
                     "plates ... where alpha-syn alone does not aggregate during the time frame acquired",
        n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_gm3_02_quiet", **_g, label="DOPC + 10% GM3 SUV 0.2 mM, quiescent",
      formulation="SUV", prep_method="probe sonication", vesicle_size_nm="SUV",
      plate="Corning 3881 nonbinding half-area", agitation="quiescent",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=180, role="main", note=""),
                  dict(lipid_id="GM3", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM=200,
                       component_conc_uM=20, role="anionic", note="")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 8C", control_id="grey2015_ctrl_quiet_nb",
        source_quote="the addition of these vesicles to the monomeric recombinant alpha-syn was found to accelerate the aggregation process in a concentration-dependent manner",
        n_rep="8", quality_flag="digitization_pending")]),
    C(condition_id="grey2015_c_exolipid", **_g, label="extracted exosome-lipid SUV",
      formulation="SUV", prep_method="Bligh-Dyer extract + sonication", vesicle_size_nm="SUV",
      plate="Costar 3631", agitation="100 rpm",
      components=[dict(lipid_id="", mol_fraction="", fraction_basis="", total_lipid_uM="",
                       component_conc_uM="", role="natural_extract", note="exosome lipid extract (mixture)")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration_except_highest_conc",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 6D/7B", control_id="grey2015_ctrl_shake",
        source_quote="SUVs made of extracted exosome lipids accelerate aggregation except at the highest "
                     "concentration where we did not observe any aggregation", quality_flag="natural_mixture")]),
]

# ============================= GALVAGNION 2016 ==============================
# common: aSyn WT, 20 mM Na phosphate pH 6.5, 50 uM ThT, 30C, quiescent,
#         Corning 3881 nonbinding half-area, lipid SUV. obs ~50 h for censored.
_gv = dict(paper="galvagnion2016", assay_type="ThT_kinetics", protein_variant="WT",
           buffer="20 mM sodium phosphate", pH=6.5, salt_mM=0, temp_C=30, tht_uM=50,
           agitation="quiescent", plate="Corning 3881 nonbinding half-area",
           formulation="SUV", prep_method="sonication", vesicle_size_nm="SUV",
           seeding="unseeded", obs_h=50, assay_paradigm="lipid_induced", source_page="")

CONDITIONS += [
    C(condition_id="galvagnion2016_ctrl", **_gv, label="alpha-syn alone (no lipid)",
      protein_conc_uM=100, components=[],
      measurements=[M(endpoint="effect_direction", value_text="reference_control_no_aggregation",
        evidence_category="direct_aggregation", effect_direction="not_applicable",
        evidence_type="qualitative_text", source_fig="Fig 3A",
        source_quote="alpha-synuclein was not found to form amyloid fibrils at an enhanced rate relative to "
                     "bulk aqueous solution", quality_flag="ok")]),
    C(condition_id="galvagnion2016_c_dmps100_p100", **_gv, label="DMPS 100 uM + 100 uM aSyn",
      protein_conc_uM=100,
      components=[dict(lipid_id="DMPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=100, role="main", note="")],
      measurements=[
        M(endpoint="effect_direction", value_text="triggers_fibrils",
          evidence_category="direct_aggregation", effect_direction="acceleration",
          evidence_type="qualitative_text", source_fig="Fig 3A/5", control_id="galvagnion2016_ctrl",
          source_quote="the presence of DMPS was found to promote the formation of amyloid fibrils by alpha-synuclein"),
        M(endpoint="half_time", value_text="finite_plotted", unit="h",
          evidence_category="direct_aggregation", effect_direction="acceleration",
          evidence_type="digitized", source_fig="Fig 5",
          source_quote="The half-times plotted in Fig. 5 correspond to the times at which the ThT fluorescence signal is half the signal at the plateau", quality_flag="digitization_pending"),
        M(endpoint="KD", value=0.5, unit="uM", uncertainty=0.2, evidence_category="binding_structural",
          effect_direction="not_applicable", evidence_type="measured_text", source_fig="Table 1",
          source_quote="0.5 ± 0.2"),
        M(endpoint="stoichiometry_L", value=31, unit="lipids/protein", uncertainty=2,
          evidence_category="binding_structural", effect_direction="not_applicable",
          evidence_type="measured_text", source_fig="Table 1", source_quote="31 ± 2"),
      ]),
    C(condition_id="galvagnion2016_c_dlps100_p100", **_gv, label="DLPS 100 uM + 100 uM aSyn",
      protein_conc_uM=100,
      components=[dict(lipid_id="DLPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=100, role="main", note="")],
      measurements=[
        M(endpoint="effect_direction", value_text="triggers_fibrils_faster_than_DMPS",
          evidence_category="direct_aggregation", effect_direction="strong_acceleration",
          evidence_type="qualitative_text", source_fig="Fig 3A/5", control_id="galvagnion2016_ctrl",
          source_quote="DLPS was observed to trigger fibril formation, indeed to an even greater degree than "
                       "is the case with DMPS ... the rate of aggregation was found to be significantly faster "
                       "with the shorter chain DLPS compared with that of DMPS"),
        M(endpoint="KD", value=0.3, unit="uM", uncertainty=0.1, evidence_category="binding_structural",
          effect_direction="not_applicable", evidence_type="measured_text", source_fig="Table 1",
          source_quote="0.3 ± 0.1"),
        M(endpoint="stoichiometry_L", value=28, unit="lipids/protein", uncertainty=1,
          evidence_category="binding_structural", effect_direction="not_applicable",
          evidence_type="measured_text", source_fig="Table 1", source_quote="28 ± 1"),
      ]),
    C(condition_id="galvagnion2016_c_dops100_p100", **_gv, label="DOPS 100 uM + 100 uM aSyn",
      protein_conc_uM=100,
      components=[dict(lipid_id="DOPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=100, role="main", note="")],
      measurements=[
        M(endpoint="effect_direction", value_text="no_enhanced_aggregation",
          evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
          evidence_type="qualitative_text", source_fig="Fig 3A", control_id="galvagnion2016_ctrl",
          source_quote="alpha-synuclein was not found to form amyloid fibrils at an enhanced rate relative to "
                       "bulk aqueous solution in the presence of the other model membranes in the fluid state "
                       "that were investigated here (DOPS and POPS)"),
        M(endpoint="half_time", value_text=">50", unit="h", evidence_category="direct_aggregation",
          effect_direction="no_detectable_effect", evidence_type="relative_text", source_fig="Fig 5/Methods",
          source_quote="the lower bound of the half-time ... corresponds to the incubation time ... during "
                       "which the aggregation of the protein was not observed (i.e., 50 h)", quality_flag="censored"),
        M(endpoint="KD", value=0.2, unit="uM", uncertainty=0.1, evidence_category="binding_structural",
          effect_direction="not_applicable", evidence_type="measured_text", source_fig="Table 1",
          source_quote="0.2 ± 0.1"),
      ]),
    C(condition_id="galvagnion2016_c_pops100_p100", **_gv, label="POPS 100 uM + 100 uM aSyn",
      protein_conc_uM=100,
      components=[dict(lipid_id="POPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=100, role="main", note="")],
      measurements=[
        M(endpoint="effect_direction", value_text="no_enhanced_aggregation",
          evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
          evidence_type="qualitative_text", source_fig="Fig 3A", control_id="galvagnion2016_ctrl",
          source_quote="(DOPS and POPS) ... not ... at an enhanced rate"),
        M(endpoint="half_time", value_text=">50", unit="h", evidence_category="direct_aggregation",
          effect_direction="no_detectable_effect", evidence_type="relative_text", source_fig="Fig 5/Methods",
          source_quote="not observed (i.e., 50 h)", quality_flag="censored"),
      ]),
    C(condition_id="galvagnion2016_c_dpps100_p100", **_gv, label="DPPS 100 uM + 100 uM aSyn (gel phase)",
      protein_conc_uM=100,
      components=[dict(lipid_id="DPPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=100, role="main", note="solid gel at 30C")],
      measurements=[
        M(endpoint="effect_direction", value_text="no_aggregation",
          evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
          evidence_type="qualitative_text", source_fig="Fig 3A", control_id="galvagnion2016_ctrl",
          source_quote="nor for those in the solid gel phase (DPPS)"),
        M(endpoint="half_time", value_text=">50", unit="h", evidence_category="direct_aggregation",
          effect_direction="no_detectable_effect", evidence_type="relative_text", source_fig="Fig 5/Methods",
          source_quote="not observed (i.e., 50 h)", quality_flag="censored"),
      ]),
    C(condition_id="galvagnion2016_c_dpps_50C", **{**_gv, "temp_C": 50}, label="DPPS 100 uM + aSyn at 50C (fluid)",
      protein_conc_uM=100,
      components=[dict(lipid_id="DPPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=100,
                       component_conc_uM=100, role="main", note="fluid phase at 50C")],
      measurements=[M(endpoint="effect_direction", value_text="no_aggregation",
        evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
        evidence_type="qualitative_text", source_fig="text", control_id="galvagnion2016_ctrl",
        source_quote="DPPS ... at 50 C ... we did not observe promotion of amyloid formation",
        quality_flag="censored")]),
    C(condition_id="galvagnion2016_c_synmimic", **_gv, label="DOPE:DOPS:DOPC 50:30:20 (synaptic mimic)",
      protein_conc_uM=100,
      components=[dict(lipid_id="DOPE", mol_fraction=0.50, fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="DOPS", mol_fraction=0.30, fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="anionic", note=""),
                  dict(lipid_id="DOPC", mol_fraction=0.20, fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="no_significant_amyloid",
        evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
        evidence_type="qualitative_text", source_fig="text", control_id="galvagnion2016_ctrl",
        source_quote="a lipid composition suggested to mimic closely that of synaptic vesicles ... we observed "
                     "no significant degree of amyloid formation under these conditions", quality_flag="censored")]),
    C(condition_id="galvagnion2016_c_synmimic_chol", **_gv,
      label="DOPE:DOPS:DOPC 50:30:20 + cholesterol 10-40%",
      protein_conc_uM=100,
      components=[dict(lipid_id="DOPE", mol_fraction="", fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="main", note="base 50:30:20"),
                  dict(lipid_id="DOPS", mol_fraction="", fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="anionic", note=""),
                  dict(lipid_id="DOPC", mol_fraction="", fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="Cholesterol", mol_fraction="0.10-0.40", fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="sterol_additive", note="10-40% cholesterol added")],
      measurements=[M(endpoint="effect_direction", value_text="no_aggregation_cholesterol_does_not_initiate",
        evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
        evidence_type="qualitative_text", source_fig="text", control_id="galvagnion2016_ctrl",
        source_quote="model membranes consisting of DOPE:DOPS:DOPC (50:30:20) containing increasing "
                     "concentrations of cholesterol (10-40%), indicating that the presence of cholesterol does "
                     "not itself initiate alpha-synuclein aggregation under these conditions", quality_flag="censored")]),
    C(condition_id="galvagnion2016_c_dlps_dpps", **_gv, label="DLPS:DPPS 50:50 100 uM + 100 uM aSyn",
      protein_conc_uM=100,
      components=[dict(lipid_id="DLPS", mol_fraction=0.50, fraction_basis="molar", total_lipid_uM=100, component_conc_uM=50, role="main", note=""),
                  dict(lipid_id="DPPS", mol_fraction=0.50, fraction_basis="molar", total_lipid_uM=100, component_conc_uM=50, role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="fibrils_slower_than_equimolar_DLPS",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 4C", control_id="galvagnion2016_ctrl",
        source_quote="observed the formation of fibrils, albeit at a much lower rate than that observed in the "
                     "presence of a molar equivalent of DLPS model membranes (50 uM) and a much faster rate than "
                     "that observed in the presence of DPPS")]),
    C(condition_id="galvagnion2016_c_dmpc_dmps", **_gv,
      label="DMPC:DMPS mixtures (ratio varied), SI Fig S2",
      protein_conc_uM="", components=[
        dict(lipid_id="DMPC", mol_fraction="0 to >0.25", fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="main", note="DMPC fraction varied"),
        dict(lipid_id="DMPS", mol_fraction="balance", fraction_basis="molar", total_lipid_uM="", component_conc_uM="", role="anionic", note="")],
      measurements=[
        M(endpoint="effect_direction", value_text="no_detectable_aggregation_above_25pct_DMPC",
          evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
          evidence_type="qualitative_text", source_fig="SI Appendix Fig S2B", control_id="galvagnion2016_ctrl",
          source_quote="DMPC:DMPS model membranes did not detectably stimulate the aggregation of alpha-synuclein "
                       "for DMPC:DMPS ratios above 25:75", quality_flag="ok"),
        M(endpoint="binding_vs_composition", value_text="binding_decreases_with_DMPC_fraction",
          evidence_category="binding_structural", effect_direction="not_applicable",
          evidence_type="qualitative_text", source_fig="SI Appendix Fig S2A",
          source_quote="binding of alpha-synuclein to ... (DMPC):DMPS model membranes was shown to decrease as the "
                       "fraction of DMPC increases relative to that of DMPS", quality_flag="ok"),
      ]),
]

# ============================= GALVAGNION 2015 (DMPS mechanistic) ============
_gn = dict(paper="galvagnion2015", assay_type="ThT_kinetics", protein_variant="WT",
           protein_conc_uM=50, buffer="20 mM sodium phosphate", pH=6.5, salt_mM=0, temp_C=30,
           tht_uM="", agitation="quiescent", plate="Corning half-area nonbinding",
           formulation="SUV", prep_method="sonication", vesicle_size_nm="20-100",
           seeding="unseeded", obs_h=65, assay_paradigm="lipid_induced", source_page="")
CONDITIONS += [
    C(condition_id="galvagnion2015_c_excess", **_gn, label="DMPS excess (DMPS:aSyn > 40)",
      components=[dict(lipid_id="DMPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM=">2000",
                       component_conc_uM=">2000", role="main", note="ratio>40, all protein bound")],
      measurements=[M(endpoint="effect_direction", value_text="no_aggregation_all_bound",
        evidence_category="direct_aggregation", effect_direction="inhibition",
        evidence_type="qualitative_text", source_fig="Fig 1a", control_id="",
        source_quote="no increases in ThT fluorescence were detected when alpha-syn (50 uM) was incubated in "
                     "the presence of an excess of DMPS SUVs (DMPS:alpha-syn > 40) ... consistent with ... "
                     "previous conclusions that the presence of lipid vesicles can inhibit amyloid formation",
        quality_flag="ok")]),
    C(condition_id="galvagnion2015_c_low", **_gn, label="DMPS low ratio (DMPS:aSyn 2-15)",
      components=[dict(lipid_id="DMPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM="100-750",
                       component_conc_uM="100-750", role="main", note="ratio 2-15; max rate at ratio 8")],
      measurements=[M(endpoint="effect_direction", value_text="rapid_fibril_formation_max_at_ratio8",
        evidence_category="direct_aggregation", effect_direction="strong_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 1b-d", control_id="",
        source_quote="when alpha-syn (50 uM) was incubated at lower concentrations of DMPS (DMPS:alpha-syn ratios "
                     "between 2 and 15) ... rapid formation of amyloid fibrils was observed ... the maximum rate "
                     "of amyloid formation ... is observed for DMPS:alpha-syn ratios of 8")]),
    C(condition_id="galvagnion2015_c_fibril_dissolution",
      **{**_gn, "protein_conc_uM": 20, "seeding": "preformed_fibrils"},
      label="DMPS excess (2-8 mM) + preformed fibrils (20 uM)",
      components=[dict(lipid_id="DMPS", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM="2000-8000",
                       component_conc_uM="2000-8000", role="main", note="ratio>100")],
      measurements=[M(endpoint="effect_on_existing_fibrils", value_text="fibrils_dissolve",
        evidence_category="direct_aggregation", effect_direction="fibril_dissolution",
        evidence_type="qualitative_text", source_fig="Fig 2a,b", control_id="",
        source_quote="when short pre-formed fibrils (20 uM) were incubated with an excess of DMPS SUVs ... the "
                     "protein was found to dissociate from the fibrils ... and to populate the lipid-bound monomeric "
                     "alpha-helical state", quality_flag="ok")]),
]

# ============================= GASPAR 2018 ==================================
_gp = dict(paper="gaspar2018", assay_type="ThT_kinetics", protein_variant="WT",
           protein_conc_uM=20, buffer="10 mM MES", pH=5.5, salt_mM=0, temp_C=37, tht_uM=20,
           agitation="quiescent", plate="Corning 3881 nonbinding half-area", formulation="SUV",
           prep_method="tip sonication", vesicle_size_nm="SUV", seeding="unseeded", obs_h=140,
           assay_paradigm="lipid_induced", source_page="")
CONDITIONS += [
    C(condition_id="gaspar2018_ctrl", **{**_gp, "formulation": "none"}, label="alpha-syn alone (no lipid)",
      components=[], measurements=[M(endpoint="effect_direction", value_text="reference_control_no_aggregation",
        evidence_category="direct_aggregation", effect_direction="not_applicable",
        evidence_type="qualitative_text", source_fig="Fig 2A-D",
        source_quote="alpha-syn in the absence of catalytic surfaces does not aggregate up to several days (~140 h)")]),
    C(condition_id="gaspar2018_c_gm1", **_gp, label="DOPC:GM1 9:1 SUV 0.1-0.5 mM",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="GM1", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="anionic", note="")],
      measurements=[M(endpoint="effect_direction", value_text="strong_acceleration",
        evidence_category="direct_aggregation", effect_direction="strong_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 2A", control_id="gaspar2018_ctrl",
        source_quote="All these lipid vesicle systems show strong accelerating effect on the aggregation of "
                     "alpha-syn ... aggregation is triggered and starts within 20-60 h", quality_flag="digitization_pending")]),
    C(condition_id="gaspar2018_c_gm3", **_gp, label="DOPC:GM3 9:1 SUV",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="GM3", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="anionic", note="")],
      measurements=[M(endpoint="effect_direction", value_text="strong_acceleration",
        evidence_category="direct_aggregation", effect_direction="strong_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 2B", control_id="gaspar2018_ctrl",
        source_quote="strong accelerating effect", quality_flag="digitization_pending")]),
    C(condition_id="gaspar2018_c_dops", **_gp, label="DOPC:DOPS 9:1 SUV (reference anionic)",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="DOPS", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="anionic", note="")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 2D", control_id="gaspar2018_ctrl",
        source_quote="The control model system containing DOPS was also shown to catalyse aggregation",
        quality_flag="digitization_pending")]),
    C(condition_id="gaspar2018_c_dopc", **_gp, label="pure DOPC SUV",
      components=[dict(lipid_id="DOPC", mol_fraction=1.0, fraction_basis="molar", total_lipid_uM="10-1000", component_conc_uM="", role="main", note="")],
      measurements=[M(endpoint="effect_direction", value_text="no_aggregation_no_conf_change",
        evidence_category="direct_aggregation", effect_direction="no_detectable_effect",
        evidence_type="qualitative_text", source_fig="Fig 4A", control_id="gaspar2018_ctrl",
        source_quote="In the presence of pure DOPC lipid membranes, no aggregation and no conformational change "
                     "of alpha-syn were detected", quality_flag="censored")]),
    C(condition_id="gaspar2018_c_asialogm1", **_gp, label="DOPC:Asialo-GM1 9:1 SUV",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM="10-1000", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="AsialoGM1", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM="10-1000", component_conc_uM="", role="neutral_large_head", note="")],
      measurements=[M(endpoint="effect_direction", value_text="weak_acceleration",
        evidence_category="direct_aggregation", effect_direction="weak_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 4C", control_id="gaspar2018_ctrl",
        source_quote="both Asialo-GM1 and Cer-PEG750 trigger aggregation ... although with much less efficiency "
                     "than ganglioside, PE-PEG750 and DOPS containing vesicles", quality_flag="digitization_pending")]),
    C(condition_id="gaspar2018_c_cerpeg", **_gp, label="DOPC:Cer-PEG750 9:1 SUV",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM="10-1000", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="Cer-PEG750", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM="10-1000", component_conc_uM="", role="neutral_large_head", note="")],
      measurements=[M(endpoint="effect_direction", value_text="weak_acceleration",
        evidence_category="direct_aggregation", effect_direction="weak_acceleration",
        evidence_type="qualitative_text", source_fig="Fig 4E", control_id="gaspar2018_ctrl",
        source_quote="both Asialo-GM1 and Cer-PEG750 trigger aggregation ... much less efficiency",
        quality_flag="digitization_pending")]),
    C(condition_id="gaspar2018_c_pepeg", **_gp, label="DOPC:PE-PEG750 9:1 SUV",
      components=[dict(lipid_id="DOPC", mol_fraction=0.90, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="main", note=""),
                  dict(lipid_id="PE-PEG750", mol_fraction=0.10, fraction_basis="molar", total_lipid_uM="100-500", component_conc_uM="", role="anionic", note="")],
      measurements=[M(endpoint="effect_direction", value_text="acceleration",
        evidence_category="direct_aggregation", effect_direction="acceleration",
        evidence_type="qualitative_text", source_fig="Fig 2C", control_id="gaspar2018_ctrl",
        source_quote="PE-PEG750 ... clearly triggers alpha-syn aggregation, albeit to slightly lower extent "
                     "than gangliosides", quality_flag="digitization_pending")]),
]

# ============================= MATVEYENKA 2024 (cholesterol/DPPC, aggregating baseline) =====
# common: 40 uM WT aSyn, PBS pH 7.4, 37 C, 510 rpm shaking, 1:1 lipid:protein, LUV 100nm, 2 mM ThT
_mv = dict(paper="matveyenka2024", assay_type="ThT_kinetics", protein_variant="WT",
           protein_conc_uM=40, buffer="PBS", pH=7.4, salt_mM=137, temp_C=37, tht_uM=2000,
           agitation="510 rpm", plate="96-well (Tecan)", formulation="LUV",
           prep_method="extrusion 100 nm", vesicle_size_nm=100, seeding="unseeded", obs_h=160,
           assay_paradigm="aggregating_baseline", source_page="")
CONDITIONS += [
    C(condition_id="matveyenka2024_ctrl", **{**_mv, "formulation": "none"},
      label="alpha-syn alone (lipid-free)",
      components=[],
      measurements=[
        M(endpoint="half_time", value=82, unit="h", evidence_category="direct_aggregation",
          effect_direction="not_applicable", evidence_type="measured_text", source_fig="Fig 3C",
          source_quote="all lipid-free environment ( t 1/2 = 82 h)"),
        M(endpoint="lag_time", value=16.4, unit="h", evidence_category="direct_aggregation",
          effect_direction="not_applicable", evidence_type="measured_text", source_fig="Fig 3B",
          source_quote="alpha-Syn aggregated with a lag-phase ( t lag ) of ~16.4 h")]),
    C(condition_id="matveyenka2024_dppc", **_mv, label="100% DPPC LUV, 1:1",
      components=[dict(lipid_id="DPPC", mol_fraction=1.0, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=40, role="main", note="")],
      measurements=[
        M(endpoint="lag_time", value=12.3, unit="h", evidence_category="direct_aggregation",
          effect_direction="acceleration", evidence_type="measured_text", source_fig="Fig 3B",
          control_id="matveyenka2024_ctrl",
          source_quote="100% DPPC ( t lag = 12.3 h) drastically shortened t lag of alpha-syn aggregation"),
        M(endpoint="effect_direction", value_text="accelerates_shortens_lag",
          evidence_category="direct_aggregation", effect_direction="acceleration",
          evidence_type="qualitative_text", source_fig="Fig 3", control_id="matveyenka2024_ctrl",
          source_quote="Dou and co-workers previously reported that the presence of LUVs composed of C14:0 PC "
                       "(DMPC) strongly suppressed alpha-Syn aggregation ... such effects were not observed for "
                       "DPPC ... a change in the two carbon atoms in the fatty acids of PC caused a major effect")]),
    C(condition_id="matveyenka2024_chol15", **_mv, label="15:85 Cholesterol:DPPC LUV, 1:1",
      components=[dict(lipid_id="Cholesterol", mol_fraction=0.15, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=6, role="sterol_additive", note=""),
                  dict(lipid_id="DPPC", mol_fraction=0.85, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=34, role="main", note="")],
      measurements=[
        M(endpoint="half_time", value=79.5, unit="h", evidence_category="direct_aggregation",
          effect_direction="no_detectable_effect", evidence_type="measured_text", source_fig="Fig 3C",
          control_id="matveyenka2024_ctrl",
          source_quote="This effect was not observed for LUVs composed of 15:85 (79.5 h) and 30:70 (79.3 h) Cho/DPPC")]),
    C(condition_id="matveyenka2024_chol30", **_mv, label="30:70 Cholesterol:DPPC LUV, 1:1",
      components=[dict(lipid_id="Cholesterol", mol_fraction=0.30, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=12, role="sterol_additive", note=""),
                  dict(lipid_id="DPPC", mol_fraction=0.70, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=28, role="main", note="")],
      measurements=[
        M(endpoint="half_time", value=79.3, unit="h", evidence_category="direct_aggregation",
          effect_direction="no_detectable_effect", evidence_type="measured_text", source_fig="Fig 3C",
          control_id="matveyenka2024_ctrl",
          source_quote="15:85 (79.5 h) and 30:70 (79.3 h) Cho/DPPC")]),
    C(condition_id="matveyenka2024_chol60", **_mv, label="60:40 Cholesterol:DPPC LUV, 1:1",
      components=[dict(lipid_id="Cholesterol", mol_fraction=0.60, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=24, role="sterol_additive", note="high cholesterol"),
                  dict(lipid_id="DPPC", mol_fraction=0.40, fraction_basis="molar",
                       total_lipid_uM=40, component_conc_uM=16, role="main", note="")],
      measurements=[
        M(endpoint="half_time", value=61, unit="h", evidence_category="direct_aggregation",
          effect_direction="acceleration", evidence_type="measured_text", source_fig="Fig 3C",
          control_id="matveyenka2024_ctrl",
          source_quote="LUVs composed of 60:40 Cho/DPPC drastically accelerated the rate of alpha-Syn "
                       "aggregation ( t 1/2 = 61 h) compared to all lipid-free environment ( t 1/2 = 82 h)"),
        M(endpoint="lag_time", value=12.2, unit="h", evidence_category="direct_aggregation",
          effect_direction="acceleration", evidence_type="measured_text", source_fig="Fig 3B",
          control_id="matveyenka2024_ctrl",
          source_quote="LUVs composed of 60:40 Cho/DPPC ( t lag = 12.2 h) ... drastically shortened t lag")]),
]

# Secondary-literature cross-reference (NOT a measured record; recorded as a flagged note):
CROSS_REFS = [
    dict(claim="GM1 vesicles inhibit alpha-syn aggregation at neutral pH (opposite of pH 5.5)",
         asserted_in="gaspar2018 (ref 67) and grey2015 (ref 57)",
         source_quote="The opposite effect has been reported in studies conducted at neutral pH, where GM1 "
                      "containing vesicles were found to inhibit aggregation [67] (Gaspar); The opposite effect "
                      "has been reported for alpha-syn, pH 7.5, in the presence of lipid model membranes "
                      "containing ganglioside (57) (Grey)",
         evidence_type="secondary_citation",
         note="Corroborates Martinez 2007 direction (inhibition) and locates it at neutral pH. Treated as "
              "supporting context, not a primary measured record."),
    dict(claim="DMPC (C14:0 PC) strongly SUPPRESSES alpha-syn aggregation, whereas DPPC (C16:0 PC) does not",
         asserted_in="matveyenka2024 (citing Dou et al., ref 33)",
         source_quote="Dou and co-workers previously reported that the presence of LUVs composed of C14:0 PC "
                      "(DMPC) strongly suppressed alpha-Syn aggregation ... such effects were not observed for DPPC",
         evidence_type="secondary_citation",
         note="PRIORITY download: the Dou et al. primary paper has the DMPC suppression ThT data (DMPC is a "
              "candidate). Shows a 2-carbon change (14:0 fluid -> 16:0 gel) flips PC from suppressor to inert."),
    dict(claim="Cholesterol enhances alpha-syn-membrane interaction, accelerating aggregation",
         asserted_in="matveyenka2024 (citing Jakubec et al., ref 35) + own data",
         source_quote="Jakubec and co-workers found that in lipid membranes, cholesterol (Cho) enhances "
                      "protein-membrane interactions. This results in acceleration of alpha-Syn aggregation",
         evidence_type="secondary_citation",
         note="Supports the matveyenka2024 primary finding that 60% cholesterol accelerates (via increased "
              "membrane hydrophobicity), contradicting a naive 'cholesterol orders membranes -> protective' view."),
]

if __name__ == "__main__":
    print("papers:", len(PAPERS))
    print("conditions:", len(CONDITIONS))
    print("components:", sum(len(c["components"]) for c in CONDITIONS))
    print("measurements:", sum(len(c["measurements"]) for c in CONDITIONS))
