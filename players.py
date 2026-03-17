"""
players.py
----------
Add NBA players here. Each player is a dictionary with their current team
and season statistics. The projection engine will use these stats to
calculate prop projections.

Field reference
---------------
name                   : str   - Player's full name
team                   : str   - Current NBA team (e.g. "Boston Celtics")
position               : str   - Primary position: PG, SG, SF, PF, or C
games_played           : int   - Games played this season
minutes_per_game       : float - Average minutes per game
points_per_game        : float - Average points per game
rebounds_per_game      : float - Average total rebounds per game
assists_per_game       : float - Average assists per game
steals_per_game        : float - Average steals per game
blocks_per_game        : float - Average blocks per game
three_pointers_per_game: float - Average 3-pointers made per game
field_goal_pct         : float - Field goal percentage (0.0 – 1.0)
three_point_pct        : float - Three-point percentage  (0.0 – 1.0)
free_throw_pct         : float - Free-throw percentage   (0.0 – 1.0)
turnovers_per_game     : float - Average turnovers per game

Optional performance-context fields
-------------------------------------
home_points_per_game   : float - Points per game at home  (optional)
away_points_per_game   : float - Points per game on the road (optional)
last_5_points          : list  - Points scored in each of the last 5 games (optional)
last_5_rebounds        : list  - Rebounds in each of the last 5 games (optional)
last_5_assists         : list  - Assists in each of the last 5 games (optional)

Example entry (uncomment and fill in real values):
--------------------------------------------------
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
},
"""

# ============================================================
# Add your players below. Each entry follows the format above.
# ============================================================

PLAYERS = [
    # Add player dictionaries here
]
