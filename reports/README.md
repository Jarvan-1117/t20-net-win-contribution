# Reports

- `metrics/`: compact machine-readable evaluation summaries
- `figures/`: generated charts, excluded from normal Git by default
- `model_cards/`: reviewed descriptions of released model versions

`metrics/phase_04_model_performance.json` reports validation and test log loss
for the ordered naïve, logistic-regression, and random-forest candidates, plus
the validation-selected model. No secondary performance metric is reported.
The human-readable model-feature/null dictionary is under `outputs/phase04/`.
