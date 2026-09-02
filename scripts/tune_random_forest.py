"""Tune Random Forest shape parameters with expanding chronological windows.

The final 15% test period is excluded from every tuning fold. Run this script
from anywhere inside the repository, then copy each reported selected override
to ``params.yaml`` before executing the Phase 04 notebook.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


TRACK_NAMES = [
    "female_innings_1",
    "female_innings_2",
    "male_innings_1",
    "male_innings_2",
]
FOLD_FRACTIONS = [(0.55, 0.65), (0.65, 0.75), (0.75, 0.85)]
PARAMETER_GRID = [
    {"label": "current", "max_depth": 14, "min_samples_leaf": 50, "max_features": "sqrt"},
    {"label": "shallower", "max_depth": 10, "min_samples_leaf": 50, "max_features": "sqrt"},
    {"label": "deeper", "max_depth": 18, "min_samples_leaf": 50, "max_features": "sqrt"},
    {"label": "smaller_leaf", "max_depth": 14, "min_samples_leaf": 25, "max_features": "sqrt"},
    {"label": "larger_leaf", "max_depth": 14, "min_samples_leaf": 100, "max_features": "sqrt"},
    {"label": "features_025", "max_depth": 14, "min_samples_leaf": 50, "max_features": 0.25},
    {"label": "features_040", "max_depth": 14, "min_samples_leaf": 50, "max_features": 0.40},
    {"label": "deep_leaf25_f025", "max_depth": 18, "min_samples_leaf": 25, "max_features": 0.25},
]
STATE_AUDIT_COLUMNS = [
    "match_id",
    "match_date",
    "gender",
    "match_innings",
    "source_row",
    "event_sequence",
    "batting_team_win_match",
]


def locate_project_root() -> Path:
    candidates = (Path.cwd().resolve(), *Path.cwd().resolve().parents)
    root = next((path for path in candidates if (path / "params.yaml").exists()), None)
    if root is None:
        raise FileNotFoundError("Run this script from inside the project repository.")
    return root


def add_pre_innings_states(track: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Add the same explicit pre-innings state used by Phase 04."""
    deliveries = track[[*STATE_AUDIT_COLUMNS, *feature_columns]].copy()
    deliveries["state_sequence"] = deliveries["event_sequence"].astype("int64")
    pre = (
        deliveries.sort_values(["match_id", "source_row"], kind="stable")
        .groupby("match_id", as_index=False, sort=False)
        .head(1)
        .copy()
    )
    pre["source_row"] = pd.NA
    pre["event_sequence"] = 0
    pre["state_sequence"] = 0
    for column, value in {
        "innings_score": 0,
        "innings_wickets": 0,
        "wickets_remaining": 10,
        "cumulative_innings_legal_balls": 0,
        "legal_deliveries_remaining": 120,
        "current_run_rate": np.nan,
        "powerplay": 1,
        "middle_overs": 0,
        "death_overs": 0,
        "runs_prev_10_events": 0,
        "wickets_prev_10_events": 0,
    }.items():
        pre[column] = value
    if int(track["match_innings"].iloc[0]) == 2:
        pre["runs_to_win"] = pre["target_runs"]
        pre["required_run_rate"] = 6 * pre["target_runs"] / 120
        pre["run_rate_differential"] = np.nan
        pre["target_progress"] = 0.0
    return (
        pd.concat([pre, deliveries], ignore_index=True)
        .sort_values(["match_id", "state_sequence"], kind="stable")
        .reset_index(drop=True)
    )


def cutoff_date(track: pd.DataFrame, fraction: float) -> pd.Timestamp:
    matches = track[["match_id", "match_date"]].drop_duplicates()
    cumulative = matches.groupby("match_date").size().sort_index().cumsum()
    return cumulative.sub(len(matches) * fraction).abs().idxmin()


def make_preprocessor(numeric_columns: list[str], categorical_columns: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "numeric",
                SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
                numeric_columns,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_columns,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def tune_track(
    track_name: str,
    root: Path,
    phase_03_metrics: dict,
    forest_config: dict,
    screening_trees: int,
) -> dict:
    source = root / "data" / "interim" / f"phase_03_{track_name}.csv.gz"
    track = pd.read_csv(source, parse_dates=["match_date"], low_memory=False)
    feature_columns = phase_03_metrics["tracks"][track_name]["model_feature_columns"]
    categorical_columns = ["batting_team", "bowling_team"]
    numeric_columns = [column for column in feature_columns if column not in categorical_columns]
    states = add_pre_innings_states(track, feature_columns)

    fold_results: list[dict] = []
    candidate_losses = {candidate["label"]: [] for candidate in PARAMETER_GRID}
    for fold_number, (train_fraction, validation_fraction) in enumerate(FOLD_FRACTIONS, 1):
        train_end = cutoff_date(track, train_fraction)
        validation_end = cutoff_date(track, validation_fraction)
        train_mask = states["match_date"].le(train_end)
        validation_mask = states["match_date"].gt(train_end) & states["match_date"].le(
            validation_end
        )
        X_train = states.loc[train_mask, feature_columns]
        y_train = states.loc[train_mask, "batting_team_win_match"].astype("int8")
        X_validation = states.loc[validation_mask, feature_columns]
        y_validation = states.loc[validation_mask, "batting_team_win_match"].astype("int8")

        preprocessor = make_preprocessor(numeric_columns, categorical_columns)
        X_train_transformed = preprocessor.fit_transform(X_train)
        X_validation_transformed = preprocessor.transform(X_validation)
        fold_losses = {}
        for candidate in PARAMETER_GRID:
            parameters = {
                "n_estimators": screening_trees,
                "criterion": forest_config["criterion"],
                "max_depth": candidate["max_depth"],
                "min_samples_leaf": candidate["min_samples_leaf"],
                "max_features": candidate["max_features"],
                "max_samples": forest_config["max_samples"],
                "bootstrap": forest_config["bootstrap"],
                "n_jobs": forest_config["n_jobs"],
                "random_state": forest_config["random_state"],
            }
            model = RandomForestClassifier(**parameters)
            model.fit(X_train_transformed, y_train)
            probability = model.predict_proba(X_validation_transformed)[:, 1]
            loss = float(log_loss(y_validation, probability, labels=[0, 1]))
            candidate_losses[candidate["label"]].append(loss)
            fold_losses[candidate["label"]] = loss
        fold_results.append(
            {
                "name": f"fold_{fold_number}",
                "train_fraction_end": train_fraction,
                "validation_fraction_end": validation_fraction,
                "train_end": train_end.date().isoformat(),
                "validation_end": validation_end.date().isoformat(),
                "train_states": int(train_mask.sum()),
                "validation_states": int(validation_mask.sum()),
                "candidate_log_loss": fold_losses,
            }
        )
        print(f"{track_name} fold {fold_number}/3 complete", flush=True)

    screen = []
    for candidate in PARAMETER_GRID:
        losses = candidate_losses[candidate["label"]]
        screen.append(
            {
                **candidate,
                "max_samples": forest_config["max_samples"],
                "fold_log_loss": losses,
                "mean_validation_log_loss": float(np.mean(losses)),
                "std_validation_log_loss": float(np.std(losses)),
            }
        )
    screen.sort(key=lambda result: result["mean_validation_log_loss"])
    winner = screen[0]
    override = {
        "n_estimators": 500,
        "max_depth": winner["max_depth"],
        "min_samples_leaf": winner["min_samples_leaf"],
        "max_features": winner["max_features"],
    }
    return {
        "track": track_name,
        "folds": fold_results,
        "random_forest_screen": screen,
        "selected_label": winner["label"],
        "selected_override": override,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trees", type=int, default=200, help="Trees per screening fit")
    parser.add_argument("--track", choices=["all", *TRACK_NAMES], default="all")
    args = parser.parse_args()

    root = locate_project_root()
    params = yaml.safe_load((root / "params.yaml").read_text())
    forest_config = params["model"]["random_forest"]
    phase_03_metrics = json.loads(
        (root / "reports" / "metrics" / "phase_03_historical_features.json").read_text()
    )
    selected_tracks = TRACK_NAMES if args.track == "all" else [args.track]
    output = root / "reports" / "metrics" / "phase_04_rf_tuning.json"
    report = {
        "report_version": 2,
        "selection_policy": (
            "lowest mean log loss across three expanding chronological validation windows"
        ),
        "fold_fraction_ends": FOLD_FRACTIONS,
        "test_not_used_until_after_parameter_lock": True,
        "screening_n_estimators": args.trees,
        "tracks": {},
    }
    if args.track != "all" and output.exists():
        existing = json.loads(output.read_text())
        if existing.get("report_version") == report["report_version"]:
            report["tracks"] = existing.get("tracks", {})
    for track_name in selected_tracks:
        report["tracks"][track_name] = tune_track(
            track_name, root, phase_03_metrics, forest_config, args.trees
        )

    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {output.relative_to(root)}")
    for track_name, result in report["tracks"].items():
        print(track_name, result["selected_label"], result["selected_override"])


if __name__ == "__main__":
    main()
