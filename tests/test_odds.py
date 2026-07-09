import unittest

from mlb_pitcher_props.odds import compute_market_edge, implied_probability_from_odds


class TestOddsMath(unittest.TestCase):
    def test_implied_probability_american(self) -> None:
        value = implied_probability_from_odds(-110, "american")
        self.assertAlmostEqual(value, 110.0 / 210.0, places=6)

    def test_compute_market_edge(self) -> None:
        edge = compute_market_edge(0.57, -110, "american")
        self.assertGreater(edge.edge, 0.0)
        self.assertGreater(edge.expected_value_per_unit, -1.0)

    def test_invalid_odds_raises(self) -> None:
        with self.assertRaises(ValueError):
            implied_probability_from_odds(0, "american")


if __name__ == "__main__":
    unittest.main()

