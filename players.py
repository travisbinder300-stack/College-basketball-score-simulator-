"""
players.py
----------
Add NBA players here. Each player is a dictionary with their current team
and season statistics. The projection engine will use these stats to
calculate prop projections.

Data source
-----------
Stats are sourced from Props Madness (https://propsmadness.com).
Example player reference: https://propsmadness.com/?player=204&match=5980

Roster template columns
------------------------
Team | Name | Pos | GP | PTS | FGM | FG% | 3PM | 3PA | 3P% | FTM | FT% | Reb | Ast | STL | BLK | TO

Field reference
---------------
Required fields
~~~~~~~~~~~~~~~
team                      : str   - Current NBA team (e.g. "Boston Celtics")         → Team
name                      : str   - Player's full name                                → Name
position                  : str   - Primary position: PG, SG, SF, PF, or C           → Pos
games_played              : int   - Games played this season                          → GP
points_per_game           : float - Average points per game                           → PTS
fgm                       : float - Field goals made per game                         → FGM
field_goal_pct            : float - Field goal percentage (0.0 – 1.0)                 → FG%
three_pointers_per_game   : float - 3-pointers made per game                          → 3PM
three_pointers_attempted  : float - 3-point attempts per game                         → 3PA
three_point_pct           : float - Three-point percentage (0.0 – 1.0)               → 3P%
ftm                       : float - Free throws made per game                         → FTM
free_throw_pct            : float - Free-throw percentage (0.0 – 1.0)                → FT%
rebounds_per_game         : float - Average total rebounds per game                   → Reb
assists_per_game          : float - Average assists per game                          → Ast
steals_per_game           : float - Average steals per game                           → STL
blocks_per_game           : float - Average blocks per game                           → BLK
turnovers_per_game        : float - Average turnovers per game                        → TO

Optional fields (improve projection accuracy when provided)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
minutes_per_game          : float - Average minutes per game (optional)
home_points_per_game      : float - Points per game at home (optional)
away_points_per_game      : float - Points per game on the road (optional)
last_5_points             : list  - Points in each of the last 5 games (optional)
last_5_rebounds           : list  - Rebounds in each of the last 5 games (optional)
last_5_assists            : list  - Assists in each of the last 5 games (optional)

Example entry (uncomment and fill in real values):
--------------------------------------------------
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
},
"""

# ============================================================
# Add your players below. Each entry follows the format above.
# ============================================================

PLAYERS = [
    # Add players here following the format in the header above.
]
