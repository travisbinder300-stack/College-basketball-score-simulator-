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

Unabated API Edge Screener
---------------------------
:class:`UnabatedEdgeScreener` fetches live MLB player-prop lines from the
`Unabated <https://unabated.com>`_ API and compares the market's implied
probability against the simulator's probability for each line.  When the
difference (the *edge*) exceeds a configurable threshold, the opportunity
is surfaced as an :class:`EdgeResult`.

::

    from mlb_player_props import (
        MLBPlayerPropsSimulator,
        UnabatedClient,
        UnabatedEdgeScreener,
        PitcherStats,
        BatterStats,
    )

    client  = UnabatedClient(api_key="YOUR_UNABATED_API_KEY")
    sim     = MLBPlayerPropsSimulator(stadium=stadium, weather=weather, wind=wind)
    screener = UnabatedEdgeScreener(sim, client, min_edge=0.05)

    pitcher = PitcherStats(name="Corbin Burnes", era=3.10, k_per_9=10.2,
                           innings_per_start=6.1, whip=1.05)
    edges = screener.screen_pitcher(pitcher)

    for e in edges:
        print(e)
        # e.g.  ★ EDGE  Corbin Burnes | Strikeouts | O6.5
        #               Model 64.2 %  vs  Market 51.3 %  (+12.9 pp)
        #               Market odds: +95

Toronto Blue Jays 2026 Roster
------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Toronto Blue Jays lineup and starting rotation are available
as module-level constants and via the :class:`BlueJaysRoster` helper:

* ``BLUE_JAYS_LINEUP_2026``   – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``BLUE_JAYS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``BLUE_JAYS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import BlueJaysRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = BlueJaysRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Kevin Gausman) against Unabated's live lines
    edges = screener.screen_pitcher(roster.rotation[0])

    # Screen Vladimir Guerrero Jr. (lineup[1], 1B) for batter props
    edges += screener.screen_batter(roster.lineup[1])

Chicago White Sox 2026 Depth Chart
------------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Chicago White Sox depth-chart starters, starting rotation,
and bullpen are available via the :class:`WhiteSoxRoster` helper:

* ``WHITE_SOX_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``WHITE_SOX_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``WHITE_SOX_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import WhiteSoxRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = WhiteSoxRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen all starters
    for batter in roster.lineup:
        for edge in screener.screen_batter(batter):
            print(edge)

    # Screen the closer (Seranthony Dominguez)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Cleveland Guardians 2026 Depth Chart
--------------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Cleveland Guardians depth-chart starters, starting rotation,
and bullpen are available via the :class:`GuardiansRoster` helper:

* ``GUARDIANS_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``GUARDIANS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``GUARDIANS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import GuardiansRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = GuardiansRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen Jose Ramirez for batter props
    for edge in screener.screen_batter(roster.lineup[3]):
        print(edge)

    # Screen the closer (Cade Smith)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Detroit Tigers 2026 Depth Chart
---------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Detroit Tigers depth-chart starters, starting rotation,
and bullpen are available via the :class:`TigersRoster` helper:

* ``TIGERS_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``TIGERS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``TIGERS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import TigersRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = TigersRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Tarik Skubal) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (Kenley Jansen)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Kansas City Royals 2026 Depth Chart
--------------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Kansas City Royals depth-chart starters, starting rotation,
and bullpen are available via the :class:`RoyalsRoster` helper:

* ``ROYALS_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``ROYALS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``ROYALS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import RoyalsRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = RoyalsRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Cole Ragans) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (Carlos Estevez)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Minnesota Twins 2026 Depth Chart
-----------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Minnesota Twins depth-chart starters, starting rotation,
and bullpen are available via the :class:`TwinsRoster` helper:

* ``TWINS_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``TWINS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``TWINS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import TwinsRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = TwinsRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Joe Ryan) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (Taylor Rogers)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Baltimore Orioles 2026 Depth Chart
-------------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Baltimore Orioles depth-chart starters, starting rotation,
and bullpen are available via the :class:`OriolesRoster` helper:

* ``ORIOLES_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``ORIOLES_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``ORIOLES_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import OriolesRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = OriolesRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Trevor Rogers) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (Ryan Helsley)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Boston Red Sox 2026 Depth Chart
----------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Boston Red Sox depth-chart starters, starting rotation,
and bullpen are available via the :class:`RedSoxRoster` helper:

* ``RED_SOX_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``RED_SOX_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``RED_SOX_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import RedSoxRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = RedSoxRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Garrett Crochet) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (Aroldis Chapman)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

New York Yankees 2026 Depth Chart
------------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 New York Yankees depth-chart starters, starting rotation,
and bullpen are available via the :class:`YankeesRoster` helper:

* ``YANKEES_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``YANKEES_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``YANKEES_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import YankeesRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = YankeesRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Max Fried) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (David Bednar)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Tampa Bay Rays 2026 Depth Chart
-----------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Tampa Bay Rays depth-chart starters, starting rotation,
and bullpen are available via the :class:`RaysRoster` helper:

* ``RAYS_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``RAYS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``RAYS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import RaysRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = RaysRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Drew Rasmussen) for strikeout props
    for edge in screener.screen_pitcher(roster.rotation[0]):
        print(edge)

    # Screen the closer (Griffin Jax)
    for edge in screener.screen_pitcher(roster.bullpen[-1]):
        print(edge)

Athletics 2026 Depth Chart
------------------------------------
Pre-built :class:`BatterStats` / :class:`PitcherStats` objects for the
projected 2026 Athletics depth-chart starters, starting rotation,
and bullpen are available via the :class:`AthleticsRoster` helper:

* ``ATHLETICS_LINEUP_2026``  – ``List[BatterStats]``, position starters
  (C → 1B → 2B → 3B → SS → LF → CF → RF → DH)
* ``ATHLETICS_ROTATION_2026`` – ``List[PitcherStats]``, rotation order 1–5
* ``ATHLETICS_BULLPEN_2026``  – ``List[PitcherStats]``, setup + closer (index 5)

::

    from mlb_player_props import AthleticsRoster, UnabatedEdgeScreener, UnabatedClient

    roster   = AthleticsRoster.default()
    screener = UnabatedEdgeScreener(sim, UnabatedClient("YOUR_KEY"))

    # Screen the ace (Luis Severino) for strikeout props
    edges = screener.screen_pitcher(roster.rotation[0])

    # Screen the cleanup hitter (Brent Rooker, DH) for batter props
    edges += screener.screen_batter(roster.lineup[8])
"""

from __future__ import annotations

import json
import math
import random
import statistics
import urllib.error
import urllib.request
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
# Unabated API — edge-screener constants
# ---------------------------------------------------------------------------
# Base URL for the Unabated public REST API (v1).  All requests are sent as
# GET requests; authentication is via an ``X-Api-Key`` header.
UNABATED_BASE_URL: str = "https://api.unabated.com/v1"

# Default minimum edge (in probability percentage points) required before an
# opportunity is surfaced as an :class:`EdgeResult`.  A value of 0.05 means
# the simulator's probability must be at least 5 percentage points higher
# than the market's implied probability.
UNABATED_DEFAULT_MIN_EDGE: float = 0.05

# Default HTTP request timeout in seconds for all Unabated API calls.
UNABATED_DEFAULT_REQUEST_TIMEOUT: int = 10

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
# Odds helpers
# ---------------------------------------------------------------------------


def odds_to_implied_prob(american_odds: float) -> float:
    """
    Convert American (moneyline) odds to an implied probability.

    Parameters
    ----------
    american_odds : float
        Positive (e.g. ``+150``) or negative (e.g. ``-110``) American odds.

    Returns
    -------
    float
        Implied probability in the range (0, 1).  The returned value is the
        *raw* (vig-inclusive) probability; no vig-stripping is applied.

    Examples
    --------
    >>> round(odds_to_implied_prob(-110), 4)
    0.5238
    >>> round(odds_to_implied_prob(+100), 4)
    0.5
    """
    if american_odds < 0:
        return (-american_odds) / (-american_odds + 100.0)
    return 100.0 / (american_odds + 100.0)


def implied_prob_to_american_odds(prob: float) -> float:
    """
    Convert an implied probability to American (moneyline) odds.

    Parameters
    ----------
    prob : float
        Probability in the range (0, 1).  Values outside this range raise
        :class:`ValueError`.

    Returns
    -------
    float
        American odds.  Returns negative odds when ``prob > 0.5``, positive
        when ``prob < 0.5``, and exactly ``+100`` / ``-100`` at 50 %.

    Examples
    --------
    >>> implied_prob_to_american_odds(0.5238)
    -109.96...
    """
    if not (0.0 < prob < 1.0):
        raise ValueError("prob must be strictly between 0 and 1")
    if prob >= 0.5:
        return -(prob * 100.0) / (1.0 - prob)
    return (1.0 - prob) * 100.0 / prob


# ---------------------------------------------------------------------------
# Unabated edge-screening
# ---------------------------------------------------------------------------


@dataclass
class EdgeResult:
    """
    A single prop-line opportunity where the simulator disagrees with the market.

    Attributes
    ----------
    player_name : str
        Display name of the player.
    prop : str
        Prop type, e.g. ``"Strikeouts"``, ``"Hits"``, ``"Home Runs"``.
    line : float
        The over/under line value (e.g. ``6.5`` for O/U 6.5 strikeouts).
    side : str
        ``"over"`` or ``"under"``.
    sim_prob : float
        The simulator's probability for the bet direction (0–1).
    market_prob : float
        Implied probability derived from the market's American odds (0–1).
    edge : float
        ``sim_prob − market_prob`` (positive = model favours the bet).
    american_odds : float
        The American odds fetched from the market for this line/side.
    book : str
        Name of the sportsbook offering these odds (as reported by Unabated).
        Empty string when book information is unavailable.
    """

    player_name: str
    prop: str
    line: float
    side: str
    sim_prob: float
    market_prob: float
    edge: float
    american_odds: float
    book: str = ""

    def __str__(self) -> str:
        direction = "O" if self.side == "over" else "U"
        sign = "+" if self.american_odds >= 0 else ""
        return (
            f"★ EDGE  {self.player_name} | {self.prop} | {direction}{self.line:.1f}\n"
            f"        Model {self.sim_prob*100:.1f}%  vs  "
            f"Market {self.market_prob*100:.1f}%  "
            f"(+{self.edge*100:.1f} pp)\n"
            f"        Market odds: {sign}{self.american_odds:.0f}"
            + (f"  [{self.book}]" if self.book else "")
        )


class UnabatedClient:
    """
    Thin HTTP client for the Unabated player-props API.

    Uses only the Python standard library (:mod:`urllib.request`) — no
    external packages are required.

    Parameters
    ----------
    api_key : str
        Your Unabated API key.  Sent as the ``X-Api-Key`` header on every
        request.  When empty the header is still sent; Unabated will return
        a ``401`` response in that case.
    base_url : str
        API base URL.  Defaults to :data:`UNABATED_BASE_URL`.
    timeout : int
        HTTP request timeout in seconds.  Defaults to
        :data:`UNABATED_DEFAULT_REQUEST_TIMEOUT`.

    Notes
    -----
    The Unabated REST API returns JSON.  The ``fetch_player_props`` method
    returns the *parsed* JSON payload (a list of market-line dicts) so that
    the caller (typically :class:`UnabatedEdgeScreener`) can process it without
    repeated HTTP calls.

    If the request fails for any reason (network error, non-2xx response, or
    malformed JSON) a :class:`UnabatedAPIError` is raised.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = UNABATED_BASE_URL,
        timeout: int = UNABATED_DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        if not isinstance(api_key, str):
            raise TypeError("api_key must be a string")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_player_props(
        self,
        sport: str = "mlb",
        market_type: str = "player_props",
    ) -> List[Dict]:
        """
        Fetch live player-prop lines from the Unabated API.

        Parameters
        ----------
        sport : str
            Sport slug.  Defaults to ``"mlb"``.
        market_type : str
            Market-type filter.  Defaults to ``"player_props"``.

        Returns
        -------
        list of dict
            Each dict represents one market line with at minimum the keys:

            ``player_name`` (str), ``prop_type`` (str), ``line`` (float),
            ``over_odds`` (float), ``under_odds`` (float),
            ``book`` (str).

            The exact schema is normalised in :meth:`_normalise_response`
            before being returned.

        Raises
        ------
        UnabatedAPIError
            On any HTTP error, timeout, or JSON decode failure.
        """
        url = f"{self.base_url}/markets?sport={sport}&market_type={market_type}"
        req = urllib.request.Request(
            url,
            headers={"X-Api-Key": self.api_key, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise UnabatedAPIError(
                f"Unabated API returned HTTP {exc.code}: {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise UnabatedAPIError(
                f"Unabated API request failed: {exc.reason}"
            ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise UnabatedAPIError(
                f"Unabated API returned non-JSON response: {exc}"
            ) from exc

        return self._normalise_response(payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_response(payload: object) -> List[Dict]:
        """
        Normalise a raw Unabated API response to a flat list of line dicts.

        The Unabated API may wrap the data inside a ``"data"`` key or return
        a list directly.  Each normalised dict is guaranteed to have:

        ``player_name``, ``prop_type``, ``line``, ``over_odds``,
        ``under_odds``, ``book``.

        Unknown / missing fields default to sensible values (empty string /
        ``None`` for odds / 0 for line).
        """
        # Unwrap {"data": [...]} envelope if present.
        if isinstance(payload, dict):
            items = payload.get("data", payload.get("markets", []))
            if not isinstance(items, list):
                items = [payload]
        elif isinstance(payload, list):
            items = payload
        else:
            return []

        normalised: List[Dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalised.append({
                "player_name": str(item.get("player_name", item.get("name", ""))),
                "prop_type":   str(item.get("prop_type", item.get("stat_type", ""))),
                "line":        float(item.get("line", item.get("value", 0))),
                "over_odds":   item.get("over_odds", item.get("over", None)),
                "under_odds":  item.get("under_odds", item.get("under", None)),
                "book":        str(item.get("book", item.get("sportsbook", ""))),
            })
        return normalised


class UnabatedAPIError(Exception):
    """Raised when an Unabated API request fails."""


class UnabatedEdgeScreener:
    """
    Screen MLB player props for edges by comparing the simulator's
    probabilities against Unabated's live market lines.

    An *edge* exists when:

        ``sim_prob − market_implied_prob ≥ min_edge``

    Both the over and the under side of every line are evaluated.  Only
    results that clear the threshold are returned.

    Parameters
    ----------
    simulator : MLBPlayerPropsSimulator
        A configured simulator instance (stadium, weather, wind, optional
        calibrator already set).
    client : UnabatedClient
        An authenticated Unabated API client.
    min_edge : float
        Minimum edge in probability percentage points for a result to be
        surfaced.  Defaults to :data:`UNABATED_DEFAULT_MIN_EDGE` (0.05 = 5 pp).

    Examples
    --------
    ::

        screener = UnabatedEdgeScreener(sim, client, min_edge=0.04)
        edges = screener.screen_pitcher(pitcher_stats)
        for e in sorted(edges, key=lambda x: -x.edge):
            print(e)
    """

    # Map from Unabated ``prop_type`` strings (case-insensitive) to the
    # simulator's internal prop names used in PropResult.prop_name.
    _PROP_TYPE_MAP: ClassVar[Dict[str, str]] = {
        "strikeouts": "Strikeouts",
        "pitcher strikeouts": "Strikeouts",
        "outs recorded": "Outs Recorded",
        "pitcher outs": "Outs Recorded",
        "runs allowed": "Runs Allowed",
        "pitcher runs allowed": "Runs Allowed",
        "pitch count": "Pitch Count",
        "pitcher pitch count": "Pitch Count",
        "hits": "Hits",
        "batter hits": "Hits",
        "doubles": "Doubles",
        "batter doubles": "Doubles",
        "home runs": "Home Runs",
        "batter home runs": "Home Runs",
        "stolen bases": "Stolen Bases",
        "batter stolen bases": "Stolen Bases",
        "plate appearances": "Plate Appearances",
        "batter plate appearances": "Plate Appearances",
        "h+r+rbi": "H+R+RBI",
        "hits + runs + rbi": "H+R+RBI",
    }

    def __init__(
        self,
        simulator: "MLBPlayerPropsSimulator",
        client: UnabatedClient,
        min_edge: float = UNABATED_DEFAULT_MIN_EDGE,
    ) -> None:
        self.simulator = simulator
        self.client = client
        self.min_edge = min_edge

    # ------------------------------------------------------------------
    # Public screening API
    # ------------------------------------------------------------------

    def screen_pitcher(
        self,
        stats: "PitcherStats",
        market_lines: Optional[List[Dict]] = None,
        opponent_bats: Optional[str] = None,
        is_home: Optional[bool] = None,
    ) -> List[EdgeResult]:
        """
        Find edges for a starting pitcher.

        Parameters
        ----------
        stats : PitcherStats
        market_lines : list of dict, optional
            Pre-fetched Unabated market lines (useful for testing or batching
            many calls without repeated HTTP requests).  When ``None``,
            :meth:`UnabatedClient.fetch_player_props` is called automatically.
        opponent_bats : str, optional
            Batting hand of the opposing lineup (``"R"``, ``"L"``, ``"S"``).
        is_home : bool, optional
            Whether the pitcher is at home.

        Returns
        -------
        list of EdgeResult
            Sorted by edge descending (largest edge first).
        """
        report = self.simulator.simulate_pitcher(
            stats, opponent_bats=opponent_bats, is_home=is_home
        )
        lines = market_lines if market_lines is not None else self.client.fetch_player_props()
        return self._find_edges(stats.name, report, lines)

    def screen_batter(
        self,
        stats: "BatterStats",
        market_lines: Optional[List[Dict]] = None,
        opponent_throws: Optional[str] = None,
        is_home: Optional[bool] = None,
    ) -> List[EdgeResult]:
        """
        Find edges for a batter.

        Parameters
        ----------
        stats : BatterStats
        market_lines : list of dict, optional
            Pre-fetched Unabated market lines.
        opponent_throws : str, optional
            Throwing hand of the opposing pitcher (``"R"`` or ``"L"``).
        is_home : bool, optional
            Whether the batter is at home.

        Returns
        -------
        list of EdgeResult
            Sorted by edge descending.
        """
        report = self.simulator.simulate_batter(
            stats, opponent_throws=opponent_throws, is_home=is_home
        )
        lines = market_lines if market_lines is not None else self.client.fetch_player_props()
        return self._find_edges(stats.name, report, lines)

    def screen_matchup(
        self,
        pitcher: "PitcherStats",
        batters: List["BatterStats"],
        market_lines: Optional[List[Dict]] = None,
        pitcher_is_home: Optional[bool] = None,
    ) -> List[EdgeResult]:
        """
        Find edges for an entire pitcher vs lineup matchup.

        Parameters
        ----------
        pitcher : PitcherStats
        batters : list of BatterStats
        market_lines : list of dict, optional
            Pre-fetched Unabated market lines.  When ``None``, the API is
            called once and the result shared across all players.
        pitcher_is_home : bool, optional

        Returns
        -------
        list of EdgeResult
            All edges for all players in the matchup, sorted by edge descending.
        """
        lines = market_lines if market_lines is not None else self.client.fetch_player_props()
        all_edges: List[EdgeResult] = []
        batter_is_home: Optional[bool] = (
            None if pitcher_is_home is None else not pitcher_is_home
        )
        rep_bats = batters[0].bats if batters else "R"
        all_edges.extend(
            self.screen_pitcher(pitcher, market_lines=lines,
                                opponent_bats=rep_bats, is_home=pitcher_is_home)
        )
        for batter in batters:
            all_edges.extend(
                self.screen_batter(batter, market_lines=lines,
                                   opponent_throws=pitcher.throws, is_home=batter_is_home)
            )
        all_edges.sort(key=lambda e: -e.edge)
        return all_edges

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _normalise_prop_type(cls, raw: str) -> Optional[str]:
        """Map a raw Unabated prop-type string to the simulator's prop name."""
        return cls._PROP_TYPE_MAP.get(raw.strip().lower())

    def _find_edges(
        self,
        player_name: str,
        report: "PlayerPropsReport",
        market_lines: List[Dict],
    ) -> List[EdgeResult]:
        """
        Compare a PlayerPropsReport against market lines and return edges.

        Only lines whose player name (case-insensitive) matches ``player_name``
        are considered.  Both the over and under side of each line are checked
        against the simulator's ``over_probabilities`` dict in the relevant
        :class:`PropResult`.
        """
        # Build a lookup: prop_name → PropResult for fast access.
        prop_lookup: Dict[str, "PropResult"] = {
            pr.prop_name: pr for pr in report.props
        }

        player_lower = player_name.strip().lower()
        edges: List[EdgeResult] = []

        for mkt in market_lines:
            # Filter by player name (partial match — e.g. "Burnes" matches
            # "Corbin Burnes").
            mkt_player = mkt.get("player_name", "")
            if player_lower not in mkt_player.strip().lower():
                continue

            prop_name = self._normalise_prop_type(mkt.get("prop_type", ""))
            if prop_name is None or prop_name not in prop_lookup:
                continue

            pr = prop_lookup[prop_name]
            line_val = float(mkt.get("line", 0))

            for side, odds_key in (("over", "over_odds"), ("under", "under_odds")):
                raw_odds = mkt.get(odds_key)
                if raw_odds is None:
                    continue
                try:
                    american_odds = float(raw_odds)
                except (TypeError, ValueError):
                    continue

                market_prob = odds_to_implied_prob(american_odds)

                # Retrieve the simulator's probability for this side/line.
                if side == "over":
                    sim_prob = pr.over_probabilities.get(line_val)
                else:
                    over_prob = pr.over_probabilities.get(line_val)
                    sim_prob = 1.0 - over_prob if over_prob is not None else None

                if sim_prob is None:
                    continue

                edge = sim_prob - market_prob
                if edge >= self.min_edge:
                    edges.append(EdgeResult(
                        player_name=player_name,
                        prop=prop_name,
                        line=line_val,
                        side=side,
                        sim_prob=sim_prob,
                        market_prob=market_prob,
                        edge=edge,
                        american_odds=american_odds,
                        book=mkt.get("book", ""),
                    ))

        edges.sort(key=lambda e: -e.edge)
        return edges


# ---------------------------------------------------------------------------
# Toronto Blue Jays — 2026 roster
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the Toronto Blue Jays'
# projected 2026 lineup and starting rotation.  Statistics are modelled on
# each player's recent MLB (and, for Okamoto, NPB) performance.
#
# Usage — run the entire lineup through the Unabated edge screener:
#
#   from mlb_player_props import (
#       BlueJaysRoster,
#       MLBPlayerPropsSimulator,
#       WeatherConditions,
#       WindConditions,
#       Stadium,
#       UnabatedClient,
#       UnabatedEdgeScreener,
#   )
#
#   roster  = BlueJaysRoster.default()
#   sim     = MLBPlayerPropsSimulator(Stadium.from_name("Rogers Centre"),
#                 WeatherConditions(temp_f=72, precipitation="none",
#                                   humidity=0.55, game_time="dome"),
#                 WindConditions(speed_mph=0, direction="calm"))
#   client  = UnabatedClient(api_key="YOUR_KEY")
#   screener = UnabatedEdgeScreener(sim, client, min_edge=0.05)
#
#   # Screen the ace starter (Kevin Gausman, rotation[0])
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen every position starter against the opener
#   for batter in roster.lineup:
#       for edge in screener.screen_batter(batter, opponent_throws="R"):
#           print(edge)
#
# Note on lineup construction (2026):
#   Bo Bichette's departure leaves Vladimir Guerrero Jr. as the unquestioned
#   lineup anchor.  Toronto is expected to platoon several spots (LF, 3B, 2B)
#   heavily and bat Vladdy 3rd against both right-handed and left-handed
#   starters.  Anthony Santander is projected to miss most of the season
#   following shoulder surgery, making Nathan Lukes the de-facto starting LF.
#   Kazuma Okamoto arrives from the NPB (Tokyo Yakult Swallows) as a power bat
#   at 3B.  Ernie Clement provides a low-cost, high-contact option at 2B.
#   Andrés Giménez was acquired in the off-season to shore up SS defence.
# ---------------------------------------------------------------------------


# -- Nine-man batting order --------------------------------------------------

#: George Springer — DH, bats right, strong power/speed combo.
_BJ_SPRINGER = BatterStats(
    name="George Springer",
    avg=0.262,
    obp=0.347,
    slg=0.462,
    hr_per_600_pa=25.0,
    sb_per_season=7.0,
    doubles_per_600_pa=28.0,
    games_played=130,
    power_rating=72.0,
    bats="R",
    pitches_per_pa=3.92,
    rbi_per_season=66.0,
    runs_per_season=80.0,
)

#: Addison Barger — RF, bats left, ascending contact/power profile.
_BJ_BARGER = BatterStats(
    name="Addison Barger",
    avg=0.242,
    obp=0.305,
    slg=0.425,
    hr_per_600_pa=18.0,
    sb_per_season=6.0,
    doubles_per_600_pa=32.0,
    games_played=145,
    power_rating=60.0,
    bats="L",
    pitches_per_pa=3.72,
    rbi_per_season=55.0,
    runs_per_season=62.0,
)

#: Vladimir Guerrero Jr. — 1B, bats right, franchise cornerstone.
_BJ_GUERRERO = BatterStats(
    name="Vladimir Guerrero Jr.",
    avg=0.285,
    obp=0.357,
    slg=0.502,
    hr_per_600_pa=32.0,
    sb_per_season=3.0,
    doubles_per_600_pa=38.0,
    games_played=158,
    power_rating=88.0,
    bats="R",
    pitches_per_pa=4.02,
    rbi_per_season=100.0,
    runs_per_season=85.0,
)

#: Alejandro Kirk — C, bats right, elite contact, below-average power.
_BJ_KIRK = BatterStats(
    name="Alejandro Kirk",
    avg=0.258,
    obp=0.348,
    slg=0.390,
    hr_per_600_pa=12.0,
    sb_per_season=0.0,
    doubles_per_600_pa=26.0,
    games_played=120,
    power_rating=44.0,
    bats="R",
    pitches_per_pa=4.10,
    rbi_per_season=50.0,
    runs_per_season=44.0,
)

#: Daulton Varsho — CF, bats left, speed/power combination.
_BJ_VARSHO = BatterStats(
    name="Daulton Varsho",
    avg=0.228,
    obp=0.298,
    slg=0.418,
    hr_per_600_pa=22.0,
    sb_per_season=20.0,
    doubles_per_600_pa=30.0,
    games_played=148,
    power_rating=65.0,
    bats="L",
    pitches_per_pa=3.62,
    rbi_per_season=62.0,
    runs_per_season=72.0,
)

#: Nathan Lukes — LF, bats left, contact-oriented bench-to-starter.
_BJ_LUKES = BatterStats(
    name="Nathan Lukes",
    avg=0.258,
    obp=0.318,
    slg=0.372,
    hr_per_600_pa=6.0,
    sb_per_season=8.0,
    doubles_per_600_pa=30.0,
    games_played=135,
    power_rating=35.0,
    bats="L",
    pitches_per_pa=3.58,
    rbi_per_season=40.0,
    runs_per_season=52.0,
)

#: Kazuma Okamoto — 3B, bats right, NPB power import (Tokyo Yakult Swallows).
_BJ_OKAMOTO = BatterStats(
    name="Kazuma Okamoto",
    avg=0.265,
    obp=0.330,
    slg=0.478,
    hr_per_600_pa=28.0,
    sb_per_season=3.0,
    doubles_per_600_pa=35.0,
    games_played=155,
    power_rating=78.0,
    bats="R",
    pitches_per_pa=3.72,
    rbi_per_season=82.0,
    runs_per_season=70.0,
)

#: Ernie Clement — 2B, bats right, high-contact utility/starter.
_BJ_CLEMENT = BatterStats(
    name="Ernie Clement",
    avg=0.248,
    obp=0.292,
    slg=0.338,
    hr_per_600_pa=5.0,
    sb_per_season=8.0,
    doubles_per_600_pa=25.0,
    games_played=130,
    power_rating=30.0,
    bats="R",
    pitches_per_pa=3.42,
    rbi_per_season=35.0,
    runs_per_season=46.0,
)

#: Andrés Giménez — SS, switch-hitter, defence-first profile.
_BJ_GIMENEZ = BatterStats(
    name="Andrés Giménez",
    avg=0.248,
    obp=0.308,
    slg=0.372,
    hr_per_600_pa=10.0,
    sb_per_season=15.0,
    doubles_per_600_pa=28.0,
    games_played=152,
    power_rating=42.0,
    bats="S",
    pitches_per_pa=3.70,
    rbi_per_season=46.0,
    runs_per_season=62.0,
)

#: Jesús Sánchez — LF, bats right, powerful left fielder with impressive
#: raw power and improving plate discipline; solid run producer.
_BJ_SANCHEZ = BatterStats(
    name="Jesús Sánchez",
    avg=0.248,
    obp=0.320,
    slg=0.448,
    hr_per_600_pa=22.0,
    sb_per_season=8.0,
    doubles_per_600_pa=26.0,
    games_played=140,
    power_rating=66.0,
    bats="R",
    pitches_per_pa=3.78,
    rbi_per_season=62.0,
    runs_per_season=58.0,
)

#: 2026 Blue Jays projected lineup (depth-chart position-1 starters).
#: Positions: C, 1B, 2B, 3B, SS, LF, CF, RF, DH.
BLUE_JAYS_LINEUP_2026: List[BatterStats] = [
    _BJ_KIRK,
    _BJ_GUERRERO,
    _BJ_CLEMENT,
    _BJ_OKAMOTO,
    _BJ_GIMENEZ,
    _BJ_SANCHEZ,
    _BJ_VARSHO,
    _BJ_BARGER,
    _BJ_SPRINGER,
]

# -- Starting rotation -------------------------------------------------------

#: Kevin Gausman — RHP, ace, forkball specialist with elite swing-and-miss
#: ability; leads Toronto's rotation with top-end command.
_BJ_GAUSMAN = PitcherStats(
    name="Kevin Gausman",
    era=3.05,
    k_per_9=11.2,
    innings_per_start=6.0,
    whip=1.08,
    arm_strength=74.0,
    throws="R",
    pitches_per_pa=3.90,
)

#: Dylan Cease — RHP, high-K sinker/slider arsenal; excellent strikeout
#: pitcher in the second slot of the rotation.
_BJ_CEASE = PitcherStats(
    name="Dylan Cease",
    era=3.50,
    k_per_9=10.5,
    innings_per_start=5.8,
    whip=1.20,
    arm_strength=78.0,
    throws="R",
    pitches_per_pa=4.08,
)

#: Shane Bieber — RHP, elite command and plus changeup; returning from
#: injury and expected to contribute as a mid-rotation starter.
_BJ_BIEBER = PitcherStats(
    name="Shane Bieber",
    era=3.40,
    k_per_9=9.8,
    innings_per_start=5.5,
    whip=1.14,
    arm_strength=66.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Trey Yesavage — RHP, promising young arm with a developing repertoire;
#: fourth-starter option with swing-and-miss potential.
_BJ_YESAVAGE = PitcherStats(
    name="Trey Yesavage",
    era=4.20,
    k_per_9=9.2,
    innings_per_start=5.0,
    whip=1.28,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.86,
)

#: Cody Ponce — RHP, back-of-rotation innings-eater.
_BJ_PONCE = PitcherStats(
    name="Cody Ponce",
    era=5.20,
    k_per_9=7.5,
    innings_per_start=4.8,
    whip=1.45,
    arm_strength=48.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: 2026 Blue Jays projected starting rotation (rotation order 1–5).
BLUE_JAYS_ROTATION_2026: List[PitcherStats] = [
    _BJ_GAUSMAN,
    _BJ_CEASE,
    _BJ_BIEBER,
    _BJ_YESAVAGE,
    _BJ_PONCE,
]

# -- Bullpen -----------------------------------------------------------------

#: Tyler Rogers — RHP, submarine delivery specialist; high ground-ball rate
#: and reliable middle-relief arm for the Blue Jays.
_BJ_T_ROGERS = PitcherStats(
    name="Tyler Rogers",
    era=3.60,
    k_per_9=7.8,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=52.0,
    throws="R",
    pitches_per_pa=3.68,
)

#: Yimi García — RHP, power arm with improving command; mid-leverage
#: setup option in the Blue Jays bullpen.
_BJ_GARCIA = PitcherStats(
    name="Yimi García",
    era=3.80,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.24,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.75,
)

#: Louis Varland — RHP, developing reliever with late-life fastball;
#: used in middle relief and long-relief situations.
_BJ_VARLAND = PitcherStats(
    name="Louis Varland",
    era=4.00,
    k_per_9=9.2,
    innings_per_start=1.0,
    whip=1.28,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Brendon Little — LHP, crafty left-hander with deceptive delivery;
#: specialist and left-handed setup option out of the bullpen.
_BJ_LITTLE = PitcherStats(
    name="Brendon Little",
    era=3.90,
    k_per_9=10.2,
    innings_per_start=1.0,
    whip=1.26,
    arm_strength=58.0,
    throws="L",
    pitches_per_pa=3.80,
)

#: Braydon Fisher — RHP, hard-throwing setup man with triple-digit
#: velocity; high-strikeout arm used in high-leverage situations.
_BJ_FISHER = PitcherStats(
    name="Braydon Fisher",
    era=3.70,
    k_per_9=11.0,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=66.0,
    throws="R",
    pitches_per_pa=3.76,
)

#: Jeff Hoffman — CL, RHP, elite closer with plus stuff and exceptional
#: command in the ninth; shutdown arm for the Blue Jays.
_BJ_HOFFMAN = PitcherStats(
    name="Jeff Hoffman",
    era=2.65,
    k_per_9=12.8,
    innings_per_start=1.0,
    whip=1.00,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: 2026 Blue Jays bullpen (setup + closer; closer is last entry).
BLUE_JAYS_BULLPEN_2026: List[PitcherStats] = [
    _BJ_T_ROGERS,
    _BJ_GARCIA,
    _BJ_VARLAND,
    _BJ_LITTLE,
    _BJ_FISHER,
    _BJ_HOFFMAN,
]


@dataclass
class BlueJaysRoster:
    """
    Bundle of Toronto Blue Jays projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Jeff Hoffman).

    Examples
    --------
    ::

        roster = BlueJaysRoster.default()
        print(roster.rotation[0].name)   # "Kevin Gausman"
        print(roster.lineup[1].name)     # "Vladimir Guerrero Jr."
        print(roster.bullpen[-1].name)   # "Jeff Hoffman"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "BlueJaysRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(BLUE_JAYS_LINEUP_2026),
            rotation=list(BLUE_JAYS_ROTATION_2026),
            bullpen=list(BLUE_JAYS_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Chicago White Sox — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Chicago White Sox starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB (and, for Murakami,
# NPB/international) performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Kyle Teel          1B – Munetaka Murakami  2B – Chase Meidroth
#   3B – Miguel Vargas       SS – Colson Montgomery  LF – Andrew Benintendi
#   CF – Luisangel Acuña    RF – Austin Hays         DH – Lenyn Sosa
#
# Note: Kyle Teel is listed as "O" (Out) on the official depth chart; his
# stats represent his projected output when healthy.  Edgar Quero is the
# expected day-to-day replacement.
#
# Usage:
#
#   from mlb_player_props import WhiteSoxRoster, UnabatedEdgeScreener
#   roster   = WhiteSoxRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the opening-day starter
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen every batter
#   for batter in roster.lineup:
#       for edge in screener.screen_batter(batter):
#           print(edge)
#
#   # Screen the closer
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Kyle Teel — C, bats right (listed "Out"; projected healthy-season stats).
_WSX_TEEL = BatterStats(
    name="Kyle Teel",
    avg=0.258,
    obp=0.328,
    slg=0.390,
    hr_per_600_pa=10.0,
    sb_per_season=4.0,
    doubles_per_600_pa=26.0,
    games_played=100,
    power_rating=44.0,
    bats="R",
    pitches_per_pa=3.90,
    rbi_per_season=42.0,
    runs_per_season=40.0,
)

#: Munetaka Murakami — 1B, bats right, NPB power/contact star (Tokyo Yakult).
_WSX_MURAKAMI = BatterStats(
    name="Munetaka Murakami",
    avg=0.268,
    obp=0.342,
    slg=0.510,
    hr_per_600_pa=35.0,
    sb_per_season=2.0,
    doubles_per_600_pa=32.0,
    games_played=155,
    power_rating=85.0,
    bats="R",
    pitches_per_pa=3.85,
    rbi_per_season=95.0,
    runs_per_season=72.0,
)

#: Chase Meidroth — 2B, bats left, patient contact approach.
_WSX_MEIDROTH = BatterStats(
    name="Chase Meidroth",
    avg=0.252,
    obp=0.350,
    slg=0.368,
    hr_per_600_pa=6.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=32.0,
    bats="L",
    pitches_per_pa=4.05,
    rbi_per_season=38.0,
    runs_per_season=58.0,
)

#: Miguel Vargas — 3B, bats right, versatile bat with developing power.
_WSX_VARGAS = BatterStats(
    name="Miguel Vargas",
    avg=0.248,
    obp=0.315,
    slg=0.400,
    hr_per_600_pa=15.0,
    sb_per_season=8.0,
    doubles_per_600_pa=32.0,
    games_played=142,
    power_rating=52.0,
    bats="R",
    pitches_per_pa=3.80,
    rbi_per_season=52.0,
    runs_per_season=55.0,
)

#: Colson Montgomery — SS, bats left, top-10 prospect, defence-first with upside.
_WSX_MONTGOMERY = BatterStats(
    name="Colson Montgomery",
    avg=0.240,
    obp=0.322,
    slg=0.382,
    hr_per_600_pa=12.0,
    sb_per_season=10.0,
    doubles_per_600_pa=28.0,
    games_played=148,
    power_rating=45.0,
    bats="L",
    pitches_per_pa=3.95,
    rbi_per_season=44.0,
    runs_per_season=56.0,
)

#: Andrew Benintendi — LF, bats left, veteran contact/OBP bat.
_WSX_BENINTENDI = BatterStats(
    name="Andrew Benintendi",
    avg=0.272,
    obp=0.348,
    slg=0.418,
    hr_per_600_pa=14.0,
    sb_per_season=10.0,
    doubles_per_600_pa=34.0,
    games_played=140,
    power_rating=50.0,
    bats="L",
    pitches_per_pa=3.75,
    rbi_per_season=60.0,
    runs_per_season=68.0,
)

#: Luisangel Acuña — CF, bats right, elite speed and improving contact.
_WSX_ACUNA = BatterStats(
    name="Luisangel Acuña",
    avg=0.248,
    obp=0.308,
    slg=0.365,
    hr_per_600_pa=8.0,
    sb_per_season=30.0,
    doubles_per_600_pa=26.0,
    games_played=148,
    power_rating=35.0,
    bats="R",
    pitches_per_pa=3.60,
    rbi_per_season=42.0,
    runs_per_season=72.0,
)

#: Austin Hays — RF, bats right, solid power-contact blend.
_WSX_HAYS = BatterStats(
    name="Austin Hays",
    avg=0.252,
    obp=0.308,
    slg=0.420,
    hr_per_600_pa=18.0,
    sb_per_season=6.0,
    doubles_per_600_pa=30.0,
    games_played=138,
    power_rating=58.0,
    bats="R",
    pitches_per_pa=3.62,
    rbi_per_season=58.0,
    runs_per_season=54.0,
)

#: Lenyn Sosa — DH, bats right, developing power, multi-position depth.
_WSX_SOSA = BatterStats(
    name="Lenyn Sosa",
    avg=0.245,
    obp=0.295,
    slg=0.405,
    hr_per_600_pa=17.0,
    sb_per_season=5.0,
    doubles_per_600_pa=28.0,
    games_played=138,
    power_rating=55.0,
    bats="R",
    pitches_per_pa=3.55,
    rbi_per_season=55.0,
    runs_per_season=48.0,
)

#: 2026 White Sox projected starting lineup (depth-chart position-1 starters).
WHITE_SOX_LINEUP_2026: List[BatterStats] = [
    _WSX_TEEL,
    _WSX_MURAKAMI,
    _WSX_MEIDROTH,
    _WSX_VARGAS,
    _WSX_MONTGOMERY,
    _WSX_BENINTENDI,
    _WSX_ACUNA,
    _WSX_HAYS,
    _WSX_SOSA,
]

# -- Starting rotation -------------------------------------------------------

#: Shane Smith — RHP, projected opening-day starter.
_WSX_S_SMITH = PitcherStats(
    name="Shane Smith",
    era=4.80,
    k_per_9=8.5,
    innings_per_start=5.0,
    whip=1.40,
    arm_strength=52.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: Sean Burke — RHP, power arm, command still developing.
_WSX_BURKE = PitcherStats(
    name="Sean Burke",
    era=5.20,
    k_per_9=8.0,
    innings_per_start=4.8,
    whip=1.45,
    arm_strength=56.0,
    throws="R",
    pitches_per_pa=3.92,
)

#: Anthony Kay — LHP, solid mid-rotation option.
_WSX_KAY = PitcherStats(
    name="Anthony Kay",
    era=4.50,
    k_per_9=8.5,
    innings_per_start=5.2,
    whip=1.35,
    arm_strength=50.0,
    throws="L",
    pitches_per_pa=3.80,
)

#: Davis Martin — RHP, contact-suppression back-of-rotation arm.
_WSX_D_MARTIN = PitcherStats(
    name="Davis Martin",
    era=5.00,
    k_per_9=7.8,
    innings_per_start=4.9,
    whip=1.45,
    arm_strength=46.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: Erick Fedde — RHP, veteran innings-eater, best ERA in the rotation.
_WSX_FEDDE = PitcherStats(
    name="Erick Fedde",
    era=4.20,
    k_per_9=8.2,
    innings_per_start=5.5,
    whip=1.30,
    arm_strength=55.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: 2026 White Sox projected starting rotation (rotation-turn order 1–5).
WHITE_SOX_ROTATION_2026: List[PitcherStats] = [
    _WSX_S_SMITH,
    _WSX_BURKE,
    _WSX_KAY,
    _WSX_D_MARTIN,
    _WSX_FEDDE,
]

# -- Bullpen -----------------------------------------------------------------

#: Jordan Leasure — RHP reliever, high-K setup arm.
_WSX_LEASURE = PitcherStats(
    name="Jordan Leasure",
    era=3.80,
    k_per_9=10.5,
    innings_per_start=1.0,
    whip=1.15,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.95,
)

#: Grant Taylor — RHP reliever.
_WSX_G_TAYLOR = PitcherStats(
    name="Grant Taylor",
    era=4.20,
    k_per_9=9.0,
    innings_per_start=1.0,
    whip=1.25,
    arm_strength=52.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Sean Newcomb — LHP reliever, high walk-rate but strikeout upside.
_WSX_NEWCOMB = PitcherStats(
    name="Sean Newcomb",
    era=4.50,
    k_per_9=8.8,
    innings_per_start=1.0,
    whip=1.38,
    arm_strength=48.0,
    throws="L",
    pitches_per_pa=3.90,
)

#: Chris Murphy — LHP reliever, left-on-left specialist.
_WSX_C_MURPHY = PitcherStats(
    name="Chris Murphy",
    era=4.20,
    k_per_9=9.2,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=50.0,
    throws="L",
    pitches_per_pa=3.78,
)

#: Jordan Hicks — RHP reliever, elite velocity (triple-digit fastball).
_WSX_J_HICKS = PitcherStats(
    name="Jordan Hicks",
    era=3.50,
    k_per_9=10.8,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=80.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Seranthony Dominguez — CL, RHP, top-tier closer.
_WSX_DOMINGUEZ = PitcherStats(
    name="Seranthony Dominguez",
    era=3.20,
    k_per_9=11.0,
    innings_per_start=1.0,
    whip=1.10,
    arm_strength=75.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: 2026 White Sox bullpen (setup + closer; closer is last entry).
WHITE_SOX_BULLPEN_2026: List[PitcherStats] = [
    _WSX_LEASURE,
    _WSX_G_TAYLOR,
    _WSX_NEWCOMB,
    _WSX_C_MURPHY,
    _WSX_J_HICKS,
    _WSX_DOMINGUEZ,
]


@dataclass
class WhiteSoxRoster:
    """
    Bundle of Chicago White Sox projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Seranthony Dominguez).

    Examples
    --------
    ::

        roster = WhiteSoxRoster.default()
        print(roster.rotation[0].name)   # "Shane Smith"
        print(roster.lineup[1].name)     # "Munetaka Murakami"
        print(roster.bullpen[-1].name)   # "Seranthony Dominguez"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "WhiteSoxRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(WHITE_SOX_LINEUP_2026),
            rotation=list(WHITE_SOX_ROTATION_2026),
            bullpen=list(WHITE_SOX_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Cleveland Guardians — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Cleveland Guardians starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Bo Naylor          1B – Kyle Manzardo      2B – Brayan Rocchio
#   3B – Jose Ramirez        SS – Gabriel Arias       LF – Steven Kwan
#   CF – Chase DeLauter     RF – CJ Kayfus            DH – Rhys Hoskins
#
# Note: Hunter Gaddis is listed as "O" (Out) on the official depth chart.
# His stats represent projected output when healthy.
#
# Usage:
#
#   from mlb_player_props import GuardiansRoster, UnabatedEdgeScreener
#   roster   = GuardiansRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Tanner Bibee)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Jose Ramirez for batter props
#   for edge in screener.screen_batter(roster.lineup[3]):
#       print(edge)
#
#   # Screen the closer (Cade Smith)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Bo Naylor — C, switch hitter, improving power and patience.
_CG_NAYLOR = BatterStats(
    name="Bo Naylor",
    avg=0.238,
    obp=0.322,
    slg=0.418,
    hr_per_600_pa=20.0,
    sb_per_season=8.0,
    doubles_per_600_pa=24.0,
    games_played=138,
    power_rating=62.0,
    bats="S",
    pitches_per_pa=3.95,
    rbi_per_season=55.0,
    runs_per_season=50.0,
)

#: Kyle Manzardo — 1B, bats left, developing power prospect.
_CG_MANZARDO = BatterStats(
    name="Kyle Manzardo",
    avg=0.235,
    obp=0.318,
    slg=0.430,
    hr_per_600_pa=22.0,
    sb_per_season=3.0,
    doubles_per_600_pa=26.0,
    games_played=148,
    power_rating=68.0,
    bats="L",
    pitches_per_pa=3.88,
    rbi_per_season=60.0,
    runs_per_season=52.0,
)

#: Brayan Rocchio — 2B, switch hitter, speed and contact approach.
_CG_ROCCHIO = BatterStats(
    name="Brayan Rocchio",
    avg=0.262,
    obp=0.308,
    slg=0.385,
    hr_per_600_pa=9.0,
    sb_per_season=18.0,
    doubles_per_600_pa=28.0,
    games_played=150,
    power_rating=30.0,
    bats="S",
    pitches_per_pa=3.65,
    rbi_per_season=42.0,
    runs_per_season=62.0,
)

#: Jose Ramirez — 3B, switch hitter, perennial All-Star, elite power/speed.
_CG_RAMIREZ = BatterStats(
    name="Jose Ramirez",
    avg=0.278,
    obp=0.352,
    slg=0.505,
    hr_per_600_pa=30.0,
    sb_per_season=24.0,
    doubles_per_600_pa=36.0,
    games_played=155,
    power_rating=88.0,
    bats="S",
    pitches_per_pa=3.78,
    rbi_per_season=100.0,
    runs_per_season=90.0,
)

#: Gabriel Arias — SS, bats right, defensive first with developing bat.
_CG_ARIAS = BatterStats(
    name="Gabriel Arias",
    avg=0.235,
    obp=0.290,
    slg=0.370,
    hr_per_600_pa=12.0,
    sb_per_season=6.0,
    doubles_per_600_pa=24.0,
    games_played=140,
    power_rating=40.0,
    bats="R",
    pitches_per_pa=3.55,
    rbi_per_season=40.0,
    runs_per_season=42.0,
)

#: Steven Kwan — LF, bats left, elite contact and on-base skills.
_CG_KWAN = BatterStats(
    name="Steven Kwan",
    avg=0.282,
    obp=0.365,
    slg=0.415,
    hr_per_600_pa=8.0,
    sb_per_season=15.0,
    doubles_per_600_pa=30.0,
    games_played=152,
    power_rating=38.0,
    bats="L",
    pitches_per_pa=4.05,
    rbi_per_season=55.0,
    runs_per_season=72.0,
)

#: Chase DeLauter — CF, bats left, top prospect with speed and developing power.
_CG_DELAUTER = BatterStats(
    name="Chase DeLauter",
    avg=0.248,
    obp=0.325,
    slg=0.415,
    hr_per_600_pa=15.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=142,
    power_rating=50.0,
    bats="L",
    pitches_per_pa=3.82,
    rbi_per_season=48.0,
    runs_per_season=58.0,
)

#: CJ Kayfus — RF, bats left, contact-first approach with gap power.
_CG_KAYFUS = BatterStats(
    name="CJ Kayfus",
    avg=0.262,
    obp=0.330,
    slg=0.390,
    hr_per_600_pa=9.0,
    sb_per_season=14.0,
    doubles_per_600_pa=26.0,
    games_played=148,
    power_rating=35.0,
    bats="L",
    pitches_per_pa=3.72,
    rbi_per_season=44.0,
    runs_per_season=56.0,
)

#: Rhys Hoskins — DH, bats right, veteran power bat.
_CG_HOSKINS = BatterStats(
    name="Rhys Hoskins",
    avg=0.238,
    obp=0.332,
    slg=0.455,
    hr_per_600_pa=28.0,
    sb_per_season=2.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=78.0,
    bats="R",
    pitches_per_pa=3.98,
    rbi_per_season=82.0,
    runs_per_season=62.0,
)

#: 2026 Guardians projected starting lineup (depth-chart position-1 starters).
GUARDIANS_LINEUP_2026: List[BatterStats] = [
    _CG_NAYLOR,
    _CG_MANZARDO,
    _CG_ROCCHIO,
    _CG_RAMIREZ,
    _CG_ARIAS,
    _CG_KWAN,
    _CG_DELAUTER,
    _CG_KAYFUS,
    _CG_HOSKINS,
]

# -- Starting rotation -------------------------------------------------------

#: Tanner Bibee — RHP, ace, high-K sinker/slider arsenal.
_CG_BIBEE = PitcherStats(
    name="Tanner Bibee",
    era=3.50,
    k_per_9=10.2,
    innings_per_start=6.0,
    whip=1.15,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.98,
)

#: Gavin Williams — RHP, power arm, high strikeout potential.
_CG_WILLIAMS = PitcherStats(
    name="Gavin Williams",
    era=4.10,
    k_per_9=10.5,
    innings_per_start=5.5,
    whip=1.25,
    arm_strength=74.0,
    throws="R",
    pitches_per_pa=4.05,
)

#: Logan Allen — LHP, solid mid-rotation option with plus swing-and-miss.
_CG_ALLEN = PitcherStats(
    name="Logan Allen",
    era=3.85,
    k_per_9=9.2,
    innings_per_start=5.8,
    whip=1.22,
    arm_strength=52.0,
    throws="L",
    pitches_per_pa=3.90,
)

#: Slade Cecconi — RHP, developing arm, improving command.
_CG_CECCONI = PitcherStats(
    name="Slade Cecconi",
    era=4.60,
    k_per_9=8.5,
    innings_per_start=5.0,
    whip=1.38,
    arm_strength=56.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Joey Cantillo — LHP, back-of-rotation innings-eater.
_CG_CANTILLO = PitcherStats(
    name="Joey Cantillo",
    era=4.80,
    k_per_9=8.0,
    innings_per_start=4.8,
    whip=1.40,
    arm_strength=48.0,
    throws="L",
    pitches_per_pa=3.78,
)

#: 2026 Guardians projected starting rotation (rotation-turn order 1–5).
GUARDIANS_ROTATION_2026: List[PitcherStats] = [
    _CG_BIBEE,
    _CG_WILLIAMS,
    _CG_ALLEN,
    _CG_CECCONI,
    _CG_CANTILLO,
]

# -- Bullpen -----------------------------------------------------------------

#: Hunter Gaddis — RHP reliever, high-K setup arm (listed "Out").
_CG_GADDIS = PitcherStats(
    name="Hunter Gaddis",
    era=4.00,
    k_per_9=10.0,
    innings_per_start=1.0,
    whip=1.25,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.92,
)

#: Shawn Armstrong — RHP, veteran middle reliever.
_CG_ARMSTRONG = PitcherStats(
    name="Shawn Armstrong",
    era=4.20,
    k_per_9=8.8,
    innings_per_start=1.0,
    whip=1.28,
    arm_strength=52.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Erik Sabrowski — RHP, high-K setup arm.
_CG_SABROWSKI = PitcherStats(
    name="Erik Sabrowski",
    era=4.00,
    k_per_9=9.5,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Matt Festa — RHP, dependable middle relief.
_CG_FESTA = PitcherStats(
    name="Matt Festa",
    era=3.80,
    k_per_9=9.2,
    innings_per_start=1.0,
    whip=1.18,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Tim Herrin — LHP, left-on-left specialist.
_CG_HERRIN = PitcherStats(
    name="Tim Herrin",
    era=3.60,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.15,
    arm_strength=50.0,
    throws="L",
    pitches_per_pa=3.88,
)

#: Cade Smith — CL, RHP, top-tier closer with elite strikeout rate.
_CG_C_SMITH = PitcherStats(
    name="Cade Smith",
    era=3.20,
    k_per_9=11.0,
    innings_per_start=1.0,
    whip=1.05,
    arm_strength=72.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: 2026 Guardians bullpen (setup + closer; closer is last entry).
GUARDIANS_BULLPEN_2026: List[PitcherStats] = [
    _CG_GADDIS,
    _CG_ARMSTRONG,
    _CG_SABROWSKI,
    _CG_FESTA,
    _CG_HERRIN,
    _CG_C_SMITH,
]


@dataclass
class GuardiansRoster:
    """
    Bundle of Cleveland Guardians projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Cade Smith).

    Examples
    --------
    ::

        roster = GuardiansRoster.default()
        print(roster.rotation[0].name)   # "Tanner Bibee"
        print(roster.lineup[3].name)     # "Jose Ramirez"
        print(roster.bullpen[-1].name)   # "Cade Smith"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "GuardiansRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(GUARDIANS_LINEUP_2026),
            rotation=list(GUARDIANS_ROTATION_2026),
            bullpen=list(GUARDIANS_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Detroit Tigers — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Detroit Tigers starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Dillon Dingler       1B – Spencer Torkelson  2B – Gleyber Torres
#   3B – Colt Keith            SS – Kevin McGonigle    LF – Riley Greene
#   CF – Parker Meadows       RF – Wenceel Perez       DH – Kerry Carpenter
#
# Note: Jake Rogers is listed as Day-to-Day (DD) as the C backup.
#
# Usage:
#
#   from mlb_player_props import TigersRoster, UnabatedEdgeScreener
#   roster   = TigersRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Tarik Skubal)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Riley Greene for batter props
#   for edge in screener.screen_batter(roster.lineup[5]):
#       print(edge)
#
#   # Screen the closer (Kenley Jansen)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Dillon Dingler — C, bats right, developing power with improving contact.
_DET_DINGLER = BatterStats(
    name="Dillon Dingler",
    avg=0.245,
    obp=0.318,
    slg=0.420,
    hr_per_600_pa=18.0,
    sb_per_season=5.0,
    doubles_per_600_pa=26.0,
    games_played=125,
    power_rating=58.0,
    bats="R",
    pitches_per_pa=3.88,
    rbi_per_season=52.0,
    runs_per_season=44.0,
)

#: Spencer Torkelson — 1B, bats right, elite power prospect.
_DET_TORKELSON = BatterStats(
    name="Spencer Torkelson",
    avg=0.245,
    obp=0.332,
    slg=0.460,
    hr_per_600_pa=28.0,
    sb_per_season=2.0,
    doubles_per_600_pa=28.0,
    games_played=148,
    power_rating=80.0,
    bats="R",
    pitches_per_pa=3.98,
    rbi_per_season=80.0,
    runs_per_season=62.0,
)

#: Gleyber Torres — 2B, switch hitter, contact bat with gap power.
_DET_TORRES = BatterStats(
    name="Gleyber Torres",
    avg=0.258,
    obp=0.330,
    slg=0.420,
    hr_per_600_pa=18.0,
    sb_per_season=8.0,
    doubles_per_600_pa=28.0,
    games_played=148,
    power_rating=56.0,
    bats="S",
    pitches_per_pa=3.82,
    rbi_per_season=62.0,
    runs_per_season=66.0,
)

#: Colt Keith — 3B, bats left, promising bat with solid contact skills.
_DET_KEITH = BatterStats(
    name="Colt Keith",
    avg=0.262,
    obp=0.328,
    slg=0.415,
    hr_per_600_pa=14.0,
    sb_per_season=8.0,
    doubles_per_600_pa=30.0,
    games_played=148,
    power_rating=50.0,
    bats="L",
    pitches_per_pa=3.78,
    rbi_per_season=58.0,
    runs_per_season=62.0,
)

#: Kevin McGonigle — SS, bats right, young defensive-first shortstop.
_DET_MCGONIGLE = BatterStats(
    name="Kevin McGonigle",
    avg=0.240,
    obp=0.302,
    slg=0.365,
    hr_per_600_pa=9.0,
    sb_per_season=10.0,
    doubles_per_600_pa=24.0,
    games_played=140,
    power_rating=34.0,
    bats="R",
    pitches_per_pa=3.65,
    rbi_per_season=38.0,
    runs_per_season=48.0,
)

#: Riley Greene — LF, bats left, high-ceiling bat with excellent contact.
_DET_GREENE = BatterStats(
    name="Riley Greene",
    avg=0.278,
    obp=0.352,
    slg=0.460,
    hr_per_600_pa=22.0,
    sb_per_season=10.0,
    doubles_per_600_pa=32.0,
    games_played=148,
    power_rating=70.0,
    bats="L",
    pitches_per_pa=3.88,
    rbi_per_season=72.0,
    runs_per_season=75.0,
)

#: Parker Meadows — CF, bats left, elite speed with developing power.
_DET_MEADOWS = BatterStats(
    name="Parker Meadows",
    avg=0.248,
    obp=0.310,
    slg=0.415,
    hr_per_600_pa=16.0,
    sb_per_season=20.0,
    doubles_per_600_pa=28.0,
    games_played=148,
    power_rating=52.0,
    bats="L",
    pitches_per_pa=3.72,
    rbi_per_season=55.0,
    runs_per_season=65.0,
)

#: Wenceel Perez — RF, switch hitter, contact-first approach with speed.
_DET_PEREZ = BatterStats(
    name="Wenceel Perez",
    avg=0.265,
    obp=0.322,
    slg=0.380,
    hr_per_600_pa=8.0,
    sb_per_season=18.0,
    doubles_per_600_pa=26.0,
    games_played=148,
    power_rating=30.0,
    bats="S",
    pitches_per_pa=3.62,
    rbi_per_season=40.0,
    runs_per_season=58.0,
)

#: Kerry Carpenter — DH, bats left, powerful left-handed bat with pull approach.
_DET_CARPENTER = BatterStats(
    name="Kerry Carpenter",
    avg=0.258,
    obp=0.322,
    slg=0.465,
    hr_per_600_pa=26.0,
    sb_per_season=2.0,
    doubles_per_600_pa=26.0,
    games_played=138,
    power_rating=74.0,
    bats="L",
    pitches_per_pa=3.78,
    rbi_per_season=72.0,
    runs_per_season=55.0,
)

#: 2026 Tigers projected starting lineup (depth-chart position-1 starters).
TIGERS_LINEUP_2026: List[BatterStats] = [
    _DET_DINGLER,
    _DET_TORKELSON,
    _DET_TORRES,
    _DET_KEITH,
    _DET_MCGONIGLE,
    _DET_GREENE,
    _DET_MEADOWS,
    _DET_PEREZ,
    _DET_CARPENTER,
]

# -- Starting rotation -------------------------------------------------------

#: Tarik Skubal — LHP, Cy Young-calibre ace with elite swing-and-miss stuff.
_DET_SKUBAL = PitcherStats(
    name="Tarik Skubal",
    era=2.80,
    k_per_9=11.5,
    innings_per_start=6.5,
    whip=1.00,
    arm_strength=72.0,
    throws="L",
    pitches_per_pa=3.92,
)

#: Framber Valdez — LHP, elite groundball sinker/curveball combination.
_DET_VALDEZ = PitcherStats(
    name="Framber Valdez",
    era=3.20,
    k_per_9=9.8,
    innings_per_start=6.5,
    whip=1.15,
    arm_strength=66.0,
    throws="L",
    pitches_per_pa=3.85,
)

#: Jack Flaherty — RHP, veteran mid-rotation arm with swing-and-miss capability.
_DET_FLAHERTY = PitcherStats(
    name="Jack Flaherty",
    era=3.80,
    k_per_9=9.5,
    innings_per_start=5.8,
    whip=1.25,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.95,
)

#: Justin Verlander — RHP, future Hall-of-Famer, durability questions at age 43.
_DET_VERLANDER = PitcherStats(
    name="Justin Verlander",
    era=4.00,
    k_per_9=8.8,
    innings_per_start=5.5,
    whip=1.25,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Casey Mize — RHP, back-end starter rebuilding after Tommy John surgery.
_DET_MIZE = PitcherStats(
    name="Casey Mize",
    era=4.60,
    k_per_9=8.2,
    innings_per_start=5.0,
    whip=1.35,
    arm_strength=54.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: 2026 Tigers projected starting rotation (rotation-turn order 1–5).
TIGERS_ROTATION_2026: List[PitcherStats] = [
    _DET_SKUBAL,
    _DET_VALDEZ,
    _DET_FLAHERTY,
    _DET_VERLANDER,
    _DET_MIZE,
]

# -- Bullpen -----------------------------------------------------------------

#: Will Vest — RHP, high-leverage setup arm.
_DET_VEST = PitcherStats(
    name="Will Vest",
    era=3.80,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.18,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Kyle Finnegan — RHP, late-inning reliever with high strikeout rate.
_DET_FINNEGAN = PitcherStats(
    name="Kyle Finnegan",
    era=3.60,
    k_per_9=10.2,
    innings_per_start=1.0,
    whip=1.15,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: Tyler Holton — LHP, southpaw specialist and multi-inning option.
_DET_HOLTON = PitcherStats(
    name="Tyler Holton",
    era=3.50,
    k_per_9=9.5,
    innings_per_start=1.0,
    whip=1.12,
    arm_strength=54.0,
    throws="L",
    pitches_per_pa=3.82,
)

#: Brant Hurter — LHP, lefty reliever with solid strikeout capability.
_DET_HURTER = PitcherStats(
    name="Brant Hurter",
    era=3.80,
    k_per_9=9.2,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=50.0,
    throws="L",
    pitches_per_pa=3.80,
)

#: Brenan Hanifee — RHP, versatile multi-inning reliever.
_DET_HANIFEE = PitcherStats(
    name="Brenan Hanifee",
    era=4.00,
    k_per_9=8.5,
    innings_per_start=1.0,
    whip=1.25,
    arm_strength=52.0,
    throws="R",
    pitches_per_pa=3.75,
)

#: Kenley Jansen — CL, RHP, elite closer with top-tier save history.
_DET_JANSEN = PitcherStats(
    name="Kenley Jansen",
    era=3.00,
    k_per_9=11.2,
    innings_per_start=1.0,
    whip=1.05,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: 2026 Tigers bullpen (setup + closer; closer is last entry).
TIGERS_BULLPEN_2026: List[PitcherStats] = [
    _DET_VEST,
    _DET_FINNEGAN,
    _DET_HOLTON,
    _DET_HURTER,
    _DET_HANIFEE,
    _DET_JANSEN,
]


@dataclass
class TigersRoster:
    """
    Bundle of Detroit Tigers projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Kenley Jansen).

    Examples
    --------
    ::

        roster = TigersRoster.default()
        print(roster.rotation[0].name)   # "Tarik Skubal"
        print(roster.lineup[5].name)     # "Riley Greene"
        print(roster.bullpen[-1].name)   # "Kenley Jansen"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "TigersRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(TIGERS_LINEUP_2026),
            rotation=list(TIGERS_ROTATION_2026),
            bullpen=list(TIGERS_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Kansas City Royals — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Kansas City Royals starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Salvador Perez        1B – Vinnie Pasquantino  2B – Jonathan India
#   3B – Maikel Garcia          SS – Bobby Witt Jr.      LF – Isaac Collins
#   CF – Kyle Isbel             RF – Jac Caglianone      DH – Carter Jensen
#
# Usage:
#
#   from mlb_player_props import RoyalsRoster, UnabatedEdgeScreener
#   roster   = RoyalsRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Cole Ragans)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Bobby Witt Jr. for batter props
#   for edge in screener.screen_batter(roster.lineup[4]):
#       print(edge)
#
#   # Screen the closer (Carlos Estevez)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Salvador Perez — C, bats right, elite power for a catcher with veteran production.
_KC_PEREZ = BatterStats(
    name="Salvador Perez",
    avg=0.260,
    obp=0.310,
    slg=0.475,
    hr_per_600_pa=28.0,
    sb_per_season=2.0,
    doubles_per_600_pa=24.0,
    games_played=140,
    power_rating=76.0,
    bats="R",
    pitches_per_pa=3.55,
    rbi_per_season=80.0,
    runs_per_season=52.0,
)

#: Vinnie Pasquantino — 1B, bats left, high on-base skills with solid power.
_KC_PASQUANTINO = BatterStats(
    name="Vinnie Pasquantino",
    avg=0.268,
    obp=0.350,
    slg=0.460,
    hr_per_600_pa=22.0,
    sb_per_season=2.0,
    doubles_per_600_pa=30.0,
    games_played=145,
    power_rating=66.0,
    bats="L",
    pitches_per_pa=3.92,
    rbi_per_season=74.0,
    runs_per_season=62.0,
)

#: Jonathan India — 2B, bats right, patient approach with above-average OBP.
_KC_INDIA = BatterStats(
    name="Jonathan India",
    avg=0.252,
    obp=0.345,
    slg=0.410,
    hr_per_600_pa=16.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=50.0,
    bats="R",
    pitches_per_pa=4.05,
    rbi_per_season=54.0,
    runs_per_season=70.0,
)

#: Maikel Garcia — 3B, switch hitter, contact-first bat with gap power and speed.
_KC_GARCIA = BatterStats(
    name="Maikel Garcia",
    avg=0.262,
    obp=0.320,
    slg=0.385,
    hr_per_600_pa=8.0,
    sb_per_season=22.0,
    doubles_per_600_pa=26.0,
    games_played=148,
    power_rating=32.0,
    bats="S",
    pitches_per_pa=3.62,
    rbi_per_season=44.0,
    runs_per_season=68.0,
)

#: Bobby Witt Jr. — SS, bats right, franchise cornerstone with elite tools across
#: the board — power, speed, contact, and defence.
_KC_WITT = BatterStats(
    name="Bobby Witt Jr.",
    avg=0.302,
    obp=0.358,
    slg=0.540,
    hr_per_600_pa=32.0,
    sb_per_season=32.0,
    doubles_per_600_pa=34.0,
    games_played=155,
    power_rating=88.0,
    bats="R",
    pitches_per_pa=3.72,
    rbi_per_season=96.0,
    runs_per_season=98.0,
)

#: Isaac Collins — LF, bats left, speedy table-setter with developing plate skills.
_KC_COLLINS = BatterStats(
    name="Isaac Collins",
    avg=0.255,
    obp=0.315,
    slg=0.360,
    hr_per_600_pa=6.0,
    sb_per_season=24.0,
    doubles_per_600_pa=22.0,
    games_played=135,
    power_rating=24.0,
    bats="L",
    pitches_per_pa=3.65,
    rbi_per_season=32.0,
    runs_per_season=58.0,
)

#: Kyle Isbel — CF, bats left, solid defence with improving plate approach.
_KC_ISBEL = BatterStats(
    name="Kyle Isbel",
    avg=0.248,
    obp=0.312,
    slg=0.380,
    hr_per_600_pa=10.0,
    sb_per_season=18.0,
    doubles_per_600_pa=24.0,
    games_played=138,
    power_rating=36.0,
    bats="L",
    pitches_per_pa=3.70,
    rbi_per_season=40.0,
    runs_per_season=52.0,
)

#: Jac Caglianone — RF, bats left, big-bodied slugger with massive raw power.
_KC_CAGLIANONE = BatterStats(
    name="Jac Caglianone",
    avg=0.248,
    obp=0.318,
    slg=0.490,
    hr_per_600_pa=30.0,
    sb_per_season=4.0,
    doubles_per_600_pa=24.0,
    games_played=140,
    power_rating=82.0,
    bats="L",
    pitches_per_pa=3.82,
    rbi_per_season=78.0,
    runs_per_season=56.0,
)

#: Carter Jensen — DH, bats right, young catcher-convert with developing power bat.
_KC_JENSEN = BatterStats(
    name="Carter Jensen",
    avg=0.242,
    obp=0.308,
    slg=0.390,
    hr_per_600_pa=12.0,
    sb_per_season=6.0,
    doubles_per_600_pa=22.0,
    games_played=128,
    power_rating=42.0,
    bats="R",
    pitches_per_pa=3.72,
    rbi_per_season=44.0,
    runs_per_season=40.0,
)

#: 2026 Royals projected starting lineup (depth-chart position-1 starters).
ROYALS_LINEUP_2026: List[BatterStats] = [
    _KC_PEREZ,
    _KC_PASQUANTINO,
    _KC_INDIA,
    _KC_GARCIA,
    _KC_WITT,
    _KC_COLLINS,
    _KC_ISBEL,
    _KC_CAGLIANONE,
    _KC_JENSEN,
]

# -- Starting rotation -------------------------------------------------------

#: Cole Ragans — LHP, electric ace with swing-and-miss slider and elite K rate.
_KC_RAGANS = PitcherStats(
    name="Cole Ragans",
    era=3.00,
    k_per_9=11.8,
    innings_per_start=6.2,
    whip=1.08,
    arm_strength=68.0,
    throws="L",
    pitches_per_pa=3.95,
)

#: Michael Wacha — RHP, crafty veteran with strong command and changeup.
_KC_WACHA = PitcherStats(
    name="Michael Wacha",
    era=3.80,
    k_per_9=8.8,
    innings_per_start=5.8,
    whip=1.22,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Seth Lugo — RHP, durable mid-rotation starter with advanced pitch mix.
_KC_LUGO = PitcherStats(
    name="Seth Lugo",
    era=3.70,
    k_per_9=8.5,
    innings_per_start=6.0,
    whip=1.18,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Kris Bubic — LHP, lefty finesse pitcher relying on movement over velocity.
_KC_BUBIC = PitcherStats(
    name="Kris Bubic",
    era=4.30,
    k_per_9=8.0,
    innings_per_start=5.5,
    whip=1.30,
    arm_strength=50.0,
    throws="L",
    pitches_per_pa=3.80,
)

#: Noah Cameron — RHP, back-end innings eater with solid groundball profile.
_KC_CAMERON = PitcherStats(
    name="Noah Cameron",
    era=4.70,
    k_per_9=7.5,
    innings_per_start=5.0,
    whip=1.38,
    arm_strength=48.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: 2026 Royals projected starting rotation (rotation-turn order 1–5).
ROYALS_ROTATION_2026: List[PitcherStats] = [
    _KC_RAGANS,
    _KC_WACHA,
    _KC_LUGO,
    _KC_BUBIC,
    _KC_CAMERON,
]

# -- Bullpen -----------------------------------------------------------------

#: Lucas Erceg — RHP, power reliever with triple-digit heat.
_KC_ERCEG = PitcherStats(
    name="Lucas Erceg",
    era=3.20,
    k_per_9=11.5,
    innings_per_start=1.0,
    whip=1.10,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: Matt Strahm — LHP, versatile multi-inning lefty with swing-and-miss stuff.
_KC_STRAHM = PitcherStats(
    name="Matt Strahm",
    era=3.50,
    k_per_9=10.8,
    innings_per_start=1.0,
    whip=1.12,
    arm_strength=58.0,
    throws="L",
    pitches_per_pa=3.88,
)

#: John Schreiber — RHP, late-inning arm with quality breaking ball.
_KC_SCHREIBER = PitcherStats(
    name="John Schreiber",
    era=3.60,
    k_per_9=10.2,
    innings_per_start=1.0,
    whip=1.15,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Nick Mears — RHP, hard-throwing setup man.
_KC_MEARS = PitcherStats(
    name="Nick Mears",
    era=3.90,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Daniel Lynch IV — LHP, lefty specialist and multi-inning option.
_KC_LYNCH = PitcherStats(
    name="Daniel Lynch IV",
    era=4.10,
    k_per_9=9.0,
    innings_per_start=1.0,
    whip=1.28,
    arm_strength=52.0,
    throws="L",
    pitches_per_pa=3.80,
)

#: Carlos Estevez — CL, RHP, elite closer with overpowering splitter.
_KC_ESTEVEZ = PitcherStats(
    name="Carlos Estevez",
    era=2.90,
    k_per_9=12.0,
    innings_per_start=1.0,
    whip=1.05,
    arm_strength=70.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: 2026 Royals bullpen (setup + closer; closer is last entry).
ROYALS_BULLPEN_2026: List[PitcherStats] = [
    _KC_ERCEG,
    _KC_STRAHM,
    _KC_SCHREIBER,
    _KC_MEARS,
    _KC_LYNCH,
    _KC_ESTEVEZ,
]


@dataclass
class RoyalsRoster:
    """
    Bundle of Kansas City Royals projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Carlos Estevez).

    Examples
    --------
    ::

        roster = RoyalsRoster.default()
        print(roster.rotation[0].name)   # "Cole Ragans"
        print(roster.lineup[4].name)     # "Bobby Witt Jr."
        print(roster.bullpen[-1].name)   # "Carlos Estevez"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "RoyalsRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(ROYALS_LINEUP_2026),
            rotation=list(ROYALS_ROTATION_2026),
            bullpen=list(ROYALS_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Minnesota Twins — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Minnesota Twins starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Ryan Jeffers        1B – Josh Bell          2B – Luke Keaschall
#   3B – Royce Lewis          SS – Brooks Lee          LF – Alan Roden
#   CF – Byron Buxton         RF – Matt Wallner        DH – Trevor Larnach
#
# Usage:
#
#   from mlb_player_props import TwinsRoster, UnabatedEdgeScreener
#   roster   = TwinsRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Joe Ryan)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Byron Buxton for batter props
#   for edge in screener.screen_batter(roster.lineup[6]):
#       print(edge)
#
#   # Screen the closer (Taylor Rogers)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Ryan Jeffers — C, bats right, above-average power for a catcher with solid
#: receiving skills.
_MIN_JEFFERS = BatterStats(
    name="Ryan Jeffers",
    avg=0.245,
    obp=0.315,
    slg=0.450,
    hr_per_600_pa=24.0,
    sb_per_season=2.0,
    doubles_per_600_pa=22.0,
    games_played=120,
    power_rating=68.0,
    bats="R",
    pitches_per_pa=3.72,
    rbi_per_season=62.0,
    runs_per_season=46.0,
)

#: Josh Bell — 1B, switch hitter, line-drive power bat with disciplined plate
#: approach.
_MIN_BELL = BatterStats(
    name="Josh Bell",
    avg=0.252,
    obp=0.338,
    slg=0.430,
    hr_per_600_pa=20.0,
    sb_per_season=4.0,
    doubles_per_600_pa=28.0,
    games_played=140,
    power_rating=58.0,
    bats="S",
    pitches_per_pa=3.95,
    rbi_per_season=66.0,
    runs_per_season=58.0,
)

#: Luke Keaschall — 2B, bats right, developing prospect with contact-first
#: approach and gap power.
_MIN_KEASCHALL = BatterStats(
    name="Luke Keaschall",
    avg=0.258,
    obp=0.325,
    slg=0.390,
    hr_per_600_pa=10.0,
    sb_per_season=16.0,
    doubles_per_600_pa=26.0,
    games_played=138,
    power_rating=38.0,
    bats="R",
    pitches_per_pa=3.68,
    rbi_per_season=46.0,
    runs_per_season=62.0,
)

#: Royce Lewis — 3B, bats right, electrifying talent with plus power and speed
#: when healthy.
_MIN_LEWIS = BatterStats(
    name="Royce Lewis",
    avg=0.278,
    obp=0.338,
    slg=0.498,
    hr_per_600_pa=28.0,
    sb_per_season=18.0,
    doubles_per_600_pa=30.0,
    games_played=130,
    power_rating=80.0,
    bats="R",
    pitches_per_pa=3.75,
    rbi_per_season=78.0,
    runs_per_season=76.0,
)

#: Brooks Lee — SS, bats right (switch), advanced bat with solid all-around
#: skills at the plate and solid glove.
_MIN_LEE = BatterStats(
    name="Brooks Lee",
    avg=0.262,
    obp=0.328,
    slg=0.415,
    hr_per_600_pa=14.0,
    sb_per_season=10.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=48.0,
    bats="S",
    pitches_per_pa=3.80,
    rbi_per_season=52.0,
    runs_per_season=64.0,
)

#: Alan Roden — LF, bats right, patient hitter with above-average on-base
#: skills and developing power.
_MIN_RODEN = BatterStats(
    name="Alan Roden",
    avg=0.255,
    obp=0.338,
    slg=0.390,
    hr_per_600_pa=10.0,
    sb_per_season=8.0,
    doubles_per_600_pa=24.0,
    games_played=132,
    power_rating=36.0,
    bats="R",
    pitches_per_pa=3.90,
    rbi_per_season=40.0,
    runs_per_season=52.0,
)

#: Byron Buxton — CF, bats right, elite centre-fielder with superstar power and
#: speed when healthy; among the most dangerous leadoff options in baseball.
_MIN_BUXTON = BatterStats(
    name="Byron Buxton",
    avg=0.258,
    obp=0.318,
    slg=0.505,
    hr_per_600_pa=34.0,
    sb_per_season=18.0,
    doubles_per_600_pa=26.0,
    games_played=125,
    power_rating=90.0,
    bats="R",
    pitches_per_pa=3.68,
    rbi_per_season=72.0,
    runs_per_season=74.0,
)

#: Matt Wallner — RF, bats left, powerful corner outfielder with big raw power
#: and improving contact.
_MIN_WALLNER = BatterStats(
    name="Matt Wallner",
    avg=0.248,
    obp=0.332,
    slg=0.480,
    hr_per_600_pa=28.0,
    sb_per_season=4.0,
    doubles_per_600_pa=24.0,
    games_played=138,
    power_rating=76.0,
    bats="L",
    pitches_per_pa=3.88,
    rbi_per_season=68.0,
    runs_per_season=54.0,
)

#: Trevor Larnach — DH, bats left, left-handed masher with solid power and
#: good plate coverage.
_MIN_LARNACH = BatterStats(
    name="Trevor Larnach",
    avg=0.245,
    obp=0.322,
    slg=0.450,
    hr_per_600_pa=22.0,
    sb_per_season=4.0,
    doubles_per_600_pa=26.0,
    games_played=135,
    power_rating=64.0,
    bats="L",
    pitches_per_pa=3.82,
    rbi_per_season=60.0,
    runs_per_season=52.0,
)

#: 2026 Twins projected starting lineup (depth-chart position-1 starters).
TWINS_LINEUP_2026: List[BatterStats] = [
    _MIN_JEFFERS,
    _MIN_BELL,
    _MIN_KEASCHALL,
    _MIN_LEWIS,
    _MIN_LEE,
    _MIN_RODEN,
    _MIN_BUXTON,
    _MIN_WALLNER,
    _MIN_LARNACH,
]

# -- Starting rotation -------------------------------------------------------

#: Joe Ryan — RHP, deceptive ace with elite spin rates and exceptional
#: command; the clear-cut rotation leader for Minnesota.
_MIN_RYAN = PitcherStats(
    name="Joe Ryan",
    era=3.10,
    k_per_9=11.2,
    innings_per_start=6.1,
    whip=1.10,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Bailey Ober — RHP, tall righty with outstanding extension and deceptive
#: mechanics; generates weak contact.
_MIN_OBER = PitcherStats(
    name="Bailey Ober",
    era=3.60,
    k_per_9=9.5,
    innings_per_start=6.0,
    whip=1.18,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Simeon Woods Richardson — RHP, young power arm with frontline ceiling;
#: developing command.
_MIN_SWR = PitcherStats(
    name="Simeon Woods Richardson",
    era=4.00,
    k_per_9=9.8,
    innings_per_start=5.5,
    whip=1.26,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.90,
)

#: Taj Bradley — RHP, mid-rotation arm with solid stuff and improving polish.
_MIN_BRADLEY = PitcherStats(
    name="Taj Bradley",
    era=4.20,
    k_per_9=9.2,
    innings_per_start=5.2,
    whip=1.28,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.85,
)

#: Mick Abel — RHP, high-upside fifth starter with electric repertoire;
#: still maturing at the big-league level.
_MIN_ABEL = PitcherStats(
    name="Mick Abel",
    era=4.60,
    k_per_9=9.5,
    innings_per_start=5.0,
    whip=1.35,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.92,
)

#: 2026 Twins projected starting rotation (rotation-turn order 1–5).
TWINS_ROTATION_2026: List[PitcherStats] = [
    _MIN_RYAN,
    _MIN_OBER,
    _MIN_SWR,
    _MIN_BRADLEY,
    _MIN_ABEL,
]

# -- Bullpen -----------------------------------------------------------------

#: Anthony Banda — LHP, lefty specialist and multi-inning arm.
_MIN_BANDA = PitcherStats(
    name="Anthony Banda",
    era=3.80,
    k_per_9=10.2,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=52.0,
    throws="L",
    pitches_per_pa=3.85,
)

#: Kody Funderburk — RHP, power arm with sharp breaking ball.
_MIN_FUNDERBURK = PitcherStats(
    name="Kody Funderburk",
    era=3.70,
    k_per_9=10.8,
    innings_per_start=1.0,
    whip=1.18,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Eric Orze — RHP, late-inning setup man with deceptive delivery.
_MIN_ORZE = PitcherStats(
    name="Eric Orze",
    era=3.90,
    k_per_9=10.0,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Travis Adams — RHP, high-leverage reliever with improving velocity.
_MIN_ADAMS = PitcherStats(
    name="Travis Adams",
    era=4.10,
    k_per_9=9.5,
    innings_per_start=1.0,
    whip=1.28,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Zak Kent — RHP, middle-relief option with solid groundball tendencies.
_MIN_KENT = PitcherStats(
    name="Zak Kent",
    era=4.20,
    k_per_9=9.0,
    innings_per_start=1.0,
    whip=1.30,
    arm_strength=56.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Taylor Rogers — CL, LHP, elite left-handed closer with devastating slider;
#: one of the best closers in the American League.
_MIN_ROGERS = PitcherStats(
    name="Taylor Rogers",
    era=2.80,
    k_per_9=11.8,
    innings_per_start=1.0,
    whip=1.02,
    arm_strength=62.0,
    throws="L",
    pitches_per_pa=3.82,
)

#: 2026 Twins bullpen (setup + closer; closer is last entry).
TWINS_BULLPEN_2026: List[PitcherStats] = [
    _MIN_BANDA,
    _MIN_FUNDERBURK,
    _MIN_ORZE,
    _MIN_ADAMS,
    _MIN_KENT,
    _MIN_ROGERS,
]


@dataclass
class TwinsRoster:
    """
    Bundle of Minnesota Twins projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Taylor Rogers).

    Examples
    --------
    ::

        roster = TwinsRoster.default()
        print(roster.rotation[0].name)   # "Joe Ryan"
        print(roster.lineup[6].name)     # "Byron Buxton"
        print(roster.bullpen[-1].name)   # "Taylor Rogers"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "TwinsRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(TWINS_LINEUP_2026),
            rotation=list(TWINS_ROTATION_2026),
            bullpen=list(TWINS_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Baltimore Orioles — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Baltimore Orioles starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Adley Rutschman    1B – Pete Alonso         2B – Jackson Holliday
#   3B – Jordan Westburg     SS – Gunnar Henderson    LF – Taylor Ward
#   CF – Colton Cowser       RF – Dylan Beavers       DH – Samuel Basallo
#
# Usage:
#
#   from mlb_player_props import OriolesRoster, UnabatedEdgeScreener
#   roster   = OriolesRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Trevor Rogers)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Gunnar Henderson for batter props
#   for edge in screener.screen_batter(roster.lineup[4]):
#       print(edge)
#
#   # Screen the closer (Ryan Helsley)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Adley Rutschman — C, switch hitter, the best two-way catcher in baseball;
#: elite on-base skills and durable behind the dish.
_ORI_RUTSCHMAN = BatterStats(
    name="Adley Rutschman",
    avg=0.268,
    obp=0.372,
    slg=0.442,
    hr_per_600_pa=18.0,
    sb_per_season=4.0,
    doubles_per_600_pa=30.0,
    games_played=148,
    power_rating=56.0,
    bats="S",
    pitches_per_pa=4.10,
    rbi_per_season=64.0,
    runs_per_season=72.0,
)

#: Pete Alonso — 1B, bats right, prodigious power bat nicknamed "The Polar
#: Bear"; one of the premier home-run hitters in the American League.
_ORI_ALONSO = BatterStats(
    name="Pete Alonso",
    avg=0.250,
    obp=0.338,
    slg=0.510,
    hr_per_600_pa=38.0,
    sb_per_season=2.0,
    doubles_per_600_pa=26.0,
    games_played=155,
    power_rating=92.0,
    bats="R",
    pitches_per_pa=3.92,
    rbi_per_season=96.0,
    runs_per_season=78.0,
)

#: Jackson Holliday — 2B, bats left, highly-touted former #1 overall pick with
#: elite bat speed and improving approach.
_ORI_HOLLIDAY = BatterStats(
    name="Jackson Holliday",
    avg=0.262,
    obp=0.350,
    slg=0.420,
    hr_per_600_pa=14.0,
    sb_per_season=18.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=50.0,
    bats="L",
    pitches_per_pa=4.00,
    rbi_per_season=52.0,
    runs_per_season=78.0,
)

#: Jordan Westburg — 3B, bats right, versatile offensive threat with solid
#: all-around game including gap power and good contact skills.
_ORI_WESTBURG = BatterStats(
    name="Jordan Westburg",
    avg=0.255,
    obp=0.325,
    slg=0.430,
    hr_per_600_pa=16.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=52.0,
    bats="R",
    pitches_per_pa=3.82,
    rbi_per_season=58.0,
    runs_per_season=64.0,
)

#: Gunnar Henderson — SS, bats left, potential MVP-calibre shortstop with
#: elite power-speed combination; the cornerstone of the Orioles' offense.
_ORI_HENDERSON = BatterStats(
    name="Gunnar Henderson",
    avg=0.278,
    obp=0.352,
    slg=0.520,
    hr_per_600_pa=34.0,
    sb_per_season=16.0,
    doubles_per_600_pa=32.0,
    games_played=155,
    power_rating=94.0,
    bats="L",
    pitches_per_pa=3.88,
    rbi_per_season=88.0,
    runs_per_season=96.0,
)

#: Taylor Ward — LF, bats right, disciplined left fielder with above-average
#: on-base skills and solid power.
_ORI_WARD = BatterStats(
    name="Taylor Ward",
    avg=0.248,
    obp=0.340,
    slg=0.435,
    hr_per_600_pa=18.0,
    sb_per_season=6.0,
    doubles_per_600_pa=26.0,
    games_played=138,
    power_rating=54.0,
    bats="R",
    pitches_per_pa=3.95,
    rbi_per_season=56.0,
    runs_per_season=60.0,
)

#: Colton Cowser — CF, bats left, plus defensive centre fielder with emerging
#: offensive profile; solid contact and developing power.
_ORI_COWSER = BatterStats(
    name="Colton Cowser",
    avg=0.255,
    obp=0.338,
    slg=0.420,
    hr_per_600_pa=14.0,
    sb_per_season=12.0,
    doubles_per_600_pa=26.0,
    games_played=148,
    power_rating=44.0,
    bats="L",
    pitches_per_pa=3.90,
    rbi_per_season=50.0,
    runs_per_season=66.0,
)

#: Dylan Beavers — RF, bats left, athletic corner outfielder with impressive
#: tools and growing power-speed combination.
_ORI_BEAVERS = BatterStats(
    name="Dylan Beavers",
    avg=0.248,
    obp=0.322,
    slg=0.412,
    hr_per_600_pa=12.0,
    sb_per_season=14.0,
    doubles_per_600_pa=24.0,
    games_played=138,
    power_rating=40.0,
    bats="L",
    pitches_per_pa=3.85,
    rbi_per_season=44.0,
    runs_per_season=58.0,
)

#: Samuel Basallo — DH, bats left, highly-regarded prospect with electric raw
#: power and a mature approach for his age.
_ORI_BASALLO = BatterStats(
    name="Samuel Basallo",
    avg=0.258,
    obp=0.330,
    slg=0.460,
    hr_per_600_pa=22.0,
    sb_per_season=4.0,
    doubles_per_600_pa=28.0,
    games_played=140,
    power_rating=68.0,
    bats="L",
    pitches_per_pa=3.85,
    rbi_per_season=68.0,
    runs_per_season=58.0,
)

#: 2026 Orioles projected starting lineup (depth-chart position-1 starters).
ORIOLES_LINEUP_2026: List[BatterStats] = [
    _ORI_RUTSCHMAN,
    _ORI_ALONSO,
    _ORI_HOLLIDAY,
    _ORI_WESTBURG,
    _ORI_HENDERSON,
    _ORI_WARD,
    _ORI_COWSER,
    _ORI_BEAVERS,
    _ORI_BASALLO,
]

# -- Starting rotation -------------------------------------------------------

#: Trevor Rogers — LHP, crafty left-hander with elite command and deceptive
#: three-pitch mix; leads one of baseball's most well-rounded rotations.
_ORI_T_ROGERS = PitcherStats(
    name="Trevor Rogers",
    era=3.15,
    k_per_9=10.2,
    innings_per_start=6.0,
    whip=1.12,
    arm_strength=60.0,
    throws="L",
    pitches_per_pa=3.90,
)

#: Kyle Bradish — RHP, mid-rotation power arm returning from injury; plus
#: arsenal when healthy.
_ORI_BRADISH = PitcherStats(
    name="Kyle Bradish",
    era=3.60,
    k_per_9=10.0,
    innings_per_start=5.2,
    whip=1.18,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Chris Bassitt — RHP, durable veteran innings-eater with outstanding
#: command and mound presence.
_ORI_BASSITT = PitcherStats(
    name="Chris Bassitt",
    era=3.90,
    k_per_9=8.8,
    innings_per_start=6.0,
    whip=1.22,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Shane Baz — RHP, electric stuff with high-ceiling potential; working to
#: stay healthy and anchor the back of the rotation.
_ORI_BAZ = PitcherStats(
    name="Shane Baz",
    era=4.10,
    k_per_9=9.8,
    innings_per_start=5.2,
    whip=1.26,
    arm_strength=64.0,
    throws="R",
    pitches_per_pa=3.92,
)

#: Zach Eflin — RHP, sinker-heavy fifth starter who generates ground balls
#: and limits walks; reliable back-end option.
_ORI_EFLIN = PitcherStats(
    name="Zach Eflin",
    era=4.25,
    k_per_9=7.8,
    innings_per_start=5.1,
    whip=1.28,
    arm_strength=56.0,
    throws="R",
    pitches_per_pa=3.75,
)

#: 2026 Orioles projected starting rotation (rotation-turn order 1–5).
ORIOLES_ROTATION_2026: List[PitcherStats] = [
    _ORI_T_ROGERS,
    _ORI_BRADISH,
    _ORI_BASSITT,
    _ORI_BAZ,
    _ORI_EFLIN,
]

# -- Bullpen -----------------------------------------------------------------

#: Andrew Kittredge — RHP, high-leverage setup arm with elite splitter; worm-
#: killing ground-ball specialist.
_ORI_KITTREDGE = PitcherStats(
    name="Andrew Kittredge",
    era=3.50,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.14,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Keegan Akin — LHP, left-handed specialist and multiple-inning reliever
#: with sharp breaking ball.
_ORI_AKIN = PitcherStats(
    name="Keegan Akin",
    era=3.80,
    k_per_9=9.5,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=52.0,
    throws="L",
    pitches_per_pa=3.88,
)

#: Yennier Cano — RHP, dynamic power arm with a devastating sinker-splitter
#: combination; one of the most valuable setup men in the AL.
_ORI_CANO = PitcherStats(
    name="Yennier Cano",
    era=3.20,
    k_per_9=10.5,
    innings_per_start=1.0,
    whip=1.10,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Tyler Wells — RHP, multi-inning reliever option with solid mid-rotation
#: arsenal.
_ORI_WELLS = PitcherStats(
    name="Tyler Wells",
    era=4.00,
    k_per_9=9.0,
    innings_per_start=1.0,
    whip=1.24,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Rico Garcia — RHP, long-relief depth option with ability to eat innings
#: when starters exit early.
_ORI_R_GARCIA = PitcherStats(
    name="Rico Garcia",
    era=4.20,
    k_per_9=8.8,
    innings_per_start=1.0,
    whip=1.28,
    arm_strength=56.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Ryan Helsley — CL, RHP, one of the hardest throwers in baseball; elite
#: closer with triple-digit heat and an outstanding slider.
_ORI_HELSLEY = PitcherStats(
    name="Ryan Helsley",
    era=2.40,
    k_per_9=13.2,
    innings_per_start=1.0,
    whip=0.98,
    arm_strength=74.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: 2026 Orioles bullpen (setup + closer; closer is last entry).
ORIOLES_BULLPEN_2026: List[PitcherStats] = [
    _ORI_KITTREDGE,
    _ORI_AKIN,
    _ORI_CANO,
    _ORI_WELLS,
    _ORI_R_GARCIA,
    _ORI_HELSLEY,
]


@dataclass
class OriolesRoster:
    """
    Bundle of Baltimore Orioles projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Ryan Helsley).

    Examples
    --------
    ::

        roster = OriolesRoster.default()
        print(roster.rotation[0].name)   # "Trevor Rogers"
        print(roster.lineup[4].name)     # "Gunnar Henderson"
        print(roster.bullpen[-1].name)   # "Ryan Helsley"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "OriolesRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(ORIOLES_LINEUP_2026),
            rotation=list(ORIOLES_ROTATION_2026),
            bullpen=list(ORIOLES_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Boston Red Sox — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Boston Red Sox starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Carlos Narvaez      1B – Willson Contreras   2B – Marcelo Mayer
#   3B – Caleb Durbin         SS – Trevor Story        LF – Jarren Duran
#   CF – Ceddanne Rafaela     RF – Wilyer Abreu        DH – Roman Anthony
#
# Usage:
#
#   from mlb_player_props import RedSoxRoster, UnabatedEdgeScreener
#   roster   = RedSoxRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Garrett Crochet)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Roman Anthony for batter props
#   for edge in screener.screen_batter(roster.lineup[8]):
#       print(edge)
#
#   # Screen the closer (Aroldis Chapman)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Carlos Narvaez — C, bats left, strong defensive catcher with a solid
#: walk rate and developing offensive game.
_BSX_NARVAEZ = BatterStats(
    name="Carlos Narvaez",
    avg=0.248,
    obp=0.335,
    slg=0.380,
    hr_per_600_pa=10.0,
    sb_per_season=2.0,
    doubles_per_600_pa=22.0,
    games_played=120,
    power_rating=36.0,
    bats="L",
    pitches_per_pa=3.92,
    rbi_per_season=42.0,
    runs_per_season=48.0,
)

#: Willson Contreras — 1B, bats right, All-Star catcher converting to first
#: base; elite bat-to-ball skills and above-average pop.
_BSX_CONTRERAS = BatterStats(
    name="Willson Contreras",
    avg=0.265,
    obp=0.348,
    slg=0.450,
    hr_per_600_pa=20.0,
    sb_per_season=2.0,
    doubles_per_600_pa=26.0,
    games_played=145,
    power_rating=60.0,
    bats="R",
    pitches_per_pa=3.88,
    rbi_per_season=68.0,
    runs_per_season=64.0,
)

#: Marcelo Mayer — 2B, bats left, prized shortstop prospect shifting to
#: second base; polished bat with above-average power projection.
_BSX_MAYER = BatterStats(
    name="Marcelo Mayer",
    avg=0.268,
    obp=0.352,
    slg=0.440,
    hr_per_600_pa=16.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=52.0,
    bats="L",
    pitches_per_pa=4.00,
    rbi_per_season=56.0,
    runs_per_season=70.0,
)

#: Caleb Durbin — 3B, switch hitter, versatile utility infielder with plus
#: on-base skills and gap power; fills a key role at the hot corner.
_BSX_DURBIN = BatterStats(
    name="Caleb Durbin",
    avg=0.248,
    obp=0.325,
    slg=0.380,
    hr_per_600_pa=8.0,
    sb_per_season=18.0,
    doubles_per_600_pa=22.0,
    games_played=135,
    power_rating=32.0,
    bats="S",
    pitches_per_pa=3.85,
    rbi_per_season=38.0,
    runs_per_season=62.0,
)

#: Trevor Story — SS, bats right, powerful shortstop returning to full
#: health; plus raw power and well above-average arm.
_BSX_STORY = BatterStats(
    name="Trevor Story",
    avg=0.252,
    obp=0.320,
    slg=0.440,
    hr_per_600_pa=20.0,
    sb_per_season=16.0,
    doubles_per_600_pa=26.0,
    games_played=138,
    power_rating=64.0,
    bats="R",
    pitches_per_pa=3.80,
    rbi_per_season=62.0,
    runs_per_season=68.0,
)

#: Jarren Duran — LF, bats left, explosive leadoff threat with elite speed
#: and improving power; one of the AL's best offensive outfielders.
_BSX_DURAN = BatterStats(
    name="Jarren Duran",
    avg=0.285,
    obp=0.355,
    slg=0.470,
    hr_per_600_pa=14.0,
    sb_per_season=30.0,
    doubles_per_600_pa=36.0,
    games_played=155,
    power_rating=56.0,
    bats="L",
    pitches_per_pa=3.72,
    rbi_per_season=64.0,
    runs_per_season=96.0,
)

#: Ceddanne Rafaela — CF, bats right, exceptional defensive centre fielder
#: with above-average speed; offensively developing but exciting tools.
_BSX_RAFAELA = BatterStats(
    name="Ceddanne Rafaela",
    avg=0.248,
    obp=0.302,
    slg=0.410,
    hr_per_600_pa=14.0,
    sb_per_season=24.0,
    doubles_per_600_pa=24.0,
    games_played=148,
    power_rating=46.0,
    bats="R",
    pitches_per_pa=3.68,
    rbi_per_season=50.0,
    runs_per_season=68.0,
)

#: Wilyer Abreu — RF, bats right, highly athletic corner outfielder with
#: plus defence and promising offensive ceiling in right field.
_BSX_ABREU = BatterStats(
    name="Wilyer Abreu",
    avg=0.252,
    obp=0.328,
    slg=0.415,
    hr_per_600_pa=12.0,
    sb_per_season=14.0,
    doubles_per_600_pa=24.0,
    games_played=140,
    power_rating=42.0,
    bats="R",
    pitches_per_pa=3.78,
    rbi_per_season=48.0,
    runs_per_season=60.0,
)

#: Roman Anthony — DH, bats left, highly touted top prospect with premium
#: bat speed, plate discipline, and tantalising power potential.
_BSX_R_ANTHONY = BatterStats(
    name="Roman Anthony",
    avg=0.272,
    obp=0.360,
    slg=0.462,
    hr_per_600_pa=18.0,
    sb_per_season=14.0,
    doubles_per_600_pa=30.0,
    games_played=148,
    power_rating=58.0,
    bats="L",
    pitches_per_pa=4.05,
    rbi_per_season=66.0,
    runs_per_season=78.0,
)

#: 2026 Red Sox projected starting lineup (depth-chart position-1 starters).
RED_SOX_LINEUP_2026: List[BatterStats] = [
    _BSX_NARVAEZ,
    _BSX_CONTRERAS,
    _BSX_MAYER,
    _BSX_DURBIN,
    _BSX_STORY,
    _BSX_DURAN,
    _BSX_RAFAELA,
    _BSX_ABREU,
    _BSX_R_ANTHONY,
]

# -- Starting rotation -------------------------------------------------------

#: Garrett Crochet — LHP, electric ace; one of the best left-handed starters
#: in baseball with triple-digit heat and a devastating slider.
_BSX_CROCHET = PitcherStats(
    name="Garrett Crochet",
    era=2.95,
    k_per_9=11.8,
    innings_per_start=6.1,
    whip=1.08,
    arm_strength=70.0,
    throws="L",
    pitches_per_pa=3.85,
)

#: Sonny Gray — RHP, elite command and advanced pitch sequencing; veteran
#: ace-quality arm who pounds the zone with varied stuff.
_BSX_S_GRAY = PitcherStats(
    name="Sonny Gray",
    era=3.20,
    k_per_9=10.2,
    innings_per_start=6.0,
    whip=1.12,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Ranger Suarez — LHP, advanced command lefty with elite contact-management
#: skills; ground-ball specialist who limits hard contact.
_BSX_SUAREZ = PitcherStats(
    name="Ranger Suarez",
    era=3.45,
    k_per_9=8.8,
    innings_per_start=5.2,
    whip=1.18,
    arm_strength=56.0,
    throws="L",
    pitches_per_pa=3.82,
)

#: Brayan Bello — RHP, power sinker-slider combination; emerging mid-rotation
#: arm with plus velocity and developing secondary pitches.
_BSX_BELLO = PitcherStats(
    name="Brayan Bello",
    era=3.85,
    k_per_9=9.4,
    innings_per_start=5.2,
    whip=1.24,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Johan Oviedo — RHP, durable innings-eater with solid four-pitch mix;
#: reliable back-end starter who limits walks and eats innings.
_BSX_OVIEDO = PitcherStats(
    name="Johan Oviedo",
    era=4.15,
    k_per_9=8.4,
    innings_per_start=5.1,
    whip=1.28,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: 2026 Red Sox projected starting rotation (rotation-turn order 1–5).
RED_SOX_ROTATION_2026: List[PitcherStats] = [
    _BSX_CROCHET,
    _BSX_S_GRAY,
    _BSX_SUAREZ,
    _BSX_BELLO,
    _BSX_OVIEDO,
]

# -- Bullpen -----------------------------------------------------------------

#: Garrett Whitlock — RHP, high-leverage setup arm with elite splitter;
#: can work multiple innings and profile as an opener when needed.
_BSX_WHITLOCK = PitcherStats(
    name="Garrett Whitlock",
    era=3.40,
    k_per_9=10.2,
    innings_per_start=1.0,
    whip=1.12,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Justin Slaten — RHP, hard-throwing setup reliever with a devastating
#: sweeper; emerging as one of Boston's most valuable bridge arms.
_BSX_SLATEN = PitcherStats(
    name="Justin Slaten",
    era=3.60,
    k_per_9=11.0,
    innings_per_start=1.0,
    whip=1.16,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Greg Weissert — RHP, power reliever with a nasty splitter; accumulated
#: significant late-game experience as a key setup option.
_BSX_WEISSERT = PitcherStats(
    name="Greg Weissert",
    era=3.75,
    k_per_9=10.5,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Danny Coulombe — LHP, veteran left-handed specialist with excellent
#: command and a deceptive delivery that troubles left-handed hitters.
_BSX_COULOMBE = PitcherStats(
    name="Danny Coulombe",
    era=3.80,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=52.0,
    throws="L",
    pitches_per_pa=3.85,
)

#: Zack Kelly — RHP, high-octane reliever with triple-digit heat; elite
#: swing-and-miss stuff makes him a key late-inning weapon.
_BSX_Z_KELLY = PitcherStats(
    name="Zack Kelly",
    era=3.90,
    k_per_9=11.2,
    innings_per_start=1.0,
    whip=1.24,
    arm_strength=66.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Aroldis Chapman — CL, LHP, the hardest-throwing closer in baseball
#: history; triple-digit fastball and devastating slider; elite save machine.
_BSX_CHAPMAN = PitcherStats(
    name="Aroldis Chapman",
    era=2.65,
    k_per_9=14.0,
    innings_per_start=1.0,
    whip=1.00,
    arm_strength=78.0,
    throws="L",
    pitches_per_pa=3.70,
)

#: 2026 Red Sox bullpen (setup + closer; closer is last entry).
RED_SOX_BULLPEN_2026: List[PitcherStats] = [
    _BSX_WHITLOCK,
    _BSX_SLATEN,
    _BSX_WEISSERT,
    _BSX_COULOMBE,
    _BSX_Z_KELLY,
    _BSX_CHAPMAN,
]


@dataclass
class RedSoxRoster:
    """
    Bundle of Boston Red Sox projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Aroldis Chapman).

    Examples
    --------
    ::

        roster = RedSoxRoster.default()
        print(roster.rotation[0].name)   # "Garrett Crochet"
        print(roster.lineup[5].name)     # "Jarren Duran"
        print(roster.bullpen[-1].name)   # "Aroldis Chapman"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "RedSoxRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(RED_SOX_LINEUP_2026),
            rotation=list(RED_SOX_ROTATION_2026),
            bullpen=list(RED_SOX_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# New York Yankees — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# New York Yankees starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Austin Wells        1B – Ben Rice            2B – Jazz Chisholm Jr.
#   3B – Ryan McMahon        SS – Anthony Volpe        LF – Cody Bellinger
#   CF – Trent Grisham       RF – Aaron Judge          DH – Giancarlo Stanton
#
# Usage:
#
#   from mlb_player_props import YankeesRoster, UnabatedEdgeScreener
#   roster   = YankeesRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Max Fried)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen Aaron Judge for batter props
#   for edge in screener.screen_batter(roster.lineup[7]):
#       print(edge)
#
#   # Screen the closer (David Bednar)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Austin Wells — C, bats left, highly touted young catcher with plus raw
#: power and improving plate discipline; key piece of the Yankees rebuild.
_NYY_WELLS = BatterStats(
    name="Austin Wells",
    avg=0.248,
    obp=0.318,
    slg=0.430,
    hr_per_600_pa=18.0,
    sb_per_season=4.0,
    doubles_per_600_pa=24.0,
    games_played=130,
    power_rating=56.0,
    bats="L",
    pitches_per_pa=3.88,
    rbi_per_season=58.0,
    runs_per_season=56.0,
)

#: Ben Rice — 1B, bats left, athletic first-base option with above-average
#: raw power; versatile defender who made his MLB debut in 2024.
_NYY_RICE = BatterStats(
    name="Ben Rice",
    avg=0.245,
    obp=0.322,
    slg=0.430,
    hr_per_600_pa=20.0,
    sb_per_season=2.0,
    doubles_per_600_pa=22.0,
    games_played=130,
    power_rating=54.0,
    bats="L",
    pitches_per_pa=3.92,
    rbi_per_season=56.0,
    runs_per_season=60.0,
)

#: Jazz Chisholm Jr. — 2B, switch hitter, explosive leadoff bat with elite
#: speed and plus power for the position; one of the game's most dynamic players.
_NYY_CHISHOLM = BatterStats(
    name="Jazz Chisholm Jr.",
    avg=0.258,
    obp=0.330,
    slg=0.455,
    hr_per_600_pa=22.0,
    sb_per_season=26.0,
    doubles_per_600_pa=28.0,
    games_played=138,
    power_rating=64.0,
    bats="S",
    pitches_per_pa=3.82,
    rbi_per_season=64.0,
    runs_per_season=86.0,
)

#: Ryan McMahon — 3B, bats left, veteran third baseman with solid glove and
#: reliable power output; strong defender who limits strikeouts.
_NYY_MCMAHON = BatterStats(
    name="Ryan McMahon",
    avg=0.248,
    obp=0.325,
    slg=0.415,
    hr_per_600_pa=16.0,
    sb_per_season=8.0,
    doubles_per_600_pa=28.0,
    games_played=145,
    power_rating=50.0,
    bats="L",
    pitches_per_pa=3.88,
    rbi_per_season=56.0,
    runs_per_season=62.0,
)

#: Anthony Volpe — SS, bats right, talented young shortstop with elite
#: athleticism, plus defence, and developing offensive game.
_NYY_VOLPE = BatterStats(
    name="Anthony Volpe",
    avg=0.252,
    obp=0.320,
    slg=0.405,
    hr_per_600_pa=14.0,
    sb_per_season=22.0,
    doubles_per_600_pa=24.0,
    games_played=155,
    power_rating=46.0,
    bats="R",
    pitches_per_pa=3.80,
    rbi_per_season=52.0,
    runs_per_season=78.0,
)

#: Cody Bellinger — LF, bats left, powerful former MVP with plus speed and
#: above-average defence; bounced back to elite production in 2023.
_NYY_BELLINGER = BatterStats(
    name="Cody Bellinger",
    avg=0.262,
    obp=0.332,
    slg=0.450,
    hr_per_600_pa=20.0,
    sb_per_season=14.0,
    doubles_per_600_pa=28.0,
    games_played=148,
    power_rating=62.0,
    bats="L",
    pitches_per_pa=3.85,
    rbi_per_season=66.0,
    runs_per_season=74.0,
)

#: Trent Grisham — CF, bats left, solid defensive centre fielder with a
#: patient approach; provides quality at-bats and gap power.
_NYY_GRISHAM = BatterStats(
    name="Trent Grisham",
    avg=0.228,
    obp=0.330,
    slg=0.370,
    hr_per_600_pa=10.0,
    sb_per_season=14.0,
    doubles_per_600_pa=22.0,
    games_played=135,
    power_rating=36.0,
    bats="L",
    pitches_per_pa=4.05,
    rbi_per_season=38.0,
    runs_per_season=58.0,
)

#: Aaron Judge — RF, bats right, reigning AL MVP and arguably the best
#: hitter in baseball; elite power, plate discipline, and arm strength.
_NYY_JUDGE = BatterStats(
    name="Aaron Judge",
    avg=0.288,
    obp=0.405,
    slg=0.600,
    hr_per_600_pa=56.0,
    sb_per_season=10.0,
    doubles_per_600_pa=30.0,
    games_played=155,
    power_rating=100.0,
    bats="R",
    pitches_per_pa=4.10,
    rbi_per_season=112.0,
    runs_per_season=106.0,
)

#: Giancarlo Stanton — DH, bats right, one of baseball's most feared power
#: hitters when healthy; legendary raw power and elite production vs LHP.
_NYY_STANTON = BatterStats(
    name="Giancarlo Stanton",
    avg=0.238,
    obp=0.310,
    slg=0.510,
    hr_per_600_pa=38.0,
    sb_per_season=0.0,
    doubles_per_600_pa=22.0,
    games_played=120,
    power_rating=94.0,
    bats="R",
    pitches_per_pa=3.92,
    rbi_per_season=80.0,
    runs_per_season=62.0,
)

#: 2026 Yankees projected starting lineup (depth-chart position-1 starters).
YANKEES_LINEUP_2026: List[BatterStats] = [
    _NYY_WELLS,
    _NYY_RICE,
    _NYY_CHISHOLM,
    _NYY_MCMAHON,
    _NYY_VOLPE,
    _NYY_BELLINGER,
    _NYY_GRISHAM,
    _NYY_JUDGE,
    _NYY_STANTON,
]

# -- Starting rotation -------------------------------------------------------

#: Max Fried — LHP, elite ace with advanced command, plus curveball,
#: and exceptional ground-ball rate; Cy Young-calibre starter.
_NYY_FRIED = PitcherStats(
    name="Max Fried",
    era=2.80,
    k_per_9=9.6,
    innings_per_start=6.2,
    whip=1.08,
    arm_strength=62.0,
    throws="L",
    pitches_per_pa=3.82,
)

#: Gerrit Cole — RHP, elite power pitcher with elite spin rate and four-seam
#: fastball; multiple Cy Young Award votes and premier strikeout arm.
_NYY_COLE = PitcherStats(
    name="Gerrit Cole",
    era=3.10,
    k_per_9=12.2,
    innings_per_start=6.1,
    whip=1.10,
    arm_strength=66.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Carlos Rodon — LHP, high-strikeout lefty with a devastating slider;
#: can be dominant when healthy and on top of his game.
_NYY_RODON = PitcherStats(
    name="Carlos Rodon",
    era=3.55,
    k_per_9=11.0,
    innings_per_start=5.2,
    whip=1.18,
    arm_strength=60.0,
    throws="L",
    pitches_per_pa=3.85,
)

#: Cam Schlittler — RHP, young power pitcher developing into the fourth-
#: rotation slot; live fastball and improving secondary offerings.
_NYY_SCHLITTLER = PitcherStats(
    name="Cam Schlittler",
    era=4.10,
    k_per_9=9.2,
    innings_per_start=5.0,
    whip=1.28,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Will Warren — RHP, durable back-end starter with solid command of four
#: pitches; reliable innings-eater who limits the big inning.
_NYY_WARREN = PitcherStats(
    name="Will Warren",
    era=4.35,
    k_per_9=8.6,
    innings_per_start=5.0,
    whip=1.30,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: 2026 Yankees projected starting rotation (rotation-turn order 1–5).
YANKEES_ROTATION_2026: List[PitcherStats] = [
    _NYY_FRIED,
    _NYY_COLE,
    _NYY_RODON,
    _NYY_SCHLITTLER,
    _NYY_WARREN,
]

# -- Bullpen -----------------------------------------------------------------

#: Camilo Doval — RHP, elite high-leverage setup arm with a wipeout slider
#: and triple-digit velocity; former Giants closer.
_NYY_DOVAL = PitcherStats(
    name="Camilo Doval",
    era=3.20,
    k_per_9=12.0,
    innings_per_start=1.0,
    whip=1.12,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Fernando Cruz — RHP, hard-throwing reliever with swing-and-miss stuff;
#: a key cog in the late-innings bridge to the closer.
_NYY_F_CRUZ = PitcherStats(
    name="Fernando Cruz",
    era=3.40,
    k_per_9=11.2,
    innings_per_start=1.0,
    whip=1.18,
    arm_strength=64.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Tim Hill — LHP, veteran left-handed specialist with an extreme side-arm
#: delivery that generates elite ground-ball rate and tough LHB angle.
_NYY_HILL = PitcherStats(
    name="Tim Hill",
    era=3.55,
    k_per_9=7.8,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=50.0,
    throws="L",
    pitches_per_pa=3.75,
)

#: Brent Headrick — LHP, tall left-hander with a deceptive delivery and
#: plus fastball; emerging as a reliable multi-inning option.
_NYY_HEADRICK = PitcherStats(
    name="Brent Headrick",
    era=3.65,
    k_per_9=9.4,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=58.0,
    throws="L",
    pitches_per_pa=3.82,
)

#: Jake Bird — RHP, durable multi-inning reliever with a heavy sinker that
#: generates ground balls; solid middle-relief bridge option.
_NYY_BIRD = PitcherStats(
    name="Jake Bird",
    era=3.75,
    k_per_9=8.8,
    innings_per_start=1.0,
    whip=1.24,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: David Bednar — CL, RHP, elite closer with a power fastball-slider combo;
#: former Pirates All-Star closer commanding the ninth inning.
_NYY_BEDNAR = PitcherStats(
    name="David Bednar",
    era=2.55,
    k_per_9=12.8,
    innings_per_start=1.0,
    whip=1.00,
    arm_strength=70.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: 2026 Yankees bullpen (setup + closer; closer is last entry).
YANKEES_BULLPEN_2026: List[PitcherStats] = [
    _NYY_DOVAL,
    _NYY_F_CRUZ,
    _NYY_HILL,
    _NYY_HEADRICK,
    _NYY_BIRD,
    _NYY_BEDNAR,
]


@dataclass
class YankeesRoster:
    """
    Bundle of New York Yankees projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = David Bednar).

    Examples
    --------
    ::

        roster = YankeesRoster.default()
        print(roster.rotation[0].name)   # "Max Fried"
        print(roster.lineup[7].name)     # "Aaron Judge"
        print(roster.bullpen[-1].name)   # "David Bednar"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "YankeesRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(YANKEES_LINEUP_2026),
            rotation=list(YANKEES_ROTATION_2026),
            bullpen=list(YANKEES_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Tampa Bay Rays — 2026 depth chart
# ---------------------------------------------------------------------------
# Pre-built BatterStats and PitcherStats objects for the projected 2026
# Tampa Bay Rays starting lineup, starting rotation, and bullpen.
# Statistics are modelled on each player's recent MLB performance.
#
# Lineup reflects the #1-depth-slot starter at each position:
#   C  – Nick Fortes          1B – Jonathan Aranda       2B – Gavin Lux
#   3B – Junior Caminero      SS – Carson Williams        LF – Chandler Simpson
#   CF – Cedric Mullins        RF – Jake Fraley            DH – Yandy Diaz
#
# Usage:
#
#   from mlb_player_props import RaysRoster, UnabatedEdgeScreener
#   roster   = RaysRoster.default()
#   screener = UnabatedEdgeScreener(sim, client)
#
#   # Screen the ace (Drew Rasmussen)
#   edges = screener.screen_pitcher(roster.rotation[0])
#
#   # Screen the closer (Griffin Jax)
#   edges += screener.screen_pitcher(roster.bullpen[-1])
# ---------------------------------------------------------------------------


# -- Starting lineup (depth-chart position-1 slots) -------------------------

#: Nick Fortes — C, bats right, solid defensive catcher with improving
#: offensive production; a reliable option behind the plate.
_TB_FORTES = BatterStats(
    name="Nick Fortes",
    avg=0.240,
    obp=0.305,
    slg=0.375,
    hr_per_600_pa=12.0,
    sb_per_season=2.0,
    doubles_per_600_pa=20.0,
    games_played=100,
    power_rating=36.0,
    bats="R",
    pitches_per_pa=3.80,
    rbi_per_season=38.0,
    runs_per_season=40.0,
)

#: Jonathan Aranda — 1B, bats left, patient hitter with above-average
#: on-base skills and improving power; versatile infielder.
_TB_ARANDA = BatterStats(
    name="Jonathan Aranda",
    avg=0.260,
    obp=0.340,
    slg=0.420,
    hr_per_600_pa=14.0,
    sb_per_season=4.0,
    doubles_per_600_pa=26.0,
    games_played=130,
    power_rating=44.0,
    bats="L",
    pitches_per_pa=3.95,
    rbi_per_season=52.0,
    runs_per_season=56.0,
)

#: Gavin Lux — 2B, bats left, skilled contact hitter with improving power;
#: excellent defensive second baseman with plus athleticism.
_TB_LUX = BatterStats(
    name="Gavin Lux",
    avg=0.265,
    obp=0.338,
    slg=0.410,
    hr_per_600_pa=10.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=140,
    power_rating=38.0,
    bats="L",
    pitches_per_pa=3.85,
    rbi_per_season=48.0,
    runs_per_season=62.0,
)

#: Junior Caminero — 3B, bats right, elite hitting prospect with massive
#: raw power and plus bat speed; one of the most exciting young hitters.
_TB_CAMINERO = BatterStats(
    name="Junior Caminero",
    avg=0.270,
    obp=0.325,
    slg=0.490,
    hr_per_600_pa=28.0,
    sb_per_season=6.0,
    doubles_per_600_pa=30.0,
    games_played=145,
    power_rating=78.0,
    bats="R",
    pitches_per_pa=3.78,
    rbi_per_season=76.0,
    runs_per_season=68.0,
)

#: Carson Williams — SS, bats right, toolsy young shortstop with elite
#: defence and developing offensive profile; high-ceiling prospect.
_TB_C_WILLIAMS = BatterStats(
    name="Carson Williams",
    avg=0.245,
    obp=0.315,
    slg=0.400,
    hr_per_600_pa=14.0,
    sb_per_season=16.0,
    doubles_per_600_pa=24.0,
    games_played=140,
    power_rating=46.0,
    bats="R",
    pitches_per_pa=3.82,
    rbi_per_season=50.0,
    runs_per_season=64.0,
)

#: Chandler Simpson — LF, switch hitter, blazing speed on the basepaths;
#: elite stolen-base threat who creates havoc at the top of the lineup.
_TB_SIMPSON = BatterStats(
    name="Chandler Simpson",
    avg=0.265,
    obp=0.320,
    slg=0.350,
    hr_per_600_pa=2.0,
    sb_per_season=48.0,
    doubles_per_600_pa=18.0,
    games_played=135,
    power_rating=18.0,
    bats="S",
    pitches_per_pa=3.68,
    rbi_per_season=30.0,
    runs_per_season=78.0,
)

#: Cedric Mullins — CF, bats left, two-way standout with solid contact
#: skills, plus speed, and above-average outfield defence.
_TB_MULLINS = BatterStats(
    name="Cedric Mullins",
    avg=0.255,
    obp=0.322,
    slg=0.400,
    hr_per_600_pa=12.0,
    sb_per_season=22.0,
    doubles_per_600_pa=22.0,
    games_played=145,
    power_rating=40.0,
    bats="L",
    pitches_per_pa=3.80,
    rbi_per_season=44.0,
    runs_per_season=70.0,
)

#: Jake Fraley — RF, bats left, left-handed masher with a discerning eye
#: at the plate; elevated walk rate and solid gap power.
_TB_FRALEY = BatterStats(
    name="Jake Fraley",
    avg=0.238,
    obp=0.345,
    slg=0.415,
    hr_per_600_pa=16.0,
    sb_per_season=12.0,
    doubles_per_600_pa=22.0,
    games_played=130,
    power_rating=48.0,
    bats="L",
    pitches_per_pa=4.02,
    rbi_per_season=48.0,
    runs_per_season=58.0,
)

#: Yandy Diaz — DH, bats right, elite contact hitter with outstanding
#: plate discipline; consistently posts one of the best K% in the AL.
_TB_Y_DIAZ = BatterStats(
    name="Yandy Diaz",
    avg=0.278,
    obp=0.368,
    slg=0.428,
    hr_per_600_pa=14.0,
    sb_per_season=2.0,
    doubles_per_600_pa=30.0,
    games_played=140,
    power_rating=50.0,
    bats="R",
    pitches_per_pa=4.05,
    rbi_per_season=56.0,
    runs_per_season=64.0,
)

#: 2026 Rays projected starting lineup (depth-chart position-1 starters).
RAYS_LINEUP_2026: List[BatterStats] = [
    _TB_FORTES,
    _TB_ARANDA,
    _TB_LUX,
    _TB_CAMINERO,
    _TB_C_WILLIAMS,
    _TB_SIMPSON,
    _TB_MULLINS,
    _TB_FRALEY,
    _TB_Y_DIAZ,
]

# -- Starting rotation -------------------------------------------------------

#: Drew Rasmussen — RHP, ace of the Rays rotation; elite ground-ball
#: pitcher with exceptional command and plus cutter/sinker combination.
_TB_RASMUSSEN = PitcherStats(
    name="Drew Rasmussen",
    era=3.05,
    k_per_9=9.2,
    innings_per_start=6.0,
    whip=1.12,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Ryan Pepiot — RHP, developing starter with a sharp breaking ball and
#: improving fastball command; solid mid-rotation option.
_TB_PEPIOT = PitcherStats(
    name="Ryan Pepiot",
    era=3.55,
    k_per_9=9.8,
    innings_per_start=5.2,
    whip=1.18,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Shane McClanahan — LHP, former Cy Young-calibre starter returning from
#: injury; elite strikeout pitcher with a devastating slider.
_TB_MCCLANAHAN = PitcherStats(
    name="Shane McClanahan",
    era=3.20,
    k_per_9=11.4,
    innings_per_start=5.2,
    whip=1.10,
    arm_strength=64.0,
    throws="L",
    pitches_per_pa=3.80,
)

#: Steven Matz — LHP, veteran left-hander with solid command of four
#: pitches; reliable innings-eater who limits the big inning.
_TB_MATZ = PitcherStats(
    name="Steven Matz",
    era=4.05,
    k_per_9=8.2,
    innings_per_start=5.0,
    whip=1.28,
    arm_strength=54.0,
    throws="L",
    pitches_per_pa=3.78,
)

#: Nick Martinez — RHP, durable back-end starter with multi-pitch mix;
#: keeps his team in games and provides quality at-bats.
_TB_MARTINEZ = PitcherStats(
    name="Nick Martinez",
    era=4.20,
    k_per_9=7.8,
    innings_per_start=5.0,
    whip=1.30,
    arm_strength=54.0,
    throws="R",
    pitches_per_pa=3.75,
)

#: 2026 Rays projected starting rotation (rotation-turn order 1–5).
RAYS_ROTATION_2026: List[PitcherStats] = [
    _TB_RASMUSSEN,
    _TB_PEPIOT,
    _TB_MCCLANAHAN,
    _TB_MATZ,
    _TB_MARTINEZ,
]

# -- Bullpen -----------------------------------------------------------------

#: Bryan Baker — RHP, hard-throwing setup man with a wipeout slider;
#: a key bridge arm leading into the late innings.
_TB_BAKER = PitcherStats(
    name="Bryan Baker",
    era=3.40,
    k_per_9=11.0,
    innings_per_start=1.0,
    whip=1.18,
    arm_strength=64.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Hunter Bigge — RHP, power reliever with triple-digit velocity and a
#: filthy slider; used in high-leverage situations.
_TB_BIGGE = PitcherStats(
    name="Hunter Bigge",
    era=3.55,
    k_per_9=11.8,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Cole Sulser — RHP, veteran middle-relief arm with solid command of
#: multiple pitches; provides length and reliability in the bullpen.
_TB_SULSER = PitcherStats(
    name="Cole Sulser",
    era=3.75,
    k_per_9=9.4,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Steven Wilson — RHP, developing reliever with swing-and-miss stuff;
#: adds strikeout potential in middle-relief.
_TB_S_WILSON = PitcherStats(
    name="Steven Wilson",
    era=3.90,
    k_per_9=10.8,
    innings_per_start=1.0,
    whip=1.24,
    arm_strength=60.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: Mason Englert — RHP, tall right-hander with a deceptive delivery and
#: solid fastball-curveball combination; long-relief and setup option.
_TB_ENGLERT = PitcherStats(
    name="Mason Englert",
    era=4.00,
    k_per_9=9.0,
    innings_per_start=1.0,
    whip=1.26,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.78,
)

#: Griffin Jax — CL, RHP, elite closer with a high-spin four-seam and
#: devastating splitter; handles the ninth inning for the Rays.
_TB_JAX = PitcherStats(
    name="Griffin Jax",
    era=2.70,
    k_per_9=12.4,
    innings_per_start=1.0,
    whip=1.02,
    arm_strength=66.0,
    throws="R",
    pitches_per_pa=3.72,
)

#: 2026 Rays bullpen (setup + closer; closer is last entry).
RAYS_BULLPEN_2026: List[PitcherStats] = [
    _TB_BAKER,
    _TB_BIGGE,
    _TB_SULSER,
    _TB_S_WILSON,
    _TB_ENGLERT,
    _TB_JAX,
]


@dataclass
class RaysRoster:
    """
    Bundle of Tampa Bay Rays projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Griffin Jax).

    Examples
    --------
    ::

        roster = RaysRoster.default()
        print(roster.rotation[0].name)   # "Drew Rasmussen"
        print(roster.lineup[3].name)     # "Junior Caminero"
        print(roster.bullpen[-1].name)   # "Griffin Jax"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "RaysRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(RAYS_LINEUP_2026),
            rotation=list(RAYS_ROTATION_2026),
            bullpen=list(RAYS_BULLPEN_2026),
        )


# ---------------------------------------------------------------------------
# Athletics 2026 Depth Chart
# ---------------------------------------------------------------------------

# -- Position starters -------------------------------------------------------

#: Shea Langeliers — C, bats right, strong-armed defensive catcher with
#: improving power production; anchors the A's lineup from behind the plate.
_OAK_LANGELIERS = BatterStats(
    name="Shea Langeliers",
    avg=0.232,
    obp=0.296,
    slg=0.430,
    hr_per_600_pa=24.0,
    sb_per_season=2.0,
    doubles_per_600_pa=24.0,
    games_played=130,
    power_rating=62.0,
    bats="R",
    pitches_per_pa=3.68,
    rbi_per_season=58.0,
    runs_per_season=52.0,
)

#: Nick Kurtz — 1B, left-handed hitting first-round prospect with advanced
#: hit tool and plus raw power; projected as a cornerstone of the Athletics' lineup.
_OAK_KURTZ = BatterStats(
    name="Nick Kurtz",
    avg=0.262,
    obp=0.342,
    slg=0.468,
    hr_per_600_pa=24.0,
    sb_per_season=5.0,
    doubles_per_600_pa=32.0,
    games_played=148,
    power_rating=66.0,
    bats="L",
    pitches_per_pa=3.86,
    rbi_per_season=70.0,
    runs_per_season=68.0,
)

#: Jeff McNeil — 2B, bats left, contact-first veteran with exceptional
#: bat-to-ball skills and low strikeout rates; versatile lineup piece.
_OAK_MCNEIL = BatterStats(
    name="Jeff McNeil",
    avg=0.272,
    obp=0.336,
    slg=0.392,
    hr_per_600_pa=10.0,
    sb_per_season=8.0,
    doubles_per_600_pa=30.0,
    games_played=145,
    power_rating=38.0,
    bats="L",
    pitches_per_pa=3.52,
    rbi_per_season=52.0,
    runs_per_season=62.0,
)

#: Max Muncy — 3B/utility, bats left, selective hitter with elite walk rates
#: and considerable power; veteran presence in the Athletics' lineup.
_OAK_MUNCY = BatterStats(
    name="Max Muncy",
    avg=0.234,
    obp=0.360,
    slg=0.460,
    hr_per_600_pa=28.0,
    sb_per_season=2.0,
    doubles_per_600_pa=24.0,
    games_played=128,
    power_rating=72.0,
    bats="L",
    pitches_per_pa=4.20,
    rbi_per_season=70.0,
    runs_per_season=66.0,
)

#: Jacob Wilson — SS, bats right, athletic young shortstop with excellent
#: range and developing bat; top prospect contributing at the big-league level.
_OAK_WILSON = BatterStats(
    name="Jacob Wilson",
    avg=0.258,
    obp=0.318,
    slg=0.388,
    hr_per_600_pa=12.0,
    sb_per_season=12.0,
    doubles_per_600_pa=28.0,
    games_played=140,
    power_rating=46.0,
    bats="R",
    pitches_per_pa=3.72,
    rbi_per_season=50.0,
    runs_per_season=64.0,
)

#: Tyler Soderstrom — LF/utility, bats left, top prospect known for plus raw
#: power and improving approach; versatile lineup option in left field.
_OAK_SODERSTROM = BatterStats(
    name="Tyler Soderstrom",
    avg=0.248,
    obp=0.315,
    slg=0.438,
    hr_per_600_pa=22.0,
    sb_per_season=4.0,
    doubles_per_600_pa=26.0,
    games_played=132,
    power_rating=62.0,
    bats="L",
    pitches_per_pa=3.74,
    rbi_per_season=56.0,
    runs_per_season=56.0,
)

#: Denzel Clarke — CF, bats right, plus defensive center fielder with
#: impressive speed and improving bat; carries lineup value with legs.
_OAK_CLARKE = BatterStats(
    name="Denzel Clarke",
    avg=0.238,
    obp=0.302,
    slg=0.388,
    hr_per_600_pa=14.0,
    sb_per_season=22.0,
    doubles_per_600_pa=22.0,
    games_played=130,
    power_rating=46.0,
    bats="R",
    pitches_per_pa=3.62,
    rbi_per_season=46.0,
    runs_per_season=60.0,
)

#: Lawrence Butler — RF, bats left, intriguing young outfielder with solid
#: raw power and athleticism; expected to handle right field for the Athletics.
_OAK_BUTLER = BatterStats(
    name="Lawrence Butler",
    avg=0.244,
    obp=0.308,
    slg=0.428,
    hr_per_600_pa=20.0,
    sb_per_season=14.0,
    doubles_per_600_pa=24.0,
    games_played=138,
    power_rating=60.0,
    bats="L",
    pitches_per_pa=3.68,
    rbi_per_season=54.0,
    runs_per_season=58.0,
)

#: Brent Rooker — DH, bats right, high-power designated hitter with
#: exceptional pull-power and notable platoon advantage; the Athletics' run
#: producer in the cleanup role.
_OAK_ROOKER = BatterStats(
    name="Brent Rooker",
    avg=0.248,
    obp=0.326,
    slg=0.506,
    hr_per_600_pa=34.0,
    sb_per_season=4.0,
    doubles_per_600_pa=28.0,
    games_played=148,
    power_rating=82.0,
    bats="R",
    pitches_per_pa=3.80,
    rbi_per_season=90.0,
    runs_per_season=72.0,
)

#: 2026 Athletics projected lineup (depth-chart position-1 starters).
#: Positions: C, 1B, 2B, 3B, SS, LF, CF, RF, DH.
ATHLETICS_LINEUP_2026: List[BatterStats] = [
    _OAK_LANGELIERS,
    _OAK_KURTZ,
    _OAK_MCNEIL,
    _OAK_MUNCY,
    _OAK_WILSON,
    _OAK_SODERSTROM,
    _OAK_CLARKE,
    _OAK_BUTLER,
    _OAK_ROOKER,
]

# -- Starting rotation -------------------------------------------------------

#: Luis Severino — RHP, ace, power fastball/slider combination with
#: experience in big-game situations; leads the Athletics' 2026 rotation.
_OAK_SEVERINO = PitcherStats(
    name="Luis Severino",
    era=3.40,
    k_per_9=9.8,
    innings_per_start=5.8,
    whip=1.22,
    arm_strength=72.0,
    throws="R",
    pitches_per_pa=3.88,
)

#: Jeffrey Springs — LHP, crafty left-hander with deceptive delivery and
#: sharp breaking ball; fills the second rotation slot for the Athletics.
_OAK_SPRINGS = PitcherStats(
    name="Jeffrey Springs",
    era=3.80,
    k_per_9=9.4,
    innings_per_start=5.4,
    whip=1.26,
    arm_strength=58.0,
    throws="L",
    pitches_per_pa=3.84,
)

#: Aaron Civale — RHP, command-oriented mid-rotation starter with
#: plus sinker/change combination; reliable innings-logger.
_OAK_CIVALE = PitcherStats(
    name="Aaron Civale",
    era=4.10,
    k_per_9=8.6,
    innings_per_start=5.4,
    whip=1.28,
    arm_strength=58.0,
    throws="R",
    pitches_per_pa=3.80,
)

#: Jacob Lopez — LHP, fourth-rotation option with improving repertoire
#: and solid ground-ball tendencies.
_OAK_LOPEZ = PitcherStats(
    name="Jacob Lopez",
    era=4.60,
    k_per_9=8.0,
    innings_per_start=5.0,
    whip=1.36,
    arm_strength=52.0,
    throws="L",
    pitches_per_pa=3.76,
)

#: Luis Morales — RHP, young back-end starter with a developing arsenal;
#: fifth-rotation option for the Athletics.
_OAK_MORALES = PitcherStats(
    name="Luis Morales",
    era=5.00,
    k_per_9=8.2,
    innings_per_start=4.8,
    whip=1.42,
    arm_strength=50.0,
    throws="R",
    pitches_per_pa=3.82,
)

#: 2026 Athletics projected starting rotation (rotation order 1–5).
ATHLETICS_ROTATION_2026: List[PitcherStats] = [
    _OAK_SEVERINO,
    _OAK_SPRINGS,
    _OAK_CIVALE,
    _OAK_LOPEZ,
    _OAK_MORALES,
]

# -- Bullpen -----------------------------------------------------------------

#: Justin Sterner — LHP, hard-throwing reliever with plus strikeout rates;
#: setup role for the Athletics bullpen.
_OAK_STERNER = PitcherStats(
    name="Justin Sterner",
    era=3.80,
    k_per_9=11.2,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=64.0,
    throws="L",
    pitches_per_pa=3.74,
)

#: Elvis Alvarado — RHP, power reliever with a blazing fastball and
#: high-leverage capability; mid-relief role in the Athletics' pen.
_OAK_ALVARADO = PitcherStats(
    name="Elvis Alvarado",
    era=3.60,
    k_per_9=10.8,
    innings_per_start=1.0,
    whip=1.22,
    arm_strength=66.0,
    throws="R",
    pitches_per_pa=3.68,
)

#: Jeff Ridgway — LHP, specialist left-hander with deceptive arm angle;
#: key matchup option out of the A's bullpen.
_OAK_RIDGWAY = PitcherStats(
    name="Jeff Ridgway",
    era=3.90,
    k_per_9=9.8,
    innings_per_start=1.0,
    whip=1.26,
    arm_strength=54.0,
    throws="L",
    pitches_per_pa=3.72,
)

#: Luis Medina — RHP, high-velocity arm with triple-digit heat and
#: developing secondary pitches; high-leverage setup option.
_OAK_MEDINA = PitcherStats(
    name="Luis Medina",
    era=3.80,
    k_per_9=11.4,
    innings_per_start=1.0,
    whip=1.26,
    arm_strength=68.0,
    throws="R",
    pitches_per_pa=3.70,
)

#: Nick Anderson — RHP, veteran reliever with sharp slider and good
#: command; experienced bridge arm to the closer.
_OAK_ANDERSON = PitcherStats(
    name="Nick Anderson",
    era=3.70,
    k_per_9=10.6,
    innings_per_start=1.0,
    whip=1.20,
    arm_strength=62.0,
    throws="R",
    pitches_per_pa=3.76,
)

#: Hogan Harris — CL, LHP, electric closer with high-spin fastball and
#: devastating slider; locks down the ninth for the Athletics with top-tier stuff.
_OAK_HARRIS = PitcherStats(
    name="Hogan Harris",
    era=2.75,
    k_per_9=12.4,
    innings_per_start=1.0,
    whip=1.06,
    arm_strength=68.0,
    throws="L",
    pitches_per_pa=3.70,
)

#: 2026 Athletics bullpen (setup + closer; closer is last entry).
ATHLETICS_BULLPEN_2026: List[PitcherStats] = [
    _OAK_STERNER,
    _OAK_ALVARADO,
    _OAK_RIDGWAY,
    _OAK_MEDINA,
    _OAK_ANDERSON,
    _OAK_HARRIS,
]


@dataclass
class AthleticsRoster:
    """
    Bundle of Athletics projected 2026 depth-chart starters, rotation,
    and bullpen.

    Attributes
    ----------
    lineup : list of BatterStats
        Nine position starters (C, 1B, 2B, 3B, SS, LF, CF, RF, DH) drawn from
        the #1-depth-slot of each position on the 2026 depth chart.
    rotation : list of PitcherStats
        Five-man starting rotation (rotation-turn order 1–5).
    bullpen : list of PitcherStats
        Six relievers, closer last (index 5 = Hogan Harris).

    Examples
    --------
    ::

        roster = AthleticsRoster.default()
        print(roster.rotation[0].name)   # "Luis Severino"
        print(roster.lineup[8].name)     # "Brent Rooker"
        print(roster.bullpen[-1].name)   # "Hogan Harris"
    """

    lineup: List[BatterStats] = field(default_factory=list)
    rotation: List[PitcherStats] = field(default_factory=list)
    bullpen: List[PitcherStats] = field(default_factory=list)

    @classmethod
    def default(cls) -> "AthleticsRoster":
        """Return the projected 2026 depth-chart roster (shallow copies)."""
        return cls(
            lineup=list(ATHLETICS_LINEUP_2026),
            rotation=list(ATHLETICS_ROTATION_2026),
            bullpen=list(ATHLETICS_BULLPEN_2026),
        )


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
