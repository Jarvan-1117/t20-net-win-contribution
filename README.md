# Net Win Contribution

Ball-by-ball win-probability modelling and player contribution analysis for
international T20 cricket.

## Overview

The project estimates the batting team's probability of winning after every
recorded delivery, then converts successive probability changes into player-level
Net Win Contribution (NWC). Separate models are trained for female/male and
first-/second-innings cricket so that chase-specific information never enters a
first-innings model.

The complete workflow contains five reproducible stages:

1. audit and clean the source delivery stream;
2. construct post-delivery game-state features and four modelling subsets;
3. add strictly prior-date player, team, venue, and recent-form features;
4. compare a naïve baseline, logistic regression, and random forest using log loss;
5. calculate and reconcile delivery-, match-, and player-level NWC.

Implementation details and limitations are documented in
[the methodology](docs/methodology.md).

## Model results

Models are selected independently using chronological validation data. The final
15% test period is not used for model or parameter selection. Random forest is
selected in all four tracks.

| Track | Naïve test log loss | Logistic test log loss | RF test log loss |
|---|---:|---:|---:|
| Female innings 1 | 0.691459 | 0.691732 | **0.510914** |
| Female innings 2 | 0.675578 | 0.344246 | **0.273831** |
| Male innings 1 | 0.693698 | 0.754022 | **0.495486** |
| Male innings 2 | 0.688326 | 0.425597 | **0.292898** |

Each track independently selected 500 trees, `max_features=0.25`,
`max_depth=14`, and `min_samples_leaf=50` across three expanding chronological
validation windows. The tuning procedure is implemented in
[`scripts/tune_random_forest.py`](scripts/tune_random_forest.py).

## Reproduce the analysis

The project requires Python 3.12 or later. Install the dependencies declared in
[`pyproject.toml`](pyproject.toml), place the source files below in `data/raw/`,
then run the notebooks in numerical order:

```text
t20i_deliveries_data.csv
t20i_matches_data.csv

notebooks/01_data_audit_and_cleaning.ipynb
notebooks/02_game_state_features.ipynb
notebooks/03_historical_features.ipynb
notebooks/04_model_training.ipynb
notebooks/05_nwc_attribution.ipynb
```

Model and validation settings are recorded in [`params.yaml`](params.yaml).

## Repository structure

```text
data/raw/              Local source data and tracked checksums
docs/                  Technical method, phase summary, and source documents
notebooks/             Five executable analysis stages
outputs/               Presentation and modelling feature dictionary
reports/metrics/       Machine-readable audit, model, tuning, and NWC results
scripts/               Reproducible pre-test Random Forest tuning
params.yaml            Analysis and model settings
pyproject.toml         Python dependency specification
```

## Key outputs

- [Model Feature Data Dictionary](outputs/phase04/Model%20Feature%20Data%20Dictionary.xlsx):
  feature definitions, null counts, and handling rules.
- [Phase 04 model performance](reports/metrics/phase_04_model_performance.json):
  validation and test log loss for all candidates.
- [Random Forest tuning record](reports/metrics/phase_04_rf_tuning.json):
  candidate results from all chronological tuning windows.
- [Phase 05 NWC checks](reports/metrics/phase_05_nwc_attribution.json):
  attribution counts and numerical reconciliation.
- [Progress presentation](outputs/T20_NWC_Phase_01_to_04_Update.pptx):
  short presentation covering Phases 01–04.

## Data policy

Raw CSVs, derived tables, predictions, and trained models are excluded from
normal Git history. Source SHA-256 hashes are stored in
[`data/raw/manifest.sha256`](data/raw/manifest.sha256). Keep the source files
immutable and write derived data only to `data/interim/` or `data/processed/`.

Confirm the dataset's redistribution licence before making the repository public
or sharing the source data.
