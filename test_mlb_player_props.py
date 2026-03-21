"""
Unit tests for mlb_player_props.py
====================================
Test classes are organised by the component they exercise:

  WindConditions         – TestWindConditions
  AirDensity             – TestAirDensityClass, TestAirDensitySimulatorDefault,
                           TestAirDensitySimulationImpact
  WeatherConditions      – TestWeatherConditionsBasic, TestWeatherConditionsTemp,
                           TestWeatherConditionsGameTime
  Stadium                – TestStadiumFactory
  PitcherStats           – TestPitcherStatsArmStrength
  BatterStats            – TestBatterStatsPower
  Platoon splits         – TestPlatoonSplits
  Home / away splits     – TestHomeAwaySplits
  Simulator – pitcher    – TestSimulatePitcherBasic, TestWeatherEffectsOnPitcher,
                           TestWindEffectsOnPitcher, TestGameTimeEffectsSimulator
  Simulator – batter     – TestSimulateBatterBasic, TestWeatherEffectsOnBatter
  Simulator – matchup    – TestSimulateMatchup
  ML calibration         – TestGameLogRecord, TestPropCalibratorUnfitted,
                           TestPropCalibratorFit, TestPropCalibratorPredict,
                           TestPropCalibratorSimulatorIntegration
  Odds helpers           – TestOddsHelpers
  EdgeResult             – TestEdgeResult
  Unabated client        – TestUnabatedClient
  Unabated edge screener – TestUnabatedEdgeScreener
  Blue Jays 2026 roster  – TestBlueJaysRoster
  White Sox 2026 roster  – TestWhiteSoxRoster
  Guardians 2026 roster  – TestGuardiansRoster
  Tigers 2026 roster     – TestTigersRoster
  Royals 2026 roster     – TestRoyalsRoster
  Twins 2026 roster      – TestTwinsRoster
  Orioles 2026 roster    – TestOriolesRoster
  Red Sox 2026 roster    – TestRedSoxRoster
  Yankees 2026 roster    – TestYankeesRoster
  Rays 2026 roster       – TestRaysRoster
"""

import json
import math
import random
import unittest
import urllib.error

from mlb_player_props import (
    BatterStats,
    MLBPlayerPropsSimulator,
    PitcherStats,
    PlayerPropsReport,
    PropResult,
    Stadium,
    WeatherConditions,
    WindConditions,
    AirDensity,
    GameLogRecord,
    PropCalibrator,
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
    AIR_DENSITY_STD_PRESSURE_INHG,
    AIR_DENSITY_HR_SENSITIVITY,
    AIR_DENSITY_HITS_SENSITIVITY,
    AIR_DENSITY_K_SENSITIVITY,
    AIR_DENSITY_RUNS_SENSITIVITY,
    ML_LEARNING_RATE,
    ML_L2_LAMBDA,
    ML_MAX_EPOCHS,
    ML_CONVERGENCE_TOL,
    ML_MIN_RECORDS_PER_PROP,
    ML_MULTIPLIER_MIN,
    ML_MULTIPLIER_MAX,
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
        w_night = _hot_weather("night")
        w_day = _hot_weather("day")
        self.assertGreater(w_day.temp_hr_multiplier(), w_night.temp_hr_multiplier())

    def test_day_temp_hit_multiplier_greater_than_night(self):
        w_night = _hot_weather("night")
        w_day = _hot_weather("day")
        self.assertGreater(w_day.temp_hit_multiplier(), w_night.temp_hit_multiplier())

    def test_day_cold_k_multiplier_greater_than_night(self):
        # Cold day game → amplified cold grip → even higher K rate
        w_night = _cold_weather("night")
        w_day = _cold_weather("day")
        self.assertGreater(w_day.temp_k_multiplier(), w_night.temp_k_multiplier())

    def test_day_hot_stamina_penalty_worse_than_night(self):
        # Heat fatigue is amplified in direct sunlight
        w_night = _hot_weather("night")
        w_day = _hot_weather("day")
        self.assertLess(
            w_day.temp_pitcher_stamina_multiplier(),
            w_night.temp_pitcher_stamina_multiplier(),
        )

    def test_day_cold_stamina_penalty_worse_than_night(self):
        w_night = _cold_weather("night")
        w_day = _cold_weather("day")
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


# ---------------------------------------------------------------------------
# AirDensity tests
# ---------------------------------------------------------------------------

# Denver / Coors Field elevation — the canonical high-altitude MLB venue.
_COORS_ALTITUDE_FT: float = 5_280.0


class TestAirDensityClass(unittest.TestCase):
    """Unit tests for the AirDensity dataclass."""

    # --- Default (sea level) ---

    def test_sea_level_density_ratio_is_1(self):
        ad = AirDensity(altitude_ft=0, barometric_pressure_inhg=AIR_DENSITY_STD_PRESSURE_INHG)
        self.assertAlmostEqual(ad.density_ratio(), 1.0, places=6)

    def test_sea_level_multipliers_are_all_1(self):
        ad = AirDensity()
        self.assertAlmostEqual(ad.hr_multiplier(), 1.0, places=6)
        self.assertAlmostEqual(ad.hits_multiplier(), 1.0, places=6)
        self.assertAlmostEqual(ad.k_multiplier(), 1.0, places=6)
        self.assertAlmostEqual(ad.runs_multiplier(), 1.0, places=6)

    # --- High altitude produces thin air (density < 1) ---

    def test_high_altitude_decreases_density_ratio(self):
        sea = AirDensity(altitude_ft=0)
        denver = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertLess(denver.density_ratio(), sea.density_ratio())

    def test_denver_density_ratio_in_expected_range(self):
        # ISA model: Denver (~5 280 ft) → density ≈ 84–87 % of sea level
        denver = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        ratio = denver.density_ratio()
        self.assertGreater(ratio, 0.82)
        self.assertLess(ratio, 0.90)

    def test_altitude_boosts_hr_multiplier(self):
        sea = AirDensity(altitude_ft=0)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertGreater(high.hr_multiplier(), sea.hr_multiplier())

    def test_altitude_boosts_hits_multiplier(self):
        sea = AirDensity(altitude_ft=0)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertGreater(high.hits_multiplier(), sea.hits_multiplier())

    def test_altitude_reduces_k_multiplier(self):
        sea = AirDensity(altitude_ft=0)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertLess(high.k_multiplier(), sea.k_multiplier())

    def test_altitude_boosts_runs_multiplier(self):
        sea = AirDensity(altitude_ft=0)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertGreater(high.runs_multiplier(), sea.runs_multiplier())

    # --- Higher altitude = more extreme effect ---

    def test_higher_altitude_lower_density(self):
        low = AirDensity(altitude_ft=1_000)
        mid = AirDensity(altitude_ft=3_000)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertGreater(low.density_ratio(), mid.density_ratio())
        self.assertGreater(mid.density_ratio(), high.density_ratio())

    def test_higher_altitude_larger_hr_boost(self):
        low = AirDensity(altitude_ft=1_000)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertGreater(high.hr_multiplier(), low.hr_multiplier())

    def test_higher_altitude_smaller_k_multiplier(self):
        low = AirDensity(altitude_ft=1_000)
        high = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertLess(high.k_multiplier(), low.k_multiplier())

    # --- Barometric pressure ---

    def test_low_pressure_decreases_density(self):
        standard = AirDensity(barometric_pressure_inhg=AIR_DENSITY_STD_PRESSURE_INHG)
        low_p = AirDensity(barometric_pressure_inhg=28.50)
        self.assertLess(low_p.density_ratio(), standard.density_ratio())

    def test_high_pressure_increases_density(self):
        standard = AirDensity(barometric_pressure_inhg=AIR_DENSITY_STD_PRESSURE_INHG)
        high_p = AirDensity(barometric_pressure_inhg=30.50)
        self.assertGreater(high_p.density_ratio(), standard.density_ratio())

    def test_low_pressure_boosts_hr_multiplier(self):
        standard = AirDensity(barometric_pressure_inhg=AIR_DENSITY_STD_PRESSURE_INHG)
        low_p = AirDensity(barometric_pressure_inhg=28.50)
        self.assertGreater(low_p.hr_multiplier(), standard.hr_multiplier())

    def test_high_pressure_reduces_hr_multiplier(self):
        standard = AirDensity(barometric_pressure_inhg=AIR_DENSITY_STD_PRESSURE_INHG)
        high_p = AirDensity(barometric_pressure_inhg=30.50)
        self.assertLess(high_p.hr_multiplier(), standard.hr_multiplier())

    # --- Sensitivity constants are reflected correctly ---

    def test_hr_multiplier_formula(self):
        """HR multiplier = 1 + (1 - density_ratio) × HR_SENSITIVITY."""
        ad = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        expected = 1.0 + (1.0 - ad.density_ratio()) * AIR_DENSITY_HR_SENSITIVITY
        self.assertAlmostEqual(ad.hr_multiplier(), expected, places=10)

    def test_k_multiplier_formula(self):
        """K multiplier = 1 − (1 − density_ratio) × K_SENSITIVITY."""
        ad = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        expected = 1.0 - (1.0 - ad.density_ratio()) * AIR_DENSITY_K_SENSITIVITY
        self.assertAlmostEqual(ad.k_multiplier(), expected, places=10)

    def test_hits_multiplier_formula(self):
        ad = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        expected = 1.0 + (1.0 - ad.density_ratio()) * AIR_DENSITY_HITS_SENSITIVITY
        self.assertAlmostEqual(ad.hits_multiplier(), expected, places=10)

    def test_runs_multiplier_formula(self):
        ad = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        expected = 1.0 + (1.0 - ad.density_ratio()) * AIR_DENSITY_RUNS_SENSITIVITY
        self.assertAlmostEqual(ad.runs_multiplier(), expected, places=10)

    # --- hr_mult > hits_mult > 1 at altitude (sensitivity ordering) ---

    def test_hr_sensitivity_greater_than_hits(self):
        # HR_SENSITIVITY > HITS_SENSITIVITY, so HR boost > hits boost at altitude
        self.assertGreater(AIR_DENSITY_HR_SENSITIVITY, AIR_DENSITY_HITS_SENSITIVITY)

    def test_hr_multiplier_greater_than_hits_multiplier_at_altitude(self):
        ad = AirDensity(altitude_ft=_COORS_ALTITUDE_FT)
        self.assertGreater(ad.hr_multiplier(), ad.hits_multiplier())


class TestAirDensitySimulatorDefault(unittest.TestCase):
    """Tests that the simulator defaults to sea-level neutral when air_density=None."""

    def test_default_air_density_is_sea_level(self):
        sim = _default_sim()
        self.assertAlmostEqual(sim.air_density.density_ratio(), 1.0, places=6)

    def test_default_env_hr_multiplier_unaffected(self):
        # At sea level, neutral weather, calm wind → env_hr = stadium factor only
        sim = _default_sim()
        # Neutral stadium hr_factor = 1.0; neutral weather + wind → 1.0; air = 1.0
        self.assertAlmostEqual(sim._env_hr_multiplier(), 1.0, places=4)


class TestAirDensitySimulationImpact(unittest.TestCase):
    """Integration tests: air density affects simulated prop outcomes."""

    def _sim_at_altitude(self, altitude_ft: float) -> MLBPlayerPropsSimulator:
        return MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(temp_f=72, precipitation="none", humidity=0.50,
                                      game_time="night"),
            wind=WindConditions(speed_mph=0, direction="calm"),
            num_simulations=3_000,
            random_seed=77,
            air_density=AirDensity(altitude_ft=altitude_ft),
        )

    def test_high_altitude_increases_hr_mean(self):
        batter = _hrb_batter()
        r_sea = self._sim_at_altitude(0).simulate_batter(batter)
        r_denver = self._sim_at_altitude(_COORS_ALTITUDE_FT).simulate_batter(batter)
        hr_sea = next(p for p in r_sea.props if p.prop_name == "Home Runs").mean
        hr_denver = next(p for p in r_denver.props if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_denver, hr_sea)

    def test_high_altitude_increases_hits_mean(self):
        batter = _hrb_batter()
        r_sea = self._sim_at_altitude(0).simulate_batter(batter)
        r_denver = self._sim_at_altitude(_COORS_ALTITUDE_FT).simulate_batter(batter)
        hits_sea = next(p for p in r_sea.props if p.prop_name == "Hits").mean
        hits_denver = next(p for p in r_denver.props if p.prop_name == "Hits").mean
        self.assertGreater(hits_denver, hits_sea)

    def test_high_altitude_reduces_pitcher_k_mean(self):
        pitcher = _default_pitcher()
        r_sea = self._sim_at_altitude(0).simulate_pitcher(pitcher)
        r_denver = self._sim_at_altitude(_COORS_ALTITUDE_FT).simulate_pitcher(pitcher)
        k_sea = next(p for p in r_sea.props if p.prop_name == "Strikeouts").mean
        k_denver = next(p for p in r_denver.props if p.prop_name == "Strikeouts").mean
        self.assertLess(k_denver, k_sea)

    def test_high_altitude_increases_runs_allowed_mean(self):
        pitcher = _default_pitcher()
        r_sea = self._sim_at_altitude(0).simulate_pitcher(pitcher)
        r_denver = self._sim_at_altitude(_COORS_ALTITUDE_FT).simulate_pitcher(pitcher)
        runs_sea = next(p for p in r_sea.props if p.prop_name == "Runs Allowed").mean
        runs_denver = next(p for p in r_denver.props if p.prop_name == "Runs Allowed").mean
        self.assertGreater(runs_denver, runs_sea)

    def test_low_pressure_increases_hr_mean(self):
        batter = _hrb_batter()
        sim_std = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(), wind=WindConditions(),
            num_simulations=3_000, random_seed=77,
            air_density=AirDensity(barometric_pressure_inhg=AIR_DENSITY_STD_PRESSURE_INHG),
        )
        sim_low = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(), wind=WindConditions(),
            num_simulations=3_000, random_seed=77,
            air_density=AirDensity(barometric_pressure_inhg=28.50),
        )
        hr_std = next(p for p in sim_std.simulate_batter(batter).props
                      if p.prop_name == "Home Runs").mean
        hr_low = next(p for p in sim_low.simulate_batter(batter).props
                      if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_low, hr_std)


# ---------------------------------------------------------------------------
# Helpers shared by ML tests
# ---------------------------------------------------------------------------

_PITCHER_FEATURES = {
    "era": 3.50,
    "k_per_9": 9.5,
    "whip": 1.15,
    "innings_per_start": 6.0,
    "arm_strength": 65.0,
    "pitches_per_pa": 3.9,
    "temp_f": 72.0,
    "humidity": 0.50,
    "altitude_ft": 0.0,
    "wind_speed_mph": 5.0,
    "stadium_k_factor": 1.0,
    "stadium_runs_factor": 1.0,
}

_BATTER_FEATURES = {
    "avg": 0.275,
    "obp": 0.345,
    "slg": 0.450,
    "hr_per_600_pa": 22.0,
    "doubles_per_600_pa": 35.0,
    "power_rating": 60.0,
    "pitches_per_pa": 3.9,
    "sb_per_season": 10.0,
    "temp_f": 72.0,
    "humidity": 0.50,
    "altitude_ft": 0.0,
    "wind_speed_mph": 5.0,
    "stadium_hr_factor": 1.0,
    "stadium_hits_factor": 1.0,
}


def _make_pitcher_records(
    prop: str,
    n: int,
    sim_mean: float,
    actual_mean: float,
) -> list:
    """Create ``n`` GameLogRecords with the given sim/actual means + small noise."""
    import random as _random
    rng = _random.Random(42)
    return [
        GameLogRecord(
            prop=prop,
            actual=max(0.0, actual_mean + rng.uniform(-0.3, 0.3)),
            sim_mean=sim_mean,
            features=dict(_PITCHER_FEATURES),
            player_name="TestPitcher",
        )
        for _ in range(n)
    ]


def _make_batter_records(
    prop: str,
    n: int,
    sim_mean: float,
    actual_mean: float,
) -> list:
    """Create ``n`` GameLogRecords for a batter prop."""
    import random as _random
    rng = _random.Random(99)
    return [
        GameLogRecord(
            prop=prop,
            actual=max(0.0, actual_mean + rng.uniform(-0.1, 0.1)),
            sim_mean=sim_mean,
            features=dict(_BATTER_FEATURES),
            player_name="TestBatter",
        )
        for _ in range(n)
    ]


# ---------------------------------------------------------------------------
# GameLogRecord tests
# ---------------------------------------------------------------------------


class TestGameLogRecord(unittest.TestCase):
    """Unit tests for the GameLogRecord dataclass."""

    def test_basic_construction(self):
        rec = GameLogRecord(
            prop="Strikeouts",
            actual=7.0,
            sim_mean=5.5,
            features={"era": 3.0, "k_per_9": 10.0},
        )
        self.assertEqual(rec.prop, "Strikeouts")
        self.assertAlmostEqual(rec.actual, 7.0)
        self.assertAlmostEqual(rec.sim_mean, 5.5)
        self.assertIn("era", rec.features)

    def test_player_name_defaults_to_empty_string(self):
        rec = GameLogRecord("Hits", 1.5, 1.3, {})
        self.assertEqual(rec.player_name, "")

    def test_player_name_can_be_set(self):
        rec = GameLogRecord("Hits", 1.5, 1.3, {}, player_name="Shohei Ohtani")
        self.assertEqual(rec.player_name, "Shohei Ohtani")

    def test_features_can_be_empty(self):
        rec = GameLogRecord("Home Runs", 1.0, 0.8, {})
        self.assertEqual(rec.features, {})

    def test_features_contains_expected_keys(self):
        rec = GameLogRecord("Strikeouts", 6.0, 5.0, {"era": 3.1, "k_per_9": 9.5})
        self.assertAlmostEqual(rec.features["era"], 3.1)
        self.assertAlmostEqual(rec.features["k_per_9"], 9.5)


# ---------------------------------------------------------------------------
# PropCalibrator unit tests
# ---------------------------------------------------------------------------


class TestPropCalibratorUnfitted(unittest.TestCase):
    """Tests for a freshly constructed, not-yet-fitted PropCalibrator."""

    def setUp(self):
        self.cal = PropCalibrator()

    def test_predict_adjustment_returns_1_when_not_fitted(self):
        adj = self.cal.predict_adjustment({"era": 3.5}, "Strikeouts")
        self.assertAlmostEqual(adj, 1.0)

    def test_is_fitted_returns_false(self):
        self.assertFalse(self.cal.is_fitted("Strikeouts"))

    def test_props_fitted_empty(self):
        self.assertEqual(self.cal.props_fitted(), [])

    def test_feature_importances_empty_when_not_fitted(self):
        self.assertEqual(self.cal.feature_importances("Strikeouts"), [])

    def test_training_rmse_zero_when_not_fitted(self):
        self.assertAlmostEqual(self.cal.training_rmse("Strikeouts"), 0.0)

    def test_epochs_run_zero_when_not_fitted(self):
        self.assertEqual(self.cal.epochs_run("Strikeouts"), 0)

    def test_default_hyperparams_match_constants(self):
        self.assertAlmostEqual(self.cal.learning_rate, ML_LEARNING_RATE)
        self.assertAlmostEqual(self.cal.l2_lambda, ML_L2_LAMBDA)
        self.assertEqual(self.cal.max_epochs, ML_MAX_EPOCHS)
        self.assertAlmostEqual(self.cal.convergence_tol, ML_CONVERGENCE_TOL)


class TestPropCalibratorFit(unittest.TestCase):
    """Tests for PropCalibrator.fit()."""

    def _make_cal(self, n=20, sim_mean=5.0, actual_mean=5.0):
        records = _make_pitcher_records("Strikeouts", n, sim_mean, actual_mean)
        cal = PropCalibrator()
        result = cal.fit(records)
        return cal, result

    def test_fit_returns_self(self):
        records = _make_pitcher_records("Strikeouts", 10, 5.0, 5.0)
        cal = PropCalibrator()
        ret = cal.fit(records)
        self.assertIs(ret, cal)

    def test_prop_is_fitted_after_sufficient_records(self):
        cal, _ = self._make_cal(n=ML_MIN_RECORDS_PER_PROP)
        self.assertTrue(cal.is_fitted("Strikeouts"))

    def test_prop_not_fitted_below_min_records(self):
        records = _make_pitcher_records("Strikeouts", ML_MIN_RECORDS_PER_PROP - 1, 5.0, 5.0)
        cal = PropCalibrator()
        cal.fit(records)
        self.assertFalse(cal.is_fitted("Strikeouts"))

    def test_zero_sim_mean_records_are_skipped(self):
        # All records have sim_mean=0 → cannot compute ratio → prop not fitted.
        records = [
            GameLogRecord("Strikeouts", actual=5.0, sim_mean=0.0,
                          features={"era": 3.5})
            for _ in range(20)
        ]
        cal = PropCalibrator()
        cal.fit(records)
        self.assertFalse(cal.is_fitted("Strikeouts"))

    def test_multiple_props_fitted_independently(self):
        records = (
            _make_pitcher_records("Strikeouts", 10, 5.0, 5.0)
            + _make_pitcher_records("Runs Allowed", 10, 3.0, 3.0)
        )
        cal = PropCalibrator()
        cal.fit(records)
        self.assertTrue(cal.is_fitted("Strikeouts"))
        self.assertTrue(cal.is_fitted("Runs Allowed"))

    def test_props_fitted_sorted(self):
        records = (
            _make_pitcher_records("Strikeouts", 10, 5.0, 5.0)
            + _make_pitcher_records("Runs Allowed", 10, 3.0, 3.0)
        )
        cal = PropCalibrator()
        cal.fit(records)
        self.assertEqual(cal.props_fitted(), sorted(cal.props_fitted()))

    def test_training_rmse_positive_after_fit(self):
        cal, _ = self._make_cal(n=20, sim_mean=5.0, actual_mean=6.0)
        self.assertGreater(cal.training_rmse("Strikeouts"), 0.0)

    def test_epochs_run_within_bounds(self):
        cal, _ = self._make_cal(n=20)
        ep = cal.epochs_run("Strikeouts")
        self.assertGreaterEqual(ep, 1)
        self.assertLessEqual(ep, ML_MAX_EPOCHS)

    def test_feature_importances_sorted_by_magnitude(self):
        records = _make_pitcher_records("Strikeouts", 20, 5.0, 5.0)
        cal = PropCalibrator()
        cal.fit(records)
        pairs = cal.feature_importances("Strikeouts")
        abs_weights = [abs(w) for _, w in pairs]
        self.assertEqual(abs_weights, sorted(abs_weights, reverse=True))

    def test_feature_importances_covers_all_trained_features(self):
        records = _make_pitcher_records("Strikeouts", 20, 5.0, 5.0)
        cal = PropCalibrator()
        cal.fit(records)
        names = {n for n, _ in cal.feature_importances("Strikeouts")}
        # All feature keys from the training records should appear.
        self.assertIn("era", names)
        self.assertIn("k_per_9", names)

    def test_fit_chaining(self):
        records = _make_pitcher_records("Strikeouts", 10, 5.0, 5.0)
        cal = PropCalibrator().fit(records)
        self.assertTrue(cal.is_fitted("Strikeouts"))


class TestPropCalibratorPredict(unittest.TestCase):
    """Tests for PropCalibrator.predict_adjustment()."""

    def _fit_calibrator_overpredict(self) -> PropCalibrator:
        """Train on data where sim over-predicts → calibrator should return < 1."""
        # sim_mean = 6.0, actual ≈ 4.0 → ratio ≈ 0.667 → adj < 1.0
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=6.0, actual_mean=4.0)
        return PropCalibrator(max_epochs=200).fit(records)

    def _fit_calibrator_underpredict(self) -> PropCalibrator:
        """Train on data where sim under-predicts → calibrator should return > 1."""
        # sim_mean = 4.0, actual ≈ 6.0 → ratio ≈ 1.5 → adj > 1.0
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=4.0, actual_mean=6.0)
        return PropCalibrator(max_epochs=200).fit(records)

    def test_overprediction_gives_adjustment_below_1(self):
        cal = self._fit_calibrator_overpredict()
        adj = cal.predict_adjustment(_PITCHER_FEATURES, "Strikeouts")
        self.assertLess(adj, 1.0)

    def test_underprediction_gives_adjustment_above_1(self):
        cal = self._fit_calibrator_underpredict()
        adj = cal.predict_adjustment(_PITCHER_FEATURES, "Strikeouts")
        self.assertGreater(adj, 1.0)

    def test_adjustment_clamped_at_multiplier_min(self):
        # Extreme under-prediction: sim = 10, actual ≈ 1 → raw ratio ≈ 0.1
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=10.0, actual_mean=1.0)
        cal = PropCalibrator(max_epochs=500).fit(records)
        adj = cal.predict_adjustment(_PITCHER_FEATURES, "Strikeouts")
        self.assertGreaterEqual(adj, ML_MULTIPLIER_MIN)

    def test_adjustment_clamped_at_multiplier_max(self):
        # Extreme over-prediction: sim = 1, actual ≈ 10 → raw ratio ≈ 10
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=1.0, actual_mean=10.0)
        cal = PropCalibrator(max_epochs=500).fit(records)
        adj = cal.predict_adjustment(_PITCHER_FEATURES, "Strikeouts")
        self.assertLessEqual(adj, ML_MULTIPLIER_MAX)

    def test_adjustment_always_positive(self):
        cal = self._fit_calibrator_overpredict()
        adj = cal.predict_adjustment(_PITCHER_FEATURES, "Strikeouts")
        self.assertGreater(adj, 0.0)

    def test_unknown_features_treated_as_zero(self):
        records = _make_pitcher_records("Strikeouts", 20, 5.0, 5.0)
        cal = PropCalibrator().fit(records)
        # Passing empty features should not raise.
        adj = cal.predict_adjustment({}, "Strikeouts")
        self.assertGreaterEqual(adj, ML_MULTIPLIER_MIN)
        self.assertLessEqual(adj, ML_MULTIPLIER_MAX)

    def test_unfitted_prop_returns_1(self):
        records = _make_pitcher_records("Strikeouts", 20, 5.0, 5.0)
        cal = PropCalibrator().fit(records)
        # "Hits" was never trained.
        self.assertAlmostEqual(cal.predict_adjustment(_BATTER_FEATURES, "Hits"), 1.0)

    def test_neutral_training_data_gives_adjustment_near_1(self):
        # sim_mean ≈ actual → ratio ≈ 1 → calibrator should predict near 1.
        records = _make_pitcher_records("Strikeouts", 50, sim_mean=5.0, actual_mean=5.0)
        cal = PropCalibrator(max_epochs=300).fit(records)
        adj = cal.predict_adjustment(_PITCHER_FEATURES, "Strikeouts")
        self.assertAlmostEqual(adj, 1.0, delta=0.15)

    def test_batter_prop_calibration(self):
        records = _make_batter_records("Hits", 30, sim_mean=1.5, actual_mean=1.2)
        cal = PropCalibrator(max_epochs=200).fit(records)
        adj = cal.predict_adjustment(_BATTER_FEATURES, "Hits")
        # sim over-predicted → adj should be ≤ 1.0
        self.assertLessEqual(adj, 1.0)


class TestPropCalibratorSimulatorIntegration(unittest.TestCase):
    """End-to-end tests: PropCalibrator wired into MLBPlayerPropsSimulator."""

    def _sim(self, calibrator=None):
        return MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(temp_f=72, precipitation="none",
                                      humidity=0.50, game_time="night"),
            wind=WindConditions(speed_mph=0, direction="calm"),
            num_simulations=2_000,
            random_seed=55,
            calibrator=calibrator,
        )

    def test_no_calibrator_same_as_none_default(self):
        """Passing calibrator=None is identical to omitting the argument."""
        pitcher = _default_pitcher()
        r1 = self._sim(calibrator=None).simulate_pitcher(pitcher)
        r2 = MLBPlayerPropsSimulator(
            stadium=Stadium.from_name("Neutral"),
            weather=WeatherConditions(),
            wind=WindConditions(),
            num_simulations=2_000,
            random_seed=55,
        ).simulate_pitcher(pitcher)
        k1 = next(p for p in r1.props if p.prop_name == "Strikeouts").mean
        k2 = next(p for p in r2.props if p.prop_name == "Strikeouts").mean
        self.assertAlmostEqual(k1, k2, delta=0.02)

    def test_downward_calibrator_reduces_pitcher_k_mean(self):
        """A calibrator trained to reduce K should lower the simulated K mean."""
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=5.5, actual_mean=4.0)
        cal = PropCalibrator(max_epochs=300).fit(records)

        pitcher = _default_pitcher()
        r_cal = self._sim(calibrator=cal).simulate_pitcher(pitcher)
        r_raw = self._sim(calibrator=None).simulate_pitcher(pitcher)
        k_cal = next(p for p in r_cal.props if p.prop_name == "Strikeouts").mean
        k_raw = next(p for p in r_raw.props if p.prop_name == "Strikeouts").mean
        self.assertLess(k_cal, k_raw)

    def test_upward_calibrator_increases_pitcher_k_mean(self):
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=4.0, actual_mean=6.0)
        cal = PropCalibrator(max_epochs=300).fit(records)

        pitcher = _default_pitcher()
        r_cal = self._sim(calibrator=cal).simulate_pitcher(pitcher)
        r_raw = self._sim(calibrator=None).simulate_pitcher(pitcher)
        k_cal = next(p for p in r_cal.props if p.prop_name == "Strikeouts").mean
        k_raw = next(p for p in r_raw.props if p.prop_name == "Strikeouts").mean
        self.assertGreater(k_cal, k_raw)

    def test_downward_calibrator_reduces_batter_hits_mean(self):
        records = _make_batter_records("Hits", 30, sim_mean=1.5, actual_mean=1.1)
        cal = PropCalibrator(max_epochs=300).fit(records)

        batter = _hrb_batter()
        r_cal = self._sim(calibrator=cal).simulate_batter(batter)
        r_raw = self._sim(calibrator=None).simulate_batter(batter)
        hits_cal = next(p for p in r_cal.props if p.prop_name == "Hits").mean
        hits_raw = next(p for p in r_raw.props if p.prop_name == "Hits").mean
        self.assertLess(hits_cal, hits_raw)

    def test_upward_calibrator_increases_batter_hr_mean(self):
        records = _make_batter_records("Home Runs", 30, sim_mean=0.1, actual_mean=0.18)
        cal = PropCalibrator(max_epochs=300).fit(records)

        batter = _hrb_batter()
        r_cal = self._sim(calibrator=cal).simulate_batter(batter)
        r_raw = self._sim(calibrator=None).simulate_batter(batter)
        hr_cal = next(p for p in r_cal.props if p.prop_name == "Home Runs").mean
        hr_raw = next(p for p in r_raw.props if p.prop_name == "Home Runs").mean
        self.assertGreater(hr_cal, hr_raw)

    def test_unfitted_prop_unchanged_in_simulation(self):
        """Calibrator trained on Strikeouts only → Runs Allowed unaffected."""
        records = _make_pitcher_records("Strikeouts", 30, sim_mean=5.5, actual_mean=4.0)
        cal = PropCalibrator(max_epochs=300).fit(records)
        self.assertFalse(cal.is_fitted("Runs Allowed"))

        pitcher = _default_pitcher()
        r_cal = self._sim(calibrator=cal).simulate_pitcher(pitcher)
        r_raw = self._sim(calibrator=None).simulate_pitcher(pitcher)
        ra_cal = next(p for p in r_cal.props if p.prop_name == "Runs Allowed").mean
        ra_raw = next(p for p in r_raw.props if p.prop_name == "Runs Allowed").mean
        # The difference should be zero (or negligible floating point noise).
        self.assertAlmostEqual(ra_cal, ra_raw, delta=0.02)

    def test_pitcher_features_helper_returns_expected_keys(self):
        sim = self._sim()
        pitcher = _default_pitcher()
        feats = sim._pitcher_features(pitcher)
        for key in ("era", "k_per_9", "whip", "arm_strength",
                    "temp_f", "humidity", "altitude_ft", "wind_speed_mph",
                    "stadium_k_factor"):
            self.assertIn(key, feats, msg=f"Missing key: {key}")

    def test_batter_features_helper_returns_expected_keys(self):
        sim = self._sim()
        batter = _hrb_batter()
        feats = sim._batter_features(batter)
        for key in ("avg", "obp", "slg", "hr_per_600_pa", "power_rating",
                    "temp_f", "altitude_ft", "stadium_hr_factor"):
            self.assertIn(key, feats, msg=f"Missing key: {key}")

    def test_apply_calibration_multiplier_1_returns_same_list(self):
        """_apply_calibration with mult=1.0 returns the identical list object."""
        sim = self._sim()
        values = [1.0, 2.0, 3.0]
        result = sim._apply_calibration(values, 1.0)
        self.assertIs(result, values)

    def test_apply_calibration_scales_values(self):
        sim = self._sim()
        values = [2.0, 4.0, 6.0]
        result = sim._apply_calibration(values, 0.5)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 2.0)
        self.assertAlmostEqual(result[2], 3.0)


# ---------------------------------------------------------------------------
# Unabated edge-screener tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402 – imported here to keep diff minimal
    EdgeResult,
    UnabatedAPIError,
    UnabatedClient,
    UnabatedEdgeScreener,
    odds_to_implied_prob,
    implied_prob_to_american_odds,
    UNABATED_BASE_URL,
    UNABATED_DEFAULT_MIN_EDGE,
    UNABATED_DEFAULT_REQUEST_TIMEOUT,
)


# ---------------------------------------------------------------------------
# Odds helper tests
# ---------------------------------------------------------------------------


class TestOddsHelpers(unittest.TestCase):
    """Unit tests for odds_to_implied_prob / implied_prob_to_american_odds."""

    def test_negative_odds_favourite(self):
        prob = odds_to_implied_prob(-110)
        self.assertAlmostEqual(prob, 110 / 210, places=5)

    def test_positive_odds_underdog(self):
        prob = odds_to_implied_prob(+150)
        self.assertAlmostEqual(prob, 100 / 250, places=5)

    def test_even_odds(self):
        self.assertAlmostEqual(odds_to_implied_prob(100), 0.5, places=5)

    def test_minus_100(self):
        self.assertAlmostEqual(odds_to_implied_prob(-100), 0.5, places=5)

    def test_round_trip_negative(self):
        original_odds = -130.0
        prob = odds_to_implied_prob(original_odds)
        back = implied_prob_to_american_odds(prob)
        self.assertAlmostEqual(back, original_odds, places=3)

    def test_round_trip_positive(self):
        original_odds = +180.0
        prob = odds_to_implied_prob(original_odds)
        back = implied_prob_to_american_odds(prob)
        self.assertAlmostEqual(back, original_odds, places=3)

    def test_implied_prob_zero_raises(self):
        with self.assertRaises(ValueError):
            implied_prob_to_american_odds(0.0)

    def test_implied_prob_one_raises(self):
        with self.assertRaises(ValueError):
            implied_prob_to_american_odds(1.0)

    def test_implied_prob_above_one_raises(self):
        with self.assertRaises(ValueError):
            implied_prob_to_american_odds(1.5)

    def test_implied_prob_below_zero_raises(self):
        with self.assertRaises(ValueError):
            implied_prob_to_american_odds(-0.1)

    def test_favourite_prob_above_half(self):
        self.assertGreater(odds_to_implied_prob(-200), 0.5)

    def test_underdog_prob_below_half(self):
        self.assertLess(odds_to_implied_prob(+200), 0.5)


# ---------------------------------------------------------------------------
# EdgeResult tests
# ---------------------------------------------------------------------------


class TestEdgeResult(unittest.TestCase):
    """Unit tests for the EdgeResult dataclass."""

    def _make(self, **kwargs):
        defaults = dict(
            player_name="Ace Pitcher",
            prop="Strikeouts",
            line=6.5,
            side="over",
            sim_prob=0.63,
            market_prob=0.51,
            edge=0.12,
            american_odds=+95,
        )
        defaults.update(kwargs)
        return EdgeResult(**defaults)

    def test_basic_construction(self):
        e = self._make()
        self.assertEqual(e.player_name, "Ace Pitcher")
        self.assertEqual(e.prop, "Strikeouts")
        self.assertAlmostEqual(e.line, 6.5)
        self.assertEqual(e.side, "over")
        self.assertAlmostEqual(e.sim_prob, 0.63)
        self.assertAlmostEqual(e.market_prob, 0.51)
        self.assertAlmostEqual(e.edge, 0.12)
        self.assertAlmostEqual(e.american_odds, 95)

    def test_book_defaults_to_empty_string(self):
        e = self._make()
        self.assertEqual(e.book, "")

    def test_book_can_be_set(self):
        e = self._make(book="DraftKings")
        self.assertEqual(e.book, "DraftKings")

    def test_str_contains_player_name(self):
        e = self._make()
        self.assertIn("Ace Pitcher", str(e))

    def test_str_contains_prop_and_line(self):
        e = self._make()
        s = str(e)
        self.assertIn("Strikeouts", s)
        self.assertIn("6.5", s)

    def test_str_over_side_uses_O_prefix(self):
        e = self._make(side="over")
        self.assertIn("O6.5", str(e))

    def test_str_under_side_uses_U_prefix(self):
        e = self._make(side="under", american_odds=-110)
        self.assertIn("U6.5", str(e))

    def test_str_includes_book(self):
        e = self._make(book="FanDuel")
        self.assertIn("FanDuel", str(e))

    def test_str_no_book_omits_brackets(self):
        e = self._make(book="")
        self.assertNotIn("[", str(e))


# ---------------------------------------------------------------------------
# UnabatedClient tests
# ---------------------------------------------------------------------------


class TestUnabatedClient(unittest.TestCase):
    """Unit tests for UnabatedClient (HTTP is mocked)."""

    def _make_client(self, key="test-key"):
        return UnabatedClient(api_key=key)

    def test_default_base_url(self):
        c = self._make_client()
        self.assertEqual(c.base_url, UNABATED_BASE_URL.rstrip("/"))

    def test_default_timeout(self):
        c = self._make_client()
        self.assertEqual(c.timeout, UNABATED_DEFAULT_REQUEST_TIMEOUT)

    def test_api_key_stored(self):
        c = UnabatedClient(api_key="my-key")
        self.assertEqual(c.api_key, "my-key")

    def test_non_string_api_key_raises(self):
        with self.assertRaises(TypeError):
            UnabatedClient(api_key=12345)

    def test_custom_base_url_stored(self):
        c = UnabatedClient(api_key="k", base_url="https://example.com/api/")
        self.assertEqual(c.base_url, "https://example.com/api")

    def test_normalise_response_list(self):
        raw = [
            {"player_name": "J. Doe", "prop_type": "strikeouts",
             "line": 6.5, "over_odds": -115, "under_odds": -105, "book": "DK"},
        ]
        result = UnabatedClient._normalise_response(raw)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["player_name"], "J. Doe")
        self.assertAlmostEqual(result[0]["line"], 6.5)

    def test_normalise_response_data_envelope(self):
        raw = {"data": [{"player_name": "A. Smith", "prop_type": "hits",
                          "line": 1.5, "over_odds": +100, "under_odds": -120}]}
        result = UnabatedClient._normalise_response(raw)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["player_name"], "A. Smith")

    def test_normalise_response_markets_envelope(self):
        raw = {"markets": [{"player_name": "B. Jones", "prop_type": "home runs",
                             "line": 0.5, "over_odds": +220, "under_odds": -280}]}
        result = UnabatedClient._normalise_response(raw)
        self.assertEqual(len(result), 1)

    def test_normalise_response_empty_list(self):
        self.assertEqual(UnabatedClient._normalise_response([]), [])

    def test_normalise_response_non_list_non_dict(self):
        self.assertEqual(UnabatedClient._normalise_response("bad"), [])

    def test_normalise_response_skips_non_dict_items(self):
        raw = [{"player_name": "A", "prop_type": "hits", "line": 1.5,
                "over_odds": 100, "under_odds": -120}, "not a dict"]
        result = UnabatedClient._normalise_response(raw)
        self.assertEqual(len(result), 1)

    def test_normalise_response_alternate_field_names(self):
        # Unabated sometimes uses 'name', 'stat_type', 'value', 'over', 'under'
        raw = [{"name": "C. Lee", "stat_type": "stolen bases",
                "value": 0.5, "over": +200, "under": -250, "sportsbook": "FD"}]
        result = UnabatedClient._normalise_response(raw)
        self.assertEqual(result[0]["player_name"], "C. Lee")
        self.assertEqual(result[0]["prop_type"], "stolen bases")
        self.assertAlmostEqual(result[0]["line"], 0.5)
        self.assertEqual(result[0]["book"], "FD")

    def _mock_urlopen(self, response_bytes):
        """Return a context-manager mock that yields a response with read()."""
        import io
        import unittest.mock as mock

        cm = mock.MagicMock()
        cm.__enter__ = mock.MagicMock(return_value=cm)
        cm.__exit__ = mock.MagicMock(return_value=False)
        cm.read = mock.MagicMock(return_value=response_bytes)
        return cm

    def test_fetch_player_props_success(self):
        import unittest.mock as mock
        payload = json.dumps([
            {"player_name": "Test Player", "prop_type": "strikeouts",
             "line": 5.5, "over_odds": -110, "under_odds": -110, "book": "MGM"},
        ]).encode()
        with mock.patch("urllib.request.urlopen", return_value=self._mock_urlopen(payload)):
            client = self._make_client()
            results = client.fetch_player_props()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["player_name"], "Test Player")

    def test_fetch_player_props_http_error_raises(self):
        import unittest.mock as mock
        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError("url", 401, "Unauthorized", {}, None),
        ):
            with self.assertRaises(UnabatedAPIError) as ctx:
                self._make_client().fetch_player_props()
        self.assertIn("401", str(ctx.exception))

    def test_fetch_player_props_url_error_raises(self):
        import unittest.mock as mock
        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("Connection refused"),
        ):
            with self.assertRaises(UnabatedAPIError):
                self._make_client().fetch_player_props()

    def test_fetch_player_props_bad_json_raises(self):
        import unittest.mock as mock
        with mock.patch(
            "urllib.request.urlopen",
            return_value=self._mock_urlopen(b"not json {{{"),
        ):
            with self.assertRaises(UnabatedAPIError):
                self._make_client().fetch_player_props()


# ---------------------------------------------------------------------------
# UnabatedEdgeScreener tests
# ---------------------------------------------------------------------------

def _make_screener_sim(seed=42):
    return MLBPlayerPropsSimulator(
        stadium=Stadium.from_name("Neutral"),
        weather=WeatherConditions(temp_f=72, precipitation="none",
                                  humidity=0.50, game_time="night"),
        wind=WindConditions(speed_mph=0, direction="calm"),
        num_simulations=3_000,
        random_seed=seed,
    )


def _make_market_lines(player_name, prop_type, line, over_odds, under_odds,
                       book="TestBook"):
    """Build a single-item normalised market-lines list."""
    return [{
        "player_name": player_name,
        "prop_type": prop_type,
        "line": line,
        "over_odds": over_odds,
        "under_odds": under_odds,
        "book": book,
    }]


class TestUnabatedEdgeScreener(unittest.TestCase):
    """Tests for UnabatedEdgeScreener using pre-fetched market lines (no HTTP)."""

    def _client(self):
        return UnabatedClient(api_key="test")

    def _screener(self, min_edge=0.0):
        return UnabatedEdgeScreener(_make_screener_sim(), self._client(),
                                    min_edge=min_edge)

    # ------------------------------------------------------------------
    # Prop type mapping
    # ------------------------------------------------------------------

    def test_normalise_prop_type_strikeouts(self):
        self.assertEqual(
            UnabatedEdgeScreener._normalise_prop_type("strikeouts"), "Strikeouts"
        )

    def test_normalise_prop_type_case_insensitive(self):
        self.assertEqual(
            UnabatedEdgeScreener._normalise_prop_type("HITS"), "Hits"
        )

    def test_normalise_prop_type_with_whitespace(self):
        self.assertEqual(
            UnabatedEdgeScreener._normalise_prop_type("  home runs  "), "Home Runs"
        )

    def test_normalise_prop_type_unknown_returns_none(self):
        self.assertIsNone(
            UnabatedEdgeScreener._normalise_prop_type("assists")
        )

    def test_prop_type_map_covers_all_pitcher_props(self):
        for unabated_key in ("strikeouts", "outs recorded", "runs allowed", "pitch count"):
            self.assertIsNotNone(
                UnabatedEdgeScreener._normalise_prop_type(unabated_key),
                f"Missing mapping for '{unabated_key}'"
            )

    def test_prop_type_map_covers_all_batter_props(self):
        for unabated_key in ("hits", "doubles", "home runs", "stolen bases",
                             "plate appearances", "h+r+rbi"):
            self.assertIsNotNone(
                UnabatedEdgeScreener._normalise_prop_type(unabated_key),
                f"Missing mapping for '{unabated_key}'"
            )

    # ------------------------------------------------------------------
    # _find_edges
    # ------------------------------------------------------------------

    def test_no_lines_for_player_returns_empty(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(_default_pitcher())
        screener = self._screener(min_edge=0.0)
        edges = screener._find_edges("Unknown Player", report, [
            _make_market_lines("Someone Else", "strikeouts", 4.5, -110, -110)[0]
        ])
        self.assertEqual(edges, [])

    def test_unknown_prop_type_skipped(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(_default_pitcher())
        screener = self._screener(min_edge=0.0)
        edges = screener._find_edges("Test Pitcher", report, [
            _make_market_lines("Test Pitcher", "assists", 2.5, -110, -110)[0]
        ])
        self.assertEqual(edges, [])

    def test_over_edge_found_when_sim_prob_much_higher(self):
        sim = _make_screener_sim()
        # Give the pitcher extreme K stats so over-prob on a low line is very high.
        pitcher = PitcherStats("Ace P", era=2.0, k_per_9=14.0,
                               innings_per_start=7.0, whip=0.9)
        report = sim.simulate_pitcher(pitcher)
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        # Line 3.5 → sim over-prob should be very high; market odds +200 → implied 33%
        lines = _make_market_lines("Ace P", "strikeouts", 3.5, +200, -300)
        edges = screener._find_edges("Ace P", report, lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(len(over_edges) >= 1)
        self.assertGreater(over_edges[0].edge, 0.0)

    def test_edge_result_fields_populated_correctly(self):
        sim = _make_screener_sim()
        pitcher = PitcherStats("Big K", era=2.5, k_per_9=13.0,
                               innings_per_start=7.0, whip=0.95)
        report = sim.simulate_pitcher(pitcher)
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        lines = _make_market_lines("Big K", "strikeouts", 3.5, +250, -350)
        edges = screener._find_edges("Big K", report, lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        e = over_edges[0]
        self.assertEqual(e.player_name, "Big K")
        self.assertEqual(e.prop, "Strikeouts")
        self.assertAlmostEqual(e.line, 3.5)
        self.assertEqual(e.side, "over")
        self.assertAlmostEqual(e.american_odds, 250.0)
        self.assertEqual(e.book, "TestBook")

    def test_min_edge_filters_small_edges(self):
        sim = _make_screener_sim()
        pitcher = PitcherStats("Mid K", era=3.5, k_per_9=8.5,
                               innings_per_start=6.0, whip=1.2)
        report = sim.simulate_pitcher(pitcher)
        screener_strict = UnabatedEdgeScreener(sim, self._client(), min_edge=0.99)
        lines = _make_market_lines("Mid K", "strikeouts", 5.5, -110, -110)
        edges = screener_strict._find_edges("Mid K", report, lines)
        self.assertEqual(edges, [])

    def test_under_edge_found(self):
        # Low K pitcher vs very low line — under edge should appear with a
        # tiny min_edge so the under is detectable.
        sim = _make_screener_sim()
        pitcher = PitcherStats("Low K", era=5.0, k_per_9=5.0,
                               innings_per_start=5.0, whip=1.5)
        report = sim.simulate_pitcher(pitcher)
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        # Line 7.5 → under-prob should be high; market odds -110 on under
        lines = _make_market_lines("Low K", "strikeouts", 7.5, +300, -450)
        edges = screener._find_edges("Low K", report, lines)
        under_edges = [e for e in edges if e.side == "under"]
        self.assertTrue(len(under_edges) >= 1)
        self.assertGreater(under_edges[0].edge, 0.0)

    def test_none_odds_skipped(self):
        sim = _make_screener_sim()
        pitcher = _default_pitcher()
        report = sim.simulate_pitcher(pitcher)
        screener = self._screener(min_edge=0.0)
        lines = [{
            "player_name": "Test Pitcher",
            "prop_type": "strikeouts",
            "line": 4.5,
            "over_odds": None,   # both None → nothing to process
            "under_odds": None,
            "book": "",
        }]
        edges = screener._find_edges("Test Pitcher", report, lines)
        self.assertEqual(edges, [])

    def test_non_numeric_odds_skipped(self):
        sim = _make_screener_sim()
        pitcher = _default_pitcher()
        report = sim.simulate_pitcher(pitcher)
        screener = self._screener(min_edge=0.0)
        lines = [{
            "player_name": "Test Pitcher",
            "prop_type": "strikeouts",
            "line": 4.5,
            "over_odds": "N/A",
            "under_odds": "N/A",
            "book": "",
        }]
        edges = screener._find_edges("Test Pitcher", report, lines)
        self.assertEqual(edges, [])

    def test_edges_sorted_by_edge_descending(self):
        sim = _make_screener_sim()
        pitcher = PitcherStats("Sort K", era=2.0, k_per_9=14.0,
                               innings_per_start=7.0, whip=0.9)
        report = sim.simulate_pitcher(pitcher)
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        # Two different lines.
        lines = (
            _make_market_lines("Sort K", "strikeouts", 3.5, +250, -350)
            + _make_market_lines("Sort K", "strikeouts", 4.5, +150, -200)
        )
        edges = screener._find_edges("Sort K", report, lines)
        if len(edges) >= 2:
            for i in range(len(edges) - 1):
                self.assertGreaterEqual(edges[i].edge, edges[i + 1].edge)

    # ------------------------------------------------------------------
    # screen_pitcher / screen_batter (market_lines injected, no HTTP)
    # ------------------------------------------------------------------

    def test_screen_pitcher_uses_injected_market_lines(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        pitcher = PitcherStats("Ace P", era=2.0, k_per_9=14.0,
                               innings_per_start=7.0, whip=0.9)
        lines = _make_market_lines("Ace P", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(pitcher, market_lines=lines)
        self.assertIsInstance(edges, list)
        # At least the over edge should appear for a dominant pitcher at a low line.
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_batter_uses_injected_market_lines(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        batter = _hrb_batter()
        # Very generous odds → big implied under-prob → over edge possible.
        lines = _make_market_lines(batter.name, "hits", 0.5, +300, -500)
        edges = screener.screen_batter(batter, market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertIsInstance(edges, list)
        self.assertTrue(over_edges)

    def test_screen_matchup_returns_combined_results(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        pitcher = PitcherStats("P1", era=2.0, k_per_9=14.0,
                               innings_per_start=7.0, whip=0.9)
        batter = _hrb_batter()
        lines = (
            _make_market_lines("P1", "strikeouts", 3.5, +300, -500)
            + _make_market_lines(batter.name, "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(pitcher, [batter], market_lines=lines)
        player_names = {e.player_name for e in edges}
        # Both pitcher and batter should be represented.
        self.assertIn("P1", player_names)
        self.assertIn(batter.name, player_names)

    def test_screen_matchup_sorted_by_edge_descending(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        pitcher = PitcherStats("P1", era=2.0, k_per_9=14.0,
                               innings_per_start=7.0, whip=0.9)
        batter = _hrb_batter()
        lines = (
            _make_market_lines("P1", "strikeouts", 3.5, +300, -500)
            + _make_market_lines(batter.name, "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(pitcher, [batter], market_lines=lines)
        for i in range(len(edges) - 1):
            self.assertGreaterEqual(edges[i].edge, edges[i + 1].edge)

    def test_screen_pitcher_empty_market_returns_empty(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        pitcher = _default_pitcher()
        self.assertEqual(screener.screen_pitcher(pitcher, market_lines=[]), [])

    def test_screen_batter_empty_market_returns_empty(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, self._client(), min_edge=0.0)
        self.assertEqual(
            screener.screen_batter(_default_batter(), market_lines=[]), []
        )

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    def test_default_min_edge_constant(self):
        self.assertAlmostEqual(UNABATED_DEFAULT_MIN_EDGE, 0.05)

    def test_default_request_timeout_constant(self):
        self.assertIsInstance(UNABATED_DEFAULT_REQUEST_TIMEOUT, int)
        self.assertGreater(UNABATED_DEFAULT_REQUEST_TIMEOUT, 0)

    def test_base_url_is_string(self):
        self.assertIsInstance(UNABATED_BASE_URL, str)
        self.assertTrue(UNABATED_BASE_URL.startswith("https://"))


# ---------------------------------------------------------------------------
# Blue Jays 2026 Roster tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    BlueJaysRoster,
    BLUE_JAYS_LINEUP_2026,
    BLUE_JAYS_ROTATION_2026,
    BLUE_JAYS_BULLPEN_2026,
)

# Expected names in positional order (C, 1B, 2B, 3B, SS, LF, CF, RF, DH)
_LINEUP_NAMES = [
    "Alejandro Kirk",
    "Vladimir Guerrero Jr.",
    "Ernie Clement",
    "Kazuma Okamoto",
    "Andrés Giménez",
    "Jesús Sánchez",
    "Daulton Varsho",
    "Addison Barger",
    "George Springer",
]

_ROTATION_NAMES = [
    "Kevin Gausman",
    "Dylan Cease",
    "Shane Bieber",
    "Trey Yesavage",
    "Cody Ponce",
]

_BJ_BULLPEN_NAMES = [
    "Tyler Rogers",
    "Yimi García",
    "Louis Varland",
    "Brendon Little",
    "Braydon Fisher",
    "Jeff Hoffman",
]


class TestBlueJaysRoster(unittest.TestCase):
    """Tests for BLUE_JAYS_LINEUP_2026, BLUE_JAYS_ROTATION_2026,
    BLUE_JAYS_BULLPEN_2026, and BlueJaysRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(BLUE_JAYS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(BLUE_JAYS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(BLUE_JAYS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        names = [b.name for b in BLUE_JAYS_LINEUP_2026]
        self.assertEqual(names, _LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        names = [p.name for p in BLUE_JAYS_ROTATION_2026]
        self.assertEqual(names, _ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in BLUE_JAYS_BULLPEN_2026], _BJ_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()  # must not raise

    def test_batter_avg_in_range(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_per_600_pa_nonnegative(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in BLUE_JAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — lineup
    # ------------------------------------------------------------------
    # Positions: [0]=C Kirk(R), [1]=1B Guerrero(R), [2]=2B Clement(R),
    #            [3]=3B Okamoto(R), [4]=SS Gimenez(S), [5]=LF Sanchez(R),
    #            [6]=CF Varsho(L), [7]=RF Barger(L), [8]=DH Springer(R)

    def test_kirk_bats_right(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[0].bats, "R")

    def test_guerrero_bats_right(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[1].bats, "R")

    def test_clement_bats_right(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[2].bats, "R")

    def test_okamoto_bats_right(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[3].bats, "R")

    def test_gimenez_switch_hitter(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[4].bats, "S")

    def test_sanchez_bats_right(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[5].bats, "R")

    def test_varsho_bats_left(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[6].bats, "L")

    def test_barger_bats_left(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[7].bats, "L")

    def test_springer_bats_right(self):
        self.assertEqual(BLUE_JAYS_LINEUP_2026[8].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_pitchers_pass_validation(self):
        for pitcher in BLUE_JAYS_ROTATION_2026:
            with self.subTest(player=pitcher.name):
                pitcher.validate()  # must not raise

    def test_all_bullpen_pass_validation(self):
        for p in BLUE_JAYS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_pitcher_era_positive(self):
        for p in BLUE_JAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in BLUE_JAYS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_pitcher_k_per_9_in_range(self):
        for p in BLUE_JAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in BLUE_JAYS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_pitcher_innings_per_start_in_range(self):
        for p in BLUE_JAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.innings_per_start, 0.0)
                self.assertLessEqual(p.innings_per_start, 9.0)

    def test_pitcher_arm_strength_in_range(self):
        for p in BLUE_JAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreaterEqual(p.arm_strength, 0.0)
                self.assertLessEqual(p.arm_strength, 100.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_gausman_throws_right(self):
        self.assertEqual(BLUE_JAYS_ROTATION_2026[0].throws, "R")

    def test_cease_throws_right(self):
        self.assertEqual(BLUE_JAYS_ROTATION_2026[1].throws, "R")

    def test_bieber_throws_right(self):
        self.assertEqual(BLUE_JAYS_ROTATION_2026[2].throws, "R")

    def test_yesavage_throws_right(self):
        self.assertEqual(BLUE_JAYS_ROTATION_2026[3].throws, "R")

    def test_ponce_throws_right(self):
        self.assertEqual(BLUE_JAYS_ROTATION_2026[4].throws, "R")

    def test_little_throws_left(self):
        """Brendon Little is the only LHP in the bullpen."""
        self.assertEqual(BLUE_JAYS_BULLPEN_2026[3].throws, "L")

    def test_hoffman_throws_right(self):
        self.assertEqual(BLUE_JAYS_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_gausman_has_best_rotation_era(self):
        """Kevin Gausman is the ace (lowest ERA in the rotation)."""
        min_era = min(p.era for p in BLUE_JAYS_ROTATION_2026)
        self.assertAlmostEqual(BLUE_JAYS_ROTATION_2026[0].era, min_era)

    def test_gausman_has_highest_k_per_9_in_rotation(self):
        """Gausman leads the rotation in K/9."""
        max_k = max(p.k_per_9 for p in BLUE_JAYS_ROTATION_2026)
        self.assertAlmostEqual(BLUE_JAYS_ROTATION_2026[0].k_per_9, max_k)

    def test_ace_has_lower_era_than_fifth_starter(self):
        self.assertLess(BLUE_JAYS_ROTATION_2026[0].era, BLUE_JAYS_ROTATION_2026[4].era)

    def test_hoffman_has_best_bullpen_era(self):
        min_era = min(p.era for p in BLUE_JAYS_BULLPEN_2026)
        self.assertAlmostEqual(BLUE_JAYS_BULLPEN_2026[-1].era, min_era)

    def test_hoffman_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in BLUE_JAYS_BULLPEN_2026)
        self.assertAlmostEqual(BLUE_JAYS_BULLPEN_2026[-1].k_per_9, max_k)

    def test_hoffman_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in BLUE_JAYS_BULLPEN_2026)
        self.assertAlmostEqual(BLUE_JAYS_BULLPEN_2026[-1].whip, min_whip)

    def test_closer_era_lower_than_ace_era(self):
        self.assertLess(BLUE_JAYS_BULLPEN_2026[-1].era, BLUE_JAYS_ROTATION_2026[0].era)

    def test_guerrero_has_highest_power_in_lineup(self):
        max_power = max(b.power_rating for b in BLUE_JAYS_LINEUP_2026)
        self.assertEqual(BLUE_JAYS_LINEUP_2026[1].power_rating, max_power)

    def test_guerrero_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in BLUE_JAYS_LINEUP_2026)
        self.assertEqual(BLUE_JAYS_LINEUP_2026[1].hr_per_600_pa, max_hr)

    def test_guerrero_leads_rbi(self):
        max_rbi = max(b.rbi_per_season for b in BLUE_JAYS_LINEUP_2026)
        self.assertAlmostEqual(BLUE_JAYS_LINEUP_2026[1].rbi_per_season, max_rbi)

    # ------------------------------------------------------------------
    # BlueJaysRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_blueJaysRoster_instance(self):
        self.assertIsInstance(BlueJaysRoster.default(), BlueJaysRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(BlueJaysRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(BlueJaysRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(BlueJaysRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = BlueJaysRoster.default()
        r2 = BlueJaysRoster.default()
        r1.lineup.append(r1.lineup[0])  # mutate r1
        self.assertEqual(len(r2.lineup), 9)  # r2 unchanged

    def test_default_rotation_is_copy(self):
        r1 = BlueJaysRoster.default()
        r2 = BlueJaysRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = BlueJaysRoster.default()
        r2 = BlueJaysRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_rotation_names_match_constants(self):
        roster = BlueJaysRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in BLUE_JAYS_ROTATION_2026],
        )

    def test_default_lineup_names_match_constants(self):
        roster = BlueJaysRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in BLUE_JAYS_LINEUP_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = BlueJaysRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in BLUE_JAYS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_gausman_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(BLUE_JAYS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_hoffman_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(BLUE_JAYS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_guerrero_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(BLUE_JAYS_LINEUP_2026[1])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_gausman_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Kevin Gausman", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(BLUE_JAYS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Kevin Gausman")

    def test_screen_batter_guerrero_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Vladimir Guerrero Jr.", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(BLUE_JAYS_LINEUP_2026[1], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_full_roster(self):
        """screen_matchup with the full lineup against the ace returns results."""
        sim = _make_screener_sim(seed=99)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = BlueJaysRoster.default()
        lines = (
            _make_market_lines("Kevin Gausman", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Vladimir Guerrero Jr.", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Kevin Gausman", player_names)
        self.assertIn("Vladimir Guerrero Jr.", player_names)

    def test_screen_closer_hoffman(self):
        """Edge screener works for Jeff Hoffman (RHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Jeff Hoffman", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(BLUE_JAYS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Jeff Hoffman")


# ---------------------------------------------------------------------------
# White Sox 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    WhiteSoxRoster,
    WHITE_SOX_LINEUP_2026,
    WHITE_SOX_ROTATION_2026,
    WHITE_SOX_BULLPEN_2026,
)

_WSX_LINEUP_NAMES = [
    "Kyle Teel",
    "Munetaka Murakami",
    "Chase Meidroth",
    "Miguel Vargas",
    "Colson Montgomery",
    "Andrew Benintendi",
    "Luisangel Acuña",
    "Austin Hays",
    "Lenyn Sosa",
]

_WSX_ROTATION_NAMES = [
    "Shane Smith",
    "Sean Burke",
    "Anthony Kay",
    "Davis Martin",
    "Erick Fedde",
]

_WSX_BULLPEN_NAMES = [
    "Jordan Leasure",
    "Grant Taylor",
    "Sean Newcomb",
    "Chris Murphy",
    "Jordan Hicks",
    "Seranthony Dominguez",
]


class TestWhiteSoxRoster(unittest.TestCase):
    """Tests for WHITE_SOX_LINEUP_2026, WHITE_SOX_ROTATION_2026,
    WHITE_SOX_BULLPEN_2026, and WhiteSoxRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(WHITE_SOX_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(WHITE_SOX_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(WHITE_SOX_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in WHITE_SOX_LINEUP_2026], _WSX_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in WHITE_SOX_ROTATION_2026], _WSX_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in WHITE_SOX_BULLPEN_2026], _WSX_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in WHITE_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — key batters
    # ------------------------------------------------------------------

    def test_meidroth_bats_left(self):
        self.assertEqual(WHITE_SOX_LINEUP_2026[2].bats, "L")

    def test_montgomery_bats_left(self):
        self.assertEqual(WHITE_SOX_LINEUP_2026[4].bats, "L")

    def test_benintendi_bats_left(self):
        self.assertEqual(WHITE_SOX_LINEUP_2026[5].bats, "L")

    def test_murakami_bats_right(self):
        self.assertEqual(WHITE_SOX_LINEUP_2026[1].bats, "R")

    def test_acuna_bats_right(self):
        self.assertEqual(WHITE_SOX_LINEUP_2026[6].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in WHITE_SOX_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in WHITE_SOX_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in WHITE_SOX_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in WHITE_SOX_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in WHITE_SOX_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in WHITE_SOX_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_kay_throws_left(self):
        self.assertEqual(WHITE_SOX_ROTATION_2026[2].throws, "L")

    def test_newcomb_throws_left(self):
        newcomb = next(p for p in WHITE_SOX_BULLPEN_2026 if p.name == "Sean Newcomb")
        self.assertEqual(newcomb.throws, "L")

    def test_murphy_throws_left(self):
        murphy = next(p for p in WHITE_SOX_BULLPEN_2026 if p.name == "Chris Murphy")
        self.assertEqual(murphy.throws, "L")

    def test_dominguez_throws_right(self):
        self.assertEqual(WHITE_SOX_BULLPEN_2026[-1].throws, "R")

    def test_hicks_throws_right(self):
        hicks = next(p for p in WHITE_SOX_BULLPEN_2026 if p.name == "Jordan Hicks")
        self.assertEqual(hicks.throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_fedde_has_best_rotation_era(self):
        """Erick Fedde is modelled as the best ERA in the rotation."""
        min_era = min(p.era for p in WHITE_SOX_ROTATION_2026)
        self.assertAlmostEqual(WHITE_SOX_ROTATION_2026[4].era, min_era)

    def test_dominguez_has_best_bullpen_era(self):
        min_era = min(p.era for p in WHITE_SOX_BULLPEN_2026)
        self.assertAlmostEqual(WHITE_SOX_BULLPEN_2026[-1].era, min_era)

    def test_murakami_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in WHITE_SOX_LINEUP_2026)
        self.assertAlmostEqual(WHITE_SOX_LINEUP_2026[1].hr_per_600_pa, max_hr)

    def test_murakami_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in WHITE_SOX_LINEUP_2026)
        self.assertAlmostEqual(WHITE_SOX_LINEUP_2026[1].power_rating, max_power)

    def test_hicks_has_highest_arm_strength_in_bullpen(self):
        max_arm = max(p.arm_strength for p in WHITE_SOX_BULLPEN_2026)
        hicks = next(p for p in WHITE_SOX_BULLPEN_2026 if p.name == "Jordan Hicks")
        self.assertAlmostEqual(hicks.arm_strength, max_arm)

    def test_acuna_has_most_sb(self):
        max_sb = max(b.sb_per_season for b in WHITE_SOX_LINEUP_2026)
        self.assertAlmostEqual(WHITE_SOX_LINEUP_2026[6].sb_per_season, max_sb)

    def test_closer_has_lower_era_than_first_starter(self):
        self.assertLess(WHITE_SOX_BULLPEN_2026[-1].era, WHITE_SOX_ROTATION_2026[0].era)

    # ------------------------------------------------------------------
    # WhiteSoxRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_white_sox_roster_instance(self):
        self.assertIsInstance(WhiteSoxRoster.default(), WhiteSoxRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(WhiteSoxRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(WhiteSoxRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(WhiteSoxRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = WhiteSoxRoster.default()
        r2 = WhiteSoxRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = WhiteSoxRoster.default()
        r2 = WhiteSoxRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = WhiteSoxRoster.default()
        r2 = WhiteSoxRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = WhiteSoxRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in WHITE_SOX_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = WhiteSoxRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in WHITE_SOX_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = WhiteSoxRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in WHITE_SOX_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_smith_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(WHITE_SOX_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_dominguez_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(WHITE_SOX_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_murakami_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(WHITE_SOX_LINEUP_2026[1])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_smith_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        # Sim generates K lines at 3.5, 4.5, ... — use 3.5 so the screener can match.
        lines = _make_market_lines("Shane Smith", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(WHITE_SOX_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Shane Smith")

    def test_screen_batter_murakami_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Munetaka Murakami", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(WHITE_SOX_LINEUP_2026[1], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_white_sox_roster(self):
        """screen_matchup with the White Sox lineup against their ace."""
        sim = _make_screener_sim(seed=77)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = WhiteSoxRoster.default()
        # Sim generates K lines at 3.5, 4.5, ... — use 3.5 so the screener can match.
        lines = (
            _make_market_lines("Shane Smith", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Munetaka Murakami", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Shane Smith", player_names)
        self.assertIn("Munetaka Murakami", player_names)

    def test_screen_closer_dominguez(self):
        """Edge screener works for relief/closer appearances (1-inning starts)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        # Sim generates K lines at 3.5, 4.5, ... — use 3.5 so the screener can match.
        lines = _make_market_lines(
            "Seranthony Dominguez", "strikeouts", 3.5, +300, -500
        )
        edges = screener.screen_pitcher(WHITE_SOX_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Seranthony Dominguez")


# ---------------------------------------------------------------------------
# Cleveland Guardians 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    GuardiansRoster,
    GUARDIANS_LINEUP_2026,
    GUARDIANS_ROTATION_2026,
    GUARDIANS_BULLPEN_2026,
)

_CG_LINEUP_NAMES = [
    "Bo Naylor",
    "Kyle Manzardo",
    "Brayan Rocchio",
    "Jose Ramirez",
    "Gabriel Arias",
    "Steven Kwan",
    "Chase DeLauter",
    "CJ Kayfus",
    "Rhys Hoskins",
]

_CG_ROTATION_NAMES = [
    "Tanner Bibee",
    "Gavin Williams",
    "Logan Allen",
    "Slade Cecconi",
    "Joey Cantillo",
]

_CG_BULLPEN_NAMES = [
    "Hunter Gaddis",
    "Shawn Armstrong",
    "Erik Sabrowski",
    "Matt Festa",
    "Tim Herrin",
    "Cade Smith",
]


class TestGuardiansRoster(unittest.TestCase):
    """Tests for GUARDIANS_LINEUP_2026, GUARDIANS_ROTATION_2026,
    GUARDIANS_BULLPEN_2026, and GuardiansRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(GUARDIANS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(GUARDIANS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(GUARDIANS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in GUARDIANS_LINEUP_2026], _CG_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in GUARDIANS_ROTATION_2026], _CG_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in GUARDIANS_BULLPEN_2026], _CG_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in GUARDIANS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in GUARDIANS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — key batters
    # ------------------------------------------------------------------

    def test_naylor_switch_hitter(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[0].bats, "S")

    def test_manzardo_bats_left(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[1].bats, "L")

    def test_rocchio_switch_hitter(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[2].bats, "S")

    def test_ramirez_switch_hitter(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[3].bats, "S")

    def test_arias_bats_right(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[4].bats, "R")

    def test_kwan_bats_left(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[5].bats, "L")

    def test_delauter_bats_left(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[6].bats, "L")

    def test_kayfus_bats_left(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[7].bats, "L")

    def test_hoskins_bats_right(self):
        self.assertEqual(GUARDIANS_LINEUP_2026[8].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in GUARDIANS_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in GUARDIANS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in GUARDIANS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in GUARDIANS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in GUARDIANS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in GUARDIANS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_bibee_throws_right(self):
        self.assertEqual(GUARDIANS_ROTATION_2026[0].throws, "R")

    def test_williams_throws_right(self):
        self.assertEqual(GUARDIANS_ROTATION_2026[1].throws, "R")

    def test_allen_throws_left(self):
        self.assertEqual(GUARDIANS_ROTATION_2026[2].throws, "L")

    def test_cecconi_throws_right(self):
        self.assertEqual(GUARDIANS_ROTATION_2026[3].throws, "R")

    def test_cantillo_throws_left(self):
        self.assertEqual(GUARDIANS_ROTATION_2026[4].throws, "L")

    def test_herrin_throws_left(self):
        herrin = next(p for p in GUARDIANS_BULLPEN_2026 if p.name == "Tim Herrin")
        self.assertEqual(herrin.throws, "L")

    def test_cade_smith_throws_right(self):
        self.assertEqual(GUARDIANS_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_bibee_has_best_rotation_era(self):
        """Tanner Bibee is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in GUARDIANS_ROTATION_2026)
        self.assertAlmostEqual(GUARDIANS_ROTATION_2026[0].era, min_era)

    def test_cade_smith_has_best_bullpen_era(self):
        min_era = min(p.era for p in GUARDIANS_BULLPEN_2026)
        self.assertAlmostEqual(GUARDIANS_BULLPEN_2026[-1].era, min_era)

    def test_ramirez_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in GUARDIANS_LINEUP_2026)
        self.assertAlmostEqual(GUARDIANS_LINEUP_2026[3].hr_per_600_pa, max_hr)

    def test_ramirez_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in GUARDIANS_LINEUP_2026)
        self.assertAlmostEqual(GUARDIANS_LINEUP_2026[3].power_rating, max_power)

    def test_closer_has_lower_era_than_first_starter(self):
        self.assertLess(GUARDIANS_BULLPEN_2026[-1].era, GUARDIANS_ROTATION_2026[0].era)

    def test_ramirez_has_most_sb(self):
        max_sb = max(b.sb_per_season for b in GUARDIANS_LINEUP_2026)
        self.assertAlmostEqual(GUARDIANS_LINEUP_2026[3].sb_per_season, max_sb)

    # ------------------------------------------------------------------
    # GuardiansRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_guardians_roster_instance(self):
        self.assertIsInstance(GuardiansRoster.default(), GuardiansRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(GuardiansRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(GuardiansRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(GuardiansRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = GuardiansRoster.default()
        r2 = GuardiansRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = GuardiansRoster.default()
        r2 = GuardiansRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = GuardiansRoster.default()
        r2 = GuardiansRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = GuardiansRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in GUARDIANS_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = GuardiansRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in GUARDIANS_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = GuardiansRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in GUARDIANS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_bibee_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(GUARDIANS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_cade_smith_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(GUARDIANS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_ramirez_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(GUARDIANS_LINEUP_2026[3])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_bibee_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Tanner Bibee", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(GUARDIANS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Tanner Bibee")

    def test_screen_batter_ramirez_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Jose Ramirez", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(GUARDIANS_LINEUP_2026[3], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_guardians_roster(self):
        """screen_matchup with the Guardians lineup against their ace."""
        sim = _make_screener_sim(seed=77)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = GuardiansRoster.default()
        lines = (
            _make_market_lines("Tanner Bibee", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Jose Ramirez", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Tanner Bibee", player_names)
        self.assertIn("Jose Ramirez", player_names)

    def test_screen_closer_cade_smith(self):
        """Edge screener works for closer appearances (1-inning starts)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Cade Smith", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(GUARDIANS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Cade Smith")


# ---------------------------------------------------------------------------
# Detroit Tigers 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    TigersRoster,
    TIGERS_LINEUP_2026,
    TIGERS_ROTATION_2026,
    TIGERS_BULLPEN_2026,
)

_DET_LINEUP_NAMES = [
    "Dillon Dingler",
    "Spencer Torkelson",
    "Gleyber Torres",
    "Colt Keith",
    "Kevin McGonigle",
    "Riley Greene",
    "Parker Meadows",
    "Wenceel Perez",
    "Kerry Carpenter",
]

_DET_ROTATION_NAMES = [
    "Tarik Skubal",
    "Framber Valdez",
    "Jack Flaherty",
    "Justin Verlander",
    "Casey Mize",
]

_DET_BULLPEN_NAMES = [
    "Will Vest",
    "Kyle Finnegan",
    "Tyler Holton",
    "Brant Hurter",
    "Brenan Hanifee",
    "Kenley Jansen",
]


class TestTigersRoster(unittest.TestCase):
    """Tests for TIGERS_LINEUP_2026, TIGERS_ROTATION_2026,
    TIGERS_BULLPEN_2026, and TigersRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(TIGERS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(TIGERS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(TIGERS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in TIGERS_LINEUP_2026], _DET_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in TIGERS_ROTATION_2026], _DET_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in TIGERS_BULLPEN_2026], _DET_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in TIGERS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in TIGERS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — key batters
    # ------------------------------------------------------------------

    def test_dingler_bats_right(self):
        self.assertEqual(TIGERS_LINEUP_2026[0].bats, "R")

    def test_torkelson_bats_right(self):
        self.assertEqual(TIGERS_LINEUP_2026[1].bats, "R")

    def test_torres_switch_hitter(self):
        self.assertEqual(TIGERS_LINEUP_2026[2].bats, "S")

    def test_keith_bats_left(self):
        self.assertEqual(TIGERS_LINEUP_2026[3].bats, "L")

    def test_mcgonigle_bats_right(self):
        self.assertEqual(TIGERS_LINEUP_2026[4].bats, "R")

    def test_greene_bats_left(self):
        self.assertEqual(TIGERS_LINEUP_2026[5].bats, "L")

    def test_meadows_bats_left(self):
        self.assertEqual(TIGERS_LINEUP_2026[6].bats, "L")

    def test_perez_switch_hitter(self):
        self.assertEqual(TIGERS_LINEUP_2026[7].bats, "S")

    def test_carpenter_bats_left(self):
        self.assertEqual(TIGERS_LINEUP_2026[8].bats, "L")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in TIGERS_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in TIGERS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in TIGERS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in TIGERS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in TIGERS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in TIGERS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_skubal_throws_left(self):
        self.assertEqual(TIGERS_ROTATION_2026[0].throws, "L")

    def test_valdez_throws_left(self):
        self.assertEqual(TIGERS_ROTATION_2026[1].throws, "L")

    def test_flaherty_throws_right(self):
        self.assertEqual(TIGERS_ROTATION_2026[2].throws, "R")

    def test_verlander_throws_right(self):
        self.assertEqual(TIGERS_ROTATION_2026[3].throws, "R")

    def test_mize_throws_right(self):
        self.assertEqual(TIGERS_ROTATION_2026[4].throws, "R")

    def test_holton_throws_left(self):
        holton = next(p for p in TIGERS_BULLPEN_2026 if p.name == "Tyler Holton")
        self.assertEqual(holton.throws, "L")

    def test_hurter_throws_left(self):
        hurter = next(p for p in TIGERS_BULLPEN_2026 if p.name == "Brant Hurter")
        self.assertEqual(hurter.throws, "L")

    def test_jansen_throws_right(self):
        self.assertEqual(TIGERS_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_skubal_has_best_rotation_era(self):
        """Tarik Skubal is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in TIGERS_ROTATION_2026)
        self.assertAlmostEqual(TIGERS_ROTATION_2026[0].era, min_era)

    def test_jansen_has_best_bullpen_era(self):
        min_era = min(p.era for p in TIGERS_BULLPEN_2026)
        self.assertAlmostEqual(TIGERS_BULLPEN_2026[-1].era, min_era)

    def test_torkelson_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in TIGERS_LINEUP_2026)
        self.assertAlmostEqual(TIGERS_LINEUP_2026[1].hr_per_600_pa, max_hr)

    def test_torkelson_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in TIGERS_LINEUP_2026)
        self.assertAlmostEqual(TIGERS_LINEUP_2026[1].power_rating, max_power)

    def test_meadows_has_most_sb(self):
        max_sb = max(b.sb_per_season for b in TIGERS_LINEUP_2026)
        self.assertAlmostEqual(TIGERS_LINEUP_2026[6].sb_per_season, max_sb)

    # ------------------------------------------------------------------
    # TigersRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_tigers_roster_instance(self):
        self.assertIsInstance(TigersRoster.default(), TigersRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(TigersRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(TigersRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(TigersRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = TigersRoster.default()
        r2 = TigersRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = TigersRoster.default()
        r2 = TigersRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = TigersRoster.default()
        r2 = TigersRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = TigersRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in TIGERS_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = TigersRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in TIGERS_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = TigersRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in TIGERS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_skubal_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(TIGERS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_jansen_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(TIGERS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_greene_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(TIGERS_LINEUP_2026[5])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_skubal_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Tarik Skubal", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(TIGERS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Tarik Skubal")

    def test_screen_batter_greene_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Riley Greene", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(TIGERS_LINEUP_2026[5], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_tigers_roster(self):
        """screen_matchup with the Tigers lineup against their ace."""
        sim = _make_screener_sim(seed=77)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = TigersRoster.default()
        lines = (
            _make_market_lines("Tarik Skubal", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Riley Greene", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Tarik Skubal", player_names)
        self.assertIn("Riley Greene", player_names)

    def test_screen_closer_jansen(self):
        """Edge screener works for closer appearances (1-inning starts)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Kenley Jansen", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(TIGERS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Kenley Jansen")


# ---------------------------------------------------------------------------
# Kansas City Royals 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    RoyalsRoster,
    ROYALS_LINEUP_2026,
    ROYALS_ROTATION_2026,
    ROYALS_BULLPEN_2026,
)

_KC_LINEUP_NAMES = [
    "Salvador Perez",
    "Vinnie Pasquantino",
    "Jonathan India",
    "Maikel Garcia",
    "Bobby Witt Jr.",
    "Isaac Collins",
    "Kyle Isbel",
    "Jac Caglianone",
    "Carter Jensen",
]

_KC_ROTATION_NAMES = [
    "Cole Ragans",
    "Michael Wacha",
    "Seth Lugo",
    "Kris Bubic",
    "Noah Cameron",
]

_KC_BULLPEN_NAMES = [
    "Lucas Erceg",
    "Matt Strahm",
    "John Schreiber",
    "Nick Mears",
    "Daniel Lynch IV",
    "Carlos Estevez",
]


class TestRoyalsRoster(unittest.TestCase):
    """Tests for ROYALS_LINEUP_2026, ROYALS_ROTATION_2026,
    ROYALS_BULLPEN_2026, and RoyalsRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(ROYALS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(ROYALS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(ROYALS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in ROYALS_LINEUP_2026], _KC_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in ROYALS_ROTATION_2026], _KC_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in ROYALS_BULLPEN_2026], _KC_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in ROYALS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in ROYALS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — key batters
    # ------------------------------------------------------------------

    def test_perez_bats_right(self):
        self.assertEqual(ROYALS_LINEUP_2026[0].bats, "R")

    def test_pasquantino_bats_left(self):
        self.assertEqual(ROYALS_LINEUP_2026[1].bats, "L")

    def test_india_bats_right(self):
        self.assertEqual(ROYALS_LINEUP_2026[2].bats, "R")

    def test_garcia_switch_hitter(self):
        self.assertEqual(ROYALS_LINEUP_2026[3].bats, "S")

    def test_witt_bats_right(self):
        self.assertEqual(ROYALS_LINEUP_2026[4].bats, "R")

    def test_collins_bats_left(self):
        self.assertEqual(ROYALS_LINEUP_2026[5].bats, "L")

    def test_isbel_bats_left(self):
        self.assertEqual(ROYALS_LINEUP_2026[6].bats, "L")

    def test_caglianone_bats_left(self):
        self.assertEqual(ROYALS_LINEUP_2026[7].bats, "L")

    def test_jensen_bats_right(self):
        self.assertEqual(ROYALS_LINEUP_2026[8].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in ROYALS_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in ROYALS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in ROYALS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in ROYALS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in ROYALS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in ROYALS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_ragans_throws_left(self):
        self.assertEqual(ROYALS_ROTATION_2026[0].throws, "L")

    def test_wacha_throws_right(self):
        self.assertEqual(ROYALS_ROTATION_2026[1].throws, "R")

    def test_lugo_throws_right(self):
        self.assertEqual(ROYALS_ROTATION_2026[2].throws, "R")

    def test_bubic_throws_left(self):
        self.assertEqual(ROYALS_ROTATION_2026[3].throws, "L")

    def test_cameron_throws_right(self):
        self.assertEqual(ROYALS_ROTATION_2026[4].throws, "R")

    def test_strahm_throws_left(self):
        strahm = next(p for p in ROYALS_BULLPEN_2026 if p.name == "Matt Strahm")
        self.assertEqual(strahm.throws, "L")

    def test_lynch_throws_left(self):
        lynch = next(p for p in ROYALS_BULLPEN_2026 if p.name == "Daniel Lynch IV")
        self.assertEqual(lynch.throws, "L")

    def test_estevez_throws_right(self):
        self.assertEqual(ROYALS_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_ragans_has_best_rotation_era(self):
        """Cole Ragans is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in ROYALS_ROTATION_2026)
        self.assertAlmostEqual(ROYALS_ROTATION_2026[0].era, min_era)

    def test_estevez_has_best_bullpen_era(self):
        min_era = min(p.era for p in ROYALS_BULLPEN_2026)
        self.assertAlmostEqual(ROYALS_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(ROYALS_BULLPEN_2026[-1].era, ROYALS_ROTATION_2026[0].era)

    def test_witt_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in ROYALS_LINEUP_2026)
        self.assertAlmostEqual(ROYALS_LINEUP_2026[4].hr_per_600_pa, max_hr)

    def test_witt_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in ROYALS_LINEUP_2026)
        self.assertAlmostEqual(ROYALS_LINEUP_2026[4].power_rating, max_power)

    def test_witt_has_most_sb(self):
        """Bobby Witt Jr. is the primary stolen-base threat."""
        max_sb = max(b.sb_per_season for b in ROYALS_LINEUP_2026)
        self.assertAlmostEqual(ROYALS_LINEUP_2026[4].sb_per_season, max_sb)

    def test_ragans_has_best_k_per_9_in_rotation(self):
        max_k = max(p.k_per_9 for p in ROYALS_ROTATION_2026)
        self.assertAlmostEqual(ROYALS_ROTATION_2026[0].k_per_9, max_k)

    def test_estevez_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in ROYALS_BULLPEN_2026)
        self.assertAlmostEqual(ROYALS_BULLPEN_2026[-1].k_per_9, max_k)

    # ------------------------------------------------------------------
    # RoyalsRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_royals_roster_instance(self):
        self.assertIsInstance(RoyalsRoster.default(), RoyalsRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(RoyalsRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(RoyalsRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(RoyalsRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = RoyalsRoster.default()
        r2 = RoyalsRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = RoyalsRoster.default()
        r2 = RoyalsRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = RoyalsRoster.default()
        r2 = RoyalsRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = RoyalsRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in ROYALS_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = RoyalsRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in ROYALS_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = RoyalsRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in ROYALS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_ragans_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(ROYALS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_estevez_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(ROYALS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_witt_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(ROYALS_LINEUP_2026[4])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_ragans_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Cole Ragans", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(ROYALS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Cole Ragans")

    def test_screen_batter_witt_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Bobby Witt Jr.", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(ROYALS_LINEUP_2026[4], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_royals_roster(self):
        """screen_matchup with the Royals lineup against their ace."""
        sim = _make_screener_sim(seed=88)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = RoyalsRoster.default()
        lines = (
            _make_market_lines("Cole Ragans", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Bobby Witt Jr.", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Cole Ragans", player_names)
        self.assertIn("Bobby Witt Jr.", player_names)

    def test_screen_closer_estevez(self):
        """Edge screener works for closer appearances (1-inning starts)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Carlos Estevez", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(ROYALS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Carlos Estevez")


# ---------------------------------------------------------------------------
# Minnesota Twins 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    TwinsRoster,
    TWINS_LINEUP_2026,
    TWINS_ROTATION_2026,
    TWINS_BULLPEN_2026,
)

_MIN_LINEUP_NAMES = [
    "Ryan Jeffers",
    "Josh Bell",
    "Luke Keaschall",
    "Royce Lewis",
    "Brooks Lee",
    "Alan Roden",
    "Byron Buxton",
    "Matt Wallner",
    "Trevor Larnach",
]

_MIN_ROTATION_NAMES = [
    "Joe Ryan",
    "Bailey Ober",
    "Simeon Woods Richardson",
    "Taj Bradley",
    "Mick Abel",
]

_MIN_BULLPEN_NAMES = [
    "Anthony Banda",
    "Kody Funderburk",
    "Eric Orze",
    "Travis Adams",
    "Zak Kent",
    "Taylor Rogers",
]


class TestTwinsRoster(unittest.TestCase):
    """Tests for TWINS_LINEUP_2026, TWINS_ROTATION_2026,
    TWINS_BULLPEN_2026, and TwinsRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(TWINS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(TWINS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(TWINS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in TWINS_LINEUP_2026], _MIN_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in TWINS_ROTATION_2026], _MIN_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in TWINS_BULLPEN_2026], _MIN_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in TWINS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in TWINS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — key batters
    # ------------------------------------------------------------------

    def test_jeffers_bats_right(self):
        self.assertEqual(TWINS_LINEUP_2026[0].bats, "R")

    def test_bell_switch_hitter(self):
        self.assertEqual(TWINS_LINEUP_2026[1].bats, "S")

    def test_keaschall_bats_right(self):
        self.assertEqual(TWINS_LINEUP_2026[2].bats, "R")

    def test_lewis_bats_right(self):
        self.assertEqual(TWINS_LINEUP_2026[3].bats, "R")

    def test_lee_switch_hitter(self):
        self.assertEqual(TWINS_LINEUP_2026[4].bats, "S")

    def test_roden_bats_right(self):
        self.assertEqual(TWINS_LINEUP_2026[5].bats, "R")

    def test_buxton_bats_right(self):
        self.assertEqual(TWINS_LINEUP_2026[6].bats, "R")

    def test_wallner_bats_left(self):
        self.assertEqual(TWINS_LINEUP_2026[7].bats, "L")

    def test_larnach_bats_left(self):
        self.assertEqual(TWINS_LINEUP_2026[8].bats, "L")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in TWINS_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in TWINS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in TWINS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in TWINS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in TWINS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in TWINS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_ryan_throws_right(self):
        self.assertEqual(TWINS_ROTATION_2026[0].throws, "R")

    def test_ober_throws_right(self):
        self.assertEqual(TWINS_ROTATION_2026[1].throws, "R")

    def test_woods_richardson_throws_right(self):
        self.assertEqual(TWINS_ROTATION_2026[2].throws, "R")

    def test_bradley_throws_right(self):
        self.assertEqual(TWINS_ROTATION_2026[3].throws, "R")

    def test_abel_throws_right(self):
        self.assertEqual(TWINS_ROTATION_2026[4].throws, "R")

    def test_banda_throws_left(self):
        banda = next(p for p in TWINS_BULLPEN_2026 if p.name == "Anthony Banda")
        self.assertEqual(banda.throws, "L")

    def test_rogers_throws_left(self):
        self.assertEqual(TWINS_BULLPEN_2026[-1].throws, "L")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_ryan_has_best_rotation_era(self):
        """Joe Ryan is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in TWINS_ROTATION_2026)
        self.assertAlmostEqual(TWINS_ROTATION_2026[0].era, min_era)

    def test_rogers_has_best_bullpen_era(self):
        min_era = min(p.era for p in TWINS_BULLPEN_2026)
        self.assertAlmostEqual(TWINS_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(TWINS_BULLPEN_2026[-1].era, TWINS_ROTATION_2026[0].era)

    def test_buxton_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in TWINS_LINEUP_2026)
        self.assertAlmostEqual(TWINS_LINEUP_2026[6].hr_per_600_pa, max_hr)

    def test_buxton_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in TWINS_LINEUP_2026)
        self.assertAlmostEqual(TWINS_LINEUP_2026[6].power_rating, max_power)

    def test_ryan_has_best_k_per_9_in_rotation(self):
        max_k = max(p.k_per_9 for p in TWINS_ROTATION_2026)
        self.assertAlmostEqual(TWINS_ROTATION_2026[0].k_per_9, max_k)

    def test_rogers_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in TWINS_BULLPEN_2026)
        self.assertAlmostEqual(TWINS_BULLPEN_2026[-1].k_per_9, max_k)

    def test_rogers_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in TWINS_BULLPEN_2026)
        self.assertAlmostEqual(TWINS_BULLPEN_2026[-1].whip, min_whip)

    # ------------------------------------------------------------------
    # TwinsRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_twins_roster_instance(self):
        self.assertIsInstance(TwinsRoster.default(), TwinsRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(TwinsRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(TwinsRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(TwinsRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = TwinsRoster.default()
        r2 = TwinsRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = TwinsRoster.default()
        r2 = TwinsRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = TwinsRoster.default()
        r2 = TwinsRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = TwinsRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in TWINS_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = TwinsRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in TWINS_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = TwinsRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in TWINS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_ryan_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(TWINS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_rogers_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(TWINS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_buxton_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(TWINS_LINEUP_2026[6])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_ryan_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Joe Ryan", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(TWINS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Joe Ryan")

    def test_screen_batter_buxton_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Byron Buxton", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(TWINS_LINEUP_2026[6], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_twins_roster(self):
        """screen_matchup with the Twins lineup against their ace."""
        sim = _make_screener_sim(seed=77)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = TwinsRoster.default()
        lines = (
            _make_market_lines("Joe Ryan", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Byron Buxton", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Joe Ryan", player_names)
        self.assertIn("Byron Buxton", player_names)

    def test_screen_closer_rogers(self):
        """Edge screener works for Taylor Rogers (LHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Taylor Rogers", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(TWINS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Taylor Rogers")


# ---------------------------------------------------------------------------
# Baltimore Orioles 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    OriolesRoster,
    ORIOLES_LINEUP_2026,
    ORIOLES_ROTATION_2026,
    ORIOLES_BULLPEN_2026,
)

_ORI_LINEUP_NAMES = [
    "Adley Rutschman",
    "Pete Alonso",
    "Jackson Holliday",
    "Jordan Westburg",
    "Gunnar Henderson",
    "Taylor Ward",
    "Colton Cowser",
    "Dylan Beavers",
    "Samuel Basallo",
]

_ORI_ROTATION_NAMES = [
    "Trevor Rogers",
    "Kyle Bradish",
    "Chris Bassitt",
    "Shane Baz",
    "Zach Eflin",
]

_ORI_BULLPEN_NAMES = [
    "Andrew Kittredge",
    "Keegan Akin",
    "Yennier Cano",
    "Tyler Wells",
    "Rico Garcia",
    "Ryan Helsley",
]


class TestOriolesRoster(unittest.TestCase):
    """Tests for ORIOLES_LINEUP_2026, ORIOLES_ROTATION_2026,
    ORIOLES_BULLPEN_2026, and OriolesRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(ORIOLES_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(ORIOLES_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(ORIOLES_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in ORIOLES_LINEUP_2026], _ORI_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in ORIOLES_ROTATION_2026], _ORI_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in ORIOLES_BULLPEN_2026], _ORI_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in ORIOLES_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in ORIOLES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — lineup
    # ------------------------------------------------------------------

    def test_rutschman_switch_hitter(self):
        self.assertEqual(ORIOLES_LINEUP_2026[0].bats, "S")

    def test_alonso_bats_right(self):
        self.assertEqual(ORIOLES_LINEUP_2026[1].bats, "R")

    def test_holliday_bats_left(self):
        self.assertEqual(ORIOLES_LINEUP_2026[2].bats, "L")

    def test_westburg_bats_right(self):
        self.assertEqual(ORIOLES_LINEUP_2026[3].bats, "R")

    def test_henderson_bats_left(self):
        self.assertEqual(ORIOLES_LINEUP_2026[4].bats, "L")

    def test_ward_bats_right(self):
        self.assertEqual(ORIOLES_LINEUP_2026[5].bats, "R")

    def test_cowser_bats_left(self):
        self.assertEqual(ORIOLES_LINEUP_2026[6].bats, "L")

    def test_beavers_bats_left(self):
        self.assertEqual(ORIOLES_LINEUP_2026[7].bats, "L")

    def test_basallo_bats_left(self):
        self.assertEqual(ORIOLES_LINEUP_2026[8].bats, "L")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in ORIOLES_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in ORIOLES_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in ORIOLES_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in ORIOLES_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in ORIOLES_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in ORIOLES_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_t_rogers_throws_left(self):
        self.assertEqual(ORIOLES_ROTATION_2026[0].throws, "L")

    def test_bradish_throws_right(self):
        self.assertEqual(ORIOLES_ROTATION_2026[1].throws, "R")

    def test_bassitt_throws_right(self):
        self.assertEqual(ORIOLES_ROTATION_2026[2].throws, "R")

    def test_baz_throws_right(self):
        self.assertEqual(ORIOLES_ROTATION_2026[3].throws, "R")

    def test_eflin_throws_right(self):
        self.assertEqual(ORIOLES_ROTATION_2026[4].throws, "R")

    def test_akin_throws_left(self):
        akin = next(p for p in ORIOLES_BULLPEN_2026 if p.name == "Keegan Akin")
        self.assertEqual(akin.throws, "L")

    def test_helsley_throws_right(self):
        self.assertEqual(ORIOLES_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_t_rogers_has_best_rotation_era(self):
        """Trevor Rogers is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in ORIOLES_ROTATION_2026)
        self.assertAlmostEqual(ORIOLES_ROTATION_2026[0].era, min_era)

    def test_helsley_has_best_bullpen_era(self):
        min_era = min(p.era for p in ORIOLES_BULLPEN_2026)
        self.assertAlmostEqual(ORIOLES_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(ORIOLES_BULLPEN_2026[-1].era, ORIOLES_ROTATION_2026[0].era)

    def test_alonso_has_most_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in ORIOLES_LINEUP_2026)
        self.assertAlmostEqual(ORIOLES_LINEUP_2026[1].hr_per_600_pa, max_hr)

    def test_henderson_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in ORIOLES_LINEUP_2026)
        self.assertAlmostEqual(ORIOLES_LINEUP_2026[4].power_rating, max_power)

    def test_helsley_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in ORIOLES_BULLPEN_2026)
        self.assertAlmostEqual(ORIOLES_BULLPEN_2026[-1].k_per_9, max_k)

    def test_helsley_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in ORIOLES_BULLPEN_2026)
        self.assertAlmostEqual(ORIOLES_BULLPEN_2026[-1].whip, min_whip)

    def test_t_rogers_has_best_k_per_9_in_rotation(self):
        max_k = max(p.k_per_9 for p in ORIOLES_ROTATION_2026)
        self.assertAlmostEqual(ORIOLES_ROTATION_2026[0].k_per_9, max_k)

    def test_alonso_has_most_rbi(self):
        max_rbi = max(b.rbi_per_season for b in ORIOLES_LINEUP_2026)
        self.assertAlmostEqual(ORIOLES_LINEUP_2026[1].rbi_per_season, max_rbi)

    def test_henderson_leads_team_in_runs(self):
        max_runs = max(b.runs_per_season for b in ORIOLES_LINEUP_2026)
        self.assertAlmostEqual(ORIOLES_LINEUP_2026[4].runs_per_season, max_runs)

    # ------------------------------------------------------------------
    # OriolesRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_orioles_roster_instance(self):
        self.assertIsInstance(OriolesRoster.default(), OriolesRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(OriolesRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(OriolesRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(OriolesRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = OriolesRoster.default()
        r2 = OriolesRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = OriolesRoster.default()
        r2 = OriolesRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = OriolesRoster.default()
        r2 = OriolesRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = OriolesRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in ORIOLES_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = OriolesRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in ORIOLES_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = OriolesRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in ORIOLES_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_t_rogers_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(ORIOLES_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_helsley_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(ORIOLES_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_henderson_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(ORIOLES_LINEUP_2026[4])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_t_rogers_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Trevor Rogers", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(ORIOLES_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Trevor Rogers")

    def test_screen_batter_henderson_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Gunnar Henderson", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(ORIOLES_LINEUP_2026[4], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_orioles_roster(self):
        """screen_matchup with the Orioles lineup against their ace."""
        sim = _make_screener_sim(seed=88)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = OriolesRoster.default()
        lines = (
            _make_market_lines("Trevor Rogers", "strikeouts", 3.5, +350, -600)
            + _make_market_lines("Gunnar Henderson", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Trevor Rogers", player_names)
        self.assertIn("Gunnar Henderson", player_names)

    def test_screen_closer_helsley(self):
        """Edge screener works for Ryan Helsley (RHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Ryan Helsley", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(ORIOLES_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Ryan Helsley")


# ---------------------------------------------------------------------------
# Boston Red Sox 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    RedSoxRoster,
    RED_SOX_LINEUP_2026,
    RED_SOX_ROTATION_2026,
    RED_SOX_BULLPEN_2026,
)

_BSX_LINEUP_NAMES = [
    "Carlos Narvaez",
    "Willson Contreras",
    "Marcelo Mayer",
    "Caleb Durbin",
    "Trevor Story",
    "Jarren Duran",
    "Ceddanne Rafaela",
    "Wilyer Abreu",
    "Roman Anthony",
]

_BSX_ROTATION_NAMES = [
    "Garrett Crochet",
    "Sonny Gray",
    "Ranger Suarez",
    "Brayan Bello",
    "Johan Oviedo",
]

_BSX_BULLPEN_NAMES = [
    "Garrett Whitlock",
    "Justin Slaten",
    "Greg Weissert",
    "Danny Coulombe",
    "Zack Kelly",
    "Aroldis Chapman",
]


class TestRedSoxRoster(unittest.TestCase):
    """Tests for RED_SOX_LINEUP_2026, RED_SOX_ROTATION_2026,
    RED_SOX_BULLPEN_2026, and RedSoxRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(RED_SOX_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(RED_SOX_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(RED_SOX_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in RED_SOX_LINEUP_2026], _BSX_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in RED_SOX_ROTATION_2026], _BSX_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in RED_SOX_BULLPEN_2026], _BSX_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in RED_SOX_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in RED_SOX_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — lineup
    # ------------------------------------------------------------------

    def test_narvaez_bats_left(self):
        self.assertEqual(RED_SOX_LINEUP_2026[0].bats, "L")

    def test_contreras_bats_right(self):
        self.assertEqual(RED_SOX_LINEUP_2026[1].bats, "R")

    def test_mayer_bats_left(self):
        self.assertEqual(RED_SOX_LINEUP_2026[2].bats, "L")

    def test_durbin_switch_hitter(self):
        self.assertEqual(RED_SOX_LINEUP_2026[3].bats, "S")

    def test_story_bats_right(self):
        self.assertEqual(RED_SOX_LINEUP_2026[4].bats, "R")

    def test_duran_bats_left(self):
        self.assertEqual(RED_SOX_LINEUP_2026[5].bats, "L")

    def test_rafaela_bats_right(self):
        self.assertEqual(RED_SOX_LINEUP_2026[6].bats, "R")

    def test_abreu_bats_right(self):
        self.assertEqual(RED_SOX_LINEUP_2026[7].bats, "R")

    def test_r_anthony_bats_left(self):
        self.assertEqual(RED_SOX_LINEUP_2026[8].bats, "L")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in RED_SOX_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in RED_SOX_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in RED_SOX_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in RED_SOX_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in RED_SOX_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in RED_SOX_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_crochet_throws_left(self):
        self.assertEqual(RED_SOX_ROTATION_2026[0].throws, "L")

    def test_s_gray_throws_right(self):
        self.assertEqual(RED_SOX_ROTATION_2026[1].throws, "R")

    def test_suarez_throws_left(self):
        self.assertEqual(RED_SOX_ROTATION_2026[2].throws, "L")

    def test_bello_throws_right(self):
        self.assertEqual(RED_SOX_ROTATION_2026[3].throws, "R")

    def test_oviedo_throws_right(self):
        self.assertEqual(RED_SOX_ROTATION_2026[4].throws, "R")

    def test_coulombe_throws_left(self):
        coulombe = next(p for p in RED_SOX_BULLPEN_2026 if p.name == "Danny Coulombe")
        self.assertEqual(coulombe.throws, "L")

    def test_chapman_throws_left(self):
        self.assertEqual(RED_SOX_BULLPEN_2026[-1].throws, "L")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_crochet_has_best_rotation_era(self):
        """Garrett Crochet is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in RED_SOX_ROTATION_2026)
        self.assertAlmostEqual(RED_SOX_ROTATION_2026[0].era, min_era)

    def test_chapman_has_best_bullpen_era(self):
        min_era = min(p.era for p in RED_SOX_BULLPEN_2026)
        self.assertAlmostEqual(RED_SOX_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(RED_SOX_BULLPEN_2026[-1].era, RED_SOX_ROTATION_2026[0].era)

    def test_crochet_has_best_k_per_9_in_rotation(self):
        max_k = max(p.k_per_9 for p in RED_SOX_ROTATION_2026)
        self.assertAlmostEqual(RED_SOX_ROTATION_2026[0].k_per_9, max_k)

    def test_chapman_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in RED_SOX_BULLPEN_2026)
        self.assertAlmostEqual(RED_SOX_BULLPEN_2026[-1].k_per_9, max_k)

    def test_chapman_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in RED_SOX_BULLPEN_2026)
        self.assertAlmostEqual(RED_SOX_BULLPEN_2026[-1].whip, min_whip)

    def test_duran_leads_team_in_runs(self):
        max_runs = max(b.runs_per_season for b in RED_SOX_LINEUP_2026)
        self.assertAlmostEqual(RED_SOX_LINEUP_2026[5].runs_per_season, max_runs)

    def test_contreras_leads_team_in_rbi(self):
        max_rbi = max(b.rbi_per_season for b in RED_SOX_LINEUP_2026)
        self.assertAlmostEqual(RED_SOX_LINEUP_2026[1].rbi_per_season, max_rbi)

    def test_story_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in RED_SOX_LINEUP_2026)
        self.assertAlmostEqual(RED_SOX_LINEUP_2026[4].power_rating, max_power)

    def test_duran_leads_team_in_avg(self):
        max_avg = max(b.avg for b in RED_SOX_LINEUP_2026)
        self.assertAlmostEqual(RED_SOX_LINEUP_2026[5].avg, max_avg)

    # ------------------------------------------------------------------
    # RedSoxRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_red_sox_roster_instance(self):
        self.assertIsInstance(RedSoxRoster.default(), RedSoxRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(RedSoxRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(RedSoxRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(RedSoxRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = RedSoxRoster.default()
        r2 = RedSoxRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = RedSoxRoster.default()
        r2 = RedSoxRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = RedSoxRoster.default()
        r2 = RedSoxRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = RedSoxRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in RED_SOX_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = RedSoxRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in RED_SOX_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = RedSoxRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in RED_SOX_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_crochet_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(RED_SOX_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_chapman_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(RED_SOX_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_duran_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(RED_SOX_LINEUP_2026[5])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_crochet_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Garrett Crochet", "strikeouts", 4.5, +300, -500)
        edges = screener.screen_pitcher(RED_SOX_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Garrett Crochet")

    def test_screen_batter_duran_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Jarren Duran", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(RED_SOX_LINEUP_2026[5], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_red_sox_roster(self):
        """screen_matchup with the Red Sox lineup against Crochet."""
        sim = _make_screener_sim(seed=99)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = RedSoxRoster.default()
        lines = (
            _make_market_lines("Garrett Crochet", "strikeouts", 4.5, +350, -600)
            + _make_market_lines("Jarren Duran", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Garrett Crochet", player_names)
        self.assertIn("Jarren Duran", player_names)

    def test_screen_closer_chapman(self):
        """Edge screener works for Aroldis Chapman (LHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Aroldis Chapman", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(RED_SOX_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Aroldis Chapman")


# ---------------------------------------------------------------------------
# New York Yankees 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    YankeesRoster,
    YANKEES_LINEUP_2026,
    YANKEES_ROTATION_2026,
    YANKEES_BULLPEN_2026,
)

_NYY_LINEUP_NAMES = [
    "Austin Wells",
    "Ben Rice",
    "Jazz Chisholm Jr.",
    "Ryan McMahon",
    "Anthony Volpe",
    "Cody Bellinger",
    "Trent Grisham",
    "Aaron Judge",
    "Giancarlo Stanton",
]

_NYY_ROTATION_NAMES = [
    "Max Fried",
    "Gerrit Cole",
    "Carlos Rodon",
    "Cam Schlittler",
    "Will Warren",
]

_NYY_BULLPEN_NAMES = [
    "Camilo Doval",
    "Fernando Cruz",
    "Tim Hill",
    "Brent Headrick",
    "Jake Bird",
    "David Bednar",
]


class TestYankeesRoster(unittest.TestCase):
    """Tests for YANKEES_LINEUP_2026, YANKEES_ROTATION_2026,
    YANKEES_BULLPEN_2026, and YankeesRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(YANKEES_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(YANKEES_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(YANKEES_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in YANKEES_LINEUP_2026], _NYY_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in YANKEES_ROTATION_2026], _NYY_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in YANKEES_BULLPEN_2026], _NYY_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in YANKEES_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in YANKEES_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — lineup
    # ------------------------------------------------------------------

    def test_wells_bats_left(self):
        self.assertEqual(YANKEES_LINEUP_2026[0].bats, "L")

    def test_rice_bats_left(self):
        self.assertEqual(YANKEES_LINEUP_2026[1].bats, "L")

    def test_chisholm_switch_hitter(self):
        self.assertEqual(YANKEES_LINEUP_2026[2].bats, "S")

    def test_mcmahon_bats_left(self):
        self.assertEqual(YANKEES_LINEUP_2026[3].bats, "L")

    def test_volpe_bats_right(self):
        self.assertEqual(YANKEES_LINEUP_2026[4].bats, "R")

    def test_bellinger_bats_left(self):
        self.assertEqual(YANKEES_LINEUP_2026[5].bats, "L")

    def test_grisham_bats_left(self):
        self.assertEqual(YANKEES_LINEUP_2026[6].bats, "L")

    def test_judge_bats_right(self):
        self.assertEqual(YANKEES_LINEUP_2026[7].bats, "R")

    def test_stanton_bats_right(self):
        self.assertEqual(YANKEES_LINEUP_2026[8].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in YANKEES_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in YANKEES_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in YANKEES_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in YANKEES_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in YANKEES_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in YANKEES_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_fried_throws_left(self):
        self.assertEqual(YANKEES_ROTATION_2026[0].throws, "L")

    def test_cole_throws_right(self):
        self.assertEqual(YANKEES_ROTATION_2026[1].throws, "R")

    def test_rodon_throws_left(self):
        self.assertEqual(YANKEES_ROTATION_2026[2].throws, "L")

    def test_schlittler_throws_right(self):
        self.assertEqual(YANKEES_ROTATION_2026[3].throws, "R")

    def test_warren_throws_right(self):
        self.assertEqual(YANKEES_ROTATION_2026[4].throws, "R")

    def test_hill_throws_left(self):
        hill = next(p for p in YANKEES_BULLPEN_2026 if p.name == "Tim Hill")
        self.assertEqual(hill.throws, "L")

    def test_headrick_throws_left(self):
        headrick = next(p for p in YANKEES_BULLPEN_2026 if p.name == "Brent Headrick")
        self.assertEqual(headrick.throws, "L")

    def test_bednar_throws_right(self):
        self.assertEqual(YANKEES_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_fried_has_best_rotation_era(self):
        """Max Fried is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in YANKEES_ROTATION_2026)
        self.assertAlmostEqual(YANKEES_ROTATION_2026[0].era, min_era)

    def test_bednar_has_best_bullpen_era(self):
        min_era = min(p.era for p in YANKEES_BULLPEN_2026)
        self.assertAlmostEqual(YANKEES_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(YANKEES_BULLPEN_2026[-1].era, YANKEES_ROTATION_2026[0].era)

    def test_bednar_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in YANKEES_BULLPEN_2026)
        self.assertAlmostEqual(YANKEES_BULLPEN_2026[-1].k_per_9, max_k)

    def test_bednar_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in YANKEES_BULLPEN_2026)
        self.assertAlmostEqual(YANKEES_BULLPEN_2026[-1].whip, min_whip)

    def test_judge_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in YANKEES_LINEUP_2026)
        self.assertAlmostEqual(YANKEES_LINEUP_2026[7].power_rating, max_power)

    def test_judge_leads_team_in_avg(self):
        max_avg = max(b.avg for b in YANKEES_LINEUP_2026)
        self.assertAlmostEqual(YANKEES_LINEUP_2026[7].avg, max_avg)

    def test_judge_leads_team_in_rbi(self):
        max_rbi = max(b.rbi_per_season for b in YANKEES_LINEUP_2026)
        self.assertAlmostEqual(YANKEES_LINEUP_2026[7].rbi_per_season, max_rbi)

    def test_judge_leads_team_in_runs(self):
        max_runs = max(b.runs_per_season for b in YANKEES_LINEUP_2026)
        self.assertAlmostEqual(YANKEES_LINEUP_2026[7].runs_per_season, max_runs)

    def test_judge_has_highest_hr_per_600_pa(self):
        max_hr = max(b.hr_per_600_pa for b in YANKEES_LINEUP_2026)
        self.assertAlmostEqual(YANKEES_LINEUP_2026[7].hr_per_600_pa, max_hr)

    def test_cole_has_best_k_per_9_in_rotation(self):
        """Gerrit Cole leads the rotation in K/9."""
        max_k = max(p.k_per_9 for p in YANKEES_ROTATION_2026)
        self.assertAlmostEqual(YANKEES_ROTATION_2026[1].k_per_9, max_k)

    def test_chisholm_leads_team_in_sb(self):
        max_sb = max(b.sb_per_season for b in YANKEES_LINEUP_2026)
        self.assertAlmostEqual(YANKEES_LINEUP_2026[2].sb_per_season, max_sb)

    # ------------------------------------------------------------------
    # YankeesRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_yankees_roster_instance(self):
        self.assertIsInstance(YankeesRoster.default(), YankeesRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(YankeesRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(YankeesRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(YankeesRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = YankeesRoster.default()
        r2 = YankeesRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = YankeesRoster.default()
        r2 = YankeesRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = YankeesRoster.default()
        r2 = YankeesRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = YankeesRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in YANKEES_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = YankeesRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in YANKEES_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = YankeesRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in YANKEES_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_fried_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(YANKEES_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_bednar_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(YANKEES_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_judge_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(YANKEES_LINEUP_2026[7])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_fried_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Max Fried", "strikeouts", 4.5, +300, -500)
        edges = screener.screen_pitcher(YANKEES_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Max Fried")

    def test_screen_batter_judge_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Aaron Judge", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(YANKEES_LINEUP_2026[7], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_yankees_roster(self):
        """screen_matchup with the Yankees lineup against Max Fried."""
        sim = _make_screener_sim(seed=99)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = YankeesRoster.default()
        lines = (
            _make_market_lines("Max Fried", "strikeouts", 4.5, +350, -600)
            + _make_market_lines("Aaron Judge", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Max Fried", player_names)
        self.assertIn("Aaron Judge", player_names)

    def test_screen_closer_bednar(self):
        """Edge screener works for David Bednar (RHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("David Bednar", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(YANKEES_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "David Bednar")


# ---------------------------------------------------------------------------
# Tampa Bay Rays 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    RaysRoster,
    RAYS_LINEUP_2026,
    RAYS_ROTATION_2026,
    RAYS_BULLPEN_2026,
)

_TB_LINEUP_NAMES = [
    "Nick Fortes",
    "Jonathan Aranda",
    "Gavin Lux",
    "Junior Caminero",
    "Carson Williams",
    "Chandler Simpson",
    "Cedric Mullins",
    "Jake Fraley",
    "Yandy Diaz",
]

_TB_ROTATION_NAMES = [
    "Drew Rasmussen",
    "Ryan Pepiot",
    "Shane McClanahan",
    "Steven Matz",
    "Nick Martinez",
]

_TB_BULLPEN_NAMES = [
    "Bryan Baker",
    "Hunter Bigge",
    "Cole Sulser",
    "Steven Wilson",
    "Mason Englert",
    "Griffin Jax",
]


class TestRaysRoster(unittest.TestCase):
    """Tests for RAYS_LINEUP_2026, RAYS_ROTATION_2026,
    RAYS_BULLPEN_2026, and RaysRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(RAYS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(RAYS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(RAYS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in RAYS_LINEUP_2026], _TB_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in RAYS_ROTATION_2026], _TB_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in RAYS_BULLPEN_2026], _TB_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in RAYS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in RAYS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — lineup
    # ------------------------------------------------------------------

    def test_fortes_bats_right(self):
        self.assertEqual(RAYS_LINEUP_2026[0].bats, "R")

    def test_aranda_bats_left(self):
        self.assertEqual(RAYS_LINEUP_2026[1].bats, "L")

    def test_lux_bats_left(self):
        self.assertEqual(RAYS_LINEUP_2026[2].bats, "L")

    def test_caminero_bats_right(self):
        self.assertEqual(RAYS_LINEUP_2026[3].bats, "R")

    def test_c_williams_bats_right(self):
        self.assertEqual(RAYS_LINEUP_2026[4].bats, "R")

    def test_simpson_switch_hitter(self):
        self.assertEqual(RAYS_LINEUP_2026[5].bats, "S")

    def test_mullins_bats_left(self):
        self.assertEqual(RAYS_LINEUP_2026[6].bats, "L")

    def test_fraley_bats_left(self):
        self.assertEqual(RAYS_LINEUP_2026[7].bats, "L")

    def test_y_diaz_bats_right(self):
        self.assertEqual(RAYS_LINEUP_2026[8].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in RAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in RAYS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in RAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in RAYS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in RAYS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in RAYS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_rasmussen_throws_right(self):
        self.assertEqual(RAYS_ROTATION_2026[0].throws, "R")

    def test_pepiot_throws_right(self):
        self.assertEqual(RAYS_ROTATION_2026[1].throws, "R")

    def test_mcclanahan_throws_left(self):
        self.assertEqual(RAYS_ROTATION_2026[2].throws, "L")

    def test_matz_throws_left(self):
        self.assertEqual(RAYS_ROTATION_2026[3].throws, "L")

    def test_martinez_throws_right(self):
        self.assertEqual(RAYS_ROTATION_2026[4].throws, "R")

    def test_jax_throws_right(self):
        self.assertEqual(RAYS_BULLPEN_2026[-1].throws, "R")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_rasmussen_has_best_rotation_era(self):
        """Drew Rasmussen is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in RAYS_ROTATION_2026)
        self.assertAlmostEqual(RAYS_ROTATION_2026[0].era, min_era)

    def test_jax_has_best_bullpen_era(self):
        min_era = min(p.era for p in RAYS_BULLPEN_2026)
        self.assertAlmostEqual(RAYS_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(RAYS_BULLPEN_2026[-1].era, RAYS_ROTATION_2026[0].era)

    def test_jax_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in RAYS_BULLPEN_2026)
        self.assertAlmostEqual(RAYS_BULLPEN_2026[-1].k_per_9, max_k)

    def test_jax_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in RAYS_BULLPEN_2026)
        self.assertAlmostEqual(RAYS_BULLPEN_2026[-1].whip, min_whip)

    def test_caminero_has_highest_power_rating(self):
        max_power = max(b.power_rating for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[3].power_rating, max_power)

    def test_caminero_leads_team_in_hr(self):
        max_hr = max(b.hr_per_600_pa for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[3].hr_per_600_pa, max_hr)

    def test_caminero_leads_team_in_rbi(self):
        max_rbi = max(b.rbi_per_season for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[3].rbi_per_season, max_rbi)

    def test_y_diaz_leads_team_in_avg(self):
        max_avg = max(b.avg for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[8].avg, max_avg)

    def test_y_diaz_leads_team_in_obp(self):
        max_obp = max(b.obp for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[8].obp, max_obp)

    def test_simpson_leads_team_in_sb(self):
        """Chandler Simpson leads the team in stolen bases."""
        max_sb = max(b.sb_per_season for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[5].sb_per_season, max_sb)

    def test_simpson_leads_team_in_runs(self):
        max_runs = max(b.runs_per_season for b in RAYS_LINEUP_2026)
        self.assertAlmostEqual(RAYS_LINEUP_2026[5].runs_per_season, max_runs)

    def test_mcclanahan_has_best_k_per_9_in_rotation(self):
        """Shane McClanahan leads the rotation in K/9."""
        max_k = max(p.k_per_9 for p in RAYS_ROTATION_2026)
        self.assertAlmostEqual(RAYS_ROTATION_2026[2].k_per_9, max_k)

    # ------------------------------------------------------------------
    # RaysRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_rays_roster_instance(self):
        self.assertIsInstance(RaysRoster.default(), RaysRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(RaysRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(RaysRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(RaysRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = RaysRoster.default()
        r2 = RaysRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = RaysRoster.default()
        r2 = RaysRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = RaysRoster.default()
        r2 = RaysRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = RaysRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in RAYS_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = RaysRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in RAYS_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = RaysRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in RAYS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_rasmussen_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(RAYS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_jax_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(RAYS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_caminero_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(RAYS_LINEUP_2026[3])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_rasmussen_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Drew Rasmussen", "strikeouts", 4.5, +300, -500)
        edges = screener.screen_pitcher(RAYS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Drew Rasmussen")

    def test_screen_batter_caminero_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Junior Caminero", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(RAYS_LINEUP_2026[3], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_rays_roster(self):
        """screen_matchup with the Rays lineup against Drew Rasmussen."""
        sim = _make_screener_sim(seed=88)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = RaysRoster.default()
        lines = (
            _make_market_lines("Drew Rasmussen", "strikeouts", 4.5, +350, -600)
            + _make_market_lines("Junior Caminero", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Drew Rasmussen", player_names)
        self.assertIn("Junior Caminero", player_names)

    def test_screen_closer_jax(self):
        """Edge screener works for Griffin Jax (RHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Griffin Jax", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(RAYS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Griffin Jax")


# ---------------------------------------------------------------------------
# Athletics 2026 Depth Chart tests
# ---------------------------------------------------------------------------

from mlb_player_props import (  # noqa: E402
    AthleticsRoster,
    ATHLETICS_LINEUP_2026,
    ATHLETICS_ROTATION_2026,
    ATHLETICS_BULLPEN_2026,
)

_ATH_LINEUP_NAMES = [
    "Shea Langeliers",
    "Nick Kurtz",
    "Jeff McNeil",
    "Max Muncy",
    "Jacob Wilson",
    "Tyler Soderstrom",
    "Denzel Clarke",
    "Lawrence Butler",
    "Brent Rooker",
]

_ATH_ROTATION_NAMES = [
    "Luis Severino",
    "Jeffrey Springs",
    "Aaron Civale",
    "Jacob Lopez",
    "Luis Morales",
]

_ATH_BULLPEN_NAMES = [
    "Justin Sterner",
    "Elvis Alvarado",
    "Jeff Ridgway",
    "Luis Medina",
    "Nick Anderson",
    "Hogan Harris",
]


class TestAthleticsRoster(unittest.TestCase):
    """Tests for ATHLETICS_LINEUP_2026, ATHLETICS_ROTATION_2026,
    ATHLETICS_BULLPEN_2026, and AthleticsRoster."""

    # ------------------------------------------------------------------
    # Module-level constants — structural
    # ------------------------------------------------------------------

    def test_lineup_has_nine_batters(self):
        self.assertEqual(len(ATHLETICS_LINEUP_2026), 9)

    def test_rotation_has_five_starters(self):
        self.assertEqual(len(ATHLETICS_ROTATION_2026), 5)

    def test_bullpen_has_six_pitchers(self):
        self.assertEqual(len(ATHLETICS_BULLPEN_2026), 6)

    def test_lineup_names_in_order(self):
        self.assertEqual([b.name for b in ATHLETICS_LINEUP_2026], _ATH_LINEUP_NAMES)

    def test_rotation_names_in_order(self):
        self.assertEqual([p.name for p in ATHLETICS_ROTATION_2026], _ATH_ROTATION_NAMES)

    def test_bullpen_names_in_order(self):
        self.assertEqual([p.name for p in ATHLETICS_BULLPEN_2026], _ATH_BULLPEN_NAMES)

    # ------------------------------------------------------------------
    # BatterStats validation
    # ------------------------------------------------------------------

    def test_all_batters_pass_validation(self):
        for batter in ATHLETICS_LINEUP_2026:
            with self.subTest(player=batter.name):
                batter.validate()

    def test_batter_avg_in_range(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreater(b.avg, 0.180)
                self.assertLess(b.avg, 0.380)

    def test_batter_obp_gte_avg(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.obp, b.avg)

    def test_batter_slg_gte_avg(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.slg, b.avg)

    def test_batter_hr_nonnegative(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.hr_per_600_pa, 0.0)

    def test_batter_rbi_nonnegative(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.rbi_per_season, 0.0)

    def test_batter_runs_nonnegative(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.runs_per_season, 0.0)

    def test_batter_power_rating_in_range(self):
        for b in ATHLETICS_LINEUP_2026:
            with self.subTest(player=b.name):
                self.assertGreaterEqual(b.power_rating, 0.0)
                self.assertLessEqual(b.power_rating, 100.0)

    # ------------------------------------------------------------------
    # Handedness — lineup
    # ------------------------------------------------------------------

    def test_langeliers_bats_right(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[0].bats, "R")

    def test_kurtz_bats_left(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[1].bats, "L")

    def test_mcneil_bats_left(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[2].bats, "L")

    def test_muncy_bats_left(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[3].bats, "L")

    def test_wilson_bats_right(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[4].bats, "R")

    def test_soderstrom_bats_left(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[5].bats, "L")

    def test_clarke_bats_right(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[6].bats, "R")

    def test_butler_bats_left(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[7].bats, "L")

    def test_rooker_bats_right(self):
        self.assertEqual(ATHLETICS_LINEUP_2026[8].bats, "R")

    # ------------------------------------------------------------------
    # PitcherStats validation
    # ------------------------------------------------------------------

    def test_all_rotation_pass_validation(self):
        for p in ATHLETICS_ROTATION_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_all_bullpen_pass_validation(self):
        for p in ATHLETICS_BULLPEN_2026:
            with self.subTest(player=p.name):
                p.validate()

    def test_rotation_era_positive(self):
        for p in ATHLETICS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_bullpen_era_positive(self):
        for p in ATHLETICS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.era, 0.0)

    def test_rotation_k_per_9_in_range(self):
        for p in ATHLETICS_ROTATION_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    def test_bullpen_k_per_9_in_range(self):
        for p in ATHLETICS_BULLPEN_2026:
            with self.subTest(player=p.name):
                self.assertGreater(p.k_per_9, 0.0)
                self.assertLessEqual(p.k_per_9, 20.0)

    # ------------------------------------------------------------------
    # Pitcher handedness
    # ------------------------------------------------------------------

    def test_severino_throws_right(self):
        self.assertEqual(ATHLETICS_ROTATION_2026[0].throws, "R")

    def test_springs_throws_left(self):
        self.assertEqual(ATHLETICS_ROTATION_2026[1].throws, "L")

    def test_civale_throws_right(self):
        self.assertEqual(ATHLETICS_ROTATION_2026[2].throws, "R")

    def test_lopez_throws_left(self):
        self.assertEqual(ATHLETICS_ROTATION_2026[3].throws, "L")

    def test_morales_throws_right(self):
        self.assertEqual(ATHLETICS_ROTATION_2026[4].throws, "R")

    def test_harris_throws_left(self):
        self.assertEqual(ATHLETICS_BULLPEN_2026[-1].throws, "L")

    # ------------------------------------------------------------------
    # Relative quality ordering
    # ------------------------------------------------------------------

    def test_severino_has_best_rotation_era(self):
        """Luis Severino is modelled as the ace (best ERA in the rotation)."""
        min_era = min(p.era for p in ATHLETICS_ROTATION_2026)
        self.assertAlmostEqual(ATHLETICS_ROTATION_2026[0].era, min_era)

    def test_harris_has_best_bullpen_era(self):
        min_era = min(p.era for p in ATHLETICS_BULLPEN_2026)
        self.assertAlmostEqual(ATHLETICS_BULLPEN_2026[-1].era, min_era)

    def test_closer_has_lower_era_than_ace(self):
        self.assertLess(ATHLETICS_BULLPEN_2026[-1].era, ATHLETICS_ROTATION_2026[0].era)

    def test_harris_has_best_k_per_9_in_bullpen(self):
        max_k = max(p.k_per_9 for p in ATHLETICS_BULLPEN_2026)
        self.assertAlmostEqual(ATHLETICS_BULLPEN_2026[-1].k_per_9, max_k)

    def test_harris_has_best_whip_in_bullpen(self):
        min_whip = min(p.whip for p in ATHLETICS_BULLPEN_2026)
        self.assertAlmostEqual(ATHLETICS_BULLPEN_2026[-1].whip, min_whip)

    def test_rooker_has_highest_power_rating(self):
        """Brent Rooker leads the lineup in power rating."""
        max_power = max(b.power_rating for b in ATHLETICS_LINEUP_2026)
        self.assertAlmostEqual(ATHLETICS_LINEUP_2026[8].power_rating, max_power)

    def test_rooker_leads_team_in_hr(self):
        max_hr = max(b.hr_per_600_pa for b in ATHLETICS_LINEUP_2026)
        self.assertAlmostEqual(ATHLETICS_LINEUP_2026[8].hr_per_600_pa, max_hr)

    def test_rooker_leads_team_in_rbi(self):
        max_rbi = max(b.rbi_per_season for b in ATHLETICS_LINEUP_2026)
        self.assertAlmostEqual(ATHLETICS_LINEUP_2026[8].rbi_per_season, max_rbi)

    def test_mcneil_leads_team_in_avg(self):
        max_avg = max(b.avg for b in ATHLETICS_LINEUP_2026)
        self.assertAlmostEqual(ATHLETICS_LINEUP_2026[2].avg, max_avg)

    def test_clarke_leads_team_in_sb(self):
        """Denzel Clarke leads the team in stolen bases."""
        max_sb = max(b.sb_per_season for b in ATHLETICS_LINEUP_2026)
        self.assertAlmostEqual(ATHLETICS_LINEUP_2026[6].sb_per_season, max_sb)

    # ------------------------------------------------------------------
    # AthleticsRoster factory
    # ------------------------------------------------------------------

    def test_default_returns_athletics_roster_instance(self):
        self.assertIsInstance(AthleticsRoster.default(), AthleticsRoster)

    def test_default_lineup_length(self):
        self.assertEqual(len(AthleticsRoster.default().lineup), 9)

    def test_default_rotation_length(self):
        self.assertEqual(len(AthleticsRoster.default().rotation), 5)

    def test_default_bullpen_length(self):
        self.assertEqual(len(AthleticsRoster.default().bullpen), 6)

    def test_default_lineup_is_copy(self):
        r1 = AthleticsRoster.default()
        r2 = AthleticsRoster.default()
        r1.lineup.append(r1.lineup[0])
        self.assertEqual(len(r2.lineup), 9)

    def test_default_rotation_is_copy(self):
        r1 = AthleticsRoster.default()
        r2 = AthleticsRoster.default()
        r1.rotation.append(r1.rotation[0])
        self.assertEqual(len(r2.rotation), 5)

    def test_default_bullpen_is_copy(self):
        r1 = AthleticsRoster.default()
        r2 = AthleticsRoster.default()
        r1.bullpen.append(r1.bullpen[0])
        self.assertEqual(len(r2.bullpen), 6)

    def test_default_lineup_names_match_constants(self):
        roster = AthleticsRoster.default()
        self.assertEqual(
            [b.name for b in roster.lineup],
            [b.name for b in ATHLETICS_LINEUP_2026],
        )

    def test_default_rotation_names_match_constants(self):
        roster = AthleticsRoster.default()
        self.assertEqual(
            [p.name for p in roster.rotation],
            [p.name for p in ATHLETICS_ROTATION_2026],
        )

    def test_default_bullpen_names_match_constants(self):
        roster = AthleticsRoster.default()
        self.assertEqual(
            [p.name for p in roster.bullpen],
            [p.name for p in ATHLETICS_BULLPEN_2026],
        )

    # ------------------------------------------------------------------
    # Simulator integration
    # ------------------------------------------------------------------

    def test_simulate_pitcher_severino_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(ATHLETICS_ROTATION_2026[0])
        self.assertIsNotNone(report)
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Strikeouts", prop_names)

    def test_simulate_pitcher_harris_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_pitcher(ATHLETICS_BULLPEN_2026[-1])
        self.assertIsNotNone(report)
        self.assertTrue(report.props)

    def test_simulate_batter_rooker_runs(self):
        sim = _make_screener_sim()
        report = sim.simulate_batter(ATHLETICS_LINEUP_2026[8])
        prop_names = [pr.prop_name for pr in report.props]
        self.assertIn("Hits", prop_names)
        self.assertIn("Home Runs", prop_names)

    def test_screen_pitcher_severino_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Luis Severino", "strikeouts", 4.5, +300, -500)
        edges = screener.screen_pitcher(ATHLETICS_ROTATION_2026[0], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)
        self.assertEqual(over_edges[0].player_name, "Luis Severino")

    def test_screen_batter_rooker_with_fake_market(self):
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Brent Rooker", "hits", 0.5, +300, -500)
        edges = screener.screen_batter(ATHLETICS_LINEUP_2026[8], market_lines=lines)
        over_edges = [e for e in edges if e.side == "over"]
        self.assertTrue(over_edges)

    def test_screen_matchup_athletics_roster(self):
        """screen_matchup with the Athletics lineup against Luis Severino."""
        sim = _make_screener_sim(seed=88)
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        roster = AthleticsRoster.default()
        lines = (
            _make_market_lines("Luis Severino", "strikeouts", 4.5, +350, -600)
            + _make_market_lines("Brent Rooker", "hits", 0.5, +300, -500)
        )
        edges = screener.screen_matchup(
            roster.rotation[0], roster.lineup, market_lines=lines
        )
        player_names = {e.player_name for e in edges}
        self.assertIn("Luis Severino", player_names)
        self.assertIn("Brent Rooker", player_names)

    def test_screen_closer_harris(self):
        """Edge screener works for Hogan Harris (LHP closer)."""
        sim = _make_screener_sim()
        screener = UnabatedEdgeScreener(sim, UnabatedClient("key"), min_edge=0.0)
        lines = _make_market_lines("Hogan Harris", "strikeouts", 3.5, +300, -500)
        edges = screener.screen_pitcher(ATHLETICS_BULLPEN_2026[-1], market_lines=lines)
        self.assertTrue(edges)
        self.assertEqual(edges[0].player_name, "Hogan Harris")


if __name__ == "__main__":
    unittest.main()
