# Data dictionary

All tables are in `data/` as CSV. They are linked by stable IDs:
`papers.paper_id → conditions.paper_id`, `conditions.condition_id → components.condition_id`
and `→ measurements.condition_id`, `components.lipid_id → lipids.lipid_id`,
`measurements.control_id → conditions.condition_id`.

The single source of truth is `src/extraction_records.py` (hand-curated, with a verbatim
`source_quote` per measurement); the CSVs are generated from it by `src/build_dataset.py`.

## Evidence-type legend (how to read each value)
- **measured fact** – a number/statement given in the article text or table (`evidence_type`
  = `measured_text` / `relative_text`), or a qualitative direction (`qualitative_text`).
- **digitized estimate** – read off a plotted curve (`evidence_type=digitized`). None are
  populated yet; curve rows pending digitization are flagged `digitization_pending`.
- **calculated** – computed deterministically here (e.g. lipid:protein ratios).
- **model prediction / hypothesis** – never stored in these tables; they live only in
  `outputs/model_report.md` and the report's clearly-labelled sections.

---

## papers.csv
| column | meaning |
|---|---|
| paper_id | stable key (e.g. `galvagnion2016`) |
| authors, year, title, journal, doi, pmid, pmcid | bibliography |
| access_status | `full_text` / `abstract_only` |
| role | `primary_aggregation` / `primary_support` / `assay_reference` |
| notes | assay paradigm, caveats, what was/wasn't accessible |

## conditions.csv  (one row per experimental condition)
| column | meaning |
|---|---|
| condition_id | stable key |
| paper_id | → papers |
| label | human description |
| assay_type | e.g. `ThT_kinetics`, `ThT_fibrillation` |
| assay_paradigm | **`lipid_induced`** (protein alone does not aggregate; lipid can only trigger) or **`inhibition`** (protein aggregates; lipid tested to reduce it). Critical for interpreting "no effect". |
| protein_variant | WT / A53T / A30P / E46K |
| protein_conc_uM | blank if unreported |
| buffer, pH, salt_mM, temp_C, agitation, plate, tht_uM | assay conditions (blank if unreported) |
| formulation | SUV / LUV / exosome / none |
| prep_method, vesicle_size_nm | preparation |
| seeding | unseeded / preformed_fibrils |
| obs_h | observation window (hours) |
| total_lipid_uM | numeric total lipid where a single value is reported |
| lipid_to_protein_molar_ratio | **calculated** = total_lipid/protein when both numeric |
| source_page | page/section anchor |

## components.csv  (lipids making up each condition's formulation)
| column | meaning |
|---|---|
| component_id | stable key |
| condition_id | → conditions |
| lipid_id | → lipids |
| role | `main` (matrix/base), `anionic`, `cationic`, `sterol_additive`, `neutral_large_head`, `exosome`, `natural_extract` |
| mol_fraction | fraction of total lipid (number, or a textual range where the paper varied it) |
| fraction_basis | `molar` (always molar here; never mass) |
| total_lipid_uM | total lipid in this condition |
| component_conc_uM | this component's concentration (**not** the total; e.g. GM1 = 10% of total) |
| component_to_protein_molar_ratio | **calculated** |
| note | e.g. "GM1 conc = 20 uM, NOT 200 uM" |

## measurements.csv  (outcomes & provenance)
| column | meaning |
|---|---|
| measurement_id | stable key (M001…) |
| condition_id, paper_id | links |
| endpoint | `effect_direction`, `half_time`, `half_time_relative`, `KD`, `stoichiometry_L`, `helicity_induction`, `interaction`, `effect_on_existing_fibrils`, `binding_vs_composition`, `concentration_dependence` |
| evidence_category | `direct_aggregation` / `binding_structural` / `cellular` / `observational` |
| effect_direction | for direct_aggregation: `strong_acceleration`/`acceleration`/`weak_acceleration`/`no_detectable_effect`/`retardation`/`inhibition`/`fibril_dissolution`/`not_applicable` (controls) |
| value, value_text, unit, uncertainty | numeric value and/or textual value |
| n_replicates | replicate count where stated |
| control_id | matched control condition (→ conditions) |
| evidence_type | measured_text / relative_text / qualitative_text / digitized / calculated / secondary_citation |
| source_fig | figure/table/section the value came from |
| source_quote | **verbatim** supporting text (checked by `verify_provenance.py`) |
| quality_flag | ok / abstract_only / conditions_unreported / censored / natural_mixture / digitization_pending |

## curves.csv  (time-series ThT values; schema only until digitization is run)
| column | meaning |
|---|---|
| curve_id, condition_id, series_label | identity |
| time_h, tht_value | one row per point |
| normalization | raw / normalized-to-own-max / background-subtracted |
| source_fig, digitized, digitization_tool, note | provenance; `digitized=yes` marks all rows as estimates |

## lipids.csv  (structure reference)
| column | meaning |
|---|---|
| lipid_id / abbrev / name | identity |
| lipid_class | PC / PS / PE / ganglioside / sterol / sphingolipid / glycosphingolipid / PEG-lipid / cardiolipin |
| headgroup | headgroup family |
| net_charge_phys | approx net charge at neutral pH |
| acyl_chains | e.g. `14:0/14:0` (C:double bonds per chain) |
| mean_chain_carbons, total_double_bonds, n_chains | descriptors |
| tm_C | main gel→fluid melting temperature (°C) of the pure lipid; measured constant (Galvagnion 2016 for the PS series, Avanti/literature for PC & SM); blank where there is no simple two-state Tm (sterol, ganglioside, mixtures) |
| smiles | RDKit-canonical SMILES **for defined single species only** |
| smiles_input, smiles_valid, smiles_source | `built_diacyl` / `curated` / `omitted` |
| natural_mixture | 1 = natural-source mixture → SMILES deliberately omitted (no arbitrary structure assigned) |
| is_candidate | 1 = one of the 8 wet-lab candidates |
| note | caveats (e.g. sphingosine ≠ sphingomyelin) |

## cross_refs.csv
Secondary-literature cross-references (e.g. "GM1 inhibits at neutral pH" asserted in Grey/Gaspar).
Treated as **supporting context, not primary measurements**.

## model_table.csv  (generated by features.py)
Per-condition feature matrix + target (`effect_class`, `effect_score`). Derived, not a primary source.
