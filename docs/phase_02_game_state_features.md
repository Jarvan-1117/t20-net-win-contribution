# Phase 02 Game-State Features

Status: Implemented and verified

## Purpose

Phase 02 builds the first reusable post-delivery feature table for win-probability
modelling. It consumes the Phase 01 cleaned stream and writes four ignored,
reproducible tables split by gender and innings.

## Scope

Included in this phase:

- baseline-eligible matches from the Phase 01 exclusion policy;
- source-order event sequencing through `source_row` and `event_sequence`;
- score, wickets, legal-ball clock, resources remaining, and innings phase;
- second-innings chase features such as target, runs to win, required run rate,
  and target progress;
- prior-event rolling runs and wickets calculated with a shift before rolling;
- four physically separate schemas, so chase-only fields cannot enter a first-
  innings model accidentally.

Not included in this phase:

- player, team, venue, or competition historical strength;
- playing XI inference or player identity mapping;
- D/L, tie, no-result, awarded, or super-over modelling;
- final NWC attribution rules.
- train/validation/test labels; downstream Phase 04 creates date-grouped
  chronological splits while keeping whole matches and equal-date groups together.

## Feature Policy

Rows use the project-level post-delivery timestamp. Current cumulative state is
therefore valid after the delivery has happened, but raw current-event fields
such as `runs_total` and `is_wicket` are not included as model predictors. They
remain available for audit and future attribution.

Rolling features are `runs_prev_10_events` and `wickets_prev_10_events`. Their
window uses the previous 10 recorded events in source order, including illegal
events as positions, and excludes the current event. The first event of an
innings receives zero prior runs and wickets.

The first-innings files omit chase fields entirely. The second-innings files add
`target_runs`, `runs_to_win`, `required_run_rate`,
`run_rate_differential`, and `target_progress`. `runs_to_win` is clipped at
zero; rate fields are null when their denominator/state is undefined; target
progress is clipped to `[0, 1]`.

## Outputs

- `notebooks/02_game_state_features.ipynb`
- `reports/metrics/phase_02_game_state_features.json`
- `data/interim/phase_02_female_innings_1.csv.gz` — 235,716 rows, 1,871 matches, 40 columns
- `data/interim/phase_02_female_innings_2.csv.gz` — 200,554 rows, 1,871 matches, 45 columns
- `data/interim/phase_02_male_innings_1.csv.gz` — 382,777 rows, 3,104 matches, 40 columns
- `data/interim/phase_02_male_innings_2.csv.gz` — 337,168 rows, 3,104 matches, 45 columns

The four row counts reconcile exactly to the 1,156,215 Phase 01 rows. The
metrics file records each physical schema, model predictor list, match/date
coverage, outcome prevalence, null counts, and quality checks. Serialized
headers are unique; first innings has zero chase predictors; no match exceeds
120 legal balls; and all zero-legal-ball opening events are marked powerplay.
