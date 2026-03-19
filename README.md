# College Basketball Score Simulator & MLB Player Props Simulator

## MLB Player Props Simulator

`mlb_player_props.py` is a Monte Carlo simulation engine for MLB player prop bets.
It models individual player performance for a single game and applies real-world
environmental adjustments to every projection.

### Props Supported

| Category  | Props                                                         |
|-----------|---------------------------------------------------------------|
| Pitcher   | Strikeouts, Outs Recorded, Runs Allowed, Pitch Count          |
| Batter    | Hits, Doubles, Home Runs, Stolen Bases, Plate Appearances     |

### Environmental Factors

| Factor              | Effect                                                        |
|---------------------|---------------------------------------------------------------|
| **Temperature**     | Warm air → ball travels farther → more HR; cold → more Ks    |
| **Precipitation**   | Rain reduces hit probability and pitcher control              |
| **Humidity**        | High humidity makes the ball heavier, slightly fewer XBH      |
| **Wind direction**  | Blowing out → more HR/hits; blowing in → pitcher-friendly     |
| **Wind speed**      | Amplifies the direction effect proportionally                 |
| **Stadium / Park**  | Per-venue HR, hits, doubles, K, and runs factors              |

### Player Attributes

| Attribute                        | Applies to | Effect                                                  |
|----------------------------------|------------|---------------------------------------------------------|
| `arm_strength` (0–100)           | Pitcher    | Higher → more Ks, fewer runs, deeper outings            |
| `throws` ("R" / "L")             | Pitcher    | Used for platoon split adjustments                      |
| `pitches_per_pa` (default 3.8)   | Pitcher    | Average pitches thrown per batter; drives Pitch Count   |
| `power_rating` (0–100)           | Batter     | Higher → more HRs and doubles                          |
| `bats` ("R" / "L" / "S")        | Batter     | Used for platoon split adjustments                      |
| `pitches_per_pa` (default 3.8)   | Batter     | Average pitches seen per PA; influences Plate Appearances |

### Platoon / Handedness Splits

Opposite-hand matchups (e.g. RHB vs LHP) give the batter a ~4–8 % hit boost and
~7–10 % HR boost.  Same-hand matchups give the pitcher a ~5–6 % K-rate advantage.
Switch hitters (`bats="S"`) are always neutral.

```python
# Apply splits automatically via simulate_matchup
results = sim.simulate_matchup(pitcher, [batter1, batter2])

# Or explicitly per call
sim.simulate_batter(batter, opponent_throws="L")   # RHB vs LHP → batter boost
sim.simulate_pitcher(pitcher, opponent_bats="R")   # LHP vs RHB → fewer Ks
```



Coors Field, Great American Ball Park, Wrigley Field, Fenway Park, Dodger Stadium,
Oracle Park, Petco Park, Truist Park, Yankee Stadium, T-Mobile Park, Kauffman
Stadium, Busch Stadium, Globe Life Field, Minute Maid Park, and a neutral baseline.

### Quick Start

```python
from mlb_player_props import (
    MLBPlayerPropsSimulator, WeatherConditions, WindConditions,
    Stadium, PitcherStats, BatterStats,
)

stadium = Stadium.from_name("Wrigley Field")
weather = WeatherConditions(temp_f=72, precipitation="none", humidity=0.55)
wind    = WindConditions(speed_mph=15, direction="out_to_center")

sim = MLBPlayerPropsSimulator(stadium=stadium, weather=weather, wind=wind,
                              num_simulations=10_000)

# Pitcher props
pitcher = PitcherStats(name="Ace Pitcher", era=3.50, k_per_9=9.5,
                       innings_per_start=6.0, whip=1.15)
sim.print_results(sim.simulate_pitcher(pitcher))

# Batter props
batter = BatterStats(name="Power Hitter", avg=0.285, obp=0.360, slg=0.510,
                     hr_per_600_pa=32, sb_per_season=18,
                     doubles_per_600_pa=38, games_played=162)
sim.print_results(sim.simulate_batter(batter))
```

Run the built-in demo:

```bash
python mlb_player_props.py
```

### Running Tests

```bash
python -m unittest test_mlb_player_props -v
```

---

## Basketball Simulator

Basketball-simulator
