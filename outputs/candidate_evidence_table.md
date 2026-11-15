# Evidence table for the 8 wet-lab candidates

_Grounded in the extracted pilot dataset. 'No effect' in a lipid-induced assay means the lipid did not trigger aggregation and is **not** proof of inhibition (the no-lipid control is also flat)._

## Cholesterol  (sterol)
- **Direct evidence found:** Yes  (conditions: 4; papers: galvagnion2016, matveyenka2024)
- **Formulations/conditions tested:** Cho:DPPC LUVs 15:85, 30:70, 60:40 at 1:1 lipid:protein, pH 7.4, shaking (Matveyenka 2024); and 10-40% in a synaptic-mimic mix (Galvagnion 2016)
- **Effect & direction:** DOSE-DEPENDENT and NOT protective: inert at <=30% cholesterol (t1/2 ~79 h vs 82 h control) but ACCELERATES at 60% (t1/2 61 h, lag 12.2 vs 16.4 h), attributed to increased membrane hydrophobicity. Did not initiate in the low-cholesterol synaptic mimic.
- **Conflicting findings:** Overturns the intuition that cholesterol (membrane-ordering) would be protective - at high mol% it promotes aggregation.
- **Quantitative prediction supported?** Yes - explicit t1/2 and t_lag (Matveyenka 2024, Fig 3).
- **Relevance to Yuval's ThT assay:** Effect depends strongly on mol% and on membrane fluidity; test a dose series, not a single %.

## Sphingomyelin (SM)  (sphingolipid)
- **Direct evidence found:** Weak/indirect  (conditions: 1; papers: martinez2007)
- **Formulations/conditions tested:** 'Other sphingolipids' in Martinez 2007 (abstract); sphingomyelin not individually resolved. Grey tested sphingoSINE (not sphingomyelin).
- **Effect & direction:** Martinez: 'other sphingolipids showed negligible interaction' (no effect). No dedicated SM ThT curve in the accessible pilot.
- **Conflicting findings:** None, but evidence is thin and possibly conflates SM with other sphingolipids.
- **Quantitative prediction supported?** No.
- **Relevance to Yuval's ThT assay:** Under-characterised in accessible primary data. Distinguish sphingomyelin from sphingosine and from gangliosides. A dedicated ThT experiment is needed.

## DMPC  (PC)
- **Direct evidence found:** Yes  (conditions: 1; papers: galvagnion2016)
- **Formulations/conditions tested:** DMPC:DMPS mixtures, ratio varied (Galvagnion 2016 SI Fig S2); pure-DMPC LUVs in Dou et al. (cited by Matveyenka 2024)
- **Effect & direction:** Fluid (Tm 24C) neutral PC that binds enough to SEQUESTER: Dou et al. report pure DMPC LUVs STRONGLY SUPPRESS alpha-syn aggregation; and increasing DMPC fraction reduces DMPS-driven aggregation (>25% DMPC -> no stimulation). The most promising neutral candidate for suppression.
- **Conflicting findings:** Contrasts sharply with DPPC (16:0): a 2-carbon-longer, gel-phase PC does NOT suppress.
- **Quantitative prediction supported?** Ordinal from Galvagnion; numeric suppression data is in the Dou et al. primary paper (to fetch).
- **Relevance to Yuval's ThT assay:** Strong lead as a passive suppressor; get the Dou et al. paper for conditions/half-times.

## DPPC  (PC)
- **Direct evidence found:** Yes  (conditions: 4; papers: matveyenka2024)
- **Formulations/conditions tested:** Pure DPPC LUVs + Cho:DPPC mixes, 1:1 lipid:protein, pH 7.4, 37C, shaking (Matveyenka 2024)
- **Effect & direction:** Gel-phase (Tm 41C) neutral PC that does NOT suppress - pure DPPC SHORTENS the lag (12.3 vs 16.4 h), i.e. mildly promotes. Binds alpha-syn too weakly (gel) to sequester it.
- **Conflicting findings:** Directly contrasts the DMPC suppression: '...not observed for DPPC... a change in two carbon atoms caused a major effect' (Matveyenka 2024).
- **Quantitative prediction supported?** Yes - t_lag (Matveyenka 2024).
- **Relevance to Yuval's ThT assay:** Not a suppressor under these conditions; useful as a non-protective saturated-PC reference.

## DSPC  (PC)
- **Direct evidence found:** No  (conditions: 0; papers: —)
- **Formulations/conditions tested:** Not tested in the pilot primary studies.
- **Effect & direction:** No direct record in the accessible pilot.
- **Conflicting findings:** n/a
- **Quantitative prediction supported?** No
- **Relevance to Yuval's ThT assay:** No primary evidence yet; needs targeted search and/or a wet-lab experiment.

## DOPC  (PC)
- **Direct evidence found:** Yes  (conditions: 17; papers: galvagnion2016, gaspar2018, grey2015)
- **Formulations/conditions tested:** Pure DOPC SUV (Gaspar 0.01-1 mM; Grey 0.2 mM); also matrix lipid in 9:1 mixes and synaptic-mimic
- **Effect & direction:** No detectable triggering of aggregation when pure; mild retardation in Grey. In lipid_induced assays this is 'no effect', NOT demonstrated inhibition (control also flat).
- **Conflicting findings:** None across Grey/Gaspar/Galvagnion - consistently inert/retarding as a pure lipid.
- **Quantitative prediction supported?** Qualitative only (no-effect/retardation); no comparable half-time extracted.
- **Relevance to Yuval's ThT assay:** Good negative/inert reference. Note it is the standard zwitterionic matrix; effects attributed to additives, not DOPC.

## POPC  (PC)
- **Direct evidence found:** No  (conditions: 0; papers: —)
- **Formulations/conditions tested:** Not tested in the pilot primary studies (POPS, not POPC, was tested).
- **Effect & direction:** No direct record; note POPS (phosphatidylserine) was tested by Galvagnion and showed no triggering, but that is a different headgroup from POPC.
- **Conflicting findings:** n/a
- **Quantitative prediction supported?** No
- **Relevance to Yuval's ThT assay:** No primary evidence yet; do not transfer POPS result to POPC (different headgroup/charge).

## GM1  (ganglioside)
- **Direct evidence found:** Yes  (conditions: 7; papers: gaspar2018, grey2015, martinez2007)
- **Formulations/conditions tested:** 9:1 DOPC:GM1 SUV (Grey 0.1-0.5 mM, quiescent & shaking; Gaspar 0.1-0.5 mM); GM1-SUV (Martinez)
- **Effect & direction:** CONDITION-DEPENDENT. Accelerates at mildly acidic pH 5.5 (Grey, Gaspar), concentration-dependent. Inhibits/eliminates fibrillation at neutral pH (Martinez 2007; corroborated by Grey ref57/Gaspar ref67).
- **Conflicting findings:** Direct direction conflict driven by pH (accelerate at 5.5 vs inhibit at ~7.4). Also formulation differs (pure GM1-SUV vs 10% GM1 in DOPC).
- **Quantitative prediction supported?** Not yet - acceleration curves need digitization; inhibition is abstract-only (no numbers).
- **Relevance to Yuval's ThT assay:** Highest-priority candidate but direction depends on pH/formulation. Yuval's pH is decisive.
