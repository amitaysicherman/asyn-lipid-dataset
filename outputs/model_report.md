# Baseline model evaluation (pilot)

- Modelling rows (conditions with a direct-aggregation effect label): **35**
- Class balance: accelerate=16, neutral=13, reduce=6
- Driver-lipid classes present: PS=14, ganglioside=10, glycosphingolipid=2, sphingolipid=2, unknown=2, PC=2, PEG-lipid=2, cardiolipin=1

Each cell is **accuracy / macro-F1**. Macro-F1 weights the three classes equally, so it punishes a model that ignores the rare `reduce` class. Majority-class accuracy is **0.457**.

| model | Stratified-5fold (optimistic) | Leave-One-Paper-Out | Leave-One-Lipid-Out |
|---|---|---|---|
| Dummy(most_frequent) | 0.457 / 0.209 | 0.314 / 0.185 | 0.343 / 0.174 |
| Rule(heuristic) | 0.600 / 0.600 | 0.600 / 0.600 | 0.600 / 0.600 |
| NN(k=1 chem+cond) | 0.743 / 0.712 | 0.371 / 0.262 | 0.771 / 0.752 |
| Logistic(L2) | 0.714 / 0.686 | 0.457 / 0.324 | 0.800 / 0.772 |

## Leave-One-Paper-Out confusion (Logistic L2)

rows = true, cols = predicted

| true \ pred | accelerate | neutral | reduce |
|---|---|---|---|
| accelerate | 13 | 1 | 2 |
| neutral | 7 | 3 | 3 |
| reduce | 6 | 0 | 0 |

## Per-held-out-paper accuracy (Logistic L2, LOPO)

| held-out paper | n | accuracy | note |
|---|---|---|---|
| martinez2007 | 6 | 0.000 | classes: neutral,reduce.  |
| grey2015 | 10 | 0.800 | classes: accelerate,neutral.  |
| galvagnion2016 | 10 | 0.100 | classes: accelerate,neutral.  |
| galvagnion2015 | 2 | 0.500 | classes: accelerate,reduce.  |
| gaspar2018 | 7 | 0.857 | classes: accelerate,neutral.  |

## Interpretation

- The **Rule heuristic** and models beat the majority baseline on the *optimistic* stratified split, confirming a real, learnable signal: **charged/ganglioside lipids trigger aggregation; zwitterionic PC/cholesterol do not**.
- Under **Leave-One-Paper-Out** and **Leave-One-Lipid-Out**, performance drops toward baseline and the `reduce` (inhibition) class collapses: nearly all inhibition evidence is Martinez 2007, so when it is held out the model cannot predict inhibition at all. The direction of GM1 is set by **pH**, which is confounded with paper.
- **Conclusion:** the pilot supports a coarse, interpretable *triggering* classifier under published conditions, but does **not** support quantitative or inhibition prediction, and must not be presented as a validated predictor of the 8 candidates or of Yuval's assay. This is a methodology demonstration and an honest sparsity diagnosis, not a deployable model.