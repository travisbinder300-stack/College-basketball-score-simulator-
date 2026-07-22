"""Tests for schema dataclasses."""

from datetime import date
import unittest

from multisports.data.schema import Game, Player, Team, TrainingRow


class SchemaTests(unittest.TestCase):
    """Validate core schema objects."""

    def test_team_player_and_game_creation(self) -> None:
        team = Team("t1", "Lions", "LIO", "nba", "East", "A")
        player = Player("p1", "Jane Doe", "t1", "nba", "G")
        game = Game(
            id="g1",
            sport="nba",
            date=date(2024, 1, 1),
            season="2023-2024",
            home_team_id="t1",
            away_team_id="t2",
            home_score=110,
            away_score=101,
            venue="Arena",
            is_neutral_site=False,
            home_rest_days=2,
            away_rest_days=1,
        )
        row = TrainingRow.from_game_and_features(game, {"feature_a": 1.5})

        self.assertEqual(team.name, "Lions")
        self.assertEqual(player.team_id, "t1")
        self.assertEqual(game.total_score, 211)
        self.assertEqual(row.to_dict()["feature_a"], 1.5)

    def test_game_validation(self) -> None:
        with self.assertRaises(ValueError):
            Game(
                id="g2",
                sport="nba",
                date=date(2024, 1, 2),
                season="2023-2024",
                home_team_id="t1",
                away_team_id="t2",
                home_score=-1,
                away_score=100,
                venue="Arena",
                is_neutral_site=False,
                home_rest_days=2,
                away_rest_days=2,
            )

        with self.assertRaises(TypeError):
            Game(
                id="g3",
                sport="nba",
                date="2024-01-02",
                season="2023-2024",
                home_team_id="t1",
                away_team_id="t2",
                home_score=100,
                away_score=98,
                venue="Arena",
                is_neutral_site=False,
                home_rest_days=2,
                away_rest_days=2,
            )


if __name__ == "__main__":
    unittest.main()
