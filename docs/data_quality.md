# Data Quality Register

Status: Phases 01 through 04 implemented and rerun

Implemented controls:

- The empty delivery-level `date` is dropped; `match_date` comes from the match table via a validated many-to-one join.
- `source_row` is retained and is the only event-order key. Displayed `over`/`ball` is never used to sort a delivery stream.
- Innings are segmented from event-stream resets, then matches with other than two segments are excluded from the initial baseline.
- Ties, no-results, D/L matches, awarded matches, and records without a winner are excluded before the binary target is created.
- Two-innings matches with incomplete terminal states, cumulative wicket-accounting failures, post-target events, or winner/target contradictions are excluded with explicit reason codes.
- Innings above 120 counted legal deliveries are excluded, never clipped.
- `is_wicket` is consumed as a boolean source field, not compared to the string `TRUE`.
- `match_winner`, `winning_outcome`, `match_id`, and current-event fields are retained only for audit, targets, grouping, or later NWC attribution.
- Phase 02 writes four physical tables. First-innings headers contain no target, runs-to-win, required-run-rate, run-rate-difference, or target-progress fields.
- Chase rates are guarded at completed states; target progress is bounded to `[0, 1]`; opening wides/no-balls remain in the powerplay.
- Recent form uses the previous 10 recorded source events and excludes the current event.
- Player, team, and venue histories use only matches dated strictly before the
  current match. All same-date matches receive the same pre-date history.
- Phase 03 preserves Phase 02 columns and rows exactly, then appends 23
  historical predictors. Exposure counts are zero for unseen entities;
  undefined rates remain null for Phase 04 train-only imputation.
- Player identity remains the exact source display name within gender. The
  audit found 95 display names associated with more than one batting team;
  these are flagged but not guessed into separate or merged identities.
- Phase 04 splits whole matches chronologically at indivisible calendar-date
  groups. Both innings for one gender share the same cutoff dates.
- One explicit pre-innings state is added per match and innings track.
- Median imputation and missingness indicators are fitted independently on
  each candidate's training split. Logistic-regression standardisation is also
  fitted on training only. Validation labels select among the naïve baseline,
  logistic regression, and random forest; test labels are reserved for final
  log-loss evaluation.
- Serialized state probabilities have unique headers, one bounded probability
  for each candidate, the selected probability, and exactly one pre-innings
  state per match.

Current verified baseline: 4,975 matches and 1,156,215 delivery rows (1,871
female matches; 3,104 male matches). Phase 01 records all raw and exclusion
counts in `reports/metrics/phase_01_raw_data_audit.json`; Phase 02 records each
track's schema and checks in `reports/metrics/phase_02_game_state_features.json`.
Phase 03 definitions, null counts, exposure counts, and leakage checks are in
`reports/metrics/phase_03_historical_features.json`.
Phase 04 split, preprocessing, candidate-model, selection, probability, and log-loss checks
are in `reports/metrics/phase_04_model_performance.json`.

Known limitations that are intentionally deferred:

- Playing-XI information is absent, limiting exact remaining-batting-resource features.
- Player names are display strings rather than stable player identifiers.
- Venue-country and home-ground mappings in the legacy notebook are manual and incomplete.
- D/L, ties, super overs, and non-standard matches need a dedicated target and attribution policy before they can enter production.
- Phase 05 attribution still requires an accepted rule for non-bowler/non-striker events and reconciliation.

All future cleaning stages should publish row counts, exclusion counts, null checks, range checks, and reconciliation results.
