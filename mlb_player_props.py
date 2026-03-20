"""
MLB Player Props Simulator
==========================
Simulates individual player prop outcomes for MLB games including:
  - Pitcher props: Strikeouts, Outs recorded, Runs Allowed, Pitch Count
  - Batter props:  Hits, Doubles, Home Runs, Stolen Bases, Plate Appearances,
                   H+R+RBI (Hits + Runs Scored + RBI)

Environmental modifiers applied to every simulation:
  - Weather conditions  (temperature, precipitation, humidity)
  - Wind conditions     (speed, direction relative to field)
  - Air density         (altitude and barometric pressure)
      * Thin air (high altitude / low pressure) boosts HR, hits, and runs;
        slightly reduces K rate (less pitch-break effectiveness).
      * Standard sea-level density produces neutral multipliers (1.0).
      * See AirDensity class.  Examples: Denver ≈ 5 280 ft, New York ≈ 0 ft.
  - Stadium / Park factors (per-venue adjustments for each stat type)
  - Game time           (``"day"`` | ``"night"`` | ``"dome"``)
      * ``"day"``  – noon/afternoon game: solar heating amplifies temperature
        effects on ball travel and contact; afternoon convection makes wind
        deviations ~15 % stronger.
      * ``"night"`` – evening game (default): all effects applied at face value.
      * ``"dome"``  – climate-controlled indoor stadium: temperature and
        humidity effects are neutralised; precipitation never applies; wind
        effects are zero regardless of WindConditions values.

Player-attribute modifiers:
  - Pitcher arm strength (0–100 scale) – affects K rate, runs allowed, and
    innings pitched depth.
  - Pitcher pitches per plate appearance (`pitches_per_pa`) – how efficient/
    dominant the pitcher is per batter faced; higher = deeper counts.
  - Batter power rating  (0–100 scale) – affects HR rate and doubles rate.
  - Batter pitches per plate appearance (`pitches_per_pa`) – how deep the
    batter works counts; higher = more pitches seen per trip to the plate.

Platoon / handedness splits:
  - Pitcher throwing hand (`throws`: "R" or "L").
  - Batter batting hand   (`bats`:   "R", "L", or "S" for switch).
  - Opposite-hand matchups (e.g. RHB vs LHP) favour the batter; same-hand
    matchups favour the pitcher.  See PLATOON_SPLITS for per-combo adjustments.

Home / Away splits:
  - Pass ``is_home=True`` to ``simulate_pitcher`` / ``simulate_batter`` when
    the player is playing at their home ballpark, or ``is_home=False`` for a
    road game.  Omitting the argument (``None``) skips the adjustment.
  - On average batters hit ~3–5 % better at home; pitchers allow ~3 % fewer
    runs at home.  See HOME_AWAY_BATTER_SPLITS and HOME_AWAY_PITCHER_SPLITS.

Usage example
-------------
    from mlb_player_props import (
        MLBPlayerPropsSimulator,
        WeatherConditions,
        WindConditions,
        AirDensity,
        Stadium,
        PitcherStats,
        BatterStats,
    )

    stadium = Stadium.from_name("Wrigley Field")
    weather = WeatherConditions(temp_f=72, precipitation="none", humidity=0.55,
                                game_time="night")   # "day" | "night" | "dome"
    wind    = WindConditions(speed_mph=15, direction="out_to_center")
    air     = AirDensity(altitude_ft=0, barometric_pressure_inhg=29.92)  # sea level

    sim = MLBPlayerPropsSimulator(stadium=stadium, weather=weather, wind=wind,
                                  air_density=air, num_simulations=10_000)

    # Left-handed pitcher — pitching at home (is_home=True)
    pitcher = PitcherStats(name="Ace Pitcher", era=3.50, k_per_9=9.5,
                           innings_per_start=6.0, whip=1.15,
                           arm_strength=75, throws="L", pitches_per_pa=4.1)
    # Right-handed power hitter — away game (is_home=False)
    batter  = BatterStats(name="Power Hitter", avg=0.285, obp=0.360,
                          slg=0.510, hr_per_600_pa=32, sb_per_season=18,
                          doubles_per_600_pa=38, games_played=162,
                          power_rating=80, bats="R", pitches_per_pa=4.2)

    pitcher_results = sim.simulate_pitcher(pitcher, opponent_bats="R", is_home=True)
    batter_results  = sim.simulate_batter(batter, opponent_throws="L", is_home=False)

    sim.print_results(pitcher_results)
    sim.print_results(batter_results)

Machine Learning — Prop Calibration
------------------------------------
:class:`PropCalibrator` trains one Ridge Regression model per prop type
(pure Python, no external dependencies) via stochastic gradient descent with
L2 regularisation.  After fitting on historical :class:`GameLogRecord` data it
predicts a calibration multiplier that corrects systematic bias in the raw
Monte Carlo output.

::

    from mlb_player_props import GameLogRecord, PropCalibrator

    records = [
        GameLogRecord("Strikeouts", actual=7, sim_mean=5.5,
                      features={"era": 3.0, "k_per_9": 11.0, "temp_f": 70}),
        # … many more records …
    ]
    cal = PropCalibrator().fit(records)
    # Pass the fitted calibrator to the simulator:
    sim = MLBPlayerPropsSimulator(stadium=stadium, weather=weather, wind=wind,
                                  calibrator=cal)
    # Subsequent simulate_pitcher / simulate_batter calls apply calibration
    # automatically.

    # Inspect which features the model learned were most predictive:
    for feat, weight in cal.feature_importances("Strikeouts"):
        print(f"  {feat}: {weight:+.4f}")
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRECIPITATION_FACTOR: Dict[str, float] = {
    "none": 1.00,
    "light": 0.96,
    "moderate": 0.90,
    "heavy": 0.82,
}

# Wind direction effect on offensive output.
# "out_to_*" = blowing toward the outfield fence (hitter-friendly).
# "in_from_*" = blowing from outfield toward home plate (pitcher-friendly).
WIND_DIRECTION_HR_FACTOR: Dict[str, float] = {
    "out_to_center": 1.15,
    "out_to_left": 1.10,
    "out_to_right": 1.10,
    "in_from_center": 0.87,
    "in_from_left": 0.90,
    "in_from_right": 0.90,
    "cross_left_right": 1.00,
    "cross_right_left": 1.00,
    "calm": 1.00,
}

# Probability that a steal attempt succeeds (league-average baseline).
STEAL_SUCCESS_RATE: float = 0.79

# Baseline innings per game (9 innings × number of at-bats per inning ≈ 27 outs).
OUTS_PER_GAME: int = 27

# At-bats per game for a typical lineup slot.
PA_PER_GAME: float = 4.2

# Simulation tuning constants
# -----------------------------
# Innings-per-start variation: centre shift and Gaussian std-dev.
IP_FLOOR_SHIFT: float = 0.80        # The minimum-side bias so early hooks are modelled.
IP_VARIANCE: float = 0.15           # Game-to-game noise around the starter's average IP.

# Strikeout Gaussian noise relative to sqrt(expected_k).
K_VARIANCE_FACTOR: float = 0.6

# Outs-recorded minimum (pitcher must face at least one full inning).
MIN_OUTS_RECORDED: float = 3.0
# Outs-recorded Gaussian noise relative to sqrt(expected_outs).
OUTS_VARIANCE_FACTOR: float = 0.3

# WHIP adjustment: baseline WHIP considered neutral; each unit above/below
# shifts expected runs by this fraction.
WHIP_BASELINE: float = 1.20
WHIP_RUNS_ADJUSTMENT: float = 0.25

# ---------------------------------------------------------------------------
# Pitch-count model constants
# ---------------------------------------------------------------------------
# League-average pitches thrown per plate appearance faced by the pitcher.
# Source: ~3.8 P/PA is the modern MLB average.
PITCHER_PITCHES_PER_PA_DEFAULT: float = 3.8

# Minimum and maximum reasonable P/PA values for validation.
PITCHER_PITCHES_PER_PA_MIN: float = 3.0
PITCHER_PITCHES_PER_PA_MAX: float = 5.5

# Game-to-game Gaussian noise on total pitch count (relative std-dev fraction).
PITCH_COUNT_VARIANCE: float = 0.08   # 8 % relative noise ≈ ±8 pitches on a 100-pitch game

# ---------------------------------------------------------------------------
# Batter pitches-per-PA model constants
# ---------------------------------------------------------------------------
# League-average pitches seen per plate appearance by the batter.
BATTER_PITCHES_PER_PA_DEFAULT: float = 3.8

# Minimum and maximum for validation.
BATTER_PITCHES_PER_PA_MIN: float = 2.5
BATTER_PITCHES_PER_PA_MAX: float = 5.5

# Game-to-game noise on batter pitches seen (relative std-dev fraction).
BATTER_PITCHES_VARIANCE: float = 0.10  # 10 % relative noise per game

# Plate-appearance variation around PA_PER_GAME (centre shift + std-dev).
PA_FLOOR_SHIFT: float = 0.85
PA_VARIANCE: float = 0.12

# Approximate ratio of at-bats to plate appearances (league average ~0.88).
PA_TO_AB_RATIO: float = 0.88

# Stolen-base per-game model noise (centre shift + std-dev fraction).
SB_FLOOR_SHIFT: float = 0.8
SB_VARIANCE: float = 0.4            # 40 % relative noise captures day-to-day variability.

# Maximum steal opportunities modelled per game (caps tail of distribution).
MAX_STEAL_OPPORTUNITIES_PER_GAME: int = 3

# ---------------------------------------------------------------------------
# Runs scored and RBI per-game model constants
# ---------------------------------------------------------------------------
# Runs scored per game: modelled from the player's season runs-per-game rate
# with a floor shift and Gaussian noise.
# ~35 % of on-base events turn into runs (dependent on lineup context).
RUNS_FLOOR_SHIFT: float = 0.80   # slight lower-side bias (bad nights, quick innings)
RUNS_VARIANCE: float = 0.35      # 35 % relative noise per game

# RBI per game: similar model; power drives RBI so the HR multiplier is used.
RBI_FLOOR_SHIFT: float = 0.80
RBI_VARIANCE: float = 0.35       # 35 % relative noise per game

# Temperature effects on batter contact rate.
# Baseline is 72 °F; each degree below baseline reduces contact slightly (slower
# bat speed in cold; stiff hands).  Warm weather provides a marginal boost.
TEMP_HIT_RATE_PER_DEGREE_F: float = 0.0015   # ±0.15 % per °F deviation from 72 °F

# Temperature thresholds and rates for pitcher stamina.
# Cold weather below TEMP_COLD_THRESHOLD_F reduces expected innings pitched.
# Extreme heat above TEMP_HOT_THRESHOLD_F also reduces stamina.
TEMP_COLD_THRESHOLD_F: float = 60.0
TEMP_HOT_THRESHOLD_F: float = 90.0
TEMP_COLD_STAMINA_RATE: float = 0.004   # −0.4 % of IP per °F below cold threshold
TEMP_HOT_STAMINA_RATE: float = 0.003    # −0.3 % of IP per °F above hot threshold

# Wind K-rate adjustment constants.
# In-blowing wind (pitcher-friendly) enhances pitch movement and slightly lifts Ks.
# Out-blowing or cross wind has a smaller boosting effect (distraction for batters).
WIND_K_IN_RATE: float = 0.002    # +0.2 % per mph when wind blows in
WIND_K_OTHER_RATE: float = 0.001  # +0.1 % per mph for other directions

# Wind runs-allowed adjustment (mirrors HR factor but dampened for general runs).
# This value is used as: magnitude = speed_mph / 5.0 * WIND_RUNS_SPEED_FACTOR
# and then scaled by the direction's deviation from neutral, so the constant
# represents the runs-adjustment increment per 5-mph of wind speed per unit of
# directional deviation.
WIND_RUNS_SPEED_FACTOR: float = 0.015

# ---------------------------------------------------------------------------
# Air density constants
# ---------------------------------------------------------------------------
# Air density affects how far a batted ball carries (less-dense air = less
# drag = more distance = more HR and hits).  At altitude, thinner air also
# slightly reduces pitcher break / spin effectiveness, lowering K rates.
#
# Physical model (International Standard Atmosphere):
#   density_ratio(h, P) = ISA_alt_factor(h) × (P_actual / P_std)
#
#   ISA_alt_factor(h) = (1 - ALTITUDE_LAPSE × h) ^ ALTITUDE_EXPONENT
#   where h is feet above sea level.
#
# Calibration: Denver / Coors Field (5 280 ft) → density ≈ 85 % of sea level.
#   Empirically this produces roughly +9 % HR carry and +4 % hit carry, which
#   is distinct from the full Coors park factor (which also includes park
#   dimensions, local hitting culture, etc.).

# Standard sea-level barometric pressure used as the baseline.
AIR_DENSITY_STD_PRESSURE_INHG: float = 29.92  # inches of mercury (ISA sea level)

# ISA barometric-formula coefficients (altitude in feet).
AIR_DENSITY_ALTITUDE_LAPSE:    float = 6.87559e-6   # ft⁻¹ temperature lapse coefficient
AIR_DENSITY_ALTITUDE_EXPONENT: float = 4.25587       # dimensionless ISA exponent

# Sensitivity constants: multiply (1 − density_ratio) to get the fractional
# change in each stat.  Positive → thin air boosts the stat; negative → reduces.
AIR_DENSITY_HR_SENSITIVITY:    float = 0.60  # 60 % of density deficit → HR boost
AIR_DENSITY_HITS_SENSITIVITY:  float = 0.25  # 25 % of density deficit → hits boost
AIR_DENSITY_K_SENSITIVITY:     float = 0.15  # 15 % of density deficit → K reduction
AIR_DENSITY_RUNS_SENSITIVITY:  float = 0.40  # 40 % of density deficit → runs boost

# ---------------------------------------------------------------------------
# Machine Learning — Prop Calibration constants
# ---------------------------------------------------------------------------
# PropCalibrator trains one L2-regularised linear model (Ridge Regression) per
# prop type via stochastic gradient descent (SGD).  Once trained, it predicts a
# calibration multiplier that adjusts the raw Monte Carlo simulation mean to
# reduce systematic bias when historical game-log data is available.
#
# The entire implementation is pure Python — no numpy or scikit-learn required.

# SGD learning rate (step size for each parameter update).
ML_LEARNING_RATE: float = 0.01

# L2 regularisation strength (ridge penalty applied to weights, not the bias).
# Larger values keep weights small and reduce overfitting.
ML_L2_LAMBDA: float = 0.001

# Maximum number of SGD passes over the training data (epochs).
ML_MAX_EPOCHS: int = 500

# Early-stopping threshold: training halts when the epoch-to-epoch loss
# improvement falls below this absolute value (avoids unnecessary iterations).
ML_CONVERGENCE_TOL: float = 1e-6

# Minimum number of historical records required for a given prop before the
# calibrator will train a model for that prop.
ML_MIN_RECORDS_PER_PROP: int = 5

# The calibration multiplier is clamped to this range to prevent extreme
# corrections that would override the physics-based simulation entirely.
ML_MULTIPLIER_MIN: float = 0.70   # at most 30 % downward correction
ML_MULTIPLIER_MAX: float = 1.30   # at most 30 % upward correction

# ---------------------------------------------------------------------------
# Game-time (day / night / dome) constants
# ---------------------------------------------------------------------------
# "day"   – noon / afternoon game played outdoors in direct sunlight.
#           Solar radiation heats the ball and air beyond the stated air
#           temperature, amplifying temperature-driven effects.  Daytime
#           convective mixing also tends to make winds gustier.
# "night" – evening game under artificial lighting; effects are applied at
#           face value (this is the historical default / baseline).
# "dome"  – indoor stadium with climate control.  Temperature is held near
#           72 °F and precipitation never occurs, so the corresponding
#           multipliers are neutralised.  Wind is also effectively zero
#           regardless of any WindConditions values.
#
# Valid game_time values accepted by WeatherConditions.
VALID_GAME_TIMES: frozenset[str] = frozenset({"day", "night", "dome"})

# Day game: direct sunlight amplifies the per-degree temperature effect on
# ball travel and batter contact (ball is warmer/harder than stated temp).
DAY_GAME_TEMP_AMPLIFIER: float = 1.5      # 50 % larger temperature-deviation effect

# Day game: afternoon convective winds tend to be gustier; scale wind
# deviations from neutral by this factor in day games.
DAY_GAME_WIND_AMPLIFIER: float = 1.15    # 15 % stronger effective wind deviation

# Dome game: all environmental effects are neutralised.
DOME_TEMP_AMPLIFIER: float = 0.0          # no temperature effect in a controlled dome
DOME_WIND_AMPLIFIER: float = 0.0          # no wind effect in an indoor stadium

# ---------------------------------------------------------------------------
# Pitcher arm-strength tuning constants
# ---------------------------------------------------------------------------
# Arm strength is expressed on a 0–100 scale where 50 is league-average.
# The three rates below define how far each output shifts per point of
# arm-strength deviation from the baseline.

ARM_STRENGTH_BASELINE: float = 50.0  # neutral midpoint (league average)
# Each point above the baseline adds this fraction to expected K rate.
ARM_K_RATE: float = 0.006            # ±0.6 % per point  (10-pt swing ≈ ±6 %)
# Each point above the baseline *reduces* expected runs allowed by this fraction.
ARM_RUNS_RATE: float = 0.004         # ±0.4 % per point  (10-pt swing ≈ ±4 %)
# Each point above the baseline extends expected innings pitched by this fraction.
ARM_IP_RATE: float = 0.003           # ±0.3 % per point  (10-pt swing ≈ ±3 %)

# ---------------------------------------------------------------------------
# Batter power-rating tuning constants
# ---------------------------------------------------------------------------
# Power rating is expressed on a 0–100 scale where 50 is league-average.

POWER_BASELINE: float = 50.0         # neutral midpoint (league average)
# Each point above the baseline adds this fraction to expected HR rate.
POWER_HR_RATE: float = 0.010         # ±1.0 % per point  (10-pt swing ≈ ±10 %)
# Each point above the baseline adds this fraction to expected doubles rate.
POWER_DOUBLES_RATE: float = 0.005    # ±0.5 % per point  (10-pt swing ≈ ±5 %)

# ---------------------------------------------------------------------------
# Platoon split constants (batter handedness × pitcher handedness)
# ---------------------------------------------------------------------------
# Each entry maps a (bats, throws) tuple to a dict of multipliers applied on
# top of all other modifiers:
#   hits    – batter hit rate adjustment
#   hr      – batter home-run rate adjustment
#   doubles – batter doubles rate adjustment
#   k       – pitcher strikeout rate adjustment  (>1 = pitcher advantage)
#   runs    – pitcher runs-allowed adjustment    (>1 = more runs for pitcher)
#
# Calibration basis:
#   Opposite-hand matchups (e.g. RHB vs LHP) historically yield ~4–8 % more
#   hits and ~7–10 % more HRs for the batter; same-hand matchups yield a
#   ~3–5 % batter penalty (pitcher advantage in Ks, fewer runs scored).
#   Switch hitters ("S") are always neutral regardless of pitcher hand.

PLATOON_SPLITS: Dict[Tuple[str, str], Dict[str, float]] = {
    # (bats, throws) : batter boost   , pitcher K boost
    ("R", "R"): {"hits": 0.97, "hr": 0.95, "doubles": 0.97, "k": 1.05, "runs": 0.97},
    ("R", "L"): {"hits": 1.04, "hr": 1.07, "doubles": 1.04, "k": 0.95, "runs": 1.04},
    ("L", "L"): {"hits": 0.96, "hr": 0.94, "doubles": 0.96, "k": 1.06, "runs": 0.96},
    ("L", "R"): {"hits": 1.05, "hr": 1.08, "doubles": 1.05, "k": 0.94, "runs": 1.05},
    ("S", "R"): {"hits": 1.00, "hr": 1.00, "doubles": 1.00, "k": 1.00, "runs": 1.00},
    ("S", "L"): {"hits": 1.00, "hr": 1.00, "doubles": 1.00, "k": 1.00, "runs": 1.00},
}

# Sentinel value returned when the (bats, throws) combination is not found.
_PLATOON_NEUTRAL: Dict[str, float] = {
    "hits": 1.00, "hr": 1.00, "doubles": 1.00, "k": 1.00, "runs": 1.00
}


def platoon_splits_for(bats: str, throws: str) -> Dict[str, float]:
    """
    Return the platoon-split multiplier dict for a given (bats, throws) combo.

    Parameters
    ----------
    bats   : "R" (right), "L" (left), or "S" (switch hitter)
    throws : "R" (right) or "L" (left)

    Returns
    -------
    Dict with keys "hits", "hr", "doubles", "k", "runs".
    Falls back to all-1.0 neutral values for unrecognised combinations.

    Examples
    --------
    >>> platoon_splits_for("R", "L")          # RHB vs LHP – batter advantage
    {'hits': 1.04, 'hr': 1.07, 'doubles': 1.04, 'k': 0.95, 'runs': 1.04}
    >>> platoon_splits_for("L", "R")          # LHB vs RHP – batter advantage
    {'hits': 1.05, 'hr': 1.08, 'doubles': 1.05, 'k': 0.94, 'runs': 1.05}
    >>> platoon_splits_for("R", "R")          # RHB vs RHP – pitcher advantage
    {'hits': 0.97, 'hr': 0.95, 'doubles': 0.97, 'k': 1.05, 'runs': 0.97}
    >>> platoon_splits_for("S", "L")          # Switch hitter – always neutral
    {'hits': 1.0, 'hr': 1.0, 'doubles': 1.0, 'k': 1.0, 'runs': 1.0}
    """
    return PLATOON_SPLITS.get((bats, throws), _PLATOON_NEUTRAL)


# ---------------------------------------------------------------------------
# Home / Away split constants
# ---------------------------------------------------------------------------
# Calibration basis:
#   Historically MLB home teams win ~54 % of games. Batters hit approximately
#   3–5 % better at home (comfort, familiarity with the park, crowd energy).
#   Pitchers allow ~3 % fewer runs at home and go slightly deeper into games.
#
# Keys for each dict:
#   Batter  splits — "hits", "hr", "doubles"
#   Pitcher splits — "k" (strikeout rate), "runs" (runs allowed), "ip" (innings)
#
# Using "home" / "away" string keys keeps the dict easily extendable (e.g. a
# future "neutral" site for playoff games).

HOME_AWAY_BATTER_SPLITS: Dict[str, Dict[str, float]] = {
    "home": {"hits": 1.03, "hr": 1.05, "doubles": 1.03},
    "away": {"hits": 0.97, "hr": 0.95, "doubles": 0.97},
}

HOME_AWAY_PITCHER_SPLITS: Dict[str, Dict[str, float]] = {
    "home": {"k": 1.02, "runs": 0.97, "ip": 1.01},
    "away": {"k": 0.98, "runs": 1.03, "ip": 0.99},
}

# Sentinel neutral values (used when is_home is None).
_HOME_AWAY_BATTER_NEUTRAL: Dict[str, float] = {"hits": 1.00, "hr": 1.00, "doubles": 1.00}
_HOME_AWAY_PITCHER_NEUTRAL: Dict[str, float] = {"k": 1.00, "runs": 1.00, "ip": 1.00}


def home_away_batter_splits_for(is_home: Optional[bool]) -> Dict[str, float]:
    """
    Return the home/away multiplier dict for a batter.

    Parameters
    ----------
    is_home : True for a home game, False for an away game, None for neutral
              (no adjustment applied).

    Returns
    -------
    Dict with keys "hits", "hr", "doubles".

    Examples
    --------
    >>> home_away_batter_splits_for(True)
    {'hits': 1.03, 'hr': 1.05, 'doubles': 1.03}
    >>> home_away_batter_splits_for(False)
    {'hits': 0.97, 'hr': 0.95, 'doubles': 0.97}
    >>> home_away_batter_splits_for(None)
    {'hits': 1.0, 'hr': 1.0, 'doubles': 1.0}
    """
    if is_home is None:
        return _HOME_AWAY_BATTER_NEUTRAL
    return HOME_AWAY_BATTER_SPLITS["home" if is_home else "away"]


def home_away_pitcher_splits_for(is_home: Optional[bool]) -> Dict[str, float]:
    """
    Return the home/away multiplier dict for a pitcher.

    Parameters
    ----------
    is_home : True for a home game, False for an away game, None for neutral
              (no adjustment applied).

    Returns
    -------
    Dict with keys "k", "runs", "ip".

    Examples
    --------
    >>> home_away_pitcher_splits_for(True)
    {'k': 1.02, 'runs': 0.97, 'ip': 1.01}
    >>> home_away_pitcher_splits_for(False)
    {'k': 0.98, 'runs': 1.03, 'ip': 0.99}
    >>> home_away_pitcher_splits_for(None)
    {'k': 1.0, 'runs': 1.0, 'ip': 1.0}
    """
    if is_home is None:
        return _HOME_AWAY_PITCHER_NEUTRAL
    return HOME_AWAY_PITCHER_SPLITS["home" if is_home else "away"]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class WindConditions:
    """Describes the wind at game time."""

    speed_mph: float = 0.0
    direction: str = "calm"  # See WIND_DIRECTION_HR_FACTOR keys

    def hr_multiplier(self) -> float:
        """Return a home-run distance multiplier based on wind speed and direction."""
        base = WIND_DIRECTION_HR_FACTOR.get(self.direction, 1.00)
        # Each 5 mph of "out" wind adds ~2 % to HR probability; "in" wind subtracts.
        magnitude = self.speed_mph / 5.0 * 0.02
        if base > 1.0:
            return base + magnitude * (base - 1.0) * 5
        elif base < 1.0:
            return base - magnitude * (1.0 - base) * 5
        return 1.00

    def hit_multiplier(self) -> float:
        """Blowing-out wind helps elevate fly balls into hits; blowing-in hurts."""
        base = WIND_DIRECTION_HR_FACTOR.get(self.direction, 1.00)
        # Smaller effect on overall hits than on HR.
        return 1.0 + (base - 1.0) * 0.4

    def k_multiplier(self) -> float:
        """
        Wind direction effect on pitcher strikeout rate.

        * In-blowing wind (pitcher-friendly directions) enhances pitch movement
          and makes it harder for batters to track off-speed pitches.
        * Out-blowing or cross wind has a smaller but still positive effect —
          batters must adjust their eye on wind-affected trajectories.
        * Effect scales with wind speed.
        """
        base = WIND_DIRECTION_HR_FACTOR.get(self.direction, 1.00)
        if base < 1.0:
            # Wind blowing in — helps pitch movement more
            return 1.0 + self.speed_mph * WIND_K_IN_RATE
        # Calm, cross, or out wind — smaller K boost
        return 1.0 + self.speed_mph * WIND_K_OTHER_RATE

    def runs_multiplier(self) -> float:
        """
        Wind direction effect on runs allowed.

        Mirrors the HR factor directional logic (out-blowing wind carries more
        balls to the outfield seats, increasing run scoring) but with a
        dampened speed-scaling compared to the pure HR multiplier.
        """
        base = WIND_DIRECTION_HR_FACTOR.get(self.direction, 1.00)
        magnitude = self.speed_mph / 5.0 * WIND_RUNS_SPEED_FACTOR
        if base > 1.0:
            return base + magnitude * (base - 1.0) * 5
        elif base < 1.0:
            return base - magnitude * (1.0 - base) * 5
        return 1.00


@dataclass
class AirDensity:
    """
    Describes the air density at the game venue.

    Air density determines how much drag a batted ball experiences in flight:

    * **Thin air** (high altitude or low barometric pressure) reduces aerodynamic
      drag, causing fly balls to carry farther.  This boosts HR probability, hit
      rate, and run scoring while slightly reducing pitcher break effectiveness
      (lower K rate).
    * **Dense air** (near sea level or high barometric pressure) increases drag,
      suppressing carry distance (slight HR and hits penalty).
    * **Sea-level baseline** (``altitude_ft=0``, ``barometric_pressure_inhg=29.92``)
      produces a ``density_ratio`` of exactly 1.0 and all multipliers equal 1.0.

    Parameters
    ----------
    altitude_ft : float
        Venue elevation above sea level in feet.  Examples: Denver ≈ 5 280 ft,
        Atlanta ≈ 1 050 ft, New York / Boston ≈ 0–50 ft.
    barometric_pressure_inhg : float
        Actual barometric pressure at game time in inches of mercury.
        Defaults to the International Standard Atmosphere (ISA) sea-level value
        of 29.92 inHg.  Low pressure (e.g., a storm system) further reduces
        density; high pressure (e.g., cold high-pressure ridge) increases it.
    """

    altitude_ft: float = 0.0
    barometric_pressure_inhg: float = AIR_DENSITY_STD_PRESSURE_INHG

    def density_ratio(self) -> float:
        """
        Ratio of actual air density to the ISA sea-level standard density.

        Uses the International Standard Atmosphere barometric formula:

        ``density_ratio = (1 − LAPSE × altitude_ft)^EXPONENT × (P_actual / P_std)``

        Returns 1.0 at sea level with standard pressure; < 1.0 in thin air
        (high altitude or low pressure); > 1.0 in dense air (below sea level
        or high barometric pressure).
        """
        alt_factor = (
            (1.0 - AIR_DENSITY_ALTITUDE_LAPSE * self.altitude_ft)
            ** AIR_DENSITY_ALTITUDE_EXPONENT
        )
        pressure_factor = self.barometric_pressure_inhg / AIR_DENSITY_STD_PRESSURE_INHG
        return alt_factor * pressure_factor

    def hr_multiplier(self) -> float:
        """
        Home-run probability multiplier from air density.

        Thin air (density < 1) boosts HR carry; dense air (density > 1)
        suppresses it.  Linear scaling by AIR_DENSITY_HR_SENSITIVITY.
        """
        return 1.0 + (1.0 - self.density_ratio()) * AIR_DENSITY_HR_SENSITIVITY

    def hits_multiplier(self) -> float:
        """
        Overall hit-rate multiplier from air density.

        Thinner air carries fly balls and line drives slightly farther, turning
        more outs into hits.  Effect is smaller than the HR effect.
        """
        return 1.0 + (1.0 - self.density_ratio()) * AIR_DENSITY_HITS_SENSITIVITY

    def k_multiplier(self) -> float:
        """
        Pitcher strikeout-rate multiplier from air density.

        In thin air, breaking balls have reduced spin effectiveness, making them
        easier to track and lay off.  This slightly reduces K rate.
        Returns < 1 at altitude; > 1 in dense (sea-level) air.
        """
        return 1.0 - (1.0 - self.density_ratio()) * AIR_DENSITY_K_SENSITIVITY

    def runs_multiplier(self) -> float:
        """
        Runs-allowed multiplier from air density.

        Mirrors the HR multiplier logic (thin air → more run scoring) but with
        a slightly smaller sensitivity constant.
        """
        return 1.0 + (1.0 - self.density_ratio()) * AIR_DENSITY_RUNS_SENSITIVITY


@dataclass
class WeatherConditions:
    """Describes the weather at game time.

    game_time selects one of three environmental regimes:

    * ``"night"`` (default) – evening game under artificial lighting.
      All temperature, wind, and precipitation values are applied at
      face value.  This is the historical baseline.
    * ``"day"`` – noon or afternoon game in direct sunlight.  Solar
      heating amplifies temperature-driven effects (ball travels farther
      than the stated air temperature alone would suggest) and daytime
      convective mixing makes wind deviations gustier.
    * ``"dome"`` – indoor, climate-controlled stadium.  Temperature is
      held near 72 °F and precipitation never occurs, so all temperature
      and humidity multipliers return 1.0.  Wind is also neutralised (see
      :meth:`game_time_wind_amplifier`).
    """

    temp_f: float = 72.0
    precipitation: str = "none"   # none | light | moderate | heavy
    humidity: float = 0.50        # 0.0 – 1.0
    game_time: str = "night"      # "day" | "night" | "dome"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _game_time_temp_amplifier(self) -> float:
        """
        Scaling factor applied to every per-degree temperature deviation.

        * ``"day"``   → ``DAY_GAME_TEMP_AMPLIFIER`` (> 1; solar heating amplifies)
        * ``"night"`` → 1.0 (baseline — no change vs historical behaviour)
        * ``"dome"``  → ``DOME_TEMP_AMPLIFIER`` (0.0; controlled environment)
        """
        if self.game_time == "dome":
            return DOME_TEMP_AMPLIFIER
        if self.game_time == "day":
            return DAY_GAME_TEMP_AMPLIFIER
        return 1.0  # night: baseline

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def game_time_wind_amplifier(self) -> float:
        """
        Scaling factor applied to every wind-deviation in the simulator.

        * ``"day"``   → ``DAY_GAME_WIND_AMPLIFIER`` (> 1; afternoon gusts)
        * ``"night"`` → 1.0 (baseline)
        * ``"dome"``  → ``DOME_WIND_AMPLIFIER`` (0.0; no outdoor wind)
        """
        if self.game_time == "dome":
            return DOME_WIND_AMPLIFIER
        if self.game_time == "day":
            return DAY_GAME_WIND_AMPLIFIER
        return 1.0  # night: baseline

    def validate(self) -> None:
        if self.game_time not in VALID_GAME_TIMES:
            raise ValueError(
                f"game_time must be one of {sorted(VALID_GAME_TIMES)}, "
                f"got {self.game_time!r}"
            )
        if not (0.0 <= self.humidity <= 1.0):
            raise ValueError("humidity must be between 0.0 and 1.0")

    def temp_hr_multiplier(self) -> float:
        """
        Ball travels farther in warm air (less dense).
        Baseline is 72 °F; every 10 °F adds/subtracts ~3 %.

        In a dome the controlled environment removes all temperature
        deviation; in a day game solar heating amplifies the effect.
        """
        return 1.0 + (self.temp_f - 72) * 0.003 * self._game_time_temp_amplifier()

    def temp_k_multiplier(self) -> float:
        """
        Cold weather → harder grip → slight increase in Ks.

        Effect is scaled by the game-time amplifier (dome → no effect;
        day → amplified cold/heat deviation).
        """
        return 1.0 - (self.temp_f - 72) * 0.001 * self._game_time_temp_amplifier()

    def precip_factor(self) -> float:
        """
        Precipitation suppresses offensive output.

        In a dome precipitation never occurs and this always returns 1.0
        regardless of the ``precipitation`` field value.
        """
        if self.game_time == "dome":
            return 1.0
        return PRECIPITATION_FACTOR.get(self.precipitation, 1.00)

    def humidity_hit_multiplier(self) -> float:
        """
        High humidity makes the ball slightly heavier and harder to hit far.
        Effect is small (~2 % max).

        In a dome humidity is climate-controlled and this returns 1.0.
        """
        if self.game_time == "dome":
            return 1.0
        return 1.0 - (self.humidity - 0.50) * 0.04

    def temp_hit_multiplier(self) -> float:
        """
        Temperature effect on batter contact rate.

        Cold weather slows bat speed and stiffens hands, reducing batting
        average.  Warm weather provides a small positive boost to contact.
        Baseline is 72 °F; effect scales linearly at
        TEMP_HIT_RATE_PER_DEGREE_F per degree.

        The per-degree rate is further scaled by the game-time amplifier.
        """
        return 1.0 + (self.temp_f - 72) * TEMP_HIT_RATE_PER_DEGREE_F * self._game_time_temp_amplifier()

    def temp_pitcher_stamina_multiplier(self) -> float:
        """
        Temperature effect on pitcher stamina (expected innings pitched).

        * Below TEMP_COLD_THRESHOLD_F: cold reduces grip, increases effort per
          pitch, and leads to shorter outings.
        * Above TEMP_HOT_THRESHOLD_F: heat fatigue also shortens outings.
        * Between the two thresholds: no stamina penalty (returns 1.0).
        * In a dome: always 1.0 (climate-controlled).

        In a day game the per-degree penalty is amplified by
        ``DAY_GAME_TEMP_AMPLIFIER``, reflecting the additional strain of
        pitching in direct sunlight.
        """
        if self.game_time == "dome":
            return 1.0
        amp = self._game_time_temp_amplifier()
        if self.temp_f < TEMP_COLD_THRESHOLD_F:
            return 1.0 - (TEMP_COLD_THRESHOLD_F - self.temp_f) * TEMP_COLD_STAMINA_RATE * amp
        if self.temp_f > TEMP_HOT_THRESHOLD_F:
            return 1.0 - (self.temp_f - TEMP_HOT_THRESHOLD_F) * TEMP_HOT_STAMINA_RATE * amp
        return 1.0


@dataclass
class Stadium:
    """
    Park factors relative to a neutral 1.00 baseline.
    Values > 1.00 favour hitters / the listed event; < 1.00 favour pitchers.
    """

    name: str
    hr_factor: float = 1.00
    hits_factor: float = 1.00
    doubles_factor: float = 1.00
    k_factor: float = 1.00        # strikeouts (pitcher view)
    runs_factor: float = 1.00

    # ------------------------------------------------------------------
    # Built-in stadium catalogue
    # ------------------------------------------------------------------
    _STADIUMS: ClassVar[Dict[str, Dict]] = {
        # Name              hr     hits   2B     K      runs
        "Coors Field":        {"hr_factor": 1.39, "hits_factor": 1.13, "doubles_factor": 1.18, "k_factor": 0.91, "runs_factor": 1.35},
        "Great American Ball Park": {"hr_factor": 1.25, "hits_factor": 1.05, "doubles_factor": 1.08, "k_factor": 0.97, "runs_factor": 1.18},
        "Wrigley Field":      {"hr_factor": 1.12, "hits_factor": 1.03, "doubles_factor": 1.05, "k_factor": 0.99, "runs_factor": 1.07},
        "Fenway Park":        {"hr_factor": 1.04, "hits_factor": 1.08, "doubles_factor": 1.22, "k_factor": 0.98, "runs_factor": 1.05},
        "Dodger Stadium":     {"hr_factor": 0.95, "hits_factor": 0.97, "doubles_factor": 0.96, "k_factor": 1.02, "runs_factor": 0.94},
        "Oracle Park":        {"hr_factor": 0.79, "hits_factor": 0.95, "doubles_factor": 1.04, "k_factor": 1.03, "runs_factor": 0.89},
        "Petco Park":         {"hr_factor": 0.85, "hits_factor": 0.94, "doubles_factor": 0.97, "k_factor": 1.04, "runs_factor": 0.88},
        "Truist Park":        {"hr_factor": 1.08, "hits_factor": 1.02, "doubles_factor": 1.03, "k_factor": 1.00, "runs_factor": 1.04},
        "Yankee Stadium":     {"hr_factor": 1.20, "hits_factor": 1.01, "doubles_factor": 0.99, "k_factor": 0.99, "runs_factor": 1.08},
        "T-Mobile Park":      {"hr_factor": 0.96, "hits_factor": 0.97, "doubles_factor": 1.00, "k_factor": 1.01, "runs_factor": 0.95},
        "Kauffman Stadium":   {"hr_factor": 0.90, "hits_factor": 1.00, "doubles_factor": 1.02, "k_factor": 1.01, "runs_factor": 0.96},
        "Busch Stadium":      {"hr_factor": 0.92, "hits_factor": 0.99, "doubles_factor": 1.01, "k_factor": 1.02, "runs_factor": 0.94},
        "Globe Life Field":   {"hr_factor": 1.02, "hits_factor": 1.01, "doubles_factor": 1.01, "k_factor": 1.00, "runs_factor": 1.01},
        "Minute Maid Park":   {"hr_factor": 1.05, "hits_factor": 1.01, "doubles_factor": 1.08, "k_factor": 0.99, "runs_factor": 1.03},
        "Neutral":            {"hr_factor": 1.00, "hits_factor": 1.00, "doubles_factor": 1.00, "k_factor": 1.00, "runs_factor": 1.00},
    }

    @classmethod
    def from_name(cls, name: str) -> "Stadium":
        """Create a Stadium by well-known name.  Falls back to neutral factors."""
        data = cls._STADIUMS.get(name, cls._STADIUMS["Neutral"])
        return cls(name=name, **data)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        for attr in ("hr_factor", "hits_factor", "doubles_factor", "k_factor", "runs_factor"):
            v = getattr(self, attr)
            if not (0.5 <= v <= 2.0):
                raise ValueError(f"Stadium factor '{attr}' = {v} is outside the valid range [0.5, 2.0]")


@dataclass
class PitcherStats:
    """Season / career statistics for a starting pitcher."""

    name: str
    era: float                    # Earned Run Average
    k_per_9: float                # Strikeouts per 9 innings
    innings_per_start: float      # Average innings pitched per start
    whip: float                   # Walks + Hits per Inning Pitched
    arm_strength: float = 50.0    # 0–100 scale; 50 = league-average arm
    throws: str = "R"             # Throwing hand: "R" (right) or "L" (left)
    pitches_per_pa: float = PITCHER_PITCHES_PER_PA_DEFAULT
    # Average pitches thrown per batter faced.  League average ~3.8; higher
    # values indicate a pitcher who works deeper counts (more walks/strikeouts),
    # lower values indicate a quick-count, contact-allowing pitcher.

    # ------------------------------------------------------------------
    # Arm-strength multipliers
    # ------------------------------------------------------------------

    def arm_k_multiplier(self) -> float:
        """
        Stronger arm → better velocity and pitch movement → more strikeouts.

        Returns a multiplier > 1.0 for above-average arm strength and
        < 1.0 for below-average.
        """
        return 1.0 + (self.arm_strength - ARM_STRENGTH_BASELINE) * ARM_K_RATE

    def arm_runs_multiplier(self) -> float:
        """
        Stronger arm → harder for batters to square up → fewer runs allowed.

        Returns a multiplier < 1.0 for above-average arm strength (runs go
        down) and > 1.0 for below-average (runs go up).
        """
        return 1.0 - (self.arm_strength - ARM_STRENGTH_BASELINE) * ARM_RUNS_RATE

    def arm_ip_multiplier(self) -> float:
        """
        Stronger arm → maintains velocity deeper into the game → longer outings.

        Returns a multiplier > 1.0 for above-average arm strength and
        < 1.0 for below-average.
        """
        return 1.0 + (self.arm_strength - ARM_STRENGTH_BASELINE) * ARM_IP_RATE

    def validate(self) -> None:
        if self.era < 0:
            raise ValueError("ERA cannot be negative")
        if not (0 < self.k_per_9 <= 20):
            raise ValueError("K/9 must be between 0 and 20")
        if not (0 < self.innings_per_start <= 9):
            raise ValueError("Innings per start must be between 0 and 9")
        if self.whip < 0:
            raise ValueError("WHIP cannot be negative")
        if not (0 <= self.arm_strength <= 100):
            raise ValueError("arm_strength must be between 0 and 100")
        if self.throws not in ("R", "L"):
            raise ValueError("throws must be 'R' (right) or 'L' (left)")
        if not (PITCHER_PITCHES_PER_PA_MIN <= self.pitches_per_pa <= PITCHER_PITCHES_PER_PA_MAX):
            raise ValueError(
                f"pitches_per_pa must be between {PITCHER_PITCHES_PER_PA_MIN} "
                f"and {PITCHER_PITCHES_PER_PA_MAX}"
            )


@dataclass
class BatterStats:
    """Season / career statistics for a position player."""

    name: str
    avg: float                    # Batting average
    obp: float                    # On-base percentage
    slg: float                    # Slugging percentage
    hr_per_600_pa: float          # Home runs per 600 plate appearances
    sb_per_season: float          # Stolen bases per full season
    doubles_per_600_pa: float     # Doubles per 600 plate appearances
    games_played: int = 162       # Games played (used to normalise season totals)
    power_rating: float = 50.0    # 0–100 scale; 50 = league-average raw power
    bats: str = "R"               # Batting hand: "R" (right), "L" (left), "S" (switch)
    pitches_per_pa: float = BATTER_PITCHES_PER_PA_DEFAULT
    # Average pitches seen per plate appearance.  League average ~3.8; patient
    # hitters with high OBP often see 4.0+; aggressive free-swingers ~3.3.
    rbi_per_season: float = 0.0   # Runs batted in per full season
    runs_per_season: float = 0.0  # Runs scored per full season

    # ------------------------------------------------------------------
    # Power-rating multipliers
    # ------------------------------------------------------------------

    def power_hr_multiplier(self) -> float:
        """
        Higher raw power → harder contact → elevated HR rate.

        Returns a multiplier > 1.0 for above-average power and
        < 1.0 for below-average.
        """
        return 1.0 + (self.power_rating - POWER_BASELINE) * POWER_HR_RATE

    def power_doubles_multiplier(self) -> float:
        """
        Higher raw power → more balls driven into the gaps → more doubles.

        Returns a multiplier > 1.0 for above-average power and
        < 1.0 for below-average.
        """
        return 1.0 + (self.power_rating - POWER_BASELINE) * POWER_DOUBLES_RATE

    def validate(self) -> None:
        if not (0 <= self.avg <= 1):
            raise ValueError("Batting average must be between 0 and 1")
        if not (0 <= self.obp <= 1):
            raise ValueError("OBP must be between 0 and 1")
        if not (0 <= self.slg <= 4):
            raise ValueError("SLG must be between 0 and 4")
        if self.hr_per_600_pa < 0:
            raise ValueError("HR per 600 PA cannot be negative")
        if self.sb_per_season < 0:
            raise ValueError("SB per season cannot be negative")
        if self.doubles_per_600_pa < 0:
            raise ValueError("Doubles per 600 PA cannot be negative")
        if not (0 <= self.power_rating <= 100):
            raise ValueError("power_rating must be between 0 and 100")
        if self.bats not in ("R", "L", "S"):
            raise ValueError("bats must be 'R' (right), 'L' (left), or 'S' (switch)")
        if not (BATTER_PITCHES_PER_PA_MIN <= self.pitches_per_pa <= BATTER_PITCHES_PER_PA_MAX):
            raise ValueError(
                f"pitches_per_pa must be between {BATTER_PITCHES_PER_PA_MIN} "
                f"and {BATTER_PITCHES_PER_PA_MAX}"
            )
        if self.rbi_per_season < 0:
            raise ValueError("rbi_per_season cannot be negative")
        if self.runs_per_season < 0:
            raise ValueError("runs_per_season cannot be negative")


# ---------------------------------------------------------------------------
# Machine Learning — game-log record and prop calibrator
# ---------------------------------------------------------------------------


@dataclass
class GameLogRecord:
    """
    One historical player-game observation used to train a :class:`PropCalibrator`.

    Each record pairs the raw simulation-predicted mean (``sim_mean``) with the
    actual observed outcome (``actual``) for a single prop in a single game,
    alongside the feature values that describe the player and environment for
    that game.

    Parameters
    ----------
    prop : str
        Prop type being recorded, e.g. ``"Strikeouts"``, ``"Hits"``,
        ``"Home Runs"``, ``"Runs Allowed"``.  Must match the prop names used in
        :meth:`PropCalibrator.predict_adjustment`.
    actual : float
        The real observed outcome for this player in this game
        (e.g. 7 strikeouts, 2 hits).
    sim_mean : float
        The raw Monte Carlo simulation mean for this prop before any calibration.
        Records with ``sim_mean <= 0`` are ignored during training.
    features : Dict[str, float]
        Numeric feature vector describing the player and environment.
        Typical pitcher keys: ``"era"``, ``"k_per_9"``, ``"whip"``,
        ``"innings_per_start"``, ``"arm_strength"``, ``"pitches_per_pa"``,
        ``"temp_f"``, ``"humidity"``, ``"altitude_ft"``, ``"wind_speed_mph"``,
        ``"stadium_k_factor"``, ``"stadium_runs_factor"``.
        Typical batter keys: ``"avg"``, ``"obp"``, ``"slg"``,
        ``"hr_per_600_pa"``, ``"doubles_per_600_pa"``, ``"power_rating"``,
        ``"pitches_per_pa"``, ``"sb_per_season"``, ``"temp_f"``,
        ``"humidity"``, ``"altitude_ft"``, ``"wind_speed_mph"``,
        ``"stadium_hr_factor"``, ``"stadium_hits_factor"``.
        Any numeric key is accepted; unknown keys are treated as zero at
        prediction time.
    player_name : str
        Optional annotation for logging and diagnostics.
    """

    prop: str
    actual: float
    sim_mean: float
    features: Dict[str, float]
    player_name: str = ""


class PropCalibrator:
    """
    Pure-Python Ridge Regression calibrator for prop simulation outputs.

    Trains one L2-regularised linear model per prop type using stochastic
    gradient descent (SGD).  After fitting on historical :class:`GameLogRecord`
    data, :meth:`predict_adjustment` returns a calibration multiplier that
    adjusts the raw Monte Carlo simulation mean toward observed historical
    outcomes.

    The entire implementation uses only the Python standard library — no
    numpy, pandas, or scikit-learn is required.

    Algorithm
    ---------
    For each prop type with enough records:

    1. **Target construction** — compute the calibration ratio
       ``y = actual / sim_mean`` for each record.  A ratio < 1 means the
       simulation over-predicted; > 1 means it under-predicted.
    2. **Feature standardisation** — z-score each feature column so all
       features have roughly equal gradient magnitudes.
    3. **SGD with L2 penalty** — update weights and bias per sample::

           err    = ŷ − y
           w[j]  -= lr × (2 × err × x[j]  +  2 × λ × w[j])
           bias  -= lr × 2 × err

    4. **Early stopping** — training halts when the epoch-level MSE loss
       improves by less than ``ML_CONVERGENCE_TOL``.
    5. **Output clamping** — the predicted multiplier is clamped to
       ``[ML_MULTIPLIER_MIN, ML_MULTIPLIER_MAX]`` (default 0.70 – 1.30)
       to prevent extreme corrections.

    Parameters
    ----------
    learning_rate : float
        SGD step size.  Default: ``ML_LEARNING_RATE`` (0.01).
    l2_lambda : float
        L2 regularisation strength.  Default: ``ML_L2_LAMBDA`` (0.001).
    max_epochs : int
        Maximum SGD passes over the training data.  Default: ``ML_MAX_EPOCHS``.
    convergence_tol : float
        Early-stopping threshold on loss improvement.
        Default: ``ML_CONVERGENCE_TOL``.

    Examples
    --------
    ::

        from mlb_player_props import GameLogRecord, PropCalibrator

        records = [
            GameLogRecord("Strikeouts", actual=6, sim_mean=5.2,
                          features={"era": 3.1, "k_per_9": 10.5, "temp_f": 68}),
            # … many more records …
        ]
        cal = PropCalibrator().fit(records)
        adj = cal.predict_adjustment({"era": 3.1, "k_per_9": 10.5, "temp_f": 68},
                                      prop="Strikeouts")
        # adj is a float near 1.0; multiply raw sim mean by adj.
    """

    def __init__(
        self,
        learning_rate: float = ML_LEARNING_RATE,
        l2_lambda: float = ML_L2_LAMBDA,
        max_epochs: int = ML_MAX_EPOCHS,
        convergence_tol: float = ML_CONVERGENCE_TOL,
    ) -> None:
        self.learning_rate = learning_rate
        self.l2_lambda = l2_lambda
        self.max_epochs = max_epochs
        self.convergence_tol = convergence_tol

        # Per-prop model parameters (populated by fit)
        self._weights: Dict[str, List[float]] = {}
        self._bias: Dict[str, float] = {}
        self._feature_names: Dict[str, List[str]] = {}
        self._feature_means: Dict[str, List[float]] = {}
        self._feature_stds: Dict[str, List[float]] = {}
        self._train_rmse_: Dict[str, float] = {}
        self._epochs_run_: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fit(self, records: List[GameLogRecord]) -> "PropCalibrator":
        """
        Train one Ridge Regression model per prop type.

        Records whose ``sim_mean`` is ≤ 0 are silently skipped (the
        calibration ratio would be undefined).  Props with fewer than
        ``ML_MIN_RECORDS_PER_PROP`` usable records are also skipped.

        Parameters
        ----------
        records : list of GameLogRecord

        Returns
        -------
        PropCalibrator
            Returns ``self`` for method chaining.
        """
        by_prop: Dict[str, List[GameLogRecord]] = {}
        for rec in records:
            if rec.sim_mean > 0.0:
                by_prop.setdefault(rec.prop, []).append(rec)

        for prop, prop_records in by_prop.items():
            if len(prop_records) >= ML_MIN_RECORDS_PER_PROP:
                self._fit_prop(prop, prop_records)

        return self

    def predict_adjustment(
        self,
        features: Dict[str, float],
        prop: str,
    ) -> float:
        """
        Return a calibration multiplier for the simulation mean.

        If no model has been trained for ``prop``, returns ``1.0``
        (no adjustment).  The result is always clamped to
        ``[ML_MULTIPLIER_MIN, ML_MULTIPLIER_MAX]``.

        Parameters
        ----------
        features : Dict[str, float]
            Feature vector for the prediction context.  Unknown keys are
            treated as zero (the standardised mean value).
        prop : str
            Prop type, e.g. ``"Strikeouts"`` or ``"Hits"``.

        Returns
        -------
        float
            Calibration multiplier.  Multiply the raw simulation mean (or each
            element of the raw simulation values list) by this value to obtain
            the calibrated estimate.
        """
        if not self.is_fitted(prop):
            return 1.0

        feat_names = self._feature_names[prop]
        feat_means = self._feature_means[prop]
        feat_stds = self._feature_stds[prop]
        w = self._weights[prop]
        b = self._bias[prop]

        # Standardise input features the same way as during training.
        x_std = [
            (features.get(k, 0.0) - feat_means[j]) / feat_stds[j]
            for j, k in enumerate(feat_names)
        ]
        predicted = sum(w[j] * x_std[j] for j in range(len(w))) + b
        return max(ML_MULTIPLIER_MIN, min(ML_MULTIPLIER_MAX, predicted))

    def is_fitted(self, prop: str) -> bool:
        """Return ``True`` if a model has been trained for ``prop``."""
        return prop in self._weights

    def props_fitted(self) -> List[str]:
        """Sorted list of prop types for which a model has been trained."""
        return sorted(self._weights)

    def feature_importances(self, prop: str) -> List[Tuple[str, float]]:
        """
        Sorted list of ``(feature_name, weight)`` pairs for ``prop``.

        Pairs are ordered by absolute weight magnitude descending.  Weights
        are expressed in the standardised feature space (one unit = one
        standard deviation of that feature in the training data).

        Returns an empty list if no model has been trained for ``prop``.
        """
        if not self.is_fitted(prop):
            return []
        pairs = list(zip(self._feature_names[prop], self._weights[prop]))
        pairs.sort(key=lambda p: abs(p[1]), reverse=True)
        return pairs

    def training_rmse(self, prop: str) -> float:
        """
        Root-mean-squared error on the training set for ``prop``.

        Measured in units of the calibration ratio (actual / sim_mean).
        Returns ``0.0`` if no model has been trained.
        """
        return self._train_rmse_.get(prop, 0.0)

    def epochs_run(self, prop: str) -> int:
        """Number of SGD epochs actually completed for ``prop``."""
        return self._epochs_run_.get(prop, 0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fit_prop(self, prop: str, records: List[GameLogRecord]) -> None:
        """Fit a ridge regression model for one prop type via SGD."""
        # Collect all feature names (sorted for determinism).
        all_keys: List[str] = sorted({k for r in records for k in r.features})
        n = len(records)
        d = len(all_keys)

        # Build design matrix X (n × d) and target vector y (n,).
        # Target: calibration ratio = actual / sim_mean.
        X = [[r.features.get(k, 0.0) for k in all_keys] for r in records]
        y = [r.actual / r.sim_mean for r in records]

        # Compute per-feature mean and std for z-score standardisation.
        feat_means = [sum(X[i][j] for i in range(n)) / n for j in range(d)]
        feat_vars = [
            sum((X[i][j] - feat_means[j]) ** 2 for i in range(n)) / max(n - 1, 1)
            for j in range(d)
        ]
        feat_stds = [math.sqrt(max(v, 1e-8)) for v in feat_vars]

        # Standardise X.
        X_std = [
            [(X[i][j] - feat_means[j]) / feat_stds[j] for j in range(d)]
            for i in range(n)
        ]

        # Initialise weights to zero; initialise bias to the mean target.
        w = [0.0] * d
        b = sum(y) / n

        lr = self.learning_rate
        lam = self.l2_lambda
        prev_loss = float("inf")
        epochs_run = 0

        for _epoch in range(self.max_epochs):
            # Shuffle record order each epoch (SGD).
            indices = list(range(n))
            random.shuffle(indices)

            for i in indices:
                xi = X_std[i]
                yi = y[i]
                # Forward pass.
                y_hat = sum(w[j] * xi[j] for j in range(d)) + b
                err = y_hat - yi
                # Gradient descent update with L2 penalty on weights (not bias).
                for j in range(d):
                    w[j] -= lr * (2.0 * err * xi[j] + 2.0 * lam * w[j])
                b -= lr * (2.0 * err)

            # Compute epoch MSE + L2 loss for convergence check.
            loss = 0.0
            for i in range(n):
                xi = X_std[i]
                y_hat = sum(w[j] * xi[j] for j in range(d)) + b
                loss += (y_hat - y[i]) ** 2
            loss = loss / n + lam * sum(wj ** 2 for wj in w)
            epochs_run += 1

            if abs(prev_loss - loss) < self.convergence_tol:
                break
            prev_loss = loss

        # Compute final training RMSE.
        sse = sum(
            (sum(w[j] * X_std[i][j] for j in range(d)) + b - y[i]) ** 2
            for i in range(n)
        )
        rmse = math.sqrt(sse / n)

        # Store fitted model.
        self._weights[prop] = w
        self._bias[prop] = b
        self._feature_names[prop] = all_keys
        self._feature_means[prop] = feat_means
        self._feature_stds[prop] = feat_stds
        self._train_rmse_[prop] = rmse
        self._epochs_run_[prop] = epochs_run


# ---------------------------------------------------------------------------
# Simulation result containers
# ---------------------------------------------------------------------------


@dataclass
class PropResult:
    """Summary statistics for a simulated prop line."""

    player_name: str
    prop_name: str
    mean: float
    median: float
    std_dev: float
    percentile_10: float
    percentile_25: float
    percentile_75: float
    percentile_90: float
    over_probabilities: Dict[float, float] = field(default_factory=dict)

    def __str__(self) -> str:  # pragma: no cover
        lines = [
            f"  {self.prop_name}",
            f"    Mean:    {self.mean:.2f}",
            f"    Median:  {self.median:.2f}",
            f"    Std Dev: {self.std_dev:.2f}",
            f"    P10/P25/P75/P90: {self.percentile_10:.1f} / "
            f"{self.percentile_25:.1f} / {self.percentile_75:.1f} / {self.percentile_90:.1f}",
        ]
        if self.over_probabilities:
            lines.append("    Over Probabilities:")
            for line_val, prob in sorted(self.over_probabilities.items()):
                lines.append(f"      O{line_val:.1f}: {prob*100:.1f}%")
        return "\n".join(lines)


@dataclass
class PlayerPropsReport:
    """All prop results for a single player."""

    player_name: str
    props: List[PropResult] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        lines = [f"\n{'='*50}", f"  {self.player_name}", f"{'='*50}"]
        lines += [str(p) for p in self.props]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core simulator
# ---------------------------------------------------------------------------


class MLBPlayerPropsSimulator:
    """
    Monte Carlo simulator for MLB player props.

    Parameters
    ----------
    stadium        : Stadium  – venue-specific park factors
    weather        : WeatherConditions
    wind           : WindConditions
    num_simulations: int      – number of Monte Carlo trials (default 10 000)
    random_seed    : int|None – optional seed for reproducibility
    air_density    : AirDensity | None – altitude and barometric-pressure effects
                     on ball carry.  Pass ``None`` (default) to use sea-level
                     neutral conditions (no air density adjustment).
    calibrator     : PropCalibrator | None – a fitted ML calibrator that adjusts
                     the raw Monte Carlo simulation output toward observed
                     historical outcomes.  Pass ``None`` (default) to skip ML
                     calibration (pure physics-based simulation).  When provided
                     the calibrator's multiplier is applied to every simulated
                     value before summary statistics are computed, preserving the
                     full distribution shape while shifting location.
    """

    def __init__(
        self,
        stadium: Stadium,
        weather: WeatherConditions,
        wind: WindConditions,
        num_simulations: int = 10_000,
        random_seed: Optional[int] = None,
        air_density: Optional[AirDensity] = None,
        calibrator: Optional[PropCalibrator] = None,
    ) -> None:
        self.stadium = stadium
        self.weather = weather
        self.wind = wind
        self.air_density = air_density if air_density is not None else AirDensity()
        self.calibrator = calibrator
        self.num_simulations = num_simulations
        if random_seed is not None:
            random.seed(random_seed)

    # ------------------------------------------------------------------
    # Composite environmental multipliers
    # ------------------------------------------------------------------

    def _effective_wind_mult(self, raw_wind_mult: float) -> float:
        """
        Apply game-time scaling to a raw wind multiplier.

        Wind deviations from neutral (1.0) are scaled by the game-time
        wind amplifier from ``self.weather``:

        * **night** – amplifier = 1.0 → raw multiplier returned unchanged.
        * **day**   – amplifier = 1.15 → 15 % larger wind deviation (gustier
          afternoon convection amplifies outfield wind effects).
        * **dome**  – amplifier = 0.0 → wind deviation cancelled (returns 1.0;
          there is no outdoor wind inside an enclosed stadium).
        """
        amp = self.weather.game_time_wind_amplifier()
        return 1.0 + (raw_wind_mult - 1.0) * amp

    def _env_hr_multiplier(self) -> float:
        return (
            self.stadium.hr_factor
            * self.weather.temp_hr_multiplier()
            * self.weather.precip_factor()
            * self.weather.humidity_hit_multiplier()
            * self._effective_wind_mult(self.wind.hr_multiplier())
            * self.air_density.hr_multiplier()
        )

    def _env_hits_multiplier(self) -> float:
        return (
            self.stadium.hits_factor
            * self.weather.temp_hit_multiplier()
            * self.weather.precip_factor()
            * self.weather.humidity_hit_multiplier()
            * self._effective_wind_mult(self.wind.hit_multiplier())
            * self.air_density.hits_multiplier()
        )

    def _env_doubles_multiplier(self) -> float:
        return (
            self.stadium.doubles_factor
            * self.weather.temp_hit_multiplier()
            * self.weather.precip_factor()
            * self.weather.humidity_hit_multiplier()
            * self._effective_wind_mult(self.wind.hit_multiplier())
            * self.air_density.hits_multiplier()
        )

    def _env_k_multiplier(self) -> float:
        return (
            self.stadium.k_factor
            * self.weather.temp_k_multiplier()
            * self.weather.precip_factor()
            * self._effective_wind_mult(self.wind.k_multiplier())
            * self.air_density.k_multiplier()
        )

    def _env_runs_multiplier(self) -> float:
        return (
            self.stadium.runs_factor
            * self.weather.temp_hr_multiplier()
            * self.weather.precip_factor()
            * self._effective_wind_mult(self.wind.runs_multiplier())
            * self.air_density.runs_multiplier()
        )

    # ------------------------------------------------------------------
    # ML calibration: feature extraction helpers
    # ------------------------------------------------------------------

    def _pitcher_features(self, stats: "PitcherStats") -> Dict[str, float]:
        """
        Build the numeric feature dictionary for a pitcher simulation context.

        This dictionary can be passed directly to
        :meth:`PropCalibrator.predict_adjustment` or used to construct a
        :class:`GameLogRecord` for calibrator training.

        All four stadium factors are included: HR-friendly parks correlate with
        more home runs and hits *allowed* by pitchers, while high-K parks
        correlate with more strikeouts.  The ML model will learn which factors
        are predictive for each pitcher prop; unused factors shrink toward zero
        under the L2 penalty.
        """
        return {
            "era": stats.era,
            "k_per_9": stats.k_per_9,
            "whip": stats.whip,
            "innings_per_start": stats.innings_per_start,
            "arm_strength": float(stats.arm_strength),
            "pitches_per_pa": stats.pitches_per_pa,
            "temp_f": self.weather.temp_f,
            "humidity": self.weather.humidity,
            "altitude_ft": self.air_density.altitude_ft,
            "barometric_pressure_inhg": self.air_density.barometric_pressure_inhg,
            "wind_speed_mph": float(self.wind.speed_mph),
            # All stadium factors included: HR/hits factors affect pitcher
            # performance in hitter-friendly parks; K/runs factors encode
            # overall park character which the model can weight as needed.
            "stadium_hr_factor": self.stadium.hr_factor,
            "stadium_hits_factor": self.stadium.hits_factor,
            "stadium_k_factor": self.stadium.k_factor,
            "stadium_runs_factor": self.stadium.runs_factor,
        }

    def _batter_features(self, stats: "BatterStats") -> Dict[str, float]:
        """
        Build the numeric feature dictionary for a batter simulation context.

        This dictionary can be passed directly to
        :meth:`PropCalibrator.predict_adjustment` or used to construct a
        :class:`GameLogRecord` for calibrator training.

        All four stadium factors are included: HR and hits factors directly
        affect batter output; K and runs factors encode overall park character
        (high-K parks suppress contact rates).  The L2 regulariser will
        suppress irrelevant factors that are not predictive in the training
        data.
        """
        return {
            "avg": stats.avg,
            "obp": stats.obp,
            "slg": stats.slg,
            "hr_per_600_pa": float(stats.hr_per_600_pa),
            "doubles_per_600_pa": float(stats.doubles_per_600_pa),
            "power_rating": float(stats.power_rating),
            "pitches_per_pa": stats.pitches_per_pa,
            "sb_per_season": float(stats.sb_per_season),
            "temp_f": self.weather.temp_f,
            "humidity": self.weather.humidity,
            "altitude_ft": self.air_density.altitude_ft,
            "barometric_pressure_inhg": self.air_density.barometric_pressure_inhg,
            "wind_speed_mph": float(self.wind.speed_mph),
            # All stadium factors included: HR/hits factors directly drive
            # batter production; K/runs factors encode park context that
            # may suppress contact or scoring rates.
            "stadium_hr_factor": self.stadium.hr_factor,
            "stadium_hits_factor": self.stadium.hits_factor,
            "stadium_k_factor": self.stadium.k_factor,
            "stadium_runs_factor": self.stadium.runs_factor,
        }

    @staticmethod
    def _apply_calibration(
        values: List[float],
        multiplier: float,
    ) -> List[float]:
        """
        Scale every value in ``values`` by ``multiplier``.

        Returns a new list; the original is not mutated.  If ``multiplier``
        equals 1.0 the original list is returned unchanged (no allocation).
        """
        if multiplier == 1.0:
            return values
        return [v * multiplier for v in values]

    # ------------------------------------------------------------------
    # Helper: build a result from a list of simulation values
    # ------------------------------------------------------------------

    @staticmethod
    def _summarise(
        values: List[float],
        player_name: str,
        prop_name: str,
        over_lines: Optional[List[float]] = None,
    ) -> PropResult:
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mean = statistics.mean(sorted_vals)
        median = statistics.median(sorted_vals)
        std_dev = statistics.stdev(sorted_vals) if n > 1 else 0.0
        p10 = sorted_vals[int(n * 0.10)]
        p25 = sorted_vals[int(n * 0.25)]
        p75 = sorted_vals[int(n * 0.75)]
        p90 = sorted_vals[min(int(n * 0.90), n - 1)]

        over_probs: Dict[float, float] = {}
        if over_lines:
            for line in over_lines:
                over_probs[line] = sum(1 for v in values if v > line) / n

        return PropResult(
            player_name=player_name,
            prop_name=prop_name,
            mean=mean,
            median=median,
            std_dev=std_dev,
            percentile_10=p10,
            percentile_25=p25,
            percentile_75=p75,
            percentile_90=p90,
            over_probabilities=over_probs,
        )

    # ------------------------------------------------------------------
    # Simulate a single game for a pitcher
    # ------------------------------------------------------------------

    def _simulate_pitcher_game(
        self,
        stats: PitcherStats,
        k_mult: float,
        runs_mult: float,
        stamina_mult: float,
    ) -> Tuple[float, float, float, float]:
        """
        Returns (strikeouts, outs_recorded, runs_allowed, pitch_count) for one
        simulated game.  Uses a Poisson-like approach via random Gaussian
        perturbation of expected values.
        """
        # --- Expected values from season stats --------------------------
        # stamina_mult is pre-computed once per simulation run (see simulate_pitcher)
        # to avoid re-evaluating the temperature check thousands of times.
        expected_ip = (
            stats.innings_per_start
            * stamina_mult
            * (IP_FLOOR_SHIFT + random.gauss(0, IP_VARIANCE))
        )
        expected_ip = max(1.0, min(9.0, expected_ip))

        # Strikeouts: K/9 × IP / 9 × environmental multiplier
        expected_k = stats.k_per_9 * expected_ip / 9.0 * k_mult
        strikeouts = max(0.0, random.gauss(expected_k, math.sqrt(expected_k) * K_VARIANCE_FACTOR))

        # Outs recorded: innings × 3
        outs_raw = expected_ip * 3
        outs_recorded = max(MIN_OUTS_RECORDED, random.gauss(outs_raw, math.sqrt(outs_raw) * OUTS_VARIANCE_FACTOR))
        outs_recorded = min(outs_recorded, OUTS_PER_GAME)

        # Runs allowed: ERA / 9 × IP × environmental multiplier
        expected_runs = (stats.era / 9.0) * expected_ip * runs_mult
        # WHIP adds base-runner pressure
        whip_adj = 1.0 + (stats.whip - WHIP_BASELINE) * WHIP_RUNS_ADJUSTMENT
        expected_runs *= max(0.5, whip_adj)
        runs_allowed = max(0.0, random.gauss(expected_runs, math.sqrt(max(expected_runs, 0.5)) * 0.9))

        # --- Pitch count ------------------------------------------------
        # Batters faced ≈ outs_recorded + base-runners (WHIP × IP).
        # Each batter faced adds `pitches_per_pa` pitches on average.
        batters_faced = outs_recorded + stats.whip * expected_ip
        expected_pitches = batters_faced * stats.pitches_per_pa
        pitch_count = max(0.0, random.gauss(
            expected_pitches,
            expected_pitches * PITCH_COUNT_VARIANCE,
        ))

        return strikeouts, outs_recorded, runs_allowed, pitch_count

    # ------------------------------------------------------------------
    # Simulate a single game for a batter
    # ------------------------------------------------------------------

    def _simulate_batter_game(
        self,
        stats: BatterStats,
        hits_mult: float,
        doubles_mult: float,
        hr_mult: float,
    ) -> Tuple[float, float, float, float, float, float, float]:
        """
        Returns (hits, doubles, home_runs, stolen_bases, plate_appearances,
        runs_scored, rbi) for one simulated game.
        """
        pa = PA_PER_GAME * (PA_FLOOR_SHIFT + random.gauss(0, PA_VARIANCE))
        pa = max(1.0, pa)
        ab = pa * PA_TO_AB_RATIO

        # --- Hits -------------------------------------------------------
        expected_hits = ab * stats.avg * hits_mult
        hits = max(0.0, random.gauss(expected_hits, math.sqrt(max(expected_hits, 0.3)) * 0.75))

        # --- Doubles ----------------------------------------------------
        # Doubles per PA (scaled from season rate per 600 PA)
        doubles_rate_per_pa = (stats.doubles_per_600_pa / 600.0) * doubles_mult
        expected_doubles = pa * doubles_rate_per_pa
        doubles = max(0.0, random.gauss(expected_doubles, math.sqrt(max(expected_doubles, 0.1)) * 0.8))
        doubles = min(doubles, hits)  # can't have more doubles than hits

        # --- Home Runs --------------------------------------------------
        hr_rate_per_pa = (stats.hr_per_600_pa / 600.0) * hr_mult
        expected_hr = pa * hr_rate_per_pa
        home_runs = max(0.0, random.gauss(expected_hr, math.sqrt(max(expected_hr, 0.05)) * 0.8))
        home_runs = min(home_runs, hits)  # HRs are a subset of hits

        # --- Stolen Bases -----------------------------------------------
        # Pro-rate the player's season stolen bases to a per-game rate, then
        # model each game as a simple Bernoulli / Poisson draw.
        expected_sb_per_game = stats.sb_per_season / max(stats.games_played, 1)
        # Add game-to-game variance (SB_VARIANCE relative noise)
        lambda_sb = max(0.0, expected_sb_per_game * (SB_FLOOR_SHIFT + random.gauss(0, SB_VARIANCE)))
        # Simulate up to MAX_STEAL_OPPORTUNITIES_PER_GAME steal opportunities
        stolen_bases = 0.0
        for _ in range(MAX_STEAL_OPPORTUNITIES_PER_GAME):
            if random.random() < lambda_sb and random.random() < STEAL_SUCCESS_RATE:
                stolen_bases += 1.0

        # --- Plate Appearances ------------------------------------------
        # pa is already simulated above; apply batter-specific pitches_per_pa
        # noise to capture days where he sees many or few pitches.
        plate_appearances = max(
            1.0,
            random.gauss(pa, pa * BATTER_PITCHES_VARIANCE * 0.5),
        )

        # --- Runs Scored ------------------------------------------------
        # Pro-rate from the player's season runs-per-game rate.  Apply the
        # hits multiplier as a proxy for lineup-context and environment.
        expected_runs_per_game = (
            stats.runs_per_season / max(stats.games_played, 1)
        ) * hits_mult
        runs_scored = max(
            0.0,
            expected_runs_per_game * (RUNS_FLOOR_SHIFT + random.gauss(0, RUNS_VARIANCE)),
        )

        # --- RBI --------------------------------------------------------
        # Pro-rate from season RBI with power/environment via hr_mult proxy.
        expected_rbi_per_game = (
            stats.rbi_per_season / max(stats.games_played, 1)
        ) * hr_mult
        rbi = max(
            0.0,
            expected_rbi_per_game * (RBI_FLOOR_SHIFT + random.gauss(0, RBI_VARIANCE)),
        )

        return hits, doubles, home_runs, stolen_bases, plate_appearances, runs_scored, rbi

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def simulate_pitcher(
        self,
        stats: PitcherStats,
        k_lines: Optional[List[float]] = None,
        outs_lines: Optional[List[float]] = None,
        runs_lines: Optional[List[float]] = None,
        pitch_count_lines: Optional[List[float]] = None,
        opponent_bats: Optional[str] = None,
        is_home: Optional[bool] = None,
    ) -> PlayerPropsReport:
        """
        Run Monte Carlo simulations for a starting pitcher.

        Parameters
        ----------
        stats             : PitcherStats
        k_lines           : list of strikeout over/under lines to evaluate
        outs_lines        : list of outs-recorded lines to evaluate
        runs_lines        : list of runs-allowed lines to evaluate
        pitch_count_lines : list of total pitch-count over/under lines.
                            Defaults to [74.5, 84.5, 94.5, 104.5].
        opponent_bats     : batting hand of the opposing lineup ("R", "L", or "S").
                            When provided the platoon split adjusts K rate and runs
                            allowed.  None means no platoon adjustment is applied.
        is_home           : True if the pitcher is starting at his home ballpark,
                            False for a road start, None (default) for no
                            home/away adjustment.
        """
        stats.validate()
        # Compute platoon multipliers once if opponent handedness is known.
        if opponent_bats is not None:
            splits = platoon_splits_for(opponent_bats, stats.throws)
            platoon_k_mult = splits["k"]
            platoon_runs_mult = splits["runs"]
        else:
            platoon_k_mult = 1.0
            platoon_runs_mult = 1.0

        # Home / away multipliers.
        ha_splits = home_away_pitcher_splits_for(is_home)
        ha_k_mult = ha_splits["k"]
        ha_runs_mult = ha_splits["runs"]
        ha_ip_mult = ha_splits["ip"]

        k_mult = self._env_k_multiplier() * stats.arm_k_multiplier() * platoon_k_mult * ha_k_mult
        runs_mult = self._env_runs_multiplier() * stats.arm_runs_multiplier() * platoon_runs_mult * ha_runs_mult
        # Pre-compute stamina once — temperature and arm strength are fixed for
        # the whole run.  Arm strength extends/shortens outings independently of
        # the weather-based stamina penalty so they multiply together.
        # Home/away IP factor is also folded in here.
        stamina_mult = (
            self.weather.temp_pitcher_stamina_multiplier()
            * stats.arm_ip_multiplier()
            * ha_ip_mult
        )

        k_results: List[float] = []
        outs_results: List[float] = []
        runs_results: List[float] = []
        pitch_count_results: List[float] = []

        for _ in range(self.num_simulations):
            k, outs, runs, pitches = self._simulate_pitcher_game(stats, k_mult, runs_mult, stamina_mult)
            k_results.append(k)
            outs_results.append(outs)
            runs_results.append(runs)
            pitch_count_results.append(pitches)

        # Apply ML calibration if a fitted calibrator is available.
        if self.calibrator is not None:
            features = self._pitcher_features(stats)
            k_results = self._apply_calibration(
                k_results, self.calibrator.predict_adjustment(features, "Strikeouts")
            )
            outs_results = self._apply_calibration(
                outs_results, self.calibrator.predict_adjustment(features, "Outs Recorded")
            )
            runs_results = self._apply_calibration(
                runs_results, self.calibrator.predict_adjustment(features, "Runs Allowed")
            )
            pitch_count_results = self._apply_calibration(
                pitch_count_results, self.calibrator.predict_adjustment(features, "Pitch Count")
            )

        report = PlayerPropsReport(player_name=stats.name)
        report.props.append(
            self._summarise(k_results, stats.name, "Strikeouts", k_lines or [3.5, 4.5, 5.5, 6.5, 7.5])
        )
        report.props.append(
            self._summarise(outs_results, stats.name, "Outs Recorded", outs_lines or [14.5, 16.5, 18.5])
        )
        report.props.append(
            self._summarise(runs_results, stats.name, "Runs Allowed", runs_lines or [1.5, 2.5, 3.5, 4.5])
        )
        report.props.append(
            self._summarise(
                pitch_count_results,
                stats.name,
                "Pitch Count",
                pitch_count_lines or [74.5, 84.5, 94.5, 104.5],
            )
        )
        return report

    def simulate_batter(
        self,
        stats: BatterStats,
        hits_lines: Optional[List[float]] = None,
        doubles_lines: Optional[List[float]] = None,
        hr_lines: Optional[List[float]] = None,
        sb_lines: Optional[List[float]] = None,
        pa_lines: Optional[List[float]] = None,
        hrb_lines: Optional[List[float]] = None,
        opponent_throws: Optional[str] = None,
        is_home: Optional[bool] = None,
    ) -> PlayerPropsReport:
        """
        Run Monte Carlo simulations for a position player (batter).

        Parameters
        ----------
        stats           : BatterStats
        hits_lines      : list of hit over/under lines to evaluate
        doubles_lines   : list of double over/under lines to evaluate
        hr_lines        : list of home-run over/under lines to evaluate
        sb_lines        : list of stolen-base over/under lines to evaluate
        pa_lines        : list of plate-appearance over/under lines.
                          Defaults to [2.5, 3.5, 4.5, 5.5].
        hrb_lines       : list of H+R+RBI (Hits + Runs + RBI) over/under lines.
                          Defaults to [0.5, 1.5, 2.5, 3.5, 4.5].
                          Requires ``stats.rbi_per_season`` and
                          ``stats.runs_per_season`` to be non-zero for a
                          meaningful simulation.
        opponent_throws : throwing hand of the opposing pitcher ("R" or "L").
                          When provided the platoon split adjusts hits, HR, and
                          doubles rates.  None means no platoon adjustment.
        is_home         : True if the batter is playing at his home ballpark,
                          False for a road game, None (default) for no
                          home/away adjustment.
        """
        stats.validate()
        # Compute platoon multipliers once if opponent handedness is known.
        if opponent_throws is not None:
            splits = platoon_splits_for(stats.bats, opponent_throws)
            platoon_hits_mult = splits["hits"]
            platoon_hr_mult = splits["hr"]
            platoon_doubles_mult = splits["doubles"]
        else:
            platoon_hits_mult = 1.0
            platoon_hr_mult = 1.0
            platoon_doubles_mult = 1.0

        # Home / away multipliers.
        ha_splits = home_away_batter_splits_for(is_home)
        ha_hits_mult = ha_splits["hits"]
        ha_hr_mult = ha_splits["hr"]
        ha_doubles_mult = ha_splits["doubles"]

        hits_mult = self._env_hits_multiplier() * platoon_hits_mult * ha_hits_mult
        doubles_mult = (
            self._env_doubles_multiplier()
            * stats.power_doubles_multiplier()
            * platoon_doubles_mult
            * ha_doubles_mult
        )
        hr_mult = self._env_hr_multiplier() * stats.power_hr_multiplier() * platoon_hr_mult * ha_hr_mult

        hits_results: List[float] = []
        doubles_results: List[float] = []
        hr_results: List[float] = []
        sb_results: List[float] = []
        pa_results: List[float] = []
        hrb_results: List[float] = []

        for _ in range(self.num_simulations):
            h, d, hr, sb, pa, runs, rbi = self._simulate_batter_game(
                stats, hits_mult, doubles_mult, hr_mult
            )
            hits_results.append(h)
            doubles_results.append(d)
            hr_results.append(hr)
            sb_results.append(sb)
            pa_results.append(pa)
            hrb_results.append(h + runs + rbi)

        # Apply ML calibration if a fitted calibrator is available.
        if self.calibrator is not None:
            features = self._batter_features(stats)
            hits_results = self._apply_calibration(
                hits_results, self.calibrator.predict_adjustment(features, "Hits")
            )
            doubles_results = self._apply_calibration(
                doubles_results, self.calibrator.predict_adjustment(features, "Doubles")
            )
            hr_results = self._apply_calibration(
                hr_results, self.calibrator.predict_adjustment(features, "Home Runs")
            )
            sb_results = self._apply_calibration(
                sb_results, self.calibrator.predict_adjustment(features, "Stolen Bases")
            )
            pa_results = self._apply_calibration(
                pa_results, self.calibrator.predict_adjustment(features, "Plate Appearances")
            )
            hrb_results = self._apply_calibration(
                hrb_results, self.calibrator.predict_adjustment(features, "H+R+RBI")
            )

        report = PlayerPropsReport(player_name=stats.name)
        report.props.append(
            self._summarise(hits_results, stats.name, "Hits", hits_lines or [0.5, 1.5, 2.5])
        )
        report.props.append(
            self._summarise(doubles_results, stats.name, "Doubles", doubles_lines or [0.5, 1.5])
        )
        report.props.append(
            self._summarise(hr_results, stats.name, "Home Runs", hr_lines or [0.5, 1.5])
        )
        report.props.append(
            self._summarise(sb_results, stats.name, "Stolen Bases", sb_lines or [0.5, 1.5])
        )
        report.props.append(
            self._summarise(
                pa_results,
                stats.name,
                "Plate Appearances",
                pa_lines or [2.5, 3.5, 4.5, 5.5],
            )
        )
        report.props.append(
            self._summarise(
                hrb_results,
                stats.name,
                "H+R+RBI",
                hrb_lines or [0.5, 1.5, 2.5, 3.5, 4.5],
            )
        )
        return report

    def print_results(self, report: PlayerPropsReport) -> None:  # pragma: no cover
        """Pretty-print a PlayerPropsReport to stdout."""
        print(report)

    def simulate_matchup(
        self,
        pitcher: PitcherStats,
        batters: List[BatterStats],
        pitcher_is_home: Optional[bool] = None,
    ) -> Dict[str, PlayerPropsReport]:
        """
        Convenience method: simulate an entire pitcher vs lineup matchup.

        Platoon splits are applied automatically: each batter simulation uses
        the pitcher's throwing hand (``pitcher.throws``) and the pitcher
        simulation uses the first batter's batting hand as a representative
        opponent for K/runs adjustments (or "R" when no batters are provided).

        Parameters
        ----------
        pitcher        : PitcherStats for the starting pitcher.
        batters        : list of BatterStats for the opposing lineup.
        pitcher_is_home: True if the pitcher's team is the home team, False if
                         they are the visiting team, None for no home/away
                         adjustment.  When provided, batters receive the inverse
                         designation (if pitcher is home, batters are away and
                         vice versa).

        Returns a dict keyed by player name.
        """
        results: Dict[str, PlayerPropsReport] = {}
        # Determine representative opponent batting hand for the pitcher.
        rep_bats = batters[0].bats if batters else "R"
        # Batters get the opposite home/away designation from the pitcher.
        batter_is_home: Optional[bool] = (
            None if pitcher_is_home is None else not pitcher_is_home
        )
        results[pitcher.name] = self.simulate_pitcher(
            pitcher, opponent_bats=rep_bats, is_home=pitcher_is_home
        )
        for batter in batters:
            results[batter.name] = self.simulate_batter(
                batter, opponent_throws=pitcher.throws, is_home=batter_is_home
            )
        return results


# ---------------------------------------------------------------------------
# CLI entry-point (demo)
# ---------------------------------------------------------------------------


def _demo() -> None:  # pragma: no cover
    """Quick demonstration of the simulator."""
    print("MLB Player Props Simulator — Demo")
    print("=" * 50)

    # Venue
    stadium = Stadium.from_name("Wrigley Field")
    print(f"Venue   : {stadium.name}")
    print(f"  HR factor   : {stadium.hr_factor}")
    print(f"  Hits factor : {stadium.hits_factor}")
    print(f"  Doubles fac : {stadium.doubles_factor}")
    print(f"  K factor    : {stadium.k_factor}")
    print(f"  Runs factor : {stadium.runs_factor}")

    # ----------------------------------------------------------------
    # Game-time effect comparison
    # ----------------------------------------------------------------
    wind = WindConditions(speed_mph=12, direction="out_to_center")
    print(f"\nWind    : {wind.speed_mph} mph {wind.direction}")
    print(f"  HR multiplier   : {wind.hr_multiplier():.3f}")
    print(f"  Hit multiplier  : {wind.hit_multiplier():.3f}")
    print(f"  K multiplier    : {wind.k_multiplier():.3f}  (pitcher strikeout rate)")
    print(f"  Runs multiplier : {wind.runs_multiplier():.3f}  (runs allowed)")

    # Weather base (warm afternoon — good for showing game-time contrast)
    base_temp, base_precip, base_hum = 85.0, "none", 0.60
    print(f"\nGame-time comparison — {base_temp}°F, precip={base_precip}, humidity={base_hum}")
    print(f"  {'Metric':<35}  {'Night':>8}  {'Day':>8}  {'Dome':>8}")
    print(f"  {'-'*35}  {'-'*8}  {'-'*8}  {'-'*8}")
    for gt in ("night", "day", "dome"):
        w = WeatherConditions(temp_f=base_temp, precipitation=base_precip,
                              humidity=base_hum, game_time=gt)

    for label, fn in [
        ("Temp HR mult",          lambda w: w.temp_hr_multiplier()),
        ("Temp hit mult",         lambda w: w.temp_hit_multiplier()),
        ("Temp K mult",           lambda w: w.temp_k_multiplier()),
        ("Temp stamina mult",     lambda w: w.temp_pitcher_stamina_multiplier()),
        ("Precip factor",         lambda w: w.precip_factor()),
        ("Humidity hit mult",     lambda w: w.humidity_hit_multiplier()),
        ("Wind amplifier",        lambda w: w.game_time_wind_amplifier()),
    ]:
        vals = [
            WeatherConditions(temp_f=base_temp, precipitation=base_precip,
                              humidity=base_hum, game_time=gt)
            for gt in ("night", "day", "dome")
        ]
        print(f"  {label:<35}  {fn(vals[0]):>8.3f}  {fn(vals[1]):>8.3f}  {fn(vals[2]):>8.3f}")

    # ----------------------------------------------------------------
    # Air density comparison
    # ----------------------------------------------------------------
    altitudes = [
        ("Sea level (0 ft)",     0),
        ("Atlanta (~1 050 ft)",  1_050),
        ("Denver (~5 280 ft)",   5_280),
        ("Mexico City (~7 400 ft)", 7_400),
    ]
    print("\nAir density comparison (standard pressure 29.92 inHg, 72°F):")
    print(f"  {'Venue':<28}  {'Density':>9}  {'HR mult':>9}  {'Hits mult':>9}  "
          f"{'K mult':>9}  {'Runs mult':>9}")
    print(f"  {'-'*28}  {'-'*9}  {'-'*9}  {'-'*9}  {'-'*9}  {'-'*9}")
    for label, alt in altitudes:
        ad = AirDensity(altitude_ft=alt)
        print(f"  {label:<28}  {ad.density_ratio():>9.4f}  {ad.hr_multiplier():>9.3f}  "
              f"{ad.hits_multiplier():>9.3f}  {ad.k_multiplier():>9.3f}  "
              f"{ad.runs_multiplier():>9.3f}")

    # Also show the effect of low barometric pressure (storm system)
    print("\nBarometric pressure effect (sea level, 72°F):")
    for pressure in (31.00, 29.92, 29.20, 28.50):
        ad = AirDensity(altitude_ft=0, barometric_pressure_inhg=pressure)
        tag = " (high-pressure ridge)" if pressure > 29.92 else (
              " (standard)" if pressure == 29.92 else (
              " (low-pressure system)" if pressure >= 29.00 else " (strong storm)"))
        print(f"  {pressure:.2f} inHg{tag:<25}  density={ad.density_ratio():.4f}  "
              f"HR mult={ad.hr_multiplier():.3f}")

    # Weather for actual sim — night game (default)
    weather = WeatherConditions(temp_f=68, precipitation="light", humidity=0.65,
                                game_time="night")
    print(f"\nWeather (night game): {weather.temp_f}°F, precip={weather.precipitation}, "
          f"humidity={weather.humidity}, game_time={weather.game_time!r}")
    print(f"  Temp HR multiplier      : {weather.temp_hr_multiplier():.3f}")
    print(f"  Temp hit multiplier     : {weather.temp_hit_multiplier():.3f}  (batter contact rate)")
    print(f"  Temp K multiplier       : {weather.temp_k_multiplier():.3f}  (pitcher strikeout rate)")
    print(f"  Temp stamina multiplier : {weather.temp_pitcher_stamina_multiplier():.3f}  (pitcher innings)")
    print(f"  Wind amplifier          : {weather.game_time_wind_amplifier():.3f}  (x wind deviation)")

    # Simulator (small run for demo speed)
    sim = MLBPlayerPropsSimulator(
        stadium=stadium,
        weather=weather,
        wind=wind,
        air_density=AirDensity(altitude_ft=0),   # sea-level baseline
        num_simulations=5_000,
        random_seed=42,
    )

    # Pitcher — left-handed ace (arm_strength=80, throws="L", works deep counts)
    pitcher = PitcherStats(
        name="Demo Ace",
        era=3.20,
        k_per_9=10.5,
        innings_per_start=6.0,
        whip=1.08,
        arm_strength=80,
        throws="L",
        pitches_per_pa=4.1,    # works deep counts
    )
    print(f"\nPitcher : {pitcher.name}  (arm_strength={pitcher.arm_strength}, "
          f"throws={pitcher.throws}, pitches_per_pa={pitcher.pitches_per_pa})")
    print(f"  Arm K multiplier   : {pitcher.arm_k_multiplier():.3f}  (strikeout rate)")
    print(f"  Arm runs multiplier: {pitcher.arm_runs_multiplier():.3f}  (runs allowed)")
    print(f"  Arm IP multiplier  : {pitcher.arm_ip_multiplier():.3f}  (innings pitched)")

    # Show platoon K-rate shift vs opposing lineups
    for opp_bats in ("R", "L", "S"):
        sp = platoon_splits_for(opp_bats, pitcher.throws)
        print(f"  vs {opp_bats}-handed lineup : K mult {sp['k']:.2f}, runs mult {sp['runs']:.2f}")

    # Show home/away splits for the pitcher
    print("\n  Home/Away splits (pitcher):")
    for location, is_h in (("Home", True), ("Away", False)):
        ha = home_away_pitcher_splits_for(is_h)
        print(f"    {location}: K×{ha['k']:.2f}  runs×{ha['runs']:.2f}  IP×{ha['ip']:.2f}")

    # Pitcher props at home vs right-handed lineup
    pitcher_report_home = sim.simulate_pitcher(pitcher, opponent_bats="R", is_home=True)
    print("\n--- Pitcher: HOME game ---")
    sim.print_results(pitcher_report_home)

    # Pitcher props on the road vs right-handed lineup
    pitcher_report_away = sim.simulate_pitcher(pitcher, opponent_bats="R", is_home=False)
    print("\n--- Pitcher: AWAY game ---")
    sim.print_results(pitcher_report_away)

    # Batter — right-handed power hitter (power_rating=85, bats="R", patient hitter)
    # facing the left-handed pitcher → batter has platoon advantage
    batter = BatterStats(
        name="Demo Slugger",
        avg=0.255,
        obp=0.340,
        slg=0.560,
        hr_per_600_pa=40,
        sb_per_season=5,
        doubles_per_600_pa=30,
        games_played=162,
        power_rating=85,
        bats="R",
        pitches_per_pa=4.2,    # patient hitter, works long counts
        rbi_per_season=95,     # high-RBI slot (4-5 hitter)
        runs_per_season=85,    # runs well for a power hitter
    )
    print(f"\nBatter  : {batter.name}  (power_rating={batter.power_rating}, "
          f"bats={batter.bats}, pitches_per_pa={batter.pitches_per_pa})")
    print(f"  RBI per season  : {batter.rbi_per_season}  ({batter.rbi_per_season / batter.games_played:.3f}/game)")
    print(f"  Runs per season : {batter.runs_per_season}  ({batter.runs_per_season / batter.games_played:.3f}/game)")
    print(f"  Power HR multiplier     : {batter.power_hr_multiplier():.3f}  (home run rate)")
    print(f"  Power doubles multiplier: {batter.power_doubles_multiplier():.3f}  (doubles rate)")

    # Show platoon hit-rate shift vs different pitcher arms
    for opp_throws in ("R", "L"):
        sp = platoon_splits_for(batter.bats, opp_throws)
        print(f"  vs {opp_throws}-handed pitcher : hits mult {sp['hits']:.2f}, "
              f"HR mult {sp['hr']:.2f}, 2B mult {sp['doubles']:.2f}")

    # Show home/away splits for the batter
    print("\n  Home/Away splits (batter):")
    for location, is_h in (("Home", True), ("Away", False)):
        ha = home_away_batter_splits_for(is_h)
        print(f"    {location}: hits×{ha['hits']:.2f}  HR×{ha['hr']:.2f}  2B×{ha['doubles']:.2f}")

    # Batter props at home vs LHP (platoon advantage + home boost)
    batter_report_home = sim.simulate_batter(
        batter, opponent_throws=pitcher.throws, is_home=True
    )
    print("\n--- Batter: HOME game (vs LHP, platoon + home boost) ---")
    sim.print_results(batter_report_home)

    # Batter props away vs LHP (platoon advantage, away penalty)
    batter_report_away = sim.simulate_batter(
        batter, opponent_throws=pitcher.throws, is_home=False
    )
    print("\n--- Batter: AWAY game (vs LHP, platoon boost, away penalty) ---")
    sim.print_results(batter_report_away)


if __name__ == "__main__":
    _demo()
