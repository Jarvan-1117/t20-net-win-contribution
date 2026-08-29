from __future__ import annotations

import unittest

import pandas as pd

from nwc.data.baseline import assign_innings_segments, classify_matches


def _delivery(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "match_id": 1,
        "source_row": 0,
        "match_date": pd.Timestamp("2020-01-01"),
        "gender": "female",
        "game": "A v B",
        "batting_team": "A",
        "bowling_team": "B",
        "over": 0,
        "ball": 1,
        "innings_score": 0,
        "innings_wickets": 0,
        "wides": 0,
        "noballs": 0,
        "winning_outcome": "1 runs",
        "match_winner": "A",
    }
    row.update(overrides)
    return row


class BaselineTests(unittest.TestCase):
    def test_duplicate_coordinates_keep_file_order_and_same_segment(self) -> None:
        deliveries = pd.DataFrame(
            [
                _delivery(source_row=10, ball=1, innings_score=0),
                _delivery(source_row=11, ball=1, innings_score=1),  # wide then re-bowled ball
                _delivery(source_row=12, ball=2, innings_score=1),
            ]
        )
        result = assign_innings_segments(deliveries)
        self.assertEqual(result["source_row"].tolist(), [10, 11, 12])
        self.assertEqual(result["innings_segment"].tolist(), [1, 1, 1])
        self.assertEqual(result["event_sequence"].tolist(), [1, 2, 3])

    def test_score_reset_starts_new_segment_when_team_returns(self) -> None:
        deliveries = pd.DataFrame(
            [
                _delivery(source_row=0, batting_team="A", innings_score=10, over=1),
                _delivery(source_row=1, batting_team="B", innings_score=8, over=1),
                _delivery(source_row=2, batting_team="A", innings_score=0, over=0),
            ]
        )
        result = assign_innings_segments(deliveries)
        self.assertEqual(result["innings_segment"].tolist(), [1, 2, 3])

    def test_dls_tie_is_excluded_before_model_target_is_created(self) -> None:
        segmented = pd.DataFrame(
            [
                _delivery(source_row=0, innings_segment=1, winning_outcome="tie (D/L)", match_winner=None),
                _delivery(source_row=1, innings_segment=2, winning_outcome="tie (D/L)", match_winner=None),
            ]
        )
        status = classify_matches(segmented)
        self.assertEqual(status.loc[0, "exclusion_reason"], "tie")
