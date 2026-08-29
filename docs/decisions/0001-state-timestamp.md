# 0001: Model state timestamp

Status: Proposed

## Decision

Represent each model row as the match state immediately after the recorded delivery. Add an explicit pre-innings state so the first delivery also has a prior win probability.

## Consequences

All cumulative state and rolling-window features must use the same timestamp. Current-delivery event fields remain available for audit and attribution but are not automatically model predictors.

