# Methodology

This is the authoritative technical summary for Phases 01–05. Implementation,
cell-level commentary, and executed outputs remain in the numbered notebooks.

## 1. Objective and modelling structure

The model estimates a selected team's probability of winning after every
recorded delivery in a T20 international. Successive changes in that probability
are then assigned to the participating striker and bowler as Net Win
Contribution (NWC).

Four independent modelling tracks are used:

- female, first innings;
- female, second innings;
- male, first innings;
- male, second innings.

Keeping these datasets and models separate allows innings-specific relationships
without leaking chase information into first-innings observations.

## 2. Data audit and event order

Match and delivery sources are joined by `match_id`. The retained `source_row`
defines event order because displayed over/ball labels are not unique for every
recorded event. Innings are reconstructed from this ordered stream.

The baseline excludes D/L-affected matches, ties, no-results, awarded matches,
super overs, missing or inconsistent winners, innings longer than 120 legal
deliveries, and terminal states inconsistent with the match record. This leaves
4,975 eligible matches and 1,156,215 recorded events from 5,602 source matches.

## 3. Game-state features

Each row represents the state immediately after a recorded event. Core features
include cumulative runs and wickets, legal deliveries completed and remaining,
current run rate, innings phase, and runs/wickets from the previous ten recorded
events. A synthetic pre-innings state supplies the probability immediately
before the first event.

Second-innings-only features include target score, runs required, required run
rate, current-minus-required run-rate difference, and target progress. These
columns are physically absent from both first-innings tables.

## 4. Historical features and leakage controls

Phase 03 appends 25 player, team, and venue predictors. They cover prior batting
exposure and rates for the striker and non-striker, prior bowling economy,
strike and dot-ball rates, team win history, venue history, and exponentially
weighted recent team form.

All history is calculated using matches with dates strictly earlier than the
current match. Matches on the same date are treated as simultaneous and cannot
update one another. Recent team form uses a 10-match half-life. Undefined rates
for unseen players, teams, or venues remain null until model preprocessing.

`batting_team` and `bowling_team` are also included as categorical predictors.
Their encoding is learned from the training split only; unknown later teams are
handled without inspecting validation or test data.

## 5. Training and model selection

Complete matches and complete date groups are kept together in chronological
70%/15%/15% train, validation, and test partitions. Numeric median imputation,
missing-value indicators, scaling where applicable, and categorical one-hot
encoding are fitted only on training data.

Models are evaluated in this order:

1. naïve training-prevalence baseline;
2. L2 logistic regression;
3. random forest.

Log loss is the sole selection metric. The lowest validation log loss selects
the final model; the test split is used once for reporting, not for selection.
Random forest is selected in all four tracks. Each track independently compares
the same eight RF configurations across three expanding chronological validation
windows (55–65%, 65–75%, and 75–85% of match history). All four select 500 trees
and `max_features=0.25`, while retaining `max_depth=14` and
`min_samples_leaf=50`. Test periods are excluded until after parameter lock.

| Track | Test naïve | Test logistic | Test random forest |
|---|---:|---:|---:|
| Female innings 1 | 0.691459 | 0.691732 | **0.510914** |
| Female innings 2 | 0.675578 | 0.344246 | **0.273831** |
| Male innings 1 | 0.693698 | 0.754022 | **0.495486** |
| Male innings 2 | 0.688326 | 0.425597 | **0.292898** |

The modelling feature workbook records every included feature, its definition,
observed null count, and preprocessing treatment.

## 6. NWC attribution

Within an innings, let the selected batting side's probability after event
\(d\) be \(W_d\). Delivery contribution is

\[
\Delta W_d = W_d - W_{d-1}.
\]

The striker receives `+ΔW` as batting NWC and the bowler receives `−ΔW` as
bowling NWC. The first event is compared with its synthetic pre-innings state.
The innings break is not attributed. The first-innings endpoint retains the
model probability; the final second-innings state is anchored to the known
binary result.

All recorded events, including wides, no-balls, byes, leg-byes, penalties, and
dismissals, follow the same striker–bowler interaction rule. Aggregations are
produced by delivery, player-match, season, and career. Primary rankings use the
untouched test split.

The attribution reconciles numerically: each striker–bowler event pair sums to
zero, the maximum player-total mismatch within a match is approximately
`3.61e-16`, and the maximum innings telescoping error is approximately
`2.22e-16`.

## 7. Interpretation and limitations

The plotted values are model-generated conditional win probabilities, not a
descriptive percentage calculated directly from the current match. Team
identity, historical win rates, recent form, and live state jointly determine
the starting and subsequent probabilities; they therefore need not begin at
50%.

NWC is a model-dependent interaction attribution, not a causal estimate. The
source data does not identify catchers or all run-out fielders, so this version
does not separately allocate fielding contribution. Calibration and temporal
stability should be monitored when the model is extended to new seasons or
competitions.
