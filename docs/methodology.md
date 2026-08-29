# Methodology

Status: Draft

## Objective

Estimate the batting team's calibrated probability of winning after each delivery, then use successive probability changes to derive player-level Net Win Contribution.

## Proposed modelling units

- One post-delivery state per recorded event.
- One synthetic pre-innings state for the initial probability.
- Separate models by gender and match innings.
- Chronological validation with entire matches kept within one split.

## Pending decisions

- Final team and competition scope.
- Playing-XI source and remaining-resource methodology.
- Treatment of DLS, ties, no-results, and super overs beyond the initial exclusions.
- Attribution of run-outs, byes, leg-byes, penalties, and fielding events.
- Definition of model endpoints and terminal probabilities.

