"""Tests for feature generation."""

import unittest

from multisports.config.nba import NBA_CONFIG
from multisports.data.cleaning import clean_games, games_to_dataframe
from multisports.data.ingestion import generate_sample_nba_games
from multisports.features.team_features import TeamFeatureGenerator


class FeatureTests(unittest.TestCase):
    """Validate leak-safe team features."""

    def test_feature_generation_columns_and_tail_non_null(self) -> None:
        games = generate_sample_nba_games(n=220, seed=7)
        df = games_to_dataframe(clean_games(games))
        generator = TeamFeatureGenerator(NBA_CONFIG)
        featured = generator.generate(df)

        for column in NBA_CONFIG.feature_columns:
            self.assertIn(column, featured.columns)

        self.assertFalse(featured[NBA_CONFIG.feature_columns].tail(50).isna().any().any())


if __name__ == "__main__":
    unittest.main()
