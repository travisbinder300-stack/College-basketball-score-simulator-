import unittest

from mlb_pitcher_props.baseline import probability_over_line, project_pitcher_props
from mlb_pitcher_props.models import PitcherInput, WeatherConditions


class TestBaselineProjection(unittest.TestCase):
    def test_projection_outputs_positive_values(self) -> None:
        pitcher = PitcherInput(
            pitcher_name="A",
            expected_outs_baseline=18.0,
            strikeouts_per_out=0.35,
        )
        result = project_pitcher_props(pitcher, weather=WeatherConditions())
        self.assertGreater(result.projected_outs, 0)
        self.assertGreater(result.projected_strikeouts, 0)

    def test_invalid_baseline_raises(self) -> None:
        pitcher = PitcherInput(
            pitcher_name="A",
            expected_outs_baseline=0.0,
            strikeouts_per_out=0.35,
        )
        with self.assertRaises(ValueError):
            project_pitcher_props(pitcher)

    def test_probability_range(self) -> None:
        probability = probability_over_line(6.0, 5.5, 1.4)
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)


if __name__ == "__main__":
    unittest.main()

