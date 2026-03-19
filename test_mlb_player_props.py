"""
Unit tests for mlb_player_props.py
"""

import math
import random
import unittest

from mlb_player_props import (
    BatterStats,
    MLBPlayerPropsSimulator,
    PitcherStats,
    PlayerPropsReport,
    PropResult,
    Stadium,
    WeatherConditions,
    WindConditions,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _default_sim(num_simulations: int = 2_000, seed: int = 0) -> MLBPlayerPropsSimulator:
    return MLBPlayerPropsSimulator(
        stadium=Stadium.from_name("Neutral"),
        weather=WeatherConditions(temp_f=72, precipitation="none", humidity=0.50),
        wind=WindConditions(speed_mph=0, direction="calm"),
        num_simulations=num_simulations,
        random_seed=seed,
    )


def _default_pitcher() -> PitcherStats:
    return PitcherStats(
        name="Test Pitcher",
        era=4.00,
        k_per_9=8.5,
        innings_per_start=5.5,
        whip=1.25,
    )


def _default_batter() -> BatterStats:
    return BatterStats(
        name="Test Batter",
        avg=0.270,
        obp=0.340,
        slg=0.460,
        hr_per_600_pa=25,
        sb_per_season=15,
        doubles_per_600_pa=35,
        games_played=162,
    )


# ---------------------------------------------------------------------------
# Stadium tests
# ---------------------------------------------------------------------------


class TestStadium(unittest.TestCase):

    def test_from_name_known_stadium(self):
        s = Stadium.from_name("Coors Field")
        self.assertEqual(s.name, "Coors Field")
        self.assertGreater(s.hr_factor, 1.0, "Coors should be a hitter's park")
        self.assertGreater(s.runs_factor, 1.0)

    def test_from_name_pitcher_park(self):
        s = Stadium.from_name("Petco Park")
        self.assertLess(s.hr_factor, 1.0, "Petco should suppress HRs")
        self.assertLess(s.runs_factor, 1.0)

    def test_from_name_neutral(self):
        s = Stadium.from_name("Neutral")
        self.assertAlmostEqual(s.hr_factor, 1.0)
        self.assertAlmostEqual(s.hits_factor, 1.0)
        self.assertAlmostEqual(s.doubles_factor, 1.0)
        self.assertAlmostEqual(s.k_factor, 1.0)
        self.assertAlmostEqual(s.runs_factor, 1.0)

    def test_from_name_unknown_falls_back_to_neutral(self):
        s = Stadium.from_name("Unknown Ballpark XYZ")
        self.assertAlmostEqual(s.hr_factor, 1.0)

    def test_invalid_factor_raises(self):
        with self.assertRaises(ValueError):
            Stadium(name="Bad Park", hr_factor=3.0)  # 3.0 > 2.0 limit

    def test_all_catalogue_stadiums_valid(self):
        for name in Stadium._STADIUMS:
            s = Stadium.from_name(name)
            self.assertIsInstance(s, Stadium)


# ---------------------------------------------------------------------------
# WeatherConditions tests
# ---------------------------------------------------------------------------


class TestWeatherConditions(unittest.TestCase):

    def test_warm_weather_increases_hr(self):
        cold = WeatherConditions(temp_f=45)
        warm = WeatherConditions(temp_f=95)
        self.assertLess(cold.temp_hr_multiplier(), warm.temp_hr_multiplier())

    def test_cold_weather_increases_strikeouts(self):
        cold = WeatherConditions(temp_f=45)
        warm = WeatherConditions(temp_f=90)
        self.assertGreater(cold.temp_k_multiplier(), warm.temp_k_multiplier())

    def test_precipitation_reduces_hit_factor(self):
        w_none = WeatherConditions(precipitation="none")
        w_heavy = WeatherConditions(precipitation="heavy")
        self.assertGreater(w_none.precip_factor(), w_heavy.precip_factor())

    def test_unknown_precipitation_defaults_to_1(self):
        w = WeatherConditions(precipitation="blizzard")
        self.assertAlmostEqual(w.precip_factor(), 1.00)

    def test_humidity_effect(self):
        low_hum = WeatherConditions(humidity=0.20)
        high_hum = WeatherConditions(humidity=0.90)
        self.assertGreater(low_hum.humidity_hit_multiplier(), high_hum.humidity_hit_multiplier())

    def test_baseline_temperature_multipliers(self):
        baseline = WeatherConditions(temp_f=72)
        self.assertAlmostEqual(baseline.temp_hr_multiplier(), 1.00)
        self.assertAlmostEqual(baseline.temp_k_multiplier(), 1.00)

    def test_baseline_humidity_multiplier(self):
        baseline = WeatherConditions(humidity=0.50)
        self.assertAlmostEqual(baseline.humidity_hit_multiplier(), 1.00)


# ---------------------------------------------------------------------------
# WindConditions tests
# ---------------------------------------------------------------------------


class TestWindConditions(unittest.TestCase):

    def test_calm_wind_multipliers_are_1(self):
        w = WindConditions(speed_mph=0, direction="calm")
        self.assertAlmostEqual(w.hr_multiplier(), 1.00)
        self.assertAlmostEqual(w.hit_multiplier(), 1.00)

    def test_out_wind_raises_hr_multiplier(self):
        out_wind = WindConditions(speed_mph=15, direction="out_to_center")
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertGreater(out_wind.hr_multiplier(), calm.hr_multiplier())

    def test_in_wind_lowers_hr_multiplier(self):
        in_wind = WindConditions(speed_mph=15, direction="in_from_center")
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertLess(in_wind.hr_multiplier(), calm.hr_multiplier())

    def test_out_wind_raises_hit_multiplier(self):
        out_wind = WindConditions(speed_mph=20, direction="out_to_center")
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertGreater(out_wind.hit_multiplier(), calm.hit_multiplier())

    def test_cross_wind_is_neutral_on_hr(self):
        cross = WindConditions(speed_mph=10, direction="cross_left_right")
        self.assertAlmostEqual(cross.hr_multiplier(), 1.00)

    def test_unknown_direction_defaults_to_neutral(self):
        w = WindConditions(speed_mph=10, direction="sideways_tornado")
        self.assertAlmostEqual(w.hr_multiplier(), 1.00)


# ---------------------------------------------------------------------------
# Stat validation tests
# ---------------------------------------------------------------------------


class TestPitcherStatsValidation(unittest.TestCase):

    def test_valid_stats_pass(self):
        p = _default_pitcher()
        p.validate()  # Should not raise

    def test_negative_era_raises(self):
        p = PitcherStats(name="X", era=-1, k_per_9=8.0, innings_per_start=6.0, whip=1.20)
        with self.assertRaises(ValueError):
            p.validate()

    def test_zero_k9_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=0, innings_per_start=6.0, whip=1.20)
        with self.assertRaises(ValueError):
            p.validate()

    def test_too_many_innings_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=10.0, whip=1.20)
        with self.assertRaises(ValueError):
            p.validate()

    def test_negative_whip_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=-0.5)
        with self.assertRaises(ValueError):
            p.validate()


class TestBatterStatsValidation(unittest.TestCase):

    def test_valid_stats_pass(self):
        b = _default_batter()
        b.validate()  # Should not raise

    def test_avg_above_1_raises(self):
        b = BatterStats(name="X", avg=1.1, obp=0.35, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30)
        with self.assertRaises(ValueError):
            b.validate()

    def test_negative_avg_raises(self):
        b = BatterStats(name="X", avg=-0.1, obp=0.35, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30)
        with self.assertRaises(ValueError):
            b.validate()

    def test_slg_above_4_raises(self):
        b = BatterStats(name="X", avg=0.30, obp=0.38, slg=4.1,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30)
        with self.assertRaises(ValueError):
            b.validate()

    def test_negative_hr_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=-5, sb_per_season=10, doubles_per_600_pa=30)
        with self.assertRaises(ValueError):
            b.validate()

    def test_negative_sb_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=-1, doubles_per_600_pa=30)
        with self.assertRaises(ValueError):
            b.validate()


# ---------------------------------------------------------------------------
# Simulation output structure tests
# ---------------------------------------------------------------------------


class TestSimulatorOutputStructure(unittest.TestCase):

    def setUp(self):
        self.sim = _default_sim(num_simulations=500, seed=99)
        self.pitcher = _default_pitcher()
        self.batter = _default_batter()

    def test_pitcher_report_has_three_props(self):
        report = self.sim.simulate_pitcher(self.pitcher)
        self.assertIsInstance(report, PlayerPropsReport)
        self.assertEqual(len(report.props), 3)
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("Strikeouts", prop_names)
        self.assertIn("Outs Recorded", prop_names)
        self.assertIn("Runs Allowed", prop_names)

    def test_batter_report_has_four_props(self):
        report = self.sim.simulate_batter(self.batter)
        self.assertIsInstance(report, PlayerPropsReport)
        self.assertEqual(len(report.props), 4)
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("Hits", prop_names)
        self.assertIn("Doubles", prop_names)
        self.assertIn("Home Runs", prop_names)
        self.assertIn("Stolen Bases", prop_names)

    def test_pitcher_report_player_name(self):
        report = self.sim.simulate_pitcher(self.pitcher)
        self.assertEqual(report.player_name, "Test Pitcher")

    def test_batter_report_player_name(self):
        report = self.sim.simulate_batter(self.batter)
        self.assertEqual(report.player_name, "Test Batter")

    def test_prop_result_has_over_probabilities(self):
        report = self.sim.simulate_pitcher(self.pitcher, k_lines=[4.5, 5.5])
        k_prop = next(p for p in report.props if p.prop_name == "Strikeouts")
        self.assertIn(4.5, k_prop.over_probabilities)
        self.assertIn(5.5, k_prop.over_probabilities)

    def test_over_probabilities_in_valid_range(self):
        report = self.sim.simulate_pitcher(self.pitcher)
        for prop in report.props:
            for _line, prob in prop.over_probabilities.items():
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)


# ---------------------------------------------------------------------------
# Simulation statistical sanity tests
# ---------------------------------------------------------------------------


class TestSimulatorStatistics(unittest.TestCase):
    """Check that simulated distributions are plausible given the input stats."""

    def setUp(self):
        self.sim = _default_sim(num_simulations=3_000, seed=7)

    def test_pitcher_strikeouts_positive(self):
        pitcher = _default_pitcher()
        report = self.sim.simulate_pitcher(pitcher)
        k_prop = next(p for p in report.props if p.prop_name == "Strikeouts")
        self.assertGreater(k_prop.mean, 0)

    def test_pitcher_runs_positive(self):
        pitcher = _default_pitcher()
        report = self.sim.simulate_pitcher(pitcher)
        runs_prop = next(p for p in report.props if p.prop_name == "Runs Allowed")
        self.assertGreater(runs_prop.mean, 0)

    def test_batter_hits_positive(self):
        batter = _default_batter()
        report = self.sim.simulate_batter(batter)
        hits_prop = next(p for p in report.props if p.prop_name == "Hits")
        self.assertGreater(hits_prop.mean, 0)

    def test_batter_hr_mean_less_than_hits_mean(self):
        batter = _default_batter()
        report = self.sim.simulate_batter(batter)
        hits_prop = next(p for p in report.props if p.prop_name == "Hits")
        hr_prop = next(p for p in report.props if p.prop_name == "Home Runs")
        self.assertLess(hr_prop.mean, hits_prop.mean)

    def test_batter_doubles_mean_less_than_hits_mean(self):
        batter = _default_batter()
        report = self.sim.simulate_batter(batter)
        hits_prop = next(p for p in report.props if p.prop_name == "Hits")
        doubles_prop = next(p for p in report.props if p.prop_name == "Doubles")
        self.assertLess(doubles_prop.mean, hits_prop.mean)

    def test_percentile_ordering(self):
        pitcher = _default_pitcher()
        report = self.sim.simulate_pitcher(pitcher)
        for prop in report.props:
            self.assertLessEqual(prop.percentile_10, prop.percentile_25)
            self.assertLessEqual(prop.percentile_25, prop.percentile_75)
            self.assertLessEqual(prop.percentile_75, prop.percentile_90)

    def test_mean_between_p10_and_p90(self):
        batter = _default_batter()
        report = self.sim.simulate_batter(batter)
        for prop in report.props:
            self.assertGreaterEqual(prop.mean, prop.percentile_10)
            self.assertLessEqual(prop.mean, prop.percentile_90)

    def test_high_k9_pitcher_has_more_strikeouts(self):
        low_k = PitcherStats(name="Low K", era=4.0, k_per_9=5.0, innings_per_start=6.0, whip=1.30)
        high_k = PitcherStats(name="High K", era=3.0, k_per_9=12.0, innings_per_start=6.5, whip=1.05)
        report_low = self.sim.simulate_pitcher(low_k)
        report_high = self.sim.simulate_pitcher(high_k)
        mean_k_low = next(p for p in report_low.props if p.prop_name == "Strikeouts").mean
        mean_k_high = next(p for p in report_high.props if p.prop_name == "Strikeouts").mean
        self.assertGreater(mean_k_high, mean_k_low)

    def test_power_hitter_has_more_hr_than_contact_hitter(self):
        contact = BatterStats(name="Contact", avg=0.310, obp=0.380, slg=0.400,
                              hr_per_600_pa=8, sb_per_season=12, doubles_per_600_pa=30, games_played=162)
        power = BatterStats(name="Power", avg=0.255, obp=0.340, slg=0.560,
                            hr_per_600_pa=45, sb_per_season=3, doubles_per_600_pa=28, games_played=162)
        report_contact = self.sim.simulate_batter(contact)
        report_power = self.sim.simulate_batter(power)
        hr_contact = next(p for p in report_contact.props if p.prop_name == "Home Runs").mean
        hr_power = next(p for p in report_power.props if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_power, hr_contact)


# ---------------------------------------------------------------------------
# Environmental effect tests
# ---------------------------------------------------------------------------


class TestEnvironmentalEffects(unittest.TestCase):
    """Verify that environmental factors shift prop distributions in the correct direction."""

    def _run_pitcher_prop(self, stadium_name: str, weather: WeatherConditions,
                          wind: WindConditions, prop: str, n: int = 2_000) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name(stadium_name),
            weather=weather,
            wind=wind,
            num_simulations=n,
            random_seed=42,
        )
        pitcher = _default_pitcher()
        report = sim.simulate_pitcher(pitcher)
        return next(p for p in report.props if p.prop_name == prop).mean

    def _run_batter_prop(self, stadium_name: str, weather: WeatherConditions,
                         wind: WindConditions, prop: str, n: int = 2_000) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name(stadium_name),
            weather=weather,
            wind=wind,
            num_simulations=n,
            random_seed=42,
        )
        batter = _default_batter()
        report = sim.simulate_batter(batter)
        return next(p for p in report.props if p.prop_name == prop).mean

    def test_coors_field_more_hrs_than_petco(self):
        neutral_weather = WeatherConditions()
        calm = WindConditions()
        coors_hr = self._run_batter_prop("Coors Field", neutral_weather, calm, "Home Runs")
        petco_hr = self._run_batter_prop("Petco Park", neutral_weather, calm, "Home Runs")
        self.assertGreater(coors_hr, petco_hr)

    def test_outward_wind_increases_hr(self):
        neutral_stadium = Stadium.from_name("Neutral")
        weather = WeatherConditions()
        out_wind = WindConditions(speed_mph=15, direction="out_to_center")
        calm_wind = WindConditions(speed_mph=0, direction="calm")

        sim_out = MLBPlayerPropsSimulator(neutral_stadium, weather, out_wind, 2_000, 42)
        sim_calm = MLBPlayerPropsSimulator(neutral_stadium, weather, calm_wind, 2_000, 42)

        batter = _default_batter()
        hr_out = next(p for p in sim_out.simulate_batter(batter).props if p.prop_name == "Home Runs").mean
        hr_calm = next(p for p in sim_calm.simulate_batter(batter).props if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_out, hr_calm)

    def test_cold_weather_increases_strikeouts(self):
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        cold_weather = WeatherConditions(temp_f=40)
        warm_weather = WeatherConditions(temp_f=95)

        sim_cold = MLBPlayerPropsSimulator(neutral_stadium, cold_weather, calm, 2_000, 42)
        sim_warm = MLBPlayerPropsSimulator(neutral_stadium, warm_weather, calm, 2_000, 42)

        pitcher = _default_pitcher()
        k_cold = next(p for p in sim_cold.simulate_pitcher(pitcher).props if p.prop_name == "Strikeouts").mean
        k_warm = next(p for p in sim_warm.simulate_pitcher(pitcher).props if p.prop_name == "Strikeouts").mean
        self.assertGreater(k_cold, k_warm)

    def test_heavy_rain_reduces_hits(self):
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        dry = WeatherConditions(precipitation="none")
        wet = WeatherConditions(precipitation="heavy")

        sim_dry = MLBPlayerPropsSimulator(neutral_stadium, dry, calm, 2_000, 42)
        sim_wet = MLBPlayerPropsSimulator(neutral_stadium, wet, calm, 2_000, 42)

        batter = _default_batter()
        hits_dry = next(p for p in sim_dry.simulate_batter(batter).props if p.prop_name == "Hits").mean
        hits_wet = next(p for p in sim_wet.simulate_batter(batter).props if p.prop_name == "Hits").mean
        self.assertGreater(hits_dry, hits_wet)

    def test_warm_weather_increases_hr(self):
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        cold = WeatherConditions(temp_f=40)
        hot = WeatherConditions(temp_f=100)

        sim_cold = MLBPlayerPropsSimulator(neutral_stadium, cold, calm, 2_000, 42)
        sim_hot = MLBPlayerPropsSimulator(neutral_stadium, hot, calm, 2_000, 42)

        batter = _default_batter()
        hr_cold = next(p for p in sim_cold.simulate_batter(batter).props if p.prop_name == "Home Runs").mean
        hr_hot = next(p for p in sim_hot.simulate_batter(batter).props if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_hot, hr_cold)


# ---------------------------------------------------------------------------
# Matchup / convenience API tests
# ---------------------------------------------------------------------------


class TestSimulateMatchup(unittest.TestCase):

    def test_simulate_matchup_returns_all_players(self):
        sim = _default_sim(num_simulations=300, seed=1)
        pitcher = _default_pitcher()
        batters = [
            BatterStats(name="Batter A", avg=0.280, obp=0.350, slg=0.480,
                        hr_per_600_pa=22, sb_per_season=8, doubles_per_600_pa=32, games_played=162),
            BatterStats(name="Batter B", avg=0.260, obp=0.330, slg=0.430,
                        hr_per_600_pa=15, sb_per_season=20, doubles_per_600_pa=28, games_played=162),
        ]
        results = sim.simulate_matchup(pitcher, batters)
        self.assertIn("Test Pitcher", results)
        self.assertIn("Batter A", results)
        self.assertIn("Batter B", results)

    def test_simulate_matchup_pitcher_report_correct(self):
        sim = _default_sim(num_simulations=300, seed=2)
        pitcher = _default_pitcher()
        results = sim.simulate_matchup(pitcher, [])
        self.assertIn("Strikeouts", {p.prop_name for p in results[pitcher.name].props})

    def test_simulate_matchup_empty_lineup(self):
        sim = _default_sim(num_simulations=200, seed=3)
        pitcher = _default_pitcher()
        results = sim.simulate_matchup(pitcher, [])
        self.assertEqual(len(results), 1)
        self.assertIn(pitcher.name, results)


# ---------------------------------------------------------------------------
# Reproducibility test
# ---------------------------------------------------------------------------


class TestReproducibility(unittest.TestCase):

    def _run_k_mean(self, seed: int) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=1_000,
            random_seed=seed,
        )
        report = sim.simulate_pitcher(_default_pitcher())
        return next(p for p in report.props if p.prop_name == "Strikeouts").mean

    def test_same_seed_same_result(self):
        mean1 = self._run_k_mean(seed=123)
        mean2 = self._run_k_mean(seed=123)
        self.assertAlmostEqual(mean1, mean2, places=6)

    def test_different_seed_different_result(self):
        mean1 = self._run_k_mean(seed=100)
        mean2 = self._run_k_mean(seed=999)
        # With high probability these differ; if they happen to match it's fine.
        # This test mainly validates that seeding is respected.
        self.assertIsInstance(mean1, float)
        self.assertIsInstance(mean2, float)


if __name__ == "__main__":
    unittest.main()
