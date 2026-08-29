# Feature review: baseline policy

This review separates four questions that are often mixed together: whether a
field is available at the chosen timestamp, whether it leaks the final result,
whether it is well-defined for both innings, and whether the current source
can support it without external assumptions.

## Legacy notebook: what survives and what changes

The notebook establishes useful cricket concepts, but it is not a production
pipeline. Its main technical risks are:

- it infers innings from toss data rather than the delivery stream;
- it sorts by `match_id`, innings, `over`, and `ball`, which reorders duplicate
  coordinates after wides/no-balls;
- it compares a boolean `is_wicket` column with the string `"TRUE"`, producing
  an all-zero wicket feature on this extract;
- it applies a silent top-11 team filter and omits Afghanistan without a stored
  project decision;
- it exports no reproducible file, audit report, schema check, or test;
- it leaves player-quality and venue mappings as prose/manual dictionaries,
  which cannot yet be validated or made leakage-safe.

The baseline code retains the valid game-state concepts but replaces those
unsafe implementation details.

## Feature decisions for the first model baseline

| Field or feature | Decision | Reason |
|---|---|---|
| `innings_score`, `innings_wickets` | Keep | Direct post-delivery game state; available in both innings. |
| Legal balls elapsed / remaining | Keep | More reliable innings clock than displayed ball coordinates. |
| `powerplay` | Keep | Known at the delivery timestamp and captures rule-based field restrictions. |
| `first_innings_score`, `runs_to_win` | Keep only in innings 2 | Defines the chase target; unavailable/meaningless in innings 1. |
| Current and required run rate | Derive with guards | Useful state summaries; must be null at zero legal balls and outside active chases. |
| Recent runs/wickets | Defer to Phase 02 | Retain only if calculated from prior events (`shift(1)`), in source order, with a written window policy. |
| Striker, non-striker, bowler | Audit now; historical features later | Raw names are useful event identities but must be transformed from strictly prior matches to avoid leakage. |
| Batting/bowling resource quality | Defer | Playing XI is absent, so exact players remaining cannot be inferred safely. Historical statistics require chronological feature generation. |
| Venue | Candidate, not baseline | High-cardinality; needs minimum-support/unknown-venue policy and temporal validation. |
| `venue_country`, home-ground flag | Remove for now | Legacy mapping is manual and the current home-ground definition uses team rather than player evidence. |
| Toss winner/decision | Exclude from first baseline | It is pre-match and potentially useful later, but it does not replace innings identification and needs a pre-match feature policy. |
| `match_winner`, `winning_outcome` | Target/audit only | Direct outcome leakage. |
| `match_id`, source row, terminal flag | Grouping/audit only | Identifiers reveal source structure rather than cricket state. |
| Current delivery runs/extras/wicket fields | Audit/NWC attribution only | At a post-delivery timestamp they may be valid descriptive state, but including them would make a first baseline hard to interpret and can double-count state changes. |

## Leakage rules for Phase 02

- Any player, team, venue, or competition statistic must be fitted/calculated
  using matches dated strictly before the current match. Rows from the same
  match cannot update their own historical features.
- Train/validation/test splits are chronological at `match_id` level. No match
  may appear in more than one split.
- The first model will be trained separately by gender and innings. A feature
  defined only for a chase is not imputed into first innings.
- Feature availability must match a post-delivery timestamp. The prior
  probability used by NWC is obtained from the previous state (plus an explicit
  pre-innings state), not by peeking at the future delivery.

## Next decision gates

Before implementing player-quality features, agree the player identity
resolution approach and whether an external playing-XI dataset is in scope.
Before calculating NWC, agree how run-outs, byes, leg-byes, penalties, and
fielding events are attributed and publish a reconciliation rule.
