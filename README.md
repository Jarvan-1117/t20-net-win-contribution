# Net Win Contribution

T20 international cricket ball-by-ball win-probability and player contribution project.

## Current status

Phases 01 through 04 are implemented, executed, and verified as notebooks.
Phase 01 materialises a cleaned source-order delivery stream; Phase 02 writes
four separate post-delivery game-state tables (female/male by innings). First-
innings tables do not contain chase-only columns. Phase 03 adds 23 strictly
prior-date player, team, and venue historical predictors to each track. Phase
04 compares a naïve baseline, logistic regression, and random forest within four
date-grouped chronological model tracks. Validation log loss selects logistic
regression in all four tracks. NWC attribution has not been implemented.

## Intended workflow

1. Define the modelling timestamp, match exclusions, team scope, and NWC attribution policy.
2. Validate and clean match and delivery data. **Completed for the initial baseline.**
3. Build leakage-safe game-state and historical player/team features. **Completed for the initial baseline.**
4. Compare and select separate models by gender and innings. **Completed for the initial three-candidate comparison.**
5. Calculate delivery-level NWC and aggregate it by player, match, season, and career.
6. Validate calibration, temporal stability, attribution invariants, and reproducibility.

## Repository layout

```text
configs/            Experiment and model configuration
data/raw/           Original immutable datasets; not stored in normal Git
data/interim/       Reproducible cleaning-stage outputs
data/processed/     Model-ready feature tables
docs/               Methodology, quality notes, decisions, and source documents
models/             Trained artifacts; not stored in normal Git
notebooks/          Primary notebook-based analysis, modelling, and results
reports/            Metrics, figures, and model cards
src/nwc/            Future production package
tests/              Unit, integration, and small synthetic fixtures
```

## Data policy

The raw CSV files are intentionally excluded from normal Git history. Their hashes are recorded in `data/raw/manifest.sha256`. Before configuring a shared data remote, confirm the source dataset's redistribution licence.

The preferred future setup is Git for code and small metadata, plus DVC for datasets, derived tables, and trained models.

## Environment

The project will use Python 3.12 and `uv` with `pyproject.toml` and a committed `uv.lock`. The current machine did not have `uv` or DVC installed when this scaffold was created, so no lockfile or DVC metadata has been fabricated.

## Notebook commands

```bash
# Launch the notebook environment from the repository root.
jupyter lab
```

Run the numbered notebooks from top to bottom:

- `notebooks/01_data_audit_and_cleaning.ipynb`
- `notebooks/02_game_state_features.ipynb`
- `notebooks/03_historical_features.ipynb`
- `notebooks/04_model_training.ipynb`

The notebooks contain implementation, embedded validation results, and concise
Markdown explanations. See `docs/phase_01_data_audit.md` and
`docs/phase_02_game_state_features.md` for the phase records, and
`docs/feature_review.md` for feature decisions.

Phase 02 produces these ignored, reproducible files under `data/interim/`:

- `phase_02_female_innings_1.csv.gz`
- `phase_02_female_innings_2.csv.gz`
- `phase_02_male_innings_1.csv.gz`
- `phase_02_male_innings_2.csv.gz`

Phase 03 produces the corresponding `phase_03_*` files with the same delivery
rows and 23 appended historical predictors. See
`docs/phase_03_historical_features.md` for definitions and leakage controls.

Phase 04 writes ignored model artifacts under `models/`, state probabilities
under `data/processed/`, and the tracked performance record
`reports/metrics/phase_04_model_performance.json`. The complete feature/null
dictionary is `outputs/phase04/Model Feature Data Dictionary.xlsx`.

## Source material

- `docs/reference/Nett Win Contribution Project Overview.docx`
- `docs/reference/Data Dictionary.xlsx`
- `notebooks/legacy_feature_engineering.ipynb`

## Licence

Project code and data licensing are not yet declared. Do not make the repository public or redistribute the raw datasets until this is resolved.
