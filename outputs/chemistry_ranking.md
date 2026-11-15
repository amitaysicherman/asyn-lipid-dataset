# Rule-based lipid ranking for REDUCING alpha-synuclein fibril formation

Transparent, mechanism-driven (not ML). Scores decompose into binding (B), triggering risk (T), sequestration-inhibition (Iseq) and ordering/defect protection (O); `reduction_potential = Iseq + O - T` rescaled to 0-10. Rules & justification: `docs/chemistry_rules.md`. **The ranking changes with assay conditions** - that is the point.

### Scenario A - Neutral pH (7.4), HIGH lipid:protein ratio, 37 C

_Inhibition-favouring regime: excess membrane sequesters monomer; neutral pH keeps secondary nucleation slow. This is where a strong binder can actively suppress fibrils._

| rank | candidate | reduction potential (0-10) | trigger risk T | sequestration Iseq | ordering O | evidence |
|---|---|---|---|---|---|---|
| 1 | **GM1** | 8.4 | 0.09 | 3.0 | 0.0 | moderate (multiple papers; but pH-conflicted) |
| 2 | **Cholesterol** | 6.1 | 0.0 | 0.3 | 1.0 | low (one additive test: no initiation) |
| 3 | **SM** | 6.0 | 0.0 | 0.5 | 0.7 | very low (abstract: 'negligible interaction') |
| 4 | **DPPC** | 6.0 | 0.0 | 0.5 | 0.7 | none (prediction from rules only) |
| 5 | **DSPC** | 6.0 | 0.0 | 0.5 | 0.7 | none (prediction from rules only) |
| 6 | **DMPC** | 5.4 | 0.0 | 0.5 | 0.3 | low (only as DMPS diluent) |
| 7 | **DOPC** | 5.1 | 0.0 | 0.5 | 0.1 | moderate (pure DOPC tested: inert/mild retardation) |
| 8 | **POPC** | 5.1 | 0.0 | 0.5 | 0.1 | none (prediction from rules only) |

### Scenario B - Acidic pH (5.5), LOW lipid:protein ratio, 37 C

_Triggering-favouring regime (as in Grey/Gaspar). Here anionic/ganglioside lipids PROMOTE aggregation; only the inert neutral lipids are 'safe'._

| rank | candidate | reduction potential (0-10) | trigger risk T | sequestration Iseq | ordering O | evidence |
|---|---|---|---|---|---|---|
| 1 | **Cholesterol** | 5.7 | 0.0 | 0.02 | 1.0 | low (one additive test: no initiation) |
| 2 | **SM** | 5.3 | 0.0 | 0.03 | 0.7 | very low (abstract: 'negligible interaction') |
| 3 | **DPPC** | 5.3 | 0.0 | 0.03 | 0.7 | none (prediction from rules only) |
| 4 | **DSPC** | 5.3 | 0.0 | 0.03 | 0.7 | none (prediction from rules only) |
| 5 | **DMPC** | 4.8 | 0.0 | 0.03 | 0.3 | low (only as DMPS diluent) |
| 6 | **DOPC** | 4.5 | 0.0 | 0.03 | 0.1 | moderate (pure DOPC tested: inert/mild retardation) |
| 7 | **POPC** | 4.5 | 0.0 | 0.03 | 0.1 | none (prediction from rules only) |
| 8 | **GM1** | 1.0 | 2.5 | 0.18 | 0.0 | moderate (multiple papers; but pH-conflicted) |

## How to read this
- **GM1 is the only high-leverage candidate** and it is a *switch*: top of Scenario A (neutral pH, excess GM1 -> sequesters monomer, induces stable helix -> inhibits, per Martinez 2007) but a strong *promoter* in Scenario B (acidic, low ratio -> Grey/Gaspar). Its rank swings the most between scenarios.
- **The seven neutral candidates cannot strongly inhibit** (weak alpha-syn binding), but they are *safe* (they do not trigger). Among them the protective ordering term ranks the tightly-packed, defect-poor lipids first: **cholesterol > DSPC ~ DPPC ~ sphingomyelin > DMPC > POPC > DOPC**.
- So the practical answer depends entirely on which lever the wet lab can pull: a strong *active* inhibitor (GM1, only at neutral pH + high ratio) vs a *passive, safe* membrane (ordered raft lipids: cholesterol/SM/saturated-PC).
- Terms marked low-confidence (DPPC/DSPC/POPC) are **predictions from the rules, not observations** - no direct ThT data exists for them yet.