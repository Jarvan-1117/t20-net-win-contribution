# Phase 03 Historical Features

Status: Implemented and verified

## Purpose

Phase 03 adds leakage-safe historical context to each Phase 02 gender/innings
track. It preserves every Phase 02 row and column and appends 23 model
predictors. It does not infer a playing XI, resolve player identities, fit an
imputer or encoder, split data, train a model, or calculate NWC.

Run `notebooks/03_historical_features.ipynb` after Phases 01 and 02. The compact
execution record is `reports/metrics/phase_03_historical_features.json`.

## Temporal rule

Every history uses matches with `match_date` strictly earlier than the current
match date. Match-level contributions are aggregated by calendar date before
prior cumulative totals are assigned. Consequently:

- a match never updates its own predictors;
- another match on the same date cannot update the current match;
- every appearance of one entity on one date receives the same history;
- histories may use all earlier dates, including future Phase 04 training or
  test periods only when generating their own chronologically valid rows.

Phase 04 must still fit imputers, encoders, scalers, and models on training data
only.

## Historical predictors

For both striker and non-striker:

- prior batting matches and balls faced;
- prior strike rate and batting average;
- prior boundary-ball rate and dot-ball rate.

For the current bowler:

- prior bowling matches and legal balls;
- prior economy rate, bowling strike rate, and dot-ball rate.

For match context:

- prior matches and win rate for the batting team;
- prior matches and win rate for the bowling team;
- prior matches and batting-side win rate for the current gender, venue, and
  innings combination.

Batting balls are non-wide recorded events, including no-balls. Bowler runs
conceded exclude byes, leg-byes, and penalties. Run-outs, obstructing the
field, and hit-the-ball-twice dismissals are not credited to the bowler.

## Identity and fallback policy

Player identity is the exact source display name within gender. No external
player ID or playing-XI source is available. There are 95 exact display names
associated with more than one batting team; this diagnostic can include real
dual-national careers as well as unresolved collisions, so Phase 03 does not
guess a correction.

For a previously unseen entity, exposure counts are zero. A rate is null when
its prior denominator is zero—for example, batting average before a recorded
dismissal or bowling strike rate before a credited wicket. Phase 04 must choose
and fit any fallback using training data only.

## Outputs

| Track | Rows | Matches | Columns |
|---|---:|---:|---:|
| Female innings 1 | 235,716 | 1,871 | 63 |
| Female innings 2 | 200,554 | 1,871 | 68 |
| Male innings 1 | 382,777 | 3,104 | 63 |
| Male innings 2 | 337,168 | 3,104 | 68 |

The files are `data/interim/phase_03_<track>.csv.gz`. First-innings outputs
still contain no chase-only columns. All four outputs reconcile to 1,156,215
Phase 02 rows.

## Verification

The executed notebook verifies unique lookups, zero first-observation history,
valid ranges, preserved row order, unique serialized headers, and full row
reconciliation. A separate validation recomputed all 23 features for four
representative rows directly from the Phase 01 stream using only earlier dates,
confirmed same-date equality for every entity type, and proved that all Phase
02 columns are unchanged.
