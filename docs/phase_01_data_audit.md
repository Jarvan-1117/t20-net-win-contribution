# Phase 01: data audit and cleaning baseline

## What this phase does

This phase establishes a trustworthy, reproducible input stream for later
feature engineering and win-probability modelling. It does not train a model,
write to either raw CSV, or declare the final NWC attribution rule.

The source files are joined on `match_id`: the match table supplies the
authoritative `match_date` and `gender`; the delivery table supplies the
event-level cricket state. The delivery `date` column is entirely null in the
current extract, so it is not used.

Open and run the notebook from the repository root:

```bash
jupyter lab
```

Run `notebooks/01_data_audit_and_cleaning.ipynb` from top to bottom. It writes
a compact, version-controlled report at
`reports/metrics/phase_01_raw_data_audit.json` and the ignored, reproducible
cleaned stream `data/interim/phase_01_cleaned_deliveries.csv.gz`.

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
| Incomplete two-innings terminal structures | 481 matches | These require explicit treatment; 233 become the mutually exclusive baseline exclusion reason. |
| Post-target delivery streams | 14 matches | Most are already excluded for an earlier reason; 2 receive this baseline reason. |
| Winner/target contradictions | 81 matches | Most are already D/L, no-result, or otherwise excluded. |
| Eligible initial-baseline matches | 4,975 | Standard, internally consistent two-innings matches with a binary winner. |
| Eligible delivery rows | 1,156,215 | One row per preserved recorded event. |

The report contains the exact machine-generated counts. It is the audit
record; this page explains why each rule exists.

The mutually exclusive eligibility result reconciles all 5,602 matches:

| Reason | Matches |
|---|---:|
| Included | 4,975 |
| Incomplete innings | 233 |
| D/L | 182 |
| No result | 112 |
| Tie | 51 |
| Overlong legal-ball innings | 41 |
| Awarded | 4 |
| Wicket-accounting mismatch | 2 |
| Deliveries after target | 2 |

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

5. **Require a coherent terminal state.** Each innings must end through a
   normal 120-ball, all-out, chase-complete, or recorded stream endpoint that
   is consistent with the available source state. Cumulative score and wicket
   changes are reconciled against event fields. Suspect matches are excluded,
   not repaired or truncated.

6. **Keep outcome columns out of predictors.** `match_winner` and
   `winning_outcome` define the target/exclusions; `match_id` is a split and
   audit key. They would leak the answer if placed in model features. The final
   first-innings score is available only as the chase target in innings two.

7. **Do not silently impose the legacy top-11 filter.** All 4,975 otherwise
   eligible T20Is are kept. The legacy selection remains a labelled sensitivity
   analysis rather than the default project population.

## Output contract for the next phase

The notebook's cleaned file contains one row per recorded delivery, still in
source order, with 40 source and audit fields. Important derived audit fields
include:

- `match_date`, `gender`, `source_row`
- `innings_segment`, `event_sequence`, `match_innings`
- `legal_delivery`, `cumulative_innings_legal_balls`,
  `innings_score`, `innings_wickets`, and `is_terminal_delivery`
- `batting_team_win_match`

Phase 01 intentionally does not create chase or model feature columns. Phase 02
adds those under innings-specific schemas. Raw event fields are retained for
audit, Phase 03 histories, and later NWC attribution.
