# Net Win Contribution

This project estimates ball-by-ball win probability in international T20 cricket
and converts probability changes into player-level Net Win Contribution (NWC).

## What is included

The workflow is complete through Phase 05:

1. audit and clean the delivery stream;
2. build post-delivery game-state features and split the data into female/male,
   first-/second-innings tracks;
3. add strictly historical player, team, and venue features;
4. compare a naïve baseline, logistic regression, and random forest using log loss;
5. calculate delivery-, match-, and player-level NWC.

Random forest is selected on validation log loss in all four model tracks. The
main reported player results use only the untouched chronological test split.

## Run the analysis

The project requires Python 3.12 or later. Install the dependencies declared in
`pyproject.toml`, place the two source CSV files in `data/raw/`, and run the
notebooks in order:

```text
notebooks/01_data_audit_and_cleaning.ipynb
notebooks/02_game_state_features.ipynb
notebooks/03_historical_features.ipynb
notebooks/04_model_training.ipynb
notebooks/05_nwc_attribution.ipynb
```

Model settings, including the male second-innings random-forest override, are in
`params.yaml`.

## Repository guide

```text
data/raw/              Local source data instructions and checksums
docs/methodology.md    Complete technical method and validation rules
docs/project_phase_report.md
                       Concise Chinese phase report
docs/reference/        Original project brief and supplied data dictionary
notebooks/             The five executable analysis stages
outputs/               Presentation and modelling feature dictionary
reports/metrics/       Compact machine-readable results for each phase
params.yaml            Reproducible analysis and model settings
```

Large raw/derived datasets and trained model files are intentionally excluded
from normal Git history. Re-running the notebooks recreates them locally.

## Key outputs

- `outputs/phase04/Model Feature Data Dictionary.xlsx`: modelling feature
  descriptions, null counts, and handling rules.
- `reports/metrics/phase_04_model_performance.json`: validation and test log loss.
- `reports/metrics/phase_04_rf_tuning_male_innings_2.json`: chronological RF tuning record.
- `reports/metrics/phase_05_nwc_attribution.json`: NWC counts and reconciliation checks.
- `outputs/T20_NWC_Phase_01_to_04_Update.pptx`: short progress presentation.

## Data policy

The raw CSV files are not committed. Their SHA-256 hashes are recorded in
`data/raw/manifest.sha256`. Confirm the dataset's redistribution licence before
making the repository public or sharing the source data.
