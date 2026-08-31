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

The Phase-01 notebook retains the valid game-state concepts but replaces those
unsafe implementation details.

## Feature decisions for the first model baseline

| Field or feature | Decision | Reason |
|---|---|---|
| `innings_score`, `innings_wickets` | Keep | Direct post-delivery game state; available in both innings. |
| Legal balls elapsed / remaining | Keep | More reliable innings clock than displayed ball coordinates. |
| `powerplay` | Keep | Known at the delivery timestamp and captures rule-based field restrictions. |
| `target_runs`, `runs_to_win` | Keep only in innings 2 | Defines the chase; these columns are absent, not merely null, in first-innings outputs. |
| Current and required run rate | Derive with guards | Useful state summaries; must be null at zero legal balls and outside active chases. |
| Recent runs/wickets | Keep | Previous 10 recorded events, calculated in source order with `shift(1)`; the current event is excluded. |
| Striker, non-striker, bowler | Keep historical summaries | Phase 03 adds strictly prior-date rates and exposure counts using exact display names within gender. Raw names remain audit/join fields, not predictors. |
| Batting/bowling resource quality | Defer | Playing XI is absent, so exact players remaining cannot be inferred safely. Historical statistics require chronological feature generation. |
| Venue | Keep historical context only | Phase 03 adds prior batting-side win rate grouped by gender, venue, and innings; raw venue remains audit-only pending a train-only encoding policy. |
| `venue_country`, home-ground flag | Remove for now | Legacy mapping is manual and the current home-ground definition uses team rather than player evidence. |
| Toss winner/decision | Exclude from first baseline | It is pre-match and potentially useful later, but it does not replace innings identification and needs a pre-match feature policy. |
| `match_winner`, `winning_outcome` | Target/audit only | Direct outcome leakage. |
| `match_id`, source row, terminal flag | Grouping/audit only | Identifiers reveal source structure rather than cricket state. |
| Current delivery runs/extras/wicket fields | Audit/NWC attribution only | At a post-delivery timestamp they may be valid descriptive state, but including them would make a first baseline hard to interpret and can double-count state changes. |

## Leakage rules for Phases 02 and 03

- Any player, team, venue, or competition statistic must be fitted/calculated
  using matches dated strictly before the current match. Rows from the same
  match cannot update their own historical features.
- Phase 04 creates chronological train/validation/test splits at `match_id`
  level, with equal calendar dates kept together; no match appears in more than
  one split.
- The first model will be trained separately by gender and innings. A feature
  defined only for a chase is physically absent from first-innings schemas.
- Feature availability must match a post-delivery timestamp. The prior
  probability used by NWC is obtained from the previous state (plus an explicit
  pre-innings state), not by peeking at the future delivery.

## Phase 03 historical baseline

The baseline adds 23 predictors: six batting-history fields for the striker,
six for the non-striker, five bowling-history fields for the current bowler,
two fields for each team, and two venue/innings fields. Counts describe prior
exposure; rates remain null where a prior denominator does not exist.

Player history crosses innings but is separated by gender. Team history also
crosses innings. Venue history is grouped by gender, venue, and innings. All
matches on a calendar date are aggregated only after features for that date
have been assigned, so same-date matches cannot see one another.

## Next decision gates

Before implementing remaining-batting-resource or identity-resolved player
features, agree whether an external playing-XI/player-ID dataset is in scope.
Before calculating NWC, agree how run-outs, byes, leg-byes, penalties, and
fielding events are attributed and publish a reconciliation rule.
