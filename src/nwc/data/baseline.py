"""Leakage-safe raw-data audit and baseline cleaning for T20I deliveries.

The source delivery file does not contain an innings identifier and reuses an
``over``/``ball`` coordinate when an illegal delivery is followed by its
rebowled legal delivery.  This module therefore treats raw file order as the
event order.  It never sorts a delivery stream by the displayed coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd

LEGACY_TOP_11 = frozenset(
    {
        "Sri Lanka",
        "India",
        "South Africa",
        "West Indies",
        "England",
        "New Zealand",
        "Australia",
        "Ireland",
        "Pakistan",
        "Zimbabwe",
        "Bangladesh",
    }
)

MATCH_COLUMNS = frozenset({"date", "gender", "match_id", "game"})
DELIVERY_COLUMNS = frozenset(
    {
        "match_id",
        "venue",
        "batting_team",
        "bowling_team",
        "over",
        "ball",
        "striker",
        "bowler",
        "non_striker",
        "runs_batter",
        "runs_extras",
        "runs_total",
        "innings_score",
        "innings_wickets",
        "is_wicket",
        "player_out",
        "wicket_kind",
        "match_winner",
        "winning_outcome",
        "toss_winner",
        "toss_decision",
        "wides",
        "noballs",
        "byes",
        "legbyes",
        "penalty",
    }
)

TeamScope = Literal["all_teams", "legacy_top_11"]


@dataclass(frozen=True)
class RawData:
    """Validated source tables with immutable source-row ordering attached."""

    matches: pd.DataFrame
    deliveries: pd.DataFrame


def _require_columns(frame: pd.DataFrame, required: frozenset[str], table_name: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {missing}")


def load_raw_data(raw_dir: str | Path) -> RawData:
    """Read source CSVs and validate their join key and mandatory columns."""

    raw_dir = Path(raw_dir)
    matches = pd.read_csv(raw_dir / "t20i_matches_data.csv", parse_dates=["date"])
    deliveries = pd.read_csv(raw_dir / "t20i_deliveries_data.csv", low_memory=False)
    _require_columns(matches, MATCH_COLUMNS, "matches")
    _require_columns(deliveries, DELIVERY_COLUMNS, "deliveries")
    if matches["match_id"].duplicated().any():
        raise ValueError("matches must contain exactly one row per match_id")
    if deliveries["match_id"].isna().any():
        raise ValueError("deliveries contains null match_id values")
    deliveries = deliveries.copy()
    deliveries["source_row"] = range(len(deliveries))
    return RawData(matches=matches, deliveries=deliveries)


def _attach_metadata(raw: RawData) -> pd.DataFrame:
    """Attach the authoritative match date and gender with an audited many-to-one join."""

    metadata = raw.matches.rename(columns={"date": "match_date"})
    deliveries = raw.deliveries.drop(columns=["date"], errors="ignore")
    joined = deliveries.merge(
        metadata,
        on="match_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    if not (joined["_merge"] == "both").all():
        missing = int((joined["_merge"] != "both").sum())
        raise ValueError(f"{missing} delivery rows have no match metadata")
    return joined.drop(columns="_merge")


def assign_innings_segments(deliveries: pd.DataFrame) -> pd.DataFrame:
    """Assign innings segments without trusting toss information or ball coordinates.

    A new segment begins when the batting team changes or when the stream resets
    its displayed coordinate, score, or wicket count.  The latter catches a
    super over where the same batting team returns later in a match.
    """

    ordered = deliveries.sort_values(["match_id", "source_row"], kind="stable").copy()
    grouped = ordered.groupby("match_id", sort=False)
    previous_team = grouped["batting_team"].shift()
    previous_over = grouped["over"].shift()
    previous_ball = grouped["ball"].shift()
    previous_score = grouped["innings_score"].shift()
    previous_wickets = grouped["innings_wickets"].shift()

    coordinate_reset = ordered["over"].lt(previous_over) | (
        ordered["over"].eq(previous_over) & ordered["ball"].lt(previous_ball)
    )
    reset = (
        previous_team.isna()
        | ordered["batting_team"].ne(previous_team)
        | coordinate_reset
        | ordered["innings_score"].lt(previous_score)
        | ordered["innings_wickets"].lt(previous_wickets)
    )
    ordered["innings_segment"] = reset.groupby(ordered["match_id"]).cumsum().astype("int8")
    ordered["event_sequence"] = (
        ordered.groupby(["match_id", "innings_segment"], sort=False).cumcount() + 1
    )
    return ordered


def classify_matches(segmented: pd.DataFrame) -> pd.DataFrame:
    """Classify outcomes and identify matches eligible for the baseline model."""

    match_level = (
        segmented.groupby("match_id", as_index=False)
        .agg(
            match_date=("match_date", "first"),
            gender=("gender", "first"),
            game=("game", "first"),
            winning_outcome=("winning_outcome", "first"),
            match_winner=("match_winner", "first"),
            innings_segments=("innings_segment", "max"),
        )
        .copy()
    )
    legal_delivery = (~segmented["wides"].gt(0) & ~segmented["noballs"].gt(0)).astype("int16")
    legal_balls_by_segment = legal_delivery.groupby(
        [segmented["match_id"], segmented["innings_segment"]]
    ).sum()
    overlong_match_ids = legal_balls_by_segment.loc[legal_balls_by_segment.gt(120)].index.get_level_values(
        "match_id"
    )
    match_level["has_overlong_innings"] = match_level["match_id"].isin(overlong_match_ids)
    outcome = match_level["winning_outcome"].fillna("").astype(str)
    match_level["is_dls"] = outcome.str.contains(r"\(D/L\)", regex=True)
    match_level["is_tie"] = outcome.str.contains("tie", case=False, regex=False)
    match_level["is_no_result"] = outcome.str.contains("no result", case=False, regex=False)
    match_level["is_awarded"] = outcome.str.contains("awarded", case=False, regex=False)
    match_level["has_two_innings"] = match_level["innings_segments"].eq(2)
    match_level["has_winner"] = match_level["match_winner"].notna()

    # Keep a single, mutually-exclusive reason so exclusion counts reconcile.
    match_level["exclusion_reason"] = "included"
    for condition, label in (
        (match_level["is_no_result"], "no_result"),
        (match_level["is_tie"], "tie"),
        (match_level["is_dls"], "dls"),
        (match_level["is_awarded"], "awarded"),
        (~match_level["has_two_innings"], "nonstandard_innings"),
        (~match_level["has_winner"], "missing_winner"),
        (match_level["has_overlong_innings"], "overlong_legal_balls"),
    ):
        match_level.loc[
            match_level["exclusion_reason"].eq("included") & condition, "exclusion_reason"
        ] = label
    return match_level


def audit_raw_data(raw: RawData) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return segmented deliveries and a JSON-serialisable data-quality report."""

    joined = _attach_metadata(raw)
    segmented = assign_innings_segments(joined)
    match_status = classify_matches(segmented)
    coordinate_duplicates = segmented.duplicated(
        ["match_id", "innings_segment", "over", "ball"], keep=False
    )
    score_delta = segmented.groupby(["match_id", "innings_segment"])["innings_score"].diff()
    wicket_delta = segmented.groupby(["match_id", "innings_segment"])["innings_wickets"].diff()
    report: dict[str, Any] = {
        "report_version": 1,
        "source": {
            "matches_rows": int(len(raw.matches)),
            "delivery_rows": int(len(raw.deliveries)),
            "matches_with_deliveries": int(raw.deliveries["match_id"].nunique()),
            "delivery_date_null_rows": int(raw.deliveries.get("date", pd.Series(dtype=float)).isna().sum()),
            "match_date_min": raw.matches["date"].min().date().isoformat(),
            "match_date_max": raw.matches["date"].max().date().isoformat(),
        },
        "join": {
            "unmatched_delivery_rows": int(joined["match_date"].isna().sum()),
            "matches_without_deliveries": int(
                (~raw.matches["match_id"].isin(raw.deliveries["match_id"])).sum()
            ),
        },
        "quality_checks": {
            "runs_total_mismatch_rows": int(
                segmented["runs_total"].ne(segmented["runs_batter"] + segmented["runs_extras"]).sum()
            ),
            "wicket_flag_player_out_mismatch_rows": int(
                segmented["is_wicket"].ne(segmented["player_out"].notna()).sum()
            ),
            "duplicate_displayed_coordinate_rows": int(coordinate_duplicates.sum()),
            "negative_score_delta_rows_within_segment": int(score_delta.lt(0).sum()),
            "negative_wicket_delta_rows_within_segment": int(wicket_delta.lt(0).sum()),
            "overlong_legal_ball_matches": int(match_status["has_overlong_innings"].sum()),
        },
        "innings_segments_per_match": {
            str(key): int(value)
            for key, value in match_status["innings_segments"].value_counts().sort_index().items()
        },
        "exclusions": {
            str(key): int(value)
            for key, value in match_status["exclusion_reason"].value_counts().sort_index().items()
        },
        "baseline_eligible_matches": int(match_status["exclusion_reason"].eq("included").sum()),
        "gender_matches": {
            str(key): int(value)
            for key, value in raw.matches["gender"].value_counts().sort_index().items()
        },
    }
    return segmented, report


def clean_baseline(raw: RawData, team_scope: TeamScope = "all_teams") -> pd.DataFrame:
    """Create a modelling-ready, post-delivery baseline without writing raw data.

    The output retains event columns for auditing and later NWC attribution, but
    deliberately does not decide which columns are model predictors.
    """

    if team_scope not in {"all_teams", "legacy_top_11"}:
        raise ValueError("team_scope must be 'all_teams' or 'legacy_top_11'")
    segmented, _ = audit_raw_data(raw)
    status = classify_matches(segmented)
    included_ids = status.loc[status["exclusion_reason"].eq("included"), "match_id"]
    cleaned = segmented[segmented["match_id"].isin(included_ids)].copy()
    if team_scope == "legacy_top_11":
        cleaned = cleaned.loc[
            cleaned["batting_team"].isin(LEGACY_TOP_11)
            & cleaned["bowling_team"].isin(LEGACY_TOP_11)
        ].copy()

    cleaned["match_innings"] = cleaned["innings_segment"].astype("int8")
    cleaned["legal_delivery"] = (~cleaned["wides"].gt(0) & ~cleaned["noballs"].gt(0)).astype("int8")
    innings_key = [cleaned["match_id"], cleaned["match_innings"]]
    cleaned["cumulative_innings_legal_balls"] = cleaned["legal_delivery"].groupby(innings_key).cumsum()
    cleaned["legal_deliveries_remaining"] = 120 - cleaned["cumulative_innings_legal_balls"]
    cleaned["powerplay"] = cleaned["over"].lt(6).astype("int8")
    cleaned["is_terminal_delivery"] = (
        cleaned["event_sequence"].eq(cleaned.groupby(["match_id", "match_innings"])["event_sequence"].transform("max"))
    )

    first_scores = (
        cleaned.loc[cleaned["match_innings"].eq(1)]
        .groupby("match_id")["innings_score"]
        .max()
    )
    cleaned["first_innings_score"] = cleaned["match_id"].map(first_scores)
    second = cleaned["match_innings"].eq(2)
    cleaned.loc[~second, "first_innings_score"] = pd.NA
    cleaned["runs_to_win"] = pd.NA
    cleaned.loc[second, "runs_to_win"] = (
        cleaned.loc[second, "first_innings_score"] + 1 - cleaned.loc[second, "innings_score"]
    )
    cleaned["required_run_rate"] = pd.NA
    active_chase = second & cleaned["legal_deliveries_remaining"].gt(0)
    cleaned.loc[active_chase, "required_run_rate"] = (
        6
        * cleaned.loc[active_chase, "runs_to_win"]
        / cleaned.loc[active_chase, "legal_deliveries_remaining"]
    )
    cleaned["current_run_rate"] = pd.NA
    positive_legal = cleaned["cumulative_innings_legal_balls"].gt(0)
    cleaned.loc[positive_legal, "current_run_rate"] = (
        6
        * cleaned.loc[positive_legal, "innings_score"]
        / cleaned.loc[positive_legal, "cumulative_innings_legal_balls"]
    )
    cleaned["run_rate_differential"] = pd.NA
    cleaned.loc[active_chase, "run_rate_differential"] = (
        cleaned.loc[active_chase, "current_run_rate"]
        - cleaned.loc[active_chase, "required_run_rate"]
    )
    cleaned["batting_team_win_match"] = cleaned["batting_team"].eq(cleaned["match_winner"]).astype("int8")
    return cleaned.sort_values("source_row", kind="stable").reset_index(drop=True)
