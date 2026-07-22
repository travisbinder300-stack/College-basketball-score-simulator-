"""Unit tests for the rankings loader and enricher."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from multisports.data.rankings import enrich_with_rankings, load_rankings_csv


class LoadRankingsTests(unittest.TestCase):
    """Tests for load_rankings_csv."""

    def _write_csv(self, rows: list[dict], path: Path) -> None:
        fieldnames = ["rank", "team", "abbreviation", "rating", "win_pct"]
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def test_loads_ratings_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "rankings.csv"
            self._write_csv(
                [
                    {"rank": 1, "team": "Minnesota Lynx", "abbreviation": "MIN", "rating": 8.5, "win_pct": 0.68},
                    {"rank": 2, "team": "Las Vegas Aces", "abbreviation": "LVA", "rating": 7.8, "win_pct": 0.667},
                ],
                csv_path,
            )
            ratings = load_rankings_csv(str(csv_path))

        self.assertIn("MIN", ratings)
        self.assertIn("LVA", ratings)
        self.assertAlmostEqual(ratings["MIN"], 8.5)
        self.assertAlmostEqual(ratings["LVA"], 7.8)

    def test_abbreviations_uppercased(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "rankings.csv"
            self._write_csv(
                [{"rank": 1, "team": "Atlanta Dream", "abbreviation": "atl", "rating": 3.7, "win_pct": 0.533}],
                csv_path,
            )
            ratings = load_rankings_csv(str(csv_path))

        self.assertIn("ATL", ratings)
        self.assertNotIn("atl", ratings)

    def test_skips_rows_with_missing_abbreviation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "rankings.csv"
            csv_path.write_text(
                "rank,team,abbreviation,rating\n1,Some Team,,5.0\n2,Other Team,OTH,3.0\n",
                encoding="utf-8",
            )
            ratings = load_rankings_csv(str(csv_path))

        self.assertNotIn("", ratings)
        self.assertIn("OTH", ratings)

    def test_bad_rating_defaults_to_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "rankings.csv"
            csv_path.write_text(
                "rank,team,abbreviation,rating\n1,Team A,AAA,n/a\n",
                encoding="utf-8",
            )
            ratings = load_rankings_csv(str(csv_path))

        self.assertAlmostEqual(ratings["AAA"], 0.0)


class EnrichWithRankingsTests(unittest.TestCase):
    """Tests for enrich_with_rankings."""

    def _sample_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "id": ["g1", "g2", "g3"],
                "home_team_id": ["MIN", "LVA", "UNKNOWN"],
                "away_team_id": ["ATL", "MIN", "GSV"],
                "total_score": [165, 170, 155],
            }
        )

    def _sample_ratings(self) -> dict:
        return {"MIN": 8.5, "LVA": 7.8, "ATL": 3.7, "GSV": 6.2}

    def test_adds_rating_columns(self) -> None:
        df = enrich_with_rankings(self._sample_df(), self._sample_ratings())
        self.assertIn("home_predictive_rating", df.columns)
        self.assertIn("away_predictive_rating", df.columns)

    def test_known_teams_get_correct_ratings(self) -> None:
        df = enrich_with_rankings(self._sample_df(), self._sample_ratings())
        self.assertAlmostEqual(df.loc[0, "home_predictive_rating"], 8.5)  # MIN
        self.assertAlmostEqual(df.loc[0, "away_predictive_rating"], 3.7)  # ATL
        self.assertAlmostEqual(df.loc[1, "home_predictive_rating"], 7.8)  # LVA
        self.assertAlmostEqual(df.loc[1, "away_predictive_rating"], 8.5)  # MIN

    def test_unknown_team_receives_mean_rating(self) -> None:
        ratings = self._sample_ratings()
        mean_rating = sum(ratings.values()) / len(ratings)
        df = enrich_with_rankings(self._sample_df(), ratings)
        self.assertAlmostEqual(df.loc[2, "home_predictive_rating"], mean_rating)

    def test_explicit_default_rating_used_for_unknown(self) -> None:
        df = enrich_with_rankings(self._sample_df(), self._sample_ratings(), default_rating=-99.0)
        self.assertAlmostEqual(df.loc[2, "home_predictive_rating"], -99.0)

    def test_case_insensitive_lookup(self) -> None:
        df_lower = self._sample_df().copy()
        df_lower["home_team_id"] = df_lower["home_team_id"].str.lower()
        df = enrich_with_rankings(df_lower, self._sample_ratings())
        self.assertAlmostEqual(df.loc[0, "home_predictive_rating"], 8.5)  # "min" → MIN

    def test_empty_ratings_uses_zero_default(self) -> None:
        df = enrich_with_rankings(self._sample_df(), {})
        self.assertAlmostEqual(df.loc[0, "home_predictive_rating"], 0.0)
        self.assertAlmostEqual(df.loc[0, "away_predictive_rating"], 0.0)

    def test_does_not_mutate_input_df(self) -> None:
        original = self._sample_df()
        original_cols = list(original.columns)
        enrich_with_rankings(original, self._sample_ratings())
        self.assertEqual(list(original.columns), original_cols)


class WnbaRankingsCsvTests(unittest.TestCase):
    """Sanity-check the committed 2026 WNBA rankings CSV."""

    _CSV_PATH = (
        Path(__file__).parent.parent / "data" / "rankings" / "wnba_2026_predictive.csv"
    )

    def test_csv_exists(self) -> None:
        self.assertTrue(self._CSV_PATH.exists(), f"Missing {self._CSV_PATH}")

    def test_csv_has_all_15_teams(self) -> None:
        ratings = load_rankings_csv(str(self._CSV_PATH))
        self.assertEqual(len(ratings), 15)

    def test_ratings_are_floats_and_ordered(self) -> None:
        with self._CSV_PATH.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        previous_rating: float | None = None
        for row in rows:
            rating = float(row["rating"])
            if previous_rating is not None:
                self.assertLessEqual(
                    rating,
                    previous_rating,
                    "Ratings should be in descending order (best team first)",
                )
            previous_rating = rating

    def test_top_team_has_positive_rating(self) -> None:
        ratings = load_rankings_csv(str(self._CSV_PATH))
        self.assertGreater(max(ratings.values()), 0.0)

    def test_bottom_team_has_negative_rating(self) -> None:
        ratings = load_rankings_csv(str(self._CSV_PATH))
        self.assertLess(min(ratings.values()), 0.0)


if __name__ == "__main__":
    unittest.main()
