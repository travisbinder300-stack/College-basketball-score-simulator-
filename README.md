# NBA Player Prop Projections

Generate stat-line projections for NBA player props.

---

Generate stat-line projections for NBA player props based on season averages,
recent form (last 5 games), and home/away context.

### Requirements

- Python 3.8 or higher (no external dependencies)

### Roster Template

```
Team | Name | Pos | GP | PTS | FGM | FG% | 3PM | 3PA | 3P% | FTM | FT% | Reb | Ast | STL | BLK | TO
```

| Column | Field name | Description |
|---|---|---|
| Team | `team` | Current NBA team |
| Name | `name` | Player's full name |
| Pos  | `position` | PG / SG / SF / PF / C |
| GP   | `games_played` | Games played this season |
| PTS  | `points_per_game` | Points per game |
| FGM  | `fgm` | Field goals made per game |
| FG%  | `field_goal_pct` | FG percentage (0.0 – 1.0) |
| 3PM  | `three_pointers_per_game` | 3-pointers made per game |
| 3PA  | `three_pointers_attempted` | 3-point attempts per game |
| 3P%  | `three_point_pct` | 3-point percentage (0.0 – 1.0) |
| FTM  | `ftm` | Free throws made per game |
| FT%  | `free_throw_pct` | FT percentage (0.0 – 1.0) |
| Reb  | `rebounds_per_game` | Total rebounds per game |
| Ast  | `assists_per_game` | Assists per game |
| STL  | `steals_per_game` | Steals per game |
| BLK  | `blocks_per_game` | Blocks per game |
| TO   | `turnovers_per_game` | Turnovers per game |

### Setup – Add Your Players

Open **`players.py`** and add player entries to the `PLAYERS` list.
Each entry is a Python dictionary following the roster template above.

```python
PLAYERS = [
    {
        "team": "Team Name",
        "name": "Player Name",
        "position": "PG",
        "games_played": 50,
        "points_per_game": 25.4,
        "fgm": 9.8,
        "field_goal_pct": 0.471,
        "three_pointers_per_game": 2.8,
        "three_pointers_attempted": 7.4,
        "three_point_pct": 0.378,
        "ftm": 3.0,
        "free_throw_pct": 0.856,
        "rebounds_per_game": 5.1,
        "assists_per_game": 8.3,
        "steals_per_game": 1.4,
        "blocks_per_game": 0.4,
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
============================================================
  Player Name  |  Team Name  |  PG
  Games: 50   Location: Home
============================================================
  Stat                          Season Avg  Projection
  ----------------------------------------------------
  PTS  Points                        25.4        26.1
  FGM  FG Made                        9.8           —
  FG%  FG Pct                       47.1%           —
  3PM  3-Pt Made                      2.8         2.8
  3PA  3-Pt Att                       7.4           —
  3P%  3-Pt Pct                      37.8%          —
  FTM  FT Made                        3.0           —
  FT%  FT Pct                        85.6%          —
  REB  Rebounds                       5.1         5.2
  AST  Assists                        8.3         8.5
  STL  Steals                         1.4         1.4
  BLK  Blocks                         0.4         0.4
  TO   Turnovers                      2.9         2.9
  ----------------------------------------------------
  PRA  Pts+Reb+Ast                      —        39.8
  S+B  Stl+Blk                          —         1.8
============================================================
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

