# Notebooks

Notebooks are the primary implementation and communication format for this
project. Each numbered notebook should be runnable from top to bottom, combine
Markdown explanations with code, embed its key results, and state its inputs,
assumptions, checks, and outputs.

Phases 01 through 04 embed reproducible visual checks for match retention,
innings-specific feature availability, historical timing/nulls, and
candidate-model selection and interpretation.

Planned sequence:

- `01_data_audit_and_cleaning.ipynb`: source audit, innings segmentation, baseline exclusions, and the cleaned interim delivery stream.
- `02_game_state_features.ipynb`: leakage-safe delivery-state features; writes four ignored interim tables split by gender and innings.
- `03_historical_features.ipynb`: strictly prior-date player, team, and venue histories; implemented and verified.
- `04_model_training.ipynb`: date-grouped chronological splits; ordered naïve, logistic-regression, and random-forest comparison; validation selection and test log-loss evaluation; implemented and verified.
- `05_nwc_attribution.ipynb`: implemented baseline striker-bowler probability deltas, zero-sum reconciliation, and untouched-test player rankings.

Use `src/nwc/` only for small, stable helpers that are shared by multiple
notebooks. Do not maintain a parallel Python pipeline for logic owned by one
notebook.

`legacy_feature_engineering.ipynb` is retained as source material and should not be treated as the production pipeline.

Phase 02 deliberately does not add train/validation/test labels. Phase 04
creates them at whole-match level while keeping every match played on the same
calendar date in one split.

Phase 03 treats all same-date matches as simultaneous. It preserves all Phase
02 rows and columns, then appends 23 historical predictors to each track.

Phase 04 adds one pre-innings state per match/track, fits preprocessing on
training only, compares the naïve baseline, logistic regression, and random
forest in that order, selects by validation log loss, and reports log loss only.

Phase 05 uses the selected Logistic Regression probability after each recorded
event. Within an innings, the striker receives its change from the preceding
state and the bowler its negative. It does not attribute the innings boundary
or unobserved fielding actions; test-split player summaries are the primary
reporting output.
