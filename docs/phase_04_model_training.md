# Phase 04 Candidate Model Training

Status: Implemented and verified

## Instructor requirements

Phase 04 follows the Project Overview and the instructor's explicit advice:

- publish a description and null-handling record for every model predictor;
- assess performance using log loss only;
- compare a simple logistic regression with a more complex model;
- use a random forest instead of a histogram-based tree model.

The feature record is `outputs/phase04/Model Feature Data Dictionary.xlsx`.
It distinguishes fields absent from an innings schema from fields that exist
but contain undefined values.

## Split and state construction

Each gender is split chronologically by whole match, using the nearest complete
calendar-date groups to 70% training, 15% validation, and 15% test. Equal-date
matches cannot cross a boundary, and both innings for one gender share cutoffs.

Female cutoffs are 2025-05-05 and 2025-12-19. Male cutoffs are 2024-11-08 and
2025-10-09. The following dates begin the untouched test periods: 2025-12-21
for female matches and 2025-10-10 for male matches.

One synthetic pre-innings state is added to every match/innings track with
`state_sequence = 0`. Its game-state features represent 0 runs, 0 wickets, 120
legal balls remaining, powerplay active, and no recent events. Historical
features are copied from the first delivery because they are constant within a
match date. Second-innings target features are known before the chase begins.

## Missing values

Every track uses `SimpleImputer(strategy="median", add_indicator=True)`. The
imputer is fitted only on training states. Undefined current run rate, inactive
chase rates, and history rates without a prior denominator therefore receive a
training-derived median plus a training-derived missing indicator. Features
without source nulls remain unchanged. Chase features are absent rather than
imputed in first-innings models.

## Candidate models and selection

Candidates are evaluated in this fixed order for every track:

1. a constant naïve probability equal to the training outcome prevalence;
2. an L2-regularised `LogisticRegression` with train-only median imputation,
   missingness indicators, and standardisation;
3. a 200-tree `RandomForestClassifier` with `criterion="log_loss"`, maximum
   depth 14, minimum leaf size 50, square-root feature sampling, and an 80%
   bootstrap sample.

The lowest validation log loss selects the model before test probabilities are
calculated. No separate sigmoid calibration layer is used.

## Validation selection and held-out log loss

Lower values are better. No secondary performance metric is reported.

| Track | Features | Validation naïve | Validation LR | Validation RF | Selected |
|---|---:|---:|---:|---:|---|
| Female innings 1 | 34 | 0.691843 | 0.474017 | 0.489916 | Logistic regression |
| Female innings 2 | 39 | 0.676610 | 0.276118 | 0.284959 | Logistic regression |
| Male innings 1 | 34 | 0.692507 | 0.545300 | 0.566286 | Logistic regression |
| Male innings 2 | 39 | 0.693337 | 0.290637 | 0.318152 | Logistic regression |

| Track | Test naïve | Test LR | Test RF | Selected test log loss |
|---|---:|---:|---:|---:|
| Female innings 1 | 0.691459 | 0.505404 | 0.509349 | 0.505404 |
| Female innings 2 | 0.675578 | 0.271658 | 0.281555 | 0.271658 |
| Male innings 1 | 0.693698 | 0.501076 | 0.509687 | 0.501076 |
| Male innings 2 | 0.688326 | 0.285912 | 0.297197 | 0.285912 |

Logistic regression has the lowest validation log loss in all four tracks and
is therefore selected in all four. It also has the lowest test log loss in all
four, although test results were not used to revise the selection.

## Outputs and verification

The executed implementation is `notebooks/04_model_training.ipynb`. Model
artifacts are ignored under `models/`; state probabilities are ignored under
`data/processed/`; compact results are tracked at
`reports/metrics/phase_04_model_performance.json`.

Independent verification reloads both trained pipelines and each selected-model
record, confirms estimator classes and configuration, reconstructs training-only
preprocessing, checks match/date isolation, recomputes every log loss from
serialized probabilities, and reproduces candidate and selected probabilities.
