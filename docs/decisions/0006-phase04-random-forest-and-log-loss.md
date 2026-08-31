# 0006: Phase 04 candidate models and evaluation metric

Status: Accepted

## Context

The project overview says to begin with a simple logistic regression, then try
a more complex machine-learning architecture and select using log loss. The
course instructor additionally requested a model-feature data dictionary with
null-value handling, log loss as the only performance metric for the current
phase, and a random forest instead of the previously considered histogram-based
tree model.

## Decision

For each gender/innings track, evaluate candidates in this documented order:

1. the training-outcome prevalence as a constant naïve baseline;
2. a standalone `LogisticRegression` model;
3. a `RandomForestClassifier` as the more complex model.

Use validation log loss as the sole selection criterion. Lock the selected
candidate before evaluating the untouched test period. Report test log loss for
all three candidates for transparent comparison, but do not use it to change
the selection. Do not report accuracy, Brier score, AUC, or other secondary
metrics in Phase 04.

Fit median imputation and missing-value indicators independently within each
trained pipeline using the training split only. Standardise the imputed inputs
inside the logistic-regression pipeline using training statistics. Do not add a
separate sigmoid calibrator in this comparison: logistic regression is a model
candidate, not a random-forest calibration layer.

Publish a model-feature data dictionary containing definitions, track
availability, null counts, null causes, and Phase 04 handling.

## Consequences

Chronological whole-match and equal-date split isolation remains mandatory.
Both trained pipelines, the selected-model artifact, training prevalence,
feature list, and split dates must be stored for reproducibility. Additional
performance metrics can be added only in a later reviewed phase.
