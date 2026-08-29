# Raw data

This directory contains immutable source datasets used by the project.

Expected local files:

- `t20i_deliveries_data.csv`
- `t20i_matches_data.csv`

The CSV files are excluded from normal Git. Their SHA-256 hashes are recorded in `manifest.sha256` so collaborators can verify that they are using the same source version.

Do not edit raw files in place. Cleaning outputs belong in `data/interim/` or `data/processed/`.

