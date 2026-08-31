# 0005: Historical-feature timing and identity

Status: Proposed

## Decision

Construct player, team, and venue histories from matches dated strictly before
the current match. Treat all matches on the same calendar date as simultaneous.
Use exact source player display names within gender until an approved stable-ID
source exists. Preserve zero exposure counts and null undefined rates rather
than applying a full-data fallback.

## Consequences

No match can update itself or another same-date match. Player histories may
contain unresolved name collisions, documented through a multi-team-name
diagnostic. Phase 04 must fit any rate fallback or encoding on training data
only. Playing-XI and remaining-player resource features remain unavailable.
