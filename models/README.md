# Models

Trained model files are managed outside normal Git, preferably through DVC.
Phase 04 writes `logistic_regression_<track>.joblib` and
`random_forest_<track>.joblib` candidate artifacts plus
`selected_model_<track>.joblib` selection records. The candidate artifacts
contain training-fitted pipelines, ordered feature lists, split dates,
parameters, and the scikit-learn version. Small evaluation summaries belong
under `reports/`.
