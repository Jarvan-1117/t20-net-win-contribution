# 0004: Delivery order and innings segmentation

Status: Accepted

## Decision

Treat raw delivery-file order as the authoritative within-match event order.
Attach `source_row` at ingestion and never sort an event stream by displayed
`over`/`ball`. Infer an innings segment when the batting team changes or when
the stream resets its score, wickets, or displayed coordinates.

## Evidence

The current extract has 124,994 rows participating in duplicate displayed
`match_id`/segment/`over`/`ball` coordinates. Examples include a no-ball or
wide followed by a rebowled delivery at the same coordinate.

## Consequences

Legal-ball clocks, rolling windows, cumulative state, terminal rows, and future
NWC probability deltas use `source_row`/`event_sequence`. Matches with other
than two inferred segments are excluded from the initial baseline and will be
revisited with a super-over policy.
