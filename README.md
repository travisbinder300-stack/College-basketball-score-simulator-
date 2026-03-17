# College Basketball Score Simulator & NBA Player Projection Props

A Python toolkit for simulating college basketball scores and projecting NBA player
prop-bet performance using historical game-log data.

---

## NBA Player Projection Props

The `nba_projections` package projects per-game statistics for NBA players and
compares them against sportsbook prop lines, providing **Over/Under recommendations**
with confidence ratings and historical hit rates.

### How It Works

1. **Baseline** – Season-average statistics for each player.
2. **Recent Form** – A rolling average over the last N games (default: 5) is blended
   with the season average (40 % recent form / 60 % season average).
3. **Opponent Adjustment** – Each opponent has a defensive rating relative to the
   league average.  A weak defense (rating > 1.0) boosts projections; a strong
   defense (rating < 1.0) lowers them.
4. **Home/Away Boost** – A small multiplier is applied when the player is at home.
5. **Prop Comparison** – Projected values are compared against user-supplied lines.
   Edge = projection − line.  Confidence is *High* (|edge| ≥ 3.0), *Medium*
   (|edge| ≥ 1.5), or *Low* (|edge| < 1.5).
6. **Historical Hit Rate** – The fraction of logged games where the player exceeded
   the given line.

### Available Players

| ID | Name | Team |
|----|------|------|
| `luka_doncic` | Luka Doncic | DAL |
| `jayson_tatum` | Jayson Tatum | BOS |
| `nikola_jokic` | Nikola Jokic | DEN |
| `stephen_curry` | Stephen Curry | GSW |
| `giannis_antetokounmpo` | Giannis Antetokounmpo | MIL |
| `kevin_durant` | Kevin Durant | PHX |
| `lebron_james` | LeBron James | LAL |
| `joel_embiid` | Joel Embiid | PHI |

### Supported Stats

| Stat key | Description |
|----------|-------------|
| `pts` | Points |
| `reb` | Rebounds |
| `ast` | Assists |
| `stl` | Steals |
| `blk` | Blocks |
| `pts_reb_ast` | Points + Rebounds + Assists (combo) |

### Quick Start

```bash
# No external dependencies required — uses Python standard library only.

# List available players
python main.py --list-players

# Project Luka Doncic at home vs Golden State Warriors
python main.py --player luka_doncic --opponent GSW

# Add sportsbook prop lines for Over/Under recommendations
python main.py --player luka_doncic --opponent GSW \
    --props pts=28.5 reb=8.5 ast=9.5 pts_reb_ast=47.5

# Away game
python main.py --player nikola_jokic --opponent LAL --away \
    --props pts=25.5 reb=11.5 ast=8.5

# Project all players vs the same opponent
python main.py --all-players --opponent BOS

# Use a 3-game rolling window instead of 5
python main.py --player stephen_curry --opponent OKC --recent-games 3
```

#### Example Output

```
============================================================
  NBA PLAYER PROJECTION REPORT
============================================================
  Player   : Luka Doncic (DAL)
  Matchup  : Home vs GSW
------------------------------------------------------------
  STAT           PROJ    ±STD    LINE    EDGE  REC     CONF       HIT%
------------------------------------------------------------
  Points         33.7     5.9    28.5    +5.2  OVER    High       80%
  Rebounds        9.3     1.9     8.5    +0.8  OVER    Low        70%
  Assists         9.7     1.9     9.5    +0.2  OVER    Low        50%
  Steals          1.4     0.7
  Blocks          0.5     0.5
  Pts+Reb+Ast    52.7       —    47.5    +5.2  OVER    High       60%
============================================================
```

### Using the Python API

```python
from nba_projections import PlayerProjection, PropAnalyzer

# Raw projection
proj = PlayerProjection("luka_doncic", opponent="GSW", home=True)
print(proj.project())
# {'pts': 33.7, 'reb': 9.3, 'ast': 9.7, 'stl': 1.4, 'blk': 0.5, 'pts_reb_ast': 52.7}

# Prop analysis
analyzer = PropAnalyzer("luka_doncic", opponent="GSW", home=True)
result = analyzer.evaluate_prop("pts", 28.5)
print(result.recommendation, result.confidence, result.hit_rate)
# OVER High 0.8

# Full report
print(analyzer.display_report({"pts": 28.5, "reb": 8.5, "ast": 9.5}))
```

### Project Structure

```
nba_projections/
  __init__.py        – Package exports
  player_data.py     – Historical game logs & opponent defensive ratings
  projections.py     – Projection engine (PlayerProjection class)
  props.py           – Prop line analyzer (PropAnalyzer, PropResult classes)
main.py              – Command-line interface
tests/
  test_nba_projections.py  – Unit tests (32 tests)
```

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

*Data is sample/illustrative. Always verify against official sources before
making real decisions.*
