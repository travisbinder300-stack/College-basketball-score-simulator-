"""
MLB Player Props Simulator
==========================
Simulates individual player prop outcomes for MLB games including:
  - Pitcher props: Strikeouts, Outs recorded, Runs Allowed
  - Batter props:  Hits, Doubles, Home Runs, Stolen Bases

Environmental modifiers applied to every simulation:
  - Weather conditions  (temperature, precipitation)
  - Wind conditions     (speed, direction relative to field)
  - Stadium / Park factors (per-venue adjustments for each stat type)

Player-attribute modifiers:
  - Pitcher arm strength (0–100 scale) – affects K rate, runs allowed, and
    innings pitched depth.
  - Batter power rating  (0–100 scale) – affects HR rate and doubles rate.

Platoon / handedness splits:
  - Pitcher throwing hand (`throws`: "R" or "L").
  - Batter batting hand   (`bats`:   "R", "L", or "S" for switch).
  - Opposite-hand matchups (e.g. RHB vs LHP) favour the batter; same-hand
    matchups favour the pitcher.  See PLATOON_SPLITS for per-combo adjustments.

Usage example
-------------
    from mlb_player_props import (
        MLBPlayerPropsSimulator,
        WeatherConditions,
        WindConditions,
        Stadium,
        PitcherStats,
        BatterStats,
    )

    stadium = Stadium.from_name("Wrigley Field")
    weather = WeatherConditions(temp_f=72, precipitation="none", humidity=0.55)
    wind    = WindConditions(speed_mph=15, direction="out_to_center")

    sim = MLBPlayerPropsSimulator(stadium=stadium, weather=weather, wind=wind,
                                  num_simulations=10_000)

    # Left-handed pitcher with elite arm
    pitcher = PitcherStats(name="Ace Pitcher", era=3.50, k_per_9=9.5,
                           innings_per_start=6.0, whip=1.15,
                           arm_strength=75, throws="L")
    # Right-handed power hitter — has platoon advantage vs LHP
    batter  = BatterStats(name="Power Hitter", avg=0.285, obp=0.360,
                          slg=0.510, hr_per_600_pa=32, sb_per_season=18,
                          doubles_per_600_pa=38, games_played=162,
                          power_rating=80, bats="R")

    pitcher_results = sim.simulate_pitcher(pitcher, opponent_bats="R")
    batter_results  = sim.simulate_batter(batter, opponent_throws="L")

    sim.print_results(pitcher_results)
    sim.print_results(batter_results)
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
class WeatherConditions:
    """Describes the weather at game time."""

    temp_f: float = 72.0
    precipitation: str = "none"   # none | light | moderate | heavy
    humidity: float = 0.50        # 0.0 – 1.0

    def temp_hr_multiplier(self) -> float:
        """
        Ball travels farther in warm air (less dense).
        Baseline is 72 °F; every 10 °F adds/subtracts ~3 %.
        """
        return 1.0 + (self.temp_f - 72) * 0.003

    def temp_k_multiplier(self) -> float:
        """Cold weather → harder grip → slight increase in Ks."""
        return 1.0 - (self.temp_f - 72) * 0.001

    def precip_factor(self) -> float:
        return PRECIPITATION_FACTOR.get(self.precipitation, 1.00)

    def humidity_hit_multiplier(self) -> float:
        """
        High humidity makes the ball slightly heavier and harder to hit far.
        Effect is small (~2 % max).
        """
        return 1.0 - (self.humidity - 0.50) * 0.04

    def temp_hit_multiplier(self) -> float:
        """
        Temperature effect on batter contact rate.

        Cold weather slows bat speed and stiffens hands, reducing batting
        average.  Warm weather provides a small positive boost to contact.
        Baseline is 72 °F; effect scales linearly at
        TEMP_HIT_RATE_PER_DEGREE_F per degree.
        """
        return 1.0 + (self.temp_f - 72) * TEMP_HIT_RATE_PER_DEGREE_F

    def temp_pitcher_stamina_multiplier(self) -> float:
        """
        Temperature effect on pitcher stamina (expected innings pitched).

        * Below TEMP_COLD_THRESHOLD_F: cold reduces grip, increases effort per
          pitch, and leads to shorter outings.
        * Above TEMP_HOT_THRESHOLD_F: heat fatigue also shortens outings.
        * Between the two thresholds: no stamina penalty (returns 1.0).
        """
        if self.temp_f < TEMP_COLD_THRESHOLD_F:
            return 1.0 - (TEMP_COLD_THRESHOLD_F - self.temp_f) * TEMP_COLD_STAMINA_RATE
        if self.temp_f > TEMP_HOT_THRESHOLD_F:
            return 1.0 - (self.temp_f - TEMP_HOT_THRESHOLD_F) * TEMP_HOT_STAMINA_RATE
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
    """

    def __init__(
        self,
        stadium: Stadium,
        weather: WeatherConditions,
        wind: WindConditions,
        num_simulations: int = 10_000,
        random_seed: Optional[int] = None,
    ) -> None:
        self.stadium = stadium
        self.weather = weather
        self.wind = wind
        self.num_simulations = num_simulations
        if random_seed is not None:
            random.seed(random_seed)

    # ------------------------------------------------------------------
    # Composite environmental multipliers
    # ------------------------------------------------------------------

    def _env_hr_multiplier(self) -> float:
        return (
            self.stadium.hr_factor
            * self.weather.temp_hr_multiplier()
            * self.weather.precip_factor()
            * self.weather.humidity_hit_multiplier()
            * self.wind.hr_multiplier()
        )

    def _env_hits_multiplier(self) -> float:
        return (
            self.stadium.hits_factor
            * self.weather.temp_hit_multiplier()
            * self.weather.precip_factor()
            * self.weather.humidity_hit_multiplier()
            * self.wind.hit_multiplier()
        )

    def _env_doubles_multiplier(self) -> float:
        return (
            self.stadium.doubles_factor
            * self.weather.temp_hit_multiplier()
            * self.weather.precip_factor()
            * self.weather.humidity_hit_multiplier()
            * self.wind.hit_multiplier()
        )

    def _env_k_multiplier(self) -> float:
        return (
            self.stadium.k_factor
            * self.weather.temp_k_multiplier()
            * self.weather.precip_factor()
            * self.wind.k_multiplier()
        )

    def _env_runs_multiplier(self) -> float:
        return (
            self.stadium.runs_factor
            * self.weather.temp_hr_multiplier()
            * self.weather.precip_factor()
            * self.wind.runs_multiplier()
        )

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
    ) -> Tuple[float, float, float]:
        """
        Returns (strikeouts, outs_recorded, runs_allowed) for one simulated game.
        Uses a Poisson-like approach via random Gaussian perturbation of expected values.
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

        return strikeouts, outs_recorded, runs_allowed

    # ------------------------------------------------------------------
    # Simulate a single game for a batter
    # ------------------------------------------------------------------

    def _simulate_batter_game(
        self,
        stats: BatterStats,
        hits_mult: float,
        doubles_mult: float,
        hr_mult: float,
    ) -> Tuple[float, float, float, float]:
        """
        Returns (hits, doubles, home_runs, stolen_bases) for one simulated game.
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

        return hits, doubles, home_runs, stolen_bases

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def simulate_pitcher(
        self,
        stats: PitcherStats,
        k_lines: Optional[List[float]] = None,
        outs_lines: Optional[List[float]] = None,
        runs_lines: Optional[List[float]] = None,
        opponent_bats: Optional[str] = None,
    ) -> PlayerPropsReport:
        """
        Run Monte Carlo simulations for a starting pitcher.

        Parameters
        ----------
        stats         : PitcherStats
        k_lines       : list of strikeout over/under lines to evaluate
        outs_lines    : list of outs-recorded lines to evaluate
        runs_lines    : list of runs-allowed lines to evaluate
        opponent_bats : batting hand of the opposing lineup ("R", "L", or "S").
                        When provided the platoon split adjusts K rate and runs
                        allowed.  None means no platoon adjustment is applied.
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

        k_mult = self._env_k_multiplier() * stats.arm_k_multiplier() * platoon_k_mult
        runs_mult = self._env_runs_multiplier() * stats.arm_runs_multiplier() * platoon_runs_mult
        # Pre-compute stamina once — temperature and arm strength are fixed for
        # the whole run.  Arm strength extends/shortens outings independently of
        # the weather-based stamina penalty so they multiply together.
        stamina_mult = self.weather.temp_pitcher_stamina_multiplier() * stats.arm_ip_multiplier()

        k_results: List[float] = []
        outs_results: List[float] = []
        runs_results: List[float] = []

        for _ in range(self.num_simulations):
            k, outs, runs = self._simulate_pitcher_game(stats, k_mult, runs_mult, stamina_mult)
            k_results.append(k)
            outs_results.append(outs)
            runs_results.append(runs)

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
        return report

    def simulate_batter(
        self,
        stats: BatterStats,
        hits_lines: Optional[List[float]] = None,
        doubles_lines: Optional[List[float]] = None,
        hr_lines: Optional[List[float]] = None,
        sb_lines: Optional[List[float]] = None,
        opponent_throws: Optional[str] = None,
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
        opponent_throws : throwing hand of the opposing pitcher ("R" or "L").
                          When provided the platoon split adjusts hits, HR, and
                          doubles rates.  None means no platoon adjustment.
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

        hits_mult = self._env_hits_multiplier() * platoon_hits_mult
        doubles_mult = self._env_doubles_multiplier() * stats.power_doubles_multiplier() * platoon_doubles_mult
        hr_mult = self._env_hr_multiplier() * stats.power_hr_multiplier() * platoon_hr_mult

        hits_results: List[float] = []
        doubles_results: List[float] = []
        hr_results: List[float] = []
        sb_results: List[float] = []

        for _ in range(self.num_simulations):
            h, d, hr, sb = self._simulate_batter_game(stats, hits_mult, doubles_mult, hr_mult)
            hits_results.append(h)
            doubles_results.append(d)
            hr_results.append(hr)
            sb_results.append(sb)

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
        return report

    def print_results(self, report: PlayerPropsReport) -> None:  # pragma: no cover
        """Pretty-print a PlayerPropsReport to stdout."""
        print(report)

    def simulate_matchup(
        self,
        pitcher: PitcherStats,
        batters: List[BatterStats],
    ) -> Dict[str, PlayerPropsReport]:
        """
        Convenience method: simulate an entire pitcher vs lineup matchup.

        Platoon splits are applied automatically: each batter simulation uses
        the pitcher's throwing hand (``pitcher.throws``) and the pitcher
        simulation uses the first batter's batting hand as a representative
        opponent for K/runs adjustments (or "R" when no batters are provided).

        Returns a dict keyed by player name.
        """
        results: Dict[str, PlayerPropsReport] = {}
        # Determine representative opponent batting hand for the pitcher.
        rep_bats = batters[0].bats if batters else "R"
        results[pitcher.name] = self.simulate_pitcher(pitcher, opponent_bats=rep_bats)
        for batter in batters:
            results[batter.name] = self.simulate_batter(batter, opponent_throws=pitcher.throws)
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

    # Weather
    weather = WeatherConditions(temp_f=68, precipitation="light", humidity=0.65)
    print(f"\nWeather : {weather.temp_f}°F, precip={weather.precipitation}, humidity={weather.humidity}")
    print(f"  Temp HR multiplier      : {weather.temp_hr_multiplier():.3f}")
    print(f"  Temp hit multiplier     : {weather.temp_hit_multiplier():.3f}  (batter contact rate)")
    print(f"  Temp K multiplier       : {weather.temp_k_multiplier():.3f}  (pitcher strikeout rate)")
    print(f"  Temp stamina multiplier : {weather.temp_pitcher_stamina_multiplier():.3f}  (pitcher innings)")

    # Wind
    wind = WindConditions(speed_mph=12, direction="out_to_center")
    print(f"\nWind    : {wind.speed_mph} mph {wind.direction}")
    print(f"  HR multiplier   : {wind.hr_multiplier():.3f}")
    print(f"  Hit multiplier  : {wind.hit_multiplier():.3f}")
    print(f"  K multiplier    : {wind.k_multiplier():.3f}  (pitcher strikeout rate)")
    print(f"  Runs multiplier : {wind.runs_multiplier():.3f}  (runs allowed)")

    # Simulator (small run for demo speed)
    sim = MLBPlayerPropsSimulator(
        stadium=stadium,
        weather=weather,
        wind=wind,
        num_simulations=5_000,
        random_seed=42,
    )

    # Pitcher — left-handed ace (arm_strength=80, throws="L")
    pitcher = PitcherStats(
        name="Demo Ace",
        era=3.20,
        k_per_9=10.5,
        innings_per_start=6.0,
        whip=1.08,
        arm_strength=80,
        throws="L",
    )
    print(f"\nPitcher : {pitcher.name}  (arm_strength={pitcher.arm_strength}, throws={pitcher.throws})")
    print(f"  Arm K multiplier   : {pitcher.arm_k_multiplier():.3f}  (strikeout rate)")
    print(f"  Arm runs multiplier: {pitcher.arm_runs_multiplier():.3f}  (runs allowed)")
    print(f"  Arm IP multiplier  : {pitcher.arm_ip_multiplier():.3f}  (innings pitched)")

    # Show platoon K-rate shift vs opposing lineups
    for opp_bats in ("R", "L", "S"):
        sp = platoon_splits_for(opp_bats, pitcher.throws)
        print(f"  vs {opp_bats}-handed lineup : K mult {sp['k']:.2f}, runs mult {sp['runs']:.2f}")

    # Pitcher props vs right-handed lineup (RHB has platoon advantage over LHP)
    pitcher_report = sim.simulate_pitcher(pitcher, opponent_bats="R")
    sim.print_results(pitcher_report)

    # Batter — right-handed power hitter (power_rating=85, bats="R")
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
    )
    print(f"\nBatter  : {batter.name}  (power_rating={batter.power_rating}, bats={batter.bats})")
    print(f"  Power HR multiplier     : {batter.power_hr_multiplier():.3f}  (home run rate)")
    print(f"  Power doubles multiplier: {batter.power_doubles_multiplier():.3f}  (doubles rate)")

    # Show platoon hit-rate shift vs different pitcher arms
    for opp_throws in ("R", "L"):
        sp = platoon_splits_for(batter.bats, opp_throws)
        print(f"  vs {opp_throws}-handed pitcher : hits mult {sp['hits']:.2f}, "
              f"HR mult {sp['hr']:.2f}, 2B mult {sp['doubles']:.2f}")

    # Simulate with platoon split applied (RHB vs LHP → batter boost)
    batter_report = sim.simulate_batter(batter, opponent_throws=pitcher.throws)
    sim.print_results(batter_report)


if __name__ == "__main__":
    _demo()
