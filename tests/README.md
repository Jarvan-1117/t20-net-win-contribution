# Tests

The primary verification record is embedded in each numbered notebook. Every
notebook must include explicit assertions and printed/visual quality checks for
its important assumptions.

Phase 01 currently asserts joins, source ordering, exclusion reconciliation,
score/wicket accounting, terminal-state validity, and the serialized cleaned
file contract. Phase 02 asserts exact per-track headers, unique serialized
column names, four-way row reconciliation, no chase columns in first innings,
bounded chase features, powerplay handling for opening illegal events, and the
absence of forbidden predictors.

Phase 03 asserts date-batched history construction, zero prior exposure on an
entity's first observed date, unique entity/date lookups, preserved Phase 02
schemas and row order, valid rate ranges, exact serialized headers, and
four-track row reconciliation. An independent verification also directly
recomputes all 23 fields from Phase 01 for representative states and checks
same-date history equality across every track.

Phase 04 asserts whole-match and equal-date split isolation, shared gender
cutoffs, one pre-innings state per match/track, train-derived imputation
statistics, unique prediction headers, bounded probabilities, and serialized
row reconciliation. Independent verification reloads all four model artifacts,
proves they contain `RandomForestClassifier`, recomputes every reported log
loss from saved probabilities, reproduces sample predictions, and checks the
training medians directly.

When stable helpers are later extracted into `src/nwc/`, add small synthetic
tests here for legal-ball counting, delivery ordering, innings segmentation,
target construction, temporal leakage, split isolation, probability bounds,
and NWC reconciliation.
