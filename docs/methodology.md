# Methodology

Status: Draft

## Objective

Estimate the batting team's calibrated probability of winning after each delivery, then use successive probability changes to derive player-level Net Win Contribution.

## Proposed modelling units

- One post-delivery state per recorded event.
- One synthetic pre-innings state for the initial probability.
- Separate models by gender and match innings.
- Chronological validation with entire matches and equal-date match groups kept within one split.

## NWC attribution

Phase 05 implements the approved baseline striker-bowler interaction. Within
an innings, the striker receives the selected batting-side probability change
from one recorded event to the next and the bowler receives its negative. The
first event uses the explicit pre-innings state. The innings boundary is not
attributed, and terminal probabilities are not overridden. Main player
rankings are limited to the untouched test split. See ADR 0003 and
`docs/phase_05_nwc_attribution.md`.

## Remaining decisions

- Final team and competition scope.
- Playing-XI source and remaining-resource methodology.
- Treatment of DLS, ties, no-results, and super overs beyond the initial exclusions.
- Definition of model endpoints and terminal probabilities.

Phase 01 currently yields 4,975 eligible matches. Phase 02 materialises four
gender-by-innings tracks and excludes chase-only fields from both first-innings
schemas. Phase 03 adds strictly prior-date player, team, and venue histories;
same-date matches are simultaneous and undefined rates remain null. The
Phase 04 compares, in order, a training-prevalence naïve baseline, standalone
logistic regression, and random forest. It adds synthetic pre-innings states,
chronological 70/15/15 date-group splits, training-only preprocessing, selection
by validation log loss, and untouched test evaluation. Logistic regression is
selected in all four tracks. Following instructor guidance, log loss is the
only Phase 04 performance metric.
