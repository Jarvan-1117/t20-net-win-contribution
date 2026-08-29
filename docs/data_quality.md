# Data Quality Register

Status: Phase 01 baseline implemented

Implemented controls:

- The empty delivery-level `date` is dropped; `match_date` comes from the match table via a validated many-to-one join.
- `source_row` is retained and is the only event-order key. Displayed `over`/`ball` is never used to sort a delivery stream.
- Innings are segmented from event-stream resets, then matches with other than two segments are excluded from the initial baseline.
- Ties, no-results, D/L matches, awarded matches, and records without a winner are excluded before the binary target is created.
- `is_wicket` is consumed as a boolean source field, not compared to the string `TRUE`.
- `match_winner`, `winning_outcome`, final first-innings total, `match_id`, and all post-match fields are audit/target inputs, not model predictors.

Known limitations that are intentionally deferred:

- Playing-XI information is absent, limiting exact remaining-batting-resource features.
- Player names are display strings rather than stable player identifiers.
- Venue-country and home-ground mappings in the legacy notebook are manual and incomplete.
- D/L, ties, super overs, and non-standard matches need a dedicated target and attribution policy before they can enter production.

All future cleaning stages should publish row counts, exclusion counts, null checks, range checks, and reconciliation results.
