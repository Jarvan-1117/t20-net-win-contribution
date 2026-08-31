# Configurations

This directory will contain reproducible configurations for the four primary model tracks:

- female innings 1
- female innings 2
- male innings 1
- male innings 2

Do not encode experimental assumptions only inside notebooks. Material settings should be represented here and reviewed through Git.

Project-wide baseline settings currently live in `params.yaml`, including the
all-team scope, explicit exclusion categories, a post-delivery state timestamp,
and the previous-10-recorded-events rolling window. Model-specific settings can
move into this directory when Phase 04 begins.

The `features.historical` section also records Phase 03 timing, identity,
undefined-rate, batting-ball, bowler-credit, and venue-grouping policies.

The `validation` and `model` sections now record Phase 04 split fractions,
equal-date isolation, log loss as the sole metric, the ordered naïve,
logistic-regression, and random-forest candidates, train-only preprocessing,
model hyperparameters, validation selection, and final test evaluation.
