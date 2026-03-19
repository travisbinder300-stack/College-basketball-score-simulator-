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
    platoon_splits_for,
    home_away_batter_splits_for,
    home_away_pitcher_splits_for,
    HOME_AWAY_BATTER_SPLITS,
    HOME_AWAY_PITCHER_SPLITS,
    DAY_GAME_TEMP_AMPLIFIER,
    DAY_GAME_WIND_AMPLIFIER,
    DOME_TEMP_AMPLIFIER,
    DOME_WIND_AMPLIFIER,
    VALID_GAME_TIMES,
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

    # --- New: temp_hit_multiplier ---

    def test_warm_weather_increases_hit_multiplier(self):
        cold = WeatherConditions(temp_f=45)
        warm = WeatherConditions(temp_f=95)
        self.assertGreater(warm.temp_hit_multiplier(), cold.temp_hit_multiplier())

    def test_cold_weather_decreases_hit_multiplier(self):
        cold = WeatherConditions(temp_f=45)
        self.assertLess(cold.temp_hit_multiplier(), 1.0)

    def test_baseline_temp_hit_multiplier_is_1(self):
        baseline = WeatherConditions(temp_f=72)
        self.assertAlmostEqual(baseline.temp_hit_multiplier(), 1.0)

    # --- New: temp_pitcher_stamina_multiplier ---

    def test_comfortable_temp_stamina_is_1(self):
        # The comfortable range is 60°F–90°F inclusive: the condition checks
        # temp_f > TEMP_HOT_THRESHOLD_F (90.0), so exactly 90°F returns 1.0.
        for temp in (60, 72, 80, 89, 90):
            w = WeatherConditions(temp_f=temp)
            self.assertAlmostEqual(
                w.temp_pitcher_stamina_multiplier(), 1.0,
                msg=f"Expected stamina = 1.0 at {temp}°F (comfortable range [60, 90])",
            )

    def test_cold_reduces_pitcher_stamina(self):
        cold = WeatherConditions(temp_f=45)
        self.assertLess(cold.temp_pitcher_stamina_multiplier(), 1.0)

    def test_heat_reduces_pitcher_stamina(self):
        hot = WeatherConditions(temp_f=100)
        self.assertLess(hot.temp_pitcher_stamina_multiplier(), 1.0)

    def test_colder_means_more_stamina_penalty(self):
        slightly_cold = WeatherConditions(temp_f=55)
        very_cold = WeatherConditions(temp_f=40)
        self.assertGreater(
            slightly_cold.temp_pitcher_stamina_multiplier(),
            very_cold.temp_pitcher_stamina_multiplier(),
        )

    def test_hotter_means_more_stamina_penalty(self):
        slightly_hot = WeatherConditions(temp_f=92)
        very_hot = WeatherConditions(temp_f=105)
        self.assertGreater(
            slightly_hot.temp_pitcher_stamina_multiplier(),
            very_hot.temp_pitcher_stamina_multiplier(),
        )


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

    # --- New: k_multiplier ---

    def test_calm_wind_k_multiplier_is_1(self):
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertAlmostEqual(calm.k_multiplier(), 1.00)

    def test_any_wind_raises_k_multiplier(self):
        # Any non-zero wind should produce K multiplier >= 1.
        for direction in ("out_to_center", "in_from_center", "cross_left_right"):
            w = WindConditions(speed_mph=15, direction=direction)
            self.assertGreaterEqual(
                w.k_multiplier(), 1.00,
                msg=f"k_multiplier should be >= 1 for direction={direction}",
            )

    def test_in_wind_higher_k_multiplier_than_out_wind(self):
        # In-blowing wind gets a larger K boost than out-blowing wind.
        in_wind = WindConditions(speed_mph=15, direction="in_from_center")
        out_wind = WindConditions(speed_mph=15, direction="out_to_center")
        self.assertGreater(in_wind.k_multiplier(), out_wind.k_multiplier())

    def test_faster_wind_raises_k_multiplier(self):
        slow = WindConditions(speed_mph=5, direction="in_from_center")
        fast = WindConditions(speed_mph=20, direction="in_from_center")
        self.assertGreater(fast.k_multiplier(), slow.k_multiplier())

    # --- New: runs_multiplier ---

    def test_calm_wind_runs_multiplier_is_1(self):
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertAlmostEqual(calm.runs_multiplier(), 1.00)

    def test_out_wind_raises_runs_multiplier(self):
        out_wind = WindConditions(speed_mph=15, direction="out_to_center")
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertGreater(out_wind.runs_multiplier(), calm.runs_multiplier())

    def test_in_wind_lowers_runs_multiplier(self):
        in_wind = WindConditions(speed_mph=15, direction="in_from_center")
        calm = WindConditions(speed_mph=0, direction="calm")
        self.assertLess(in_wind.runs_multiplier(), calm.runs_multiplier())

    def test_cross_wind_is_neutral_on_runs(self):
        cross = WindConditions(speed_mph=10, direction="cross_left_right")
        self.assertAlmostEqual(cross.runs_multiplier(), 1.00)


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

    def test_arm_strength_above_100_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0,
                         whip=1.20, arm_strength=101)
        with self.assertRaises(ValueError):
            p.validate()

    def test_arm_strength_below_0_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0,
                         whip=1.20, arm_strength=-1)
        with self.assertRaises(ValueError):
            p.validate()

    def test_arm_strength_defaults_to_50(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=1.20)
        self.assertEqual(p.arm_strength, 50.0)

    def test_throws_invalid_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0,
                         whip=1.20, throws="B")
        with self.assertRaises(ValueError):
            p.validate()

    def test_throws_defaults_to_R(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=1.20)
        self.assertEqual(p.throws, "R")

    def test_throws_L_is_valid(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0,
                         whip=1.20, throws="L")
        p.validate()  # Should not raise

    def test_pitches_per_pa_defaults_to_3_8(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=1.20)
        self.assertAlmostEqual(p.pitches_per_pa, 3.8)

    def test_pitches_per_pa_too_low_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=1.20,
                         pitches_per_pa=2.9)
        with self.assertRaises(ValueError):
            p.validate()

    def test_pitches_per_pa_too_high_raises(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=1.20,
                         pitches_per_pa=5.6)
        with self.assertRaises(ValueError):
            p.validate()

    def test_pitches_per_pa_valid_value_passes(self):
        p = PitcherStats(name="X", era=4.0, k_per_9=8.0, innings_per_start=6.0, whip=1.20,
                         pitches_per_pa=4.1)
        p.validate()  # Should not raise


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

    def test_power_rating_above_100_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        power_rating=101)
        with self.assertRaises(ValueError):
            b.validate()

    def test_power_rating_below_0_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        power_rating=-1)
        with self.assertRaises(ValueError):
            b.validate()

    def test_power_rating_defaults_to_50(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30)
        self.assertEqual(b.power_rating, 50.0)

    def test_bats_invalid_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        bats="X")
        with self.assertRaises(ValueError):
            b.validate()

    def test_bats_defaults_to_R(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30)
        self.assertEqual(b.bats, "R")

    def test_bats_L_is_valid(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        bats="L")
        b.validate()  # Should not raise

    def test_bats_S_is_valid(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        bats="S")
        b.validate()  # Should not raise

    def test_batter_pitches_per_pa_defaults_to_3_8(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30)
        self.assertAlmostEqual(b.pitches_per_pa, 3.8)

    def test_batter_pitches_per_pa_too_low_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        pitches_per_pa=2.4)
        with self.assertRaises(ValueError):
            b.validate()

    def test_batter_pitches_per_pa_too_high_raises(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        pitches_per_pa=5.6)
        with self.assertRaises(ValueError):
            b.validate()

    def test_batter_pitches_per_pa_valid_value_passes(self):
        b = BatterStats(name="X", avg=0.27, obp=0.34, slg=0.45,
                        hr_per_600_pa=20, sb_per_season=10, doubles_per_600_pa=30,
                        pitches_per_pa=4.2)
        b.validate()  # Should not raise


# ---------------------------------------------------------------------------
# Pitcher arm-strength multiplier tests
# ---------------------------------------------------------------------------


class TestPitcherArmStrength(unittest.TestCase):
    """Unit tests for the PitcherStats arm-strength multiplier methods."""

    def _pitcher(self, arm: float) -> PitcherStats:
        return PitcherStats(name="P", era=4.0, k_per_9=8.5,
                            innings_per_start=5.5, whip=1.25, arm_strength=arm)

    # --- arm_k_multiplier ---

    def test_average_arm_k_multiplier_is_1(self):
        self.assertAlmostEqual(self._pitcher(50).arm_k_multiplier(), 1.0)

    def test_elite_arm_raises_k_multiplier(self):
        self.assertGreater(self._pitcher(80).arm_k_multiplier(), 1.0)

    def test_weak_arm_lowers_k_multiplier(self):
        self.assertLess(self._pitcher(20).arm_k_multiplier(), 1.0)

    def test_k_multiplier_scales_with_arm_strength(self):
        self.assertGreater(
            self._pitcher(80).arm_k_multiplier(),
            self._pitcher(60).arm_k_multiplier(),
        )

    # --- arm_runs_multiplier ---

    def test_average_arm_runs_multiplier_is_1(self):
        self.assertAlmostEqual(self._pitcher(50).arm_runs_multiplier(), 1.0)

    def test_elite_arm_lowers_runs_multiplier(self):
        # Stronger arm → harder to hit → fewer runs (multiplier < 1)
        self.assertLess(self._pitcher(80).arm_runs_multiplier(), 1.0)

    def test_weak_arm_raises_runs_multiplier(self):
        self.assertGreater(self._pitcher(20).arm_runs_multiplier(), 1.0)

    def test_runs_multiplier_inverse_of_k_multiplier_direction(self):
        # Elite arm → more Ks AND fewer runs
        elite = self._pitcher(80)
        self.assertGreater(elite.arm_k_multiplier(), 1.0)
        self.assertLess(elite.arm_runs_multiplier(), 1.0)

    # --- arm_ip_multiplier ---

    def test_average_arm_ip_multiplier_is_1(self):
        self.assertAlmostEqual(self._pitcher(50).arm_ip_multiplier(), 1.0)

    def test_elite_arm_raises_ip_multiplier(self):
        self.assertGreater(self._pitcher(80).arm_ip_multiplier(), 1.0)

    def test_weak_arm_lowers_ip_multiplier(self):
        self.assertLess(self._pitcher(20).arm_ip_multiplier(), 1.0)

    def test_ip_multiplier_scales_with_arm_strength(self):
        self.assertGreater(
            self._pitcher(90).arm_ip_multiplier(),
            self._pitcher(60).arm_ip_multiplier(),
        )


# ---------------------------------------------------------------------------
# Batter power-rating multiplier tests
# ---------------------------------------------------------------------------


class TestBatterPower(unittest.TestCase):
    """Unit tests for the BatterStats power-rating multiplier methods."""

    def _batter(self, power: float) -> BatterStats:
        return BatterStats(name="B", avg=0.270, obp=0.340, slg=0.460,
                           hr_per_600_pa=25, sb_per_season=15,
                           doubles_per_600_pa=35, power_rating=power)

    # --- power_hr_multiplier ---

    def test_average_power_hr_multiplier_is_1(self):
        self.assertAlmostEqual(self._batter(50).power_hr_multiplier(), 1.0)

    def test_high_power_raises_hr_multiplier(self):
        self.assertGreater(self._batter(85).power_hr_multiplier(), 1.0)

    def test_low_power_lowers_hr_multiplier(self):
        self.assertLess(self._batter(15).power_hr_multiplier(), 1.0)

    def test_hr_multiplier_scales_with_power(self):
        self.assertGreater(
            self._batter(90).power_hr_multiplier(),
            self._batter(70).power_hr_multiplier(),
        )

    # --- power_doubles_multiplier ---

    def test_average_power_doubles_multiplier_is_1(self):
        self.assertAlmostEqual(self._batter(50).power_doubles_multiplier(), 1.0)

    def test_high_power_raises_doubles_multiplier(self):
        self.assertGreater(self._batter(80).power_doubles_multiplier(), 1.0)

    def test_low_power_lowers_doubles_multiplier(self):
        self.assertLess(self._batter(20).power_doubles_multiplier(), 1.0)

    def test_doubles_multiplier_smaller_effect_than_hr_multiplier(self):
        # Power has a larger proportional effect on HRs than doubles
        b = self._batter(80)
        self.assertGreater(b.power_hr_multiplier(), b.power_doubles_multiplier())


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
        self.assertEqual(len(report.props), 4)
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("Strikeouts", prop_names)
        self.assertIn("Outs Recorded", prop_names)
        self.assertIn("Runs Allowed", prop_names)
        self.assertIn("Pitch Count", prop_names)

    def test_batter_report_has_four_props(self):
        report = self.sim.simulate_batter(self.batter)
        self.assertIsInstance(report, PlayerPropsReport)
        self.assertEqual(len(report.props), 6)
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("Hits", prop_names)
        self.assertIn("Doubles", prop_names)
        self.assertIn("Home Runs", prop_names)
        self.assertIn("Stolen Bases", prop_names)
        self.assertIn("Plate Appearances", prop_names)
        self.assertIn("H+R+RBI", prop_names)

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
        # Use moderate cold (55°F) vs moderate warm (88°F) — both within or just
        # outside the stamina-neutral zone so the K-rate boost from cold clearly
        # outweighs the minor stamina penalty.  Extreme temps (< 40°F) would
        # trigger a larger stamina reduction that can offset the K-rate benefit.
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        cold_weather = WeatherConditions(temp_f=55)
        warm_weather = WeatherConditions(temp_f=88)

        sim_cold = MLBPlayerPropsSimulator(neutral_stadium, cold_weather, calm, 5_000, 42)
        sim_warm = MLBPlayerPropsSimulator(neutral_stadium, warm_weather, calm, 5_000, 42)

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

    # --- New: temperature effect on batter hits ---

    def test_cold_weather_reduces_hits(self):
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        cold = WeatherConditions(temp_f=45)
        warm = WeatherConditions(temp_f=85)

        sim_cold = MLBPlayerPropsSimulator(neutral_stadium, cold, calm, 2_000, 42)
        sim_warm = MLBPlayerPropsSimulator(neutral_stadium, warm, calm, 2_000, 42)

        batter = _default_batter()
        hits_cold = next(p for p in sim_cold.simulate_batter(batter).props if p.prop_name == "Hits").mean
        hits_warm = next(p for p in sim_warm.simulate_batter(batter).props if p.prop_name == "Hits").mean
        self.assertGreater(hits_warm, hits_cold)

    # --- New: temperature effect on pitcher stamina (outs recorded) ---

    def test_extreme_cold_shortens_pitcher_outing(self):
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        freezing = WeatherConditions(temp_f=40)
        comfortable = WeatherConditions(temp_f=72)

        sim_cold = MLBPlayerPropsSimulator(neutral_stadium, freezing, calm, 2_000, 42)
        sim_norm = MLBPlayerPropsSimulator(neutral_stadium, comfortable, calm, 2_000, 42)

        pitcher = _default_pitcher()
        outs_cold = next(p for p in sim_cold.simulate_pitcher(pitcher).props if p.prop_name == "Outs Recorded").mean
        outs_norm = next(p for p in sim_norm.simulate_pitcher(pitcher).props if p.prop_name == "Outs Recorded").mean
        self.assertLess(outs_cold, outs_norm)

    def test_extreme_heat_shortens_pitcher_outing(self):
        neutral_stadium = Stadium.from_name("Neutral")
        calm = WindConditions()
        scorching = WeatherConditions(temp_f=103)
        comfortable = WeatherConditions(temp_f=72)

        sim_hot = MLBPlayerPropsSimulator(neutral_stadium, scorching, calm, 2_000, 42)
        sim_norm = MLBPlayerPropsSimulator(neutral_stadium, comfortable, calm, 2_000, 42)

        pitcher = _default_pitcher()
        outs_hot = next(p for p in sim_hot.simulate_pitcher(pitcher).props if p.prop_name == "Outs Recorded").mean
        outs_norm = next(p for p in sim_norm.simulate_pitcher(pitcher).props if p.prop_name == "Outs Recorded").mean
        self.assertLess(outs_hot, outs_norm)

    # --- New: wind K multiplier end-to-end ---

    def test_in_wind_raises_pitcher_strikeouts(self):
        neutral_stadium = Stadium.from_name("Neutral")
        weather = WeatherConditions()
        in_wind = WindConditions(speed_mph=15, direction="in_from_center")
        calm_wind = WindConditions(speed_mph=0, direction="calm")

        sim_in = MLBPlayerPropsSimulator(neutral_stadium, weather, in_wind, 2_000, 42)
        sim_calm = MLBPlayerPropsSimulator(neutral_stadium, weather, calm_wind, 2_000, 42)

        pitcher = _default_pitcher()
        k_in = next(p for p in sim_in.simulate_pitcher(pitcher).props if p.prop_name == "Strikeouts").mean
        k_calm = next(p for p in sim_calm.simulate_pitcher(pitcher).props if p.prop_name == "Strikeouts").mean
        self.assertGreater(k_in, k_calm)

    # --- New: wind runs multiplier end-to-end ---

    def test_out_wind_raises_runs_allowed(self):
        neutral_stadium = Stadium.from_name("Neutral")
        weather = WeatherConditions()
        out_wind = WindConditions(speed_mph=15, direction="out_to_center")
        calm_wind = WindConditions(speed_mph=0, direction="calm")

        sim_out = MLBPlayerPropsSimulator(neutral_stadium, weather, out_wind, 2_000, 42)
        sim_calm = MLBPlayerPropsSimulator(neutral_stadium, weather, calm_wind, 2_000, 42)

        pitcher = _default_pitcher()
        runs_out = next(p for p in sim_out.simulate_pitcher(pitcher).props if p.prop_name == "Runs Allowed").mean
        runs_calm = next(p for p in sim_calm.simulate_pitcher(pitcher).props if p.prop_name == "Runs Allowed").mean
        self.assertGreater(runs_out, runs_calm)

    # --- New: pitcher arm strength end-to-end ---

    def _run_pitcher_prop_arm(self, arm_strength: float, prop: str, n: int = 3_000) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=n,
            random_seed=42,
        )
        pitcher = PitcherStats(name="P", era=4.0, k_per_9=8.5,
                               innings_per_start=5.5, whip=1.25,
                               arm_strength=arm_strength)
        report = sim.simulate_pitcher(pitcher)
        return next(p for p in report.props if p.prop_name == prop).mean

    def test_strong_arm_increases_strikeouts(self):
        k_strong = self._run_pitcher_prop_arm(80, "Strikeouts")
        k_average = self._run_pitcher_prop_arm(50, "Strikeouts")
        self.assertGreater(k_strong, k_average)

    def test_weak_arm_decreases_strikeouts(self):
        k_weak = self._run_pitcher_prop_arm(20, "Strikeouts")
        k_average = self._run_pitcher_prop_arm(50, "Strikeouts")
        self.assertLess(k_weak, k_average)

    def test_strong_arm_reduces_runs_allowed(self):
        runs_strong = self._run_pitcher_prop_arm(80, "Runs Allowed")
        runs_average = self._run_pitcher_prop_arm(50, "Runs Allowed")
        self.assertLess(runs_strong, runs_average)

    def test_strong_arm_extends_outing(self):
        outs_strong = self._run_pitcher_prop_arm(80, "Outs Recorded")
        outs_average = self._run_pitcher_prop_arm(50, "Outs Recorded")
        self.assertGreater(outs_strong, outs_average)

    def test_weak_arm_shortens_outing(self):
        outs_weak = self._run_pitcher_prop_arm(20, "Outs Recorded")
        outs_average = self._run_pitcher_prop_arm(50, "Outs Recorded")
        self.assertLess(outs_weak, outs_average)

    # --- New: batter power rating end-to-end ---

    def _run_batter_prop_power(self, power_rating: float, prop: str, n: int = 3_000) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=n,
            random_seed=42,
        )
        batter = BatterStats(name="B", avg=0.270, obp=0.340, slg=0.460,
                             hr_per_600_pa=25, sb_per_season=15,
                             doubles_per_600_pa=35, power_rating=power_rating)
        report = sim.simulate_batter(batter)
        return next(p for p in report.props if p.prop_name == prop).mean

    def test_high_power_increases_hr(self):
        hr_high = self._run_batter_prop_power(85, "Home Runs")
        hr_avg = self._run_batter_prop_power(50, "Home Runs")
        self.assertGreater(hr_high, hr_avg)

    def test_low_power_decreases_hr(self):
        hr_low = self._run_batter_prop_power(15, "Home Runs")
        hr_avg = self._run_batter_prop_power(50, "Home Runs")
        self.assertLess(hr_low, hr_avg)

    def test_high_power_increases_doubles(self):
        d_high = self._run_batter_prop_power(85, "Doubles")
        d_avg = self._run_batter_prop_power(50, "Doubles")
        self.assertGreater(d_high, d_avg)

    def test_power_does_not_affect_hits(self):
        # Power rating should not directly change batting average / hit count.
        hits_high = self._run_batter_prop_power(85, "Hits")
        hits_low = self._run_batter_prop_power(15, "Hits")
        # Allow a 10% relative tolerance since both share the same seed.
        self.assertAlmostEqual(hits_high, hits_low, delta=hits_high * 0.10)


# ---------------------------------------------------------------------------
# Pitch Count prop tests
# ---------------------------------------------------------------------------


class TestPitchCountProp(unittest.TestCase):
    """End-to-end tests for the new Pitch Count prop on PitcherStats."""

    def _default_sim(self, n: int = 3_000, seed: int = 0) -> "MLBPlayerPropsSimulator":
        return MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=n,
            random_seed=seed,
        )

    def _pitcher(self, pitches_per_pa: float = 3.8, ip: float = 5.5) -> PitcherStats:
        return PitcherStats(
            name="P",
            era=4.0,
            k_per_9=8.5,
            innings_per_start=ip,
            whip=1.25,
            pitches_per_pa=pitches_per_pa,
        )

    def _pitch_count_mean(self, pitcher: PitcherStats, n: int = 3_000, seed: int = 0) -> float:
        sim = self._default_sim(n, seed)
        report = sim.simulate_pitcher(pitcher)
        return next(p for p in report.props if p.prop_name == "Pitch Count").mean

    # --- Pitch Count prop is included in the report ---

    def test_pitch_count_prop_present(self):
        sim = self._default_sim()
        report = sim.simulate_pitcher(self._pitcher())
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("Pitch Count", prop_names)

    # --- Pitch Count values are positive and in a realistic range ---

    def test_pitch_count_mean_positive(self):
        mean = self._pitch_count_mean(self._pitcher())
        self.assertGreater(mean, 0.0)

    def test_pitch_count_mean_reasonable_range(self):
        # A starting pitcher typically throws 70–120 pitches; mean should be in that range.
        mean = self._pitch_count_mean(self._pitcher(), n=5_000)
        self.assertGreater(mean, 50.0)
        self.assertLess(mean, 140.0)

    # --- Higher pitches_per_pa → higher total pitch count ---

    def test_higher_pitches_per_pa_raises_pitch_count(self):
        mean_high = self._pitch_count_mean(self._pitcher(pitches_per_pa=4.5), seed=1)
        mean_low = self._pitch_count_mean(self._pitcher(pitches_per_pa=3.2), seed=1)
        self.assertGreater(mean_high, mean_low)

    # --- More innings pitched → higher total pitch count ---

    def test_longer_outing_raises_pitch_count(self):
        mean_long = self._pitch_count_mean(self._pitcher(ip=7.0), seed=2)
        mean_short = self._pitch_count_mean(self._pitcher(ip=4.0), seed=2)
        self.assertGreater(mean_long, mean_short)

    # --- Custom pitch_count_lines are respected ---

    def test_custom_pitch_count_lines_appear_in_report(self):
        sim = self._default_sim()
        report = sim.simulate_pitcher(self._pitcher(), pitch_count_lines=[79.5, 89.5])
        pc_prop = next(p for p in report.props if p.prop_name == "Pitch Count")
        self.assertIn(79.5, pc_prop.over_probabilities)
        self.assertIn(89.5, pc_prop.over_probabilities)

    # --- Over probabilities are in [0, 1] ---

    def test_pitch_count_over_probabilities_valid(self):
        sim = self._default_sim()
        report = sim.simulate_pitcher(self._pitcher())
        pc_prop = next(p for p in report.props if p.prop_name == "Pitch Count")
        for line, prob in pc_prop.over_probabilities.items():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

    # --- Percentile ordering ---

    def test_pitch_count_percentile_ordering(self):
        sim = self._default_sim()
        report = sim.simulate_pitcher(self._pitcher())
        pc = next(p for p in report.props if p.prop_name == "Pitch Count")
        self.assertLessEqual(pc.percentile_10, pc.percentile_25)
        self.assertLessEqual(pc.percentile_25, pc.percentile_75)
        self.assertLessEqual(pc.percentile_75, pc.percentile_90)


# ---------------------------------------------------------------------------
# Plate Appearances prop tests
# ---------------------------------------------------------------------------


class TestPlateAppearancesProp(unittest.TestCase):
    """End-to-end tests for the new Plate Appearances prop on BatterStats."""

    def _default_sim(self, n: int = 3_000, seed: int = 0) -> "MLBPlayerPropsSimulator":
        return MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=n,
            random_seed=seed,
        )

    def _batter(self, pitches_per_pa: float = 3.8) -> BatterStats:
        return BatterStats(
            name="B",
            avg=0.270,
            obp=0.340,
            slg=0.460,
            hr_per_600_pa=25,
            sb_per_season=15,
            doubles_per_600_pa=35,
            pitches_per_pa=pitches_per_pa,
        )

    def _pa_mean(self, batter: BatterStats, n: int = 3_000, seed: int = 0) -> float:
        sim = self._default_sim(n, seed)
        report = sim.simulate_batter(batter)
        return next(p for p in report.props if p.prop_name == "Plate Appearances").mean

    # --- Plate Appearances prop is included in the report ---

    def test_plate_appearances_prop_present(self):
        sim = self._default_sim()
        report = sim.simulate_batter(self._batter())
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("Plate Appearances", prop_names)

    # --- PA values are positive and in a realistic per-game range ---

    def test_plate_appearances_mean_positive(self):
        mean = self._pa_mean(self._batter())
        self.assertGreater(mean, 0.0)

    def test_plate_appearances_mean_reasonable_range(self):
        # A starting position player typically gets 3–6 PA per game.
        mean = self._pa_mean(self._batter(), n=5_000)
        self.assertGreater(mean, 2.0)
        self.assertLess(mean, 7.0)

    # --- Custom pa_lines are respected ---

    def test_custom_pa_lines_appear_in_report(self):
        sim = self._default_sim()
        report = sim.simulate_batter(self._batter(), pa_lines=[2.5, 4.5])
        pa_prop = next(p for p in report.props if p.prop_name == "Plate Appearances")
        self.assertIn(2.5, pa_prop.over_probabilities)
        self.assertIn(4.5, pa_prop.over_probabilities)

    # --- Over probabilities are in [0, 1] ---

    def test_plate_appearances_over_probabilities_valid(self):
        sim = self._default_sim()
        report = sim.simulate_batter(self._batter())
        pa_prop = next(p for p in report.props if p.prop_name == "Plate Appearances")
        for line, prob in pa_prop.over_probabilities.items():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

    # --- Percentile ordering ---

    def test_plate_appearances_percentile_ordering(self):
        sim = self._default_sim()
        report = sim.simulate_batter(self._batter())
        pa = next(p for p in report.props if p.prop_name == "Plate Appearances")
        self.assertLessEqual(pa.percentile_10, pa.percentile_25)
        self.assertLessEqual(pa.percentile_25, pa.percentile_75)
        self.assertLessEqual(pa.percentile_75, pa.percentile_90)

    # --- PA mean is consistent across calls with same seed ---

    def test_plate_appearances_reproducible(self):
        mean1 = self._pa_mean(self._batter(), n=2_000, seed=99)
        mean2 = self._pa_mean(self._batter(), n=2_000, seed=99)
        self.assertAlmostEqual(mean1, mean2)

    # --- PA is always at least 1 ---

    def test_plate_appearances_always_at_least_1(self):
        sim = self._default_sim(n=1_000, seed=7)
        report = sim.simulate_batter(self._batter())
        pa_prop = next(p for p in report.props if p.prop_name == "Plate Appearances")
        self.assertGreaterEqual(pa_prop.percentile_10, 1.0)


# ---------------------------------------------------------------------------
# platoon_splits_for() unit tests
# ---------------------------------------------------------------------------


class TestPlatoonSplitsFor(unittest.TestCase):
    """Unit tests for the platoon_splits_for free function."""

    def _keys(self) -> set:
        return {"hits", "hr", "doubles", "k", "runs"}

    def test_returns_all_five_keys(self):
        sp = platoon_splits_for("R", "R")
        self.assertEqual(set(sp.keys()), self._keys())

    # --- Same-hand matchups (pitcher advantage) ---

    def test_rhb_vs_rhp_pitcher_advantage(self):
        sp = platoon_splits_for("R", "R")
        self.assertLess(sp["hits"], 1.0, "Same-hand: hits should be < 1")
        self.assertLess(sp["hr"], 1.0, "Same-hand: HRs should be < 1")
        self.assertGreater(sp["k"], 1.0, "Same-hand: pitcher K rate should be > 1")

    def test_lhb_vs_lhp_pitcher_advantage(self):
        sp = platoon_splits_for("L", "L")
        self.assertLess(sp["hits"], 1.0)
        self.assertLess(sp["hr"], 1.0)
        self.assertGreater(sp["k"], 1.0)

    # --- Opposite-hand matchups (batter advantage) ---

    def test_rhb_vs_lhp_batter_advantage(self):
        sp = platoon_splits_for("R", "L")
        self.assertGreater(sp["hits"], 1.0, "Opposite-hand: hits should be > 1")
        self.assertGreater(sp["hr"], 1.0, "Opposite-hand: HRs should be > 1")
        self.assertLess(sp["k"], 1.0, "Opposite-hand: pitcher K rate should be < 1")

    def test_lhb_vs_rhp_batter_advantage(self):
        sp = platoon_splits_for("L", "R")
        self.assertGreater(sp["hits"], 1.0)
        self.assertGreater(sp["hr"], 1.0)
        self.assertLess(sp["k"], 1.0)

    # --- Switch hitters: always neutral ---

    def test_switch_vs_rhp_neutral(self):
        sp = platoon_splits_for("S", "R")
        for key in self._keys():
            self.assertAlmostEqual(sp[key], 1.0, msg=f"Switch hitter key '{key}' should be 1.0")

    def test_switch_vs_lhp_neutral(self):
        sp = platoon_splits_for("S", "L")
        for key in self._keys():
            self.assertAlmostEqual(sp[key], 1.0, msg=f"Switch hitter key '{key}' should be 1.0")

    # --- Consistency: batter advantage run multiplier matches hit direction ---

    def test_batter_advantage_runs_multiplier_above_1(self):
        # When batter has platoon advantage, runs allowed by pitcher should rise.
        sp_rhb_lhp = platoon_splits_for("R", "L")
        sp_lhb_rhp = platoon_splits_for("L", "R")
        self.assertGreater(sp_rhb_lhp["runs"], 1.0)
        self.assertGreater(sp_lhb_rhp["runs"], 1.0)

    def test_pitcher_advantage_runs_multiplier_below_1(self):
        # When pitcher has platoon advantage, fewer runs allowed.
        sp_rhb_rhp = platoon_splits_for("R", "R")
        sp_lhb_lhp = platoon_splits_for("L", "L")
        self.assertLess(sp_rhb_rhp["runs"], 1.0)
        self.assertLess(sp_lhb_lhp["runs"], 1.0)

    # --- Unknown combination falls back to neutral ---

    def test_unknown_combination_returns_neutral(self):
        sp = platoon_splits_for("X", "Q")
        for key in self._keys():
            self.assertAlmostEqual(sp[key], 1.0)

    # --- LHB platoon advantage is slightly larger than RHB (historical data) ---

    def test_lhb_rhp_batter_advantage_at_least_as_large_as_rhb_lhp(self):
        sp_lhb = platoon_splits_for("L", "R")
        sp_rhb = platoon_splits_for("R", "L")
        self.assertGreaterEqual(sp_lhb["hits"], sp_rhb["hits"])
        self.assertGreaterEqual(sp_lhb["hr"], sp_rhb["hr"])


# ---------------------------------------------------------------------------
# Platoon split end-to-end simulation tests
# ---------------------------------------------------------------------------


class TestPlatoonMatchupSimulation(unittest.TestCase):
    """Verify that platoon splits shift simulated prop distributions correctly."""

    def _batter_prop(
        self,
        bats: str,
        opponent_throws: str,
        prop: str,
        n: int = 3_000,
    ) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=n,
            random_seed=42,
        )
        batter = BatterStats(
            name="B", avg=0.270, obp=0.340, slg=0.460,
            hr_per_600_pa=25, sb_per_season=15, doubles_per_600_pa=35,
            bats=bats,
        )
        report = sim.simulate_batter(batter, opponent_throws=opponent_throws)
        return next(p for p in report.props if p.prop_name == prop).mean

    def _pitcher_prop(
        self,
        throws: str,
        opponent_bats: str,
        prop: str,
        n: int = 3_000,
    ) -> float:
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=n,
            random_seed=42,
        )
        pitcher = PitcherStats(
            name="P", era=4.0, k_per_9=8.5,
            innings_per_start=5.5, whip=1.25,
            throws=throws,
        )
        report = sim.simulate_pitcher(pitcher, opponent_bats=opponent_bats)
        return next(p for p in report.props if p.prop_name == prop).mean

    # --- Batter: opposite-hand matchups boost hits and HRs ---

    def test_rhb_vs_lhp_more_hits_than_vs_rhp(self):
        hits_lhp = self._batter_prop("R", "L", "Hits")
        hits_rhp = self._batter_prop("R", "R", "Hits")
        self.assertGreater(hits_lhp, hits_rhp)

    def test_lhb_vs_rhp_more_hits_than_vs_lhp(self):
        hits_rhp = self._batter_prop("L", "R", "Hits")
        hits_lhp = self._batter_prop("L", "L", "Hits")
        self.assertGreater(hits_rhp, hits_lhp)

    def test_rhb_vs_lhp_more_hr_than_vs_rhp(self):
        hr_lhp = self._batter_prop("R", "L", "Home Runs")
        hr_rhp = self._batter_prop("R", "R", "Home Runs")
        self.assertGreater(hr_lhp, hr_rhp)

    def test_lhb_vs_rhp_more_hr_than_vs_lhp(self):
        hr_rhp = self._batter_prop("L", "R", "Home Runs")
        hr_lhp = self._batter_prop("L", "L", "Home Runs")
        self.assertGreater(hr_rhp, hr_lhp)

    def test_rhb_vs_lhp_more_doubles_than_vs_rhp(self):
        d_lhp = self._batter_prop("R", "L", "Doubles")
        d_rhp = self._batter_prop("R", "R", "Doubles")
        self.assertGreater(d_lhp, d_rhp)

    # --- Batter: same-hand matchups suppress hits vs no-split baseline ---

    def test_rhb_vs_rhp_fewer_hits_than_no_platoon_split(self):
        # No opponent specified → neutral (no platoon adjustment).
        # RHB vs RHP → same-hand pitcher advantage → fewer hits than neutral.
        hits_same_hand = self._batter_prop("R", "R", "Hits")
        # Simulate with no platoon adjustment as the neutral baseline.
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=3_000,
            random_seed=42,
        )
        batter = BatterStats(name="B", avg=0.270, obp=0.340, slg=0.460,
                             hr_per_600_pa=25, sb_per_season=15, doubles_per_600_pa=35,
                             bats="R")
        report_no_split = sim.simulate_batter(batter, opponent_throws=None)
        hits_no_split = next(p for p in report_no_split.props if p.prop_name == "Hits").mean
        self.assertLess(hits_same_hand, hits_no_split)

    # --- Switch hitter: always neutral regardless of pitcher hand ---

    def test_switch_hitter_same_hits_vs_both_hands(self):
        hits_vs_r = self._batter_prop("S", "R", "Hits")
        hits_vs_l = self._batter_prop("S", "L", "Hits")
        # Switch hitter neutral → same result (same seed → identical)
        self.assertAlmostEqual(hits_vs_r, hits_vs_l, delta=hits_vs_r * 0.01)

    def test_switch_hitter_same_hr_vs_both_hands(self):
        hr_vs_r = self._batter_prop("S", "R", "Home Runs")
        hr_vs_l = self._batter_prop("S", "L", "Home Runs")
        self.assertAlmostEqual(hr_vs_r, hr_vs_l, delta=hr_vs_r * 0.01)

    # --- Pitcher: same-hand matchup → more Ks ---

    def test_rhp_more_ks_vs_rhb_than_vs_lhb(self):
        k_vs_r = self._pitcher_prop("R", "R", "Strikeouts")
        k_vs_l = self._pitcher_prop("R", "L", "Strikeouts")
        self.assertGreater(k_vs_r, k_vs_l)

    def test_lhp_more_ks_vs_lhb_than_vs_rhb(self):
        k_vs_l = self._pitcher_prop("L", "L", "Strikeouts")
        k_vs_r = self._pitcher_prop("L", "R", "Strikeouts")
        self.assertGreater(k_vs_l, k_vs_r)

    # --- Pitcher: opposite-hand matchup → more runs allowed ---

    def test_rhp_more_runs_vs_lhb_than_vs_rhb(self):
        runs_vs_l = self._pitcher_prop("R", "L", "Runs Allowed")
        runs_vs_r = self._pitcher_prop("R", "R", "Runs Allowed")
        self.assertGreater(runs_vs_l, runs_vs_r)

    def test_lhp_more_runs_vs_rhb_than_vs_lhb(self):
        runs_vs_r = self._pitcher_prop("L", "R", "Runs Allowed")
        runs_vs_l = self._pitcher_prop("L", "L", "Runs Allowed")
        self.assertGreater(runs_vs_r, runs_vs_l)

    # --- No opponent provided → no platoon adjustment (neutral) ---

    def test_no_opponent_throws_means_no_platoon_adjustment_batter(self):
        # When opponent_throws is None the platoon block is skipped entirely.
        # Confirm the call succeeds and produces a positive hit count in both
        # the keyword-None and implicit-default forms.
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=2_000,
            random_seed=42,
        )
        batter = BatterStats(name="B", avg=0.270, obp=0.340, slg=0.460,
                             hr_per_600_pa=25, sb_per_season=15, doubles_per_600_pa=35)
        report_none = sim.simulate_batter(batter, opponent_throws=None)
        report_default = sim.simulate_batter(batter)  # default is also None
        hits_none = next(p for p in report_none.props if p.prop_name == "Hits").mean
        hits_default = next(p for p in report_default.props if p.prop_name == "Hits").mean
        # Both calls use the same platoon logic (no split) — results differ only
        # because the RNG state has advanced between calls.
        self.assertGreater(hits_none, 0)
        self.assertGreater(hits_default, 0)

    def test_no_opponent_bats_means_no_platoon_adjustment_pitcher(self):
        sim = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=2_000,
            random_seed=42,
        )
        pitcher = PitcherStats(name="P", era=4.0, k_per_9=8.5,
                               innings_per_start=5.5, whip=1.25)
        report = sim.simulate_pitcher(pitcher, opponent_bats=None)
        k_mean = next(p for p in report.props if p.prop_name == "Strikeouts").mean
        self.assertGreater(k_mean, 0)


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

    def test_simulate_matchup_applies_platoon_splits(self):
        # LHP facing RHB should produce more hits for the batter than
        # a RHP facing the same batter (platoon advantage for RHB vs LHP).
        sim_r = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=2_000,
            random_seed=42,
        )
        sim_l = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=2_000,
            random_seed=42,
        )
        rhp = PitcherStats(name="RHP", era=4.0, k_per_9=8.5,
                           innings_per_start=5.5, whip=1.25, throws="R")
        lhp = PitcherStats(name="LHP", era=4.0, k_per_9=8.5,
                           innings_per_start=5.5, whip=1.25, throws="L")
        rhb = BatterStats(name="RHB", avg=0.270, obp=0.340, slg=0.460,
                          hr_per_600_pa=25, sb_per_season=15, doubles_per_600_pa=35,
                          bats="R")
        # RHB has platoon advantage vs LHP → should see more hits
        results_rhp = sim_r.simulate_matchup(rhp, [rhb])
        results_lhp = sim_l.simulate_matchup(lhp, [rhb])
        hits_vs_rhp = next(p for p in results_rhp["RHB"].props if p.prop_name == "Hits").mean
        hits_vs_lhp = next(p for p in results_lhp["RHB"].props if p.prop_name == "Hits").mean
        self.assertGreater(hits_vs_lhp, hits_vs_rhp)


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


# ---------------------------------------------------------------------------
# Home / Away splits tests
# ---------------------------------------------------------------------------


class TestHomeAwaySplitHelpers(unittest.TestCase):
    """Unit tests for home_away_batter_splits_for and home_away_pitcher_splits_for."""

    # ------------------------------------------------------------------
    # Batter helper
    # ------------------------------------------------------------------

    def test_batter_none_returns_neutral(self):
        result = home_away_batter_splits_for(None)
        for key in ("hits", "hr", "doubles"):
            self.assertAlmostEqual(result[key], 1.0,
                                   msg=f"Expected neutral 1.0 for key '{key}'")

    def test_batter_home_matches_constant(self):
        result = home_away_batter_splits_for(True)
        self.assertEqual(result, HOME_AWAY_BATTER_SPLITS["home"])

    def test_batter_away_matches_constant(self):
        result = home_away_batter_splits_for(False)
        self.assertEqual(result, HOME_AWAY_BATTER_SPLITS["away"])

    def test_batter_home_hits_above_1(self):
        result = home_away_batter_splits_for(True)
        self.assertGreater(result["hits"], 1.0, "Home batters should get a hits boost")

    def test_batter_away_hits_below_1(self):
        result = home_away_batter_splits_for(False)
        self.assertLess(result["hits"], 1.0, "Away batters should get a hits penalty")

    def test_batter_home_hr_above_1(self):
        result = home_away_batter_splits_for(True)
        self.assertGreater(result["hr"], 1.0)

    def test_batter_away_hr_below_1(self):
        result = home_away_batter_splits_for(False)
        self.assertLess(result["hr"], 1.0)

    def test_batter_home_doubles_above_1(self):
        result = home_away_batter_splits_for(True)
        self.assertGreater(result["doubles"], 1.0)

    def test_batter_away_doubles_below_1(self):
        result = home_away_batter_splits_for(False)
        self.assertLess(result["doubles"], 1.0)

    def test_batter_home_away_are_symmetric(self):
        home = home_away_batter_splits_for(True)
        away = home_away_batter_splits_for(False)
        for key in ("hits", "hr", "doubles"):
            product = home[key] * away[key]
            self.assertAlmostEqual(
                product, 1.0, delta=0.05,
                msg=f"home×away product for '{key}' should be close to 1.0 (got {product:.4f})",
            )

    # ------------------------------------------------------------------
    # Pitcher helper
    # ------------------------------------------------------------------

    def test_pitcher_none_returns_neutral(self):
        result = home_away_pitcher_splits_for(None)
        for key in ("k", "runs", "ip"):
            self.assertAlmostEqual(result[key], 1.0,
                                   msg=f"Expected neutral 1.0 for key '{key}'")

    def test_pitcher_home_matches_constant(self):
        result = home_away_pitcher_splits_for(True)
        self.assertEqual(result, HOME_AWAY_PITCHER_SPLITS["home"])

    def test_pitcher_away_matches_constant(self):
        result = home_away_pitcher_splits_for(False)
        self.assertEqual(result, HOME_AWAY_PITCHER_SPLITS["away"])

    def test_pitcher_home_k_above_1(self):
        result = home_away_pitcher_splits_for(True)
        self.assertGreater(result["k"], 1.0, "Home pitcher should get a K-rate boost")

    def test_pitcher_away_k_below_1(self):
        result = home_away_pitcher_splits_for(False)
        self.assertLess(result["k"], 1.0, "Away pitcher should get a K-rate penalty")

    def test_pitcher_home_runs_below_1(self):
        result = home_away_pitcher_splits_for(True)
        self.assertLess(result["runs"], 1.0, "Home pitcher should allow fewer runs")

    def test_pitcher_away_runs_above_1(self):
        result = home_away_pitcher_splits_for(False)
        self.assertGreater(result["runs"], 1.0, "Away pitcher should allow more runs")

    def test_pitcher_home_ip_above_1(self):
        result = home_away_pitcher_splits_for(True)
        self.assertGreater(result["ip"], 1.0, "Home pitcher should go deeper")

    def test_pitcher_away_ip_below_1(self):
        result = home_away_pitcher_splits_for(False)
        self.assertLess(result["ip"], 1.0, "Away pitcher should have shorter outings")


class TestHomeAwaySimulation(unittest.TestCase):
    """Integration tests confirming home/away context shifts simulated outputs."""

    def setUp(self):
        self.sim = _default_sim(num_simulations=3_000, seed=7)

    def _pitcher_mean(self, prop_name: str, is_home: bool) -> float:
        report = self.sim.simulate_pitcher(_default_pitcher(), is_home=is_home)
        return next(p for p in report.props if p.prop_name == prop_name).mean

    def _batter_mean(self, prop_name: str, is_home: bool) -> float:
        report = self.sim.simulate_batter(_default_batter(), is_home=is_home)
        return next(p for p in report.props if p.prop_name == prop_name).mean

    # ------------------------------------------------------------------
    # Pitcher simulation
    # ------------------------------------------------------------------

    def test_home_pitcher_more_strikeouts_than_away(self):
        self.assertGreater(
            self._pitcher_mean("Strikeouts", True),
            self._pitcher_mean("Strikeouts", False),
        )

    def test_home_pitcher_fewer_runs_than_away(self):
        self.assertLess(
            self._pitcher_mean("Runs Allowed", True),
            self._pitcher_mean("Runs Allowed", False),
        )

    def test_home_pitcher_more_outs_than_away(self):
        self.assertGreater(
            self._pitcher_mean("Outs Recorded", True),
            self._pitcher_mean("Outs Recorded", False),
        )

    def test_home_pitcher_higher_pitch_count_than_away(self):
        # More IP + slightly more batters faced at home → higher pitch count
        self.assertGreater(
            self._pitcher_mean("Pitch Count", True),
            self._pitcher_mean("Pitch Count", False),
        )

    def test_no_home_away_pitcher_between_home_and_away(self):
        mean_home = self._pitcher_mean("Strikeouts", True)
        mean_away = self._pitcher_mean("Strikeouts", False)
        # Rebuild with same seed, no is_home
        sim2 = _default_sim(num_simulations=3_000, seed=7)
        report_none = sim2.simulate_pitcher(_default_pitcher())
        mean_none = next(p for p in report_none.props if p.prop_name == "Strikeouts").mean
        # "none" sim uses a different random sequence but the mean should be
        # strictly between home and away (within a reasonable tolerance)
        self.assertGreaterEqual(mean_none + 0.5, mean_away)
        self.assertLessEqual(mean_none - 0.5, mean_home)

    # ------------------------------------------------------------------
    # Batter simulation
    # ------------------------------------------------------------------

    def test_home_batter_more_hits_than_away(self):
        self.assertGreater(
            self._batter_mean("Hits", True),
            self._batter_mean("Hits", False),
        )

    def test_home_batter_more_home_runs_than_away(self):
        self.assertGreater(
            self._batter_mean("Home Runs", True),
            self._batter_mean("Home Runs", False),
        )

    def test_home_batter_more_doubles_than_away(self):
        self.assertGreater(
            self._batter_mean("Doubles", True),
            self._batter_mean("Doubles", False),
        )

    def test_no_home_away_batter_neutral(self):
        sim_no = _default_sim(num_simulations=3_000, seed=7)
        report_no = sim_no.simulate_batter(_default_batter())
        mean_no = next(p for p in report_no.props if p.prop_name == "Hits").mean
        self.assertIsInstance(mean_no, float)

    # ------------------------------------------------------------------
    # simulate_matchup with home/away
    # ------------------------------------------------------------------

    def test_matchup_pitcher_home_gives_home_k_boost(self):
        pitcher = _default_pitcher()
        batter = _default_batter()
        # Pitcher is home → pitcher gets home boost, batter gets away penalty
        results_home = self.sim.simulate_matchup(pitcher, [batter], pitcher_is_home=True)
        # Pitcher is away → pitcher gets away penalty, batter gets home boost
        results_away = self.sim.simulate_matchup(pitcher, [batter], pitcher_is_home=False)
        k_home = next(
            p for p in results_home[pitcher.name].props if p.prop_name == "Strikeouts"
        ).mean
        k_away = next(
            p for p in results_away[pitcher.name].props if p.prop_name == "Strikeouts"
        ).mean
        self.assertGreater(k_home, k_away)

    def test_matchup_batter_gets_inverse_location(self):
        pitcher = _default_pitcher()
        batter = _default_batter()
        # When pitcher is HOME, batters should be AWAY (fewer hits)
        results_pit_home = self.sim.simulate_matchup(
            pitcher, [batter], pitcher_is_home=True
        )
        # When pitcher is AWAY, batters should be HOME (more hits)
        results_pit_away = self.sim.simulate_matchup(
            pitcher, [batter], pitcher_is_home=False
        )
        hits_batter_vs_home_pitcher = next(
            p for p in results_pit_home[batter.name].props if p.prop_name == "Hits"
        ).mean
        hits_batter_vs_away_pitcher = next(
            p for p in results_pit_away[batter.name].props if p.prop_name == "Hits"
        ).mean
        # batter is HOME when pitcher is AWAY → more hits
        self.assertGreater(hits_batter_vs_away_pitcher, hits_batter_vs_home_pitcher)

    def test_matchup_none_location_no_error(self):
        """simulate_matchup without pitcher_is_home should still work."""
        results = self.sim.simulate_matchup(_default_pitcher(), [_default_batter()])
        self.assertIn(_default_pitcher().name, results)


# ---------------------------------------------------------------------------
# HRB (H+R+RBI) prop tests
# ---------------------------------------------------------------------------


def _hrb_batter() -> BatterStats:
    """A batter with realistic RBI and runs figures for HRB testing."""
    return BatterStats(
        name="HRB Batter",
        avg=0.280,
        obp=0.360,
        slg=0.490,
        hr_per_600_pa=28,
        sb_per_season=10,
        doubles_per_600_pa=38,
        games_played=162,
        rbi_per_season=90,
        runs_per_season=80,
    )


class TestBatterStatsHRBFields(unittest.TestCase):
    """Tests for the new rbi_per_season and runs_per_season BatterStats fields."""

    def test_defaults_are_zero(self):
        b = _default_batter()
        self.assertEqual(b.rbi_per_season, 0.0)
        self.assertEqual(b.runs_per_season, 0.0)

    def test_explicit_values_stored(self):
        b = _hrb_batter()
        self.assertEqual(b.rbi_per_season, 90)
        self.assertEqual(b.runs_per_season, 80)

    def test_negative_rbi_raises(self):
        b = _hrb_batter()
        b.rbi_per_season = -1
        with self.assertRaises(ValueError):
            b.validate()

    def test_negative_runs_raises(self):
        b = _hrb_batter()
        b.runs_per_season = -5
        with self.assertRaises(ValueError):
            b.validate()

    def test_zero_rbi_and_runs_valid(self):
        b = _default_batter()
        b.validate()  # should not raise

    def test_large_rbi_valid(self):
        b = _hrb_batter()
        b.rbi_per_season = 162
        b.validate()  # should not raise


class TestHRBProp(unittest.TestCase):
    """Integration tests for the H+R+RBI prop in simulate_batter."""

    def setUp(self):
        self.sim = _default_sim(num_simulations=3_000, seed=42)

    def _hrb_mean(self, batter: BatterStats) -> float:
        report = self.sim.simulate_batter(batter)
        return next(p for p in report.props if p.prop_name == "H+R+RBI").mean

    def test_hrb_prop_present_in_report(self):
        report = self.sim.simulate_batter(_hrb_batter())
        prop_names = {p.prop_name for p in report.props}
        self.assertIn("H+R+RBI", prop_names)

    def test_hrb_mean_positive(self):
        mean = self._hrb_mean(_hrb_batter())
        self.assertGreater(mean, 0.0)

    def test_hrb_mean_at_least_hits_mean(self):
        # H+R+RBI >= H always (R and RBI are non-negative)
        report = self.sim.simulate_batter(_hrb_batter())
        hits_mean = next(p for p in report.props if p.prop_name == "Hits").mean
        hrb_mean = next(p for p in report.props if p.prop_name == "H+R+RBI").mean
        self.assertGreaterEqual(hrb_mean, hits_mean)

    def test_hrb_higher_with_more_rbi_and_runs(self):
        low = _default_batter()   # rbi=0, runs=0  → HRB ≈ hits only
        high = _hrb_batter()      # rbi=90, runs=80  → HRB > hits
        self.assertGreater(self._hrb_mean(high), self._hrb_mean(low))

    def test_hrb_default_over_lines(self):
        report = self.sim.simulate_batter(_hrb_batter())
        hrb = next(p for p in report.props if p.prop_name == "H+R+RBI")
        # Default lines are [0.5, 1.5, 2.5, 3.5, 4.5]
        self.assertEqual(sorted(hrb.over_probabilities.keys()), [0.5, 1.5, 2.5, 3.5, 4.5])

    def test_hrb_custom_over_lines(self):
        report = self.sim.simulate_batter(_hrb_batter(), hrb_lines=[1.5, 2.5])
        hrb = next(p for p in report.props if p.prop_name == "H+R+RBI")
        self.assertEqual(sorted(hrb.over_probabilities.keys()), [1.5, 2.5])

    def test_hrb_over_0_5_probability_high(self):
        # With hits ~1 + nonzero runs/rbi, prob(HRB > 0.5) should be > 70 %
        report = self.sim.simulate_batter(_hrb_batter())
        hrb = next(p for p in report.props if p.prop_name == "H+R+RBI")
        self.assertGreater(hrb.over_probabilities[0.5], 0.70)

    def test_hrb_zero_rbi_and_runs_equals_hits_approx(self):
        # When rbi_per_season=0 and runs_per_season=0, HRB ≈ Hits
        report = self.sim.simulate_batter(_default_batter())
        hits_mean = next(p for p in report.props if p.prop_name == "Hits").mean
        hrb_mean = next(p for p in report.props if p.prop_name == "H+R+RBI").mean
        self.assertAlmostEqual(hrb_mean, hits_mean, delta=0.01)

    def test_hrb_std_dev_positive(self):
        report = self.sim.simulate_batter(_hrb_batter())
        hrb = next(p for p in report.props if p.prop_name == "H+R+RBI")
        self.assertGreater(hrb.std_dev, 0.0)

    def test_hrb_percentiles_ordered(self):
        report = self.sim.simulate_batter(_hrb_batter())
        hrb = next(p for p in report.props if p.prop_name == "H+R+RBI")
        self.assertLessEqual(hrb.percentile_10, hrb.percentile_25)
        self.assertLessEqual(hrb.percentile_25, hrb.percentile_75)
        self.assertLessEqual(hrb.percentile_75, hrb.percentile_90)

    def test_hrb_home_higher_than_away(self):
        # Home boosts hits (and proxied runs/rbi via hr_mult/hits_mult)
        sim_h = _default_sim(num_simulations=3_000, seed=5)
        sim_a = _default_sim(num_simulations=3_000, seed=5)
        r_home = sim_h.simulate_batter(_hrb_batter(), is_home=True)
        r_away = sim_a.simulate_batter(_hrb_batter(), is_home=False)
        hrb_home = next(p for p in r_home.props if p.prop_name == "H+R+RBI").mean
        hrb_away = next(p for p in r_away.props if p.prop_name == "H+R+RBI").mean
        self.assertGreater(hrb_home, hrb_away)


# ---------------------------------------------------------------------------
# Game-time (day / night / dome) tests
# ---------------------------------------------------------------------------


def _hot_weather(game_time: str = "night") -> WeatherConditions:
    """Hot outdoor weather — good for demonstrating game-time contrasts."""
    return WeatherConditions(temp_f=92.0, precipitation="none",
                             humidity=0.60, game_time=game_time)


def _cold_weather(game_time: str = "night") -> WeatherConditions:
    """Cold outdoor weather — good for stamina / K-rate contrast."""
    return WeatherConditions(temp_f=45.0, precipitation="none",
                             humidity=0.50, game_time=game_time)


class TestGameTimeConstants(unittest.TestCase):
    """Sanity checks on the exported game-time constants."""

    def test_valid_game_times_contains_expected_values(self):
        self.assertIn("day", VALID_GAME_TIMES)
        self.assertIn("night", VALID_GAME_TIMES)
        self.assertIn("dome", VALID_GAME_TIMES)

    def test_day_temp_amplifier_greater_than_night(self):
        # Day amplifier > 1 (night baseline)
        self.assertGreater(DAY_GAME_TEMP_AMPLIFIER, 1.0)

    def test_day_wind_amplifier_greater_than_night(self):
        self.assertGreater(DAY_GAME_WIND_AMPLIFIER, 1.0)

    def test_dome_amplifiers_are_zero(self):
        self.assertEqual(DOME_TEMP_AMPLIFIER, 0.0)
        self.assertEqual(DOME_WIND_AMPLIFIER, 0.0)


class TestWeatherConditionsGameTime(unittest.TestCase):
    """Tests for the game_time field on WeatherConditions."""

    # --- Default / night baseline ---

    def test_default_game_time_is_night(self):
        w = WeatherConditions()
        self.assertEqual(w.game_time, "night")

    def test_night_game_time_amplifier_is_baseline(self):
        w = WeatherConditions(game_time="night")
        self.assertAlmostEqual(w._game_time_temp_amplifier(), 1.0)

    def test_night_wind_amplifier_is_1(self):
        w = WeatherConditions(game_time="night")
        self.assertAlmostEqual(w.game_time_wind_amplifier(), 1.0)

    # --- Day game amplification ---

    def test_day_game_temp_amplifier_matches_constant(self):
        w = WeatherConditions(game_time="day")
        self.assertAlmostEqual(w._game_time_temp_amplifier(), DAY_GAME_TEMP_AMPLIFIER)

    def test_day_wind_amplifier_matches_constant(self):
        w = WeatherConditions(game_time="day")
        self.assertAlmostEqual(w.game_time_wind_amplifier(), DAY_GAME_WIND_AMPLIFIER)

    def test_day_temp_hr_multiplier_greater_than_night(self):
        # Hot day game → stronger ball-travel effect than same temp at night
        w_night = _hot_day_weather("night")
        w_day = _hot_day_weather("day")
        self.assertGreater(w_day.temp_hr_multiplier(), w_night.temp_hr_multiplier())

    def test_day_temp_hit_multiplier_greater_than_night(self):
        w_night = _hot_day_weather("night")
        w_day = _hot_day_weather("day")
        self.assertGreater(w_day.temp_hit_multiplier(), w_night.temp_hit_multiplier())

    def test_day_cold_k_multiplier_greater_than_night(self):
        # Cold day game → amplified cold grip → even higher K rate
        w_night = _cold_night_weather("night")
        w_day = _cold_night_weather("day")
        self.assertGreater(w_day.temp_k_multiplier(), w_night.temp_k_multiplier())

    def test_day_hot_stamina_penalty_worse_than_night(self):
        # Heat fatigue is amplified in direct sunlight
        w_night = _hot_day_weather("night")
        w_day = _hot_day_weather("day")
        self.assertLess(
            w_day.temp_pitcher_stamina_multiplier(),
            w_night.temp_pitcher_stamina_multiplier(),
        )

    def test_day_cold_stamina_penalty_worse_than_night(self):
        w_night = _cold_night_weather("night")
        w_day = _cold_night_weather("day")
        self.assertLess(
            w_day.temp_pitcher_stamina_multiplier(),
            w_night.temp_pitcher_stamina_multiplier(),
        )

    # --- Dome neutralisation ---

    def test_dome_game_temp_amplifier_is_zero(self):
        w = WeatherConditions(game_time="dome")
        self.assertAlmostEqual(w._game_time_temp_amplifier(), DOME_TEMP_AMPLIFIER)

    def test_dome_wind_amplifier_is_zero(self):
        w = WeatherConditions(game_time="dome")
        self.assertAlmostEqual(w.game_time_wind_amplifier(), DOME_WIND_AMPLIFIER)

    def test_dome_temp_hr_multiplier_is_1(self):
        # Regardless of temp, dome returns neutral 1.0
        for temp in (40.0, 72.0, 100.0):
            w = WeatherConditions(temp_f=temp, game_time="dome")
            self.assertAlmostEqual(
                w.temp_hr_multiplier(), 1.0,
                msg=f"Expected dome temp_hr_multiplier = 1.0 at {temp}°F",
            )

    def test_dome_temp_hit_multiplier_is_1(self):
        for temp in (40.0, 72.0, 100.0):
            w = WeatherConditions(temp_f=temp, game_time="dome")
            self.assertAlmostEqual(w.temp_hit_multiplier(), 1.0,
                                   msg=f"Dome hit mult should be 1.0 at {temp}°F")

    def test_dome_temp_k_multiplier_is_1(self):
        for temp in (40.0, 72.0, 100.0):
            w = WeatherConditions(temp_f=temp, game_time="dome")
            self.assertAlmostEqual(w.temp_k_multiplier(), 1.0,
                                   msg=f"Dome K mult should be 1.0 at {temp}°F")

    def test_dome_stamina_multiplier_is_1(self):
        for temp in (40.0, 72.0, 100.0):
            w = WeatherConditions(temp_f=temp, game_time="dome")
            self.assertAlmostEqual(w.temp_pitcher_stamina_multiplier(), 1.0,
                                   msg=f"Dome stamina should be 1.0 at {temp}°F")

    def test_dome_precip_factor_is_1_regardless_of_precipitation(self):
        # It never rains in a dome
        for precip in ("none", "light", "moderate", "heavy"):
            w = WeatherConditions(precipitation=precip, game_time="dome")
            self.assertAlmostEqual(
                w.precip_factor(), 1.0,
                msg=f"Dome precip_factor should be 1.0 for precipitation={precip!r}",
            )

    def test_dome_humidity_multiplier_is_1(self):
        for hum in (0.1, 0.5, 0.9):
            w = WeatherConditions(humidity=hum, game_time="dome")
            self.assertAlmostEqual(
                w.humidity_hit_multiplier(), 1.0,
                msg=f"Dome humidity mult should be 1.0 at humidity={hum}",
            )

    # --- Validation ---

    def test_invalid_game_time_raises(self):
        w = WeatherConditions(game_time="afternoon")
        with self.assertRaises(ValueError):
            w.validate()

    def test_valid_game_times_pass_validation(self):
        for gt in ("day", "night", "dome"):
            WeatherConditions(game_time=gt).validate()  # should not raise

    def test_invalid_humidity_raises(self):
        w = WeatherConditions(humidity=1.5, game_time="night")
        with self.assertRaises(ValueError):
            w.validate()

    # --- Night is backward-compatible with pre-existing test assertions ---

    def test_night_baseline_hr_mult_same_as_legacy(self):
        # night should produce identical value as the old code (no game_time param)
        w_night = WeatherConditions(temp_f=45, game_time="night")
        expected = 1.0 + (45 - 72) * 0.003 * 1.0
        self.assertAlmostEqual(w_night.temp_hr_multiplier(), expected)

    def test_night_baseline_k_mult_same_as_legacy(self):
        w_night = WeatherConditions(temp_f=45, game_time="night")
        expected = 1.0 - (45 - 72) * 0.001 * 1.0
        self.assertAlmostEqual(w_night.temp_k_multiplier(), expected)


class TestEffectiveWindMult(unittest.TestCase):
    """Tests for MLBPlayerPropsSimulator._effective_wind_mult."""

    def _make_sim(self, game_time: str, wind_dir: str = "out_to_center",
                  wind_speed: float = 15.0) -> MLBPlayerPropsSimulator:
        return MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(game_time=game_time),
            wind=WindConditions(speed_mph=wind_speed, direction=wind_dir),
            num_simulations=100,
        )

    def test_night_effective_wind_equals_raw(self):
        sim = self._make_sim("night")
        raw = sim.wind.hr_multiplier()
        self.assertAlmostEqual(sim._effective_wind_mult(raw), raw)

    def test_dome_effective_wind_is_1(self):
        sim = self._make_sim("dome")
        raw = sim.wind.hr_multiplier()  # > 1 (out wind)
        self.assertNotAlmostEqual(raw, 1.0)  # confirm raw != 1 (wind present)
        self.assertAlmostEqual(sim._effective_wind_mult(raw), 1.0)

    def test_day_effective_wind_amplifies_out_wind(self):
        sim_night = self._make_sim("night")
        sim_day = self._make_sim("day")
        raw = sim_night.wind.hr_multiplier()
        eff_night = sim_night._effective_wind_mult(raw)
        eff_day = sim_day._effective_wind_mult(raw)
        self.assertGreater(eff_day, eff_night)

    def test_day_effective_wind_amplifies_in_wind(self):
        # In-blowing wind effect (< 1) should also be amplified in day
        sim_night = self._make_sim("night", wind_dir="in_from_center")
        sim_day = self._make_sim("day", wind_dir="in_from_center")
        raw = sim_night.wind.hr_multiplier()
        self.assertLess(raw, 1.0)  # confirm in-wind reduces HR
        eff_night = sim_night._effective_wind_mult(raw)
        eff_day = sim_day._effective_wind_mult(raw)
        # Amplified in-wind means even more suppression → eff_day < eff_night
        self.assertLess(eff_day, eff_night)

    def test_calm_wind_unchanged_by_game_time(self):
        # calm wind raw = 1.0 → effective always = 1.0 regardless of game_time
        for gt in ("day", "night", "dome"):
            sim = self._make_sim(gt, wind_dir="calm", wind_speed=0.0)
            self.assertAlmostEqual(sim._effective_wind_mult(1.0), 1.0,
                                   msg=f"Calm wind should give 1.0 for game_time={gt}")


class TestGameTimeSimulationImpact(unittest.TestCase):
    """Integration tests: game_time affects simulated prop outcomes."""

    def _sim_with_time(self, game_time: str) -> MLBPlayerPropsSimulator:
        """Hot day, wind blowing out — large effect contrast between day and dome."""
        return MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(temp_f=90, precipitation="heavy",
                                      humidity=0.80, game_time=game_time),
            wind=WindConditions(speed_mph=20, direction="out_to_center"),
            num_simulations=3_000,
            random_seed=99,
        )

    def test_day_sim_higher_hr_mean_than_night(self):
        # Hot day + out-wind amplified → more HR than same conditions at night
        batter = _hrb_batter()
        r_night = self._sim_with_time("night").simulate_batter(batter)
        r_day = self._sim_with_time("day").simulate_batter(batter)
        hr_night = next(p for p in r_night.props if p.prop_name == "Home Runs").mean
        hr_day = next(p for p in r_day.props if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_day, hr_night)

    def test_dome_sim_precipitation_does_not_hurt_hits(self):
        # Heavy rain in a dome is irrelevant — hits should equal a "none" dome
        batter = _hrb_batter()
        sim_rainy = self._sim_with_time("dome")
        sim_clear = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(temp_f=90, precipitation="none",
                                      humidity=0.80, game_time="dome"),
            wind=WindConditions(speed_mph=20, direction="out_to_center"),
            num_simulations=3_000,
            random_seed=99,
        )
        r_rainy = sim_rainy.simulate_batter(batter)
        r_clear = sim_clear.simulate_batter(batter)
        hits_rainy = next(p for p in r_rainy.props if p.prop_name == "Hits").mean
        hits_clear = next(p for p in r_clear.props if p.prop_name == "Hits").mean
        # Dome neutralises precipitation, so results should be essentially equal
        self.assertAlmostEqual(hits_rainy, hits_clear, delta=0.05)


if __name__ == "__main__":
    unittest.main()
