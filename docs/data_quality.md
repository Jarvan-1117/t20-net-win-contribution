# Data Quality Register

Status: Initial audit

Known issues to resolve before modelling:

- The delivery-level date column is empty; use the match table date.
- Preserve original delivery order because over/ball coordinates repeat after wides and no-balls.
- Separate or exclude super-over segments before cumulative calculations.
- Exclude or explicitly model ties, no-results, awarded matches, and DLS targets.
- Parse `is_wicket` as a boolean rather than comparing it with the string `TRUE`.
- Remove final-result fields from predictors.
- Retain `match_id` as a grouping and audit key, not as a predictor.
- Playing-XI information is absent, limiting exact remaining-resource features.
- Player names are display strings rather than stable player identifiers.

All future cleaning stages should publish row counts, exclusion counts, null checks, range checks, and reconciliation results.

