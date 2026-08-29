# Phase 01: data audit and cleaning baseline

## What this phase does

This phase establishes a trustworthy, reproducible input stream for later
feature engineering and win-probability modelling. It does not train a model,
write to either raw CSV, or declare the final NWC attribution rule.

The source files are joined on `match_id`: the match table supplies the
authoritative `match_date` and `gender`; the delivery table supplies the
event-level cricket state. The delivery `date` column is entirely null in the
current extract, so it is not used.

Run the audit from the repository root:

```bash
PYTHONPATH=src python -m nwc.pipelines.audit_raw_data
```

The command writes a compact, version-controlled report at
`reports/metrics/phase_01_raw_data_audit.json`. It does not create a cleaned
CSV or Parquet file: derived data should only be materialised after the
feature contract is approved.

## Evidence from the current extract

| Check | Result | Interpretation |
|---|---:|---|
| Match rows | 5,602 | One row per `match_id`; no duplicate IDs. |
| Delivery rows | 1,266,835 | All delivery IDs join to a match and every match has deliveries. |
| Coverage | 2005-02-17 to 2026-08-04 | Chronological splits must be made by match, never by delivery. |
| Duplicate displayed `over`/`ball` rows | 124,994 rows participating | Illegal deliveries reuse a displayed coordinate, so coordinate sorting is unsafe. |
| `runs_total = runs_batter + runs_extras` failures | 0 | The accounting identity passes in the source. |
| Wicket flag vs `player_out` failures | 0 | The two representations agree in the source. |
| Overlong legal-ball innings | 41 matches | The extract records 121-122 legal balls; this violates the 120-ball T20 limit. |
| Eligible initial-baseline matches | 5,212 | Standard two-innings matches with a binary winner and no overlong innings. |

The report contains the exact machine-generated counts. It is the audit
record; this page explains why each rule exists.

## Cleaning rules and their rationale

1. **Preserve source order.** A wide or no-ball is followed by a rebowled
   delivery that can share the same `over` and `ball`. Sorting those fields
   scrambles the causal sequence, corrupting cumulative scores, legal-ball
   clocks, rolling windows, and any future NWC delta. `source_row` is attached
   at ingestion and becomes the event-order key.

2. **Infer innings from stream boundaries, not the toss.** The old notebook
   treated the toss winner/decision as the innings identifier. This is an
   indirect proxy and does not robustly isolate super overs. The baseline
   begins a segment when the batting team changes, or the event stream resets
   its score, wickets, or displayed coordinates. Only matches with exactly two
   segments are eligible for the initial two-innings model.

3. **Exclude non-binary or altered targets.** No-results and ties have no
   binary winner. D/L matches use a revised target, so the simple
   `first_innings_score + 1` chase rule is wrong. Awarded matches lack a normal
   on-field endpoint. Super-over matches add extra innings and need a separate
   terminal-state and attribution policy. These are exclusions, not data
   errors, and are recorded with a mutually exclusive reason.

4. **Define legal balls from extras.** A delivery is legal only when both
   `wides == 0` and `noballs == 0`. The legal-ball clock is calculated within
   the inferred innings and includes the current delivery, matching the
   project's chosen post-delivery model timestamp. Any match containing an
   innings above 120 legal balls is excluded rather than silently capped: the
   source has 41 such matches, with 121-122 counted legal deliveries.

5. **Keep outcome columns out of predictors.** `match_winner` and
   `winning_outcome` define the target/exclusions; `match_id` is a split and
   audit key. They would leak the answer if placed in model features. The final
   first-innings score is available only as the chase target in innings two.

6. **Do not silently impose the legacy top-11 filter.** That filter leaves
   1,655 baseline-eligible matches versus 5,212 when all eligible T20Is are
   kept. It may be useful as a sensitivity analysis, but it is not justified
   as the default project population. The cleaning function exposes it as an
   explicit option.

## Output contract for the next phase

`clean_baseline()` returns one row per recorded delivery, still in source
order, with these auditable fields added:

- `match_date`, `gender`, `source_row`
- `innings_segment`, `event_sequence`, `match_innings`
- `legal_delivery`, `cumulative_innings_legal_balls`,
  `legal_deliveries_remaining`, `powerplay`, `is_terminal_delivery`
- second-innings-only `first_innings_score`, `runs_to_win`,
  `required_run_rate`, and `run_rate_differential`
- `batting_team_win_match`

These columns describe post-delivery state. The feature policy in
[`feature_review.md`](feature_review.md) decides which may be predictors and
which remain audit-only.
