# NBA Player Prop Projections

Generate stat-line projections for NBA player props.

---

Generate stat-line projections for NBA player props based on season averages,
recent form (last 5 games), and home/away context.

### Requirements

- Python 3.8 or higher (no external dependencies)

### Setup – Add Your Players

Open **`players.py`** and add player entries to the `PLAYERS` list.
Each entry is a Python dictionary. See the file header for the full field
reference and an example entry.

```python
PLAYERS = [
    {
        "name": "Player Name",
        "team": "Team Name",
        "position": "PG",
        "games_played": 50,
        "minutes_per_game": 34.2,
        "points_per_game": 25.4,
        "rebounds_per_game": 5.1,
        "assists_per_game": 8.3,
        "steals_per_game": 1.4,
        "blocks_per_game": 0.4,
        "three_pointers_per_game": 2.8,
        "field_goal_pct": 0.471,
        "three_point_pct": 0.378,
        "free_throw_pct": 0.856,
        "turnovers_per_game": 2.9,
        # Optional — for more precise projections:
        # "home_points_per_game": 27.1,
        # "away_points_per_game": 23.8,
        # "last_5_points":   [28, 31, 22, 25, 30],
        # "last_5_rebounds": [4, 6, 5, 5, 7],
        # "last_5_assists":  [9, 7, 10, 8, 6],
    },
]
```

### Usage

```bash
# Project all players (home game)
python main.py

# Project all players (away game)
python main.py --away

# Project a single player (partial name match, case-insensitive)
python main.py --player "Player Name"

# Show only one prop category for all players
python main.py --prop points
python main.py --prop rebounds
python main.py --prop assists
python main.py --prop steals
python main.py --prop blocks
python main.py --prop three_pointers
python main.py --prop turnovers
python main.py --prop pra          # Points + Rebounds + Assists
python main.py --prop steals_blocks

# Combine flags
python main.py --away --player "Player Name" --prop pra
```

### Sample Output

```
========================================================
  Player Name  |  Team Name  |  PG
  Games: 50   Location: Home
========================================================
  Prop                          Projection
  --------------------------------------
  Points                              26.1
  Rebounds                             5.2
  Assists                              8.5
  Steals                               1.4
  Blocks                               0.4
  3-Pointers Made                      2.8
  Turnovers                            2.9
  --------------------------------------
  Pts + Reb + Ast (PRA)               39.8
  Steals + Blocks                      1.8
========================================================
```

### Prop Categories

| Category | Flag value | Description |
|---|---|---|
| Points | `points` | Projected points scored |
| Rebounds | `rebounds` | Projected total rebounds |
| Assists | `assists` | Projected assists |
| Steals | `steals` | Projected steals |
| Blocks | `blocks` | Projected blocks |
| 3-Pointers Made | `three_pointers` | Projected 3PM |
| Turnovers | `turnovers` | Projected turnovers |
| PRA | `pra` | Points + Rebounds + Assists |
| Steals + Blocks | `steals_blocks` | Combined defensive stats |

### How Projections Are Calculated

| Input | Weight |
|---|---|
| Season average | 70 % |
| Last-5-game average (if provided) | 30 % |

When `home_points_per_game` or `away_points_per_game` are provided, the
matching split replaces the season average for the points projection.


