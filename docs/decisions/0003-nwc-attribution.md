# 0003: NWC attribution

Status: Open

## Context

Assigning every batting-side probability change to the striker and its negative to the bowler is simple but misattributes run-outs, non-striker dismissals, byes, leg-byes, penalties, and fielding events.

## Decision required

Choose between a simple interaction metric and an expanded attribution system with batter, bowler, fielding, and residual components. The chosen system must publish reconciliation invariants.

