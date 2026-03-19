# College Basketball Score Simulator & MLB Player Props Simulator

## MLB Player Props Simulator

`mlb_player_props.py` is a Monte Carlo simulation engine for MLB player prop bets.
It models individual player performance for a single game and applies real-world
environmental adjustments to every projection.

### Props Supported

| Category  | Props                                             |
|-----------|---------------------------------------------------|
| Pitcher   | Strikeouts, Outs Recorded, Runs Allowed           |
| Batter    | Hits, Doubles, Home Runs, Stolen Bases            |

### Environmental Factors

| Factor              | Effect                                                        |
|---------------------|---------------------------------------------------------------|
| **Temperature**     | Warm air → ball travels farther → more HR; cold → more Ks    |
| **Precipitation**   | Rain reduces hit probability and pitcher control              |
| **Humidity**        | High humidity makes the ball heavier, slightly fewer XBH      |
| **Wind direction**  | Blowing out → more HR/hits; blowing in → pitcher-friendly     |
| **Wind speed**      | Amplifies the direction effect proportionally                 |
| **Stadium / Park**  | Per-venue HR, hits, doubles, K, and runs factors              |

### Built-in Stadiums

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
