# Net Win Contribution

T20 international cricket ball-by-ball win-probability and player contribution project.

## Current status

Phase 01 is complete: raw-data audit, source-order innings segmentation, and a
baseline cleaning contract are implemented. No win-probability or NWC model has
been trained yet.

## Intended workflow

1. Define the modelling timestamp, match exclusions, team scope, and NWC attribution policy.
2. Validate and clean match and delivery data. **Completed for the initial baseline.**
3. Build leakage-safe game-state and historical player/team features.
4. Train and calibrate separate models by gender and innings.
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
notebooks/          Exploration only; reusable logic belongs under src/
reports/            Metrics, figures, and model cards
src/nwc/            Future production package
tests/              Unit, integration, and small synthetic fixtures
```

## Data policy

The raw CSV files are intentionally excluded from normal Git history. Their hashes are recorded in `data/raw/manifest.sha256`. Before configuring a shared data remote, confirm the source dataset's redistribution licence.

The preferred future setup is Git for code and small metadata, plus DVC for datasets, derived tables, and trained models.

## Environment

The project will use Python 3.12 and `uv` with `pyproject.toml` and a committed `uv.lock`. The current machine did not have `uv` or DVC installed when this scaffold was created, so no lockfile or DVC metadata has been fabricated.

## Phase-01 commands

```bash
# Audit raw data without changing either source CSV.
PYTHONPATH=src python -m nwc.pipelines.audit_raw_data

# Run the standard-library unit tests.
PYTHONPATH=src python -m unittest discover -s tests -v
```

See `docs/phase_01_data_audit.md` for the cleaning rules and
`docs/feature_review.md` for the feature decisions.

## Source material

- `docs/reference/Nett Win Contribution Project Overview.docx`
- `docs/reference/Data Dictionary.xlsx`
- `notebooks/legacy_feature_engineering.ipynb`

## Licence

Project code and data licensing are not yet declared. Do not make the repository public or redistribute the raw datasets until this is resolved.
