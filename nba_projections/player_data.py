"""
Sample NBA player game log data used for projection calculations.

Each player entry includes:
  - name: Player's full name
  - team: Current team abbreviation
  - position: Primary position
  - season_avg: Season-average stats
  - game_log: List of recent game results (last 10 games, most recent first)
      Each game has: pts, reb, ast, stl, blk, min, fg_pct, ft_pct, opponent, home

Opponent difficulty ratings (opp_def_rating) represent a team's defensive
rating relative to league average.  Values > 1.0 mean easier than average
(worse defense), values < 1.0 mean harder than average (better defense).
"""

OPPONENT_DEF_RATINGS = {
    "BOS": 0.92,
    "MIA": 0.95,
    "NYK": 0.97,
    "PHI": 0.98,
    "BKN": 1.05,
    "TOR": 1.03,
    "CLE": 0.96,
    "MIL": 0.93,
    "IND": 1.02,
    "DET": 1.08,
    "CHI": 1.01,
    "ATL": 1.06,
    "ORL": 0.99,
    "WAS": 1.07,
    "CHA": 1.09,
    "MEM": 0.94,
    "GSW": 0.96,
    "LAL": 1.00,
    "LAC": 0.97,
    "PHX": 0.98,
    "SAC": 1.04,
    "POR": 1.06,
    "UTA": 1.01,
    "DEN": 0.95,
    "MIN": 0.93,
    "OKC": 0.92,
    "DAL": 0.99,
    "SAS": 1.05,
    "HOU": 1.04,
    "NOP": 1.02,
}

PLAYERS = {
    "luka_doncic": {
        "name": "Luka Doncic",
        "team": "DAL",
        "position": "PG/SF",
        "season_avg": {
            "pts": 33.9,
            "reb": 9.2,
            "ast": 9.8,
            "stl": 1.4,
            "blk": 0.5,
            "min": 36.2,
            "fg_pct": 0.480,
            "ft_pct": 0.786,
        },
        "game_log": [
            {"pts": 35, "reb": 10, "ast": 11, "stl": 2, "blk": 0, "min": 38, "fg_pct": 0.500, "ft_pct": 0.800, "opponent": "OKC", "home": True},
            {"pts": 28, "reb": 8,  "ast": 9,  "stl": 1, "blk": 1, "min": 35, "fg_pct": 0.440, "ft_pct": 0.750, "opponent": "PHX", "home": False},
            {"pts": 41, "reb": 11, "ast": 10, "stl": 1, "blk": 0, "min": 39, "fg_pct": 0.520, "ft_pct": 0.833, "opponent": "LAL", "home": True},
            {"pts": 32, "reb": 9,  "ast": 8,  "stl": 2, "blk": 1, "min": 37, "fg_pct": 0.480, "ft_pct": 0.800, "opponent": "GSW", "home": False},
            {"pts": 38, "reb": 12, "ast": 12, "stl": 1, "blk": 0, "min": 40, "fg_pct": 0.510, "ft_pct": 0.778, "opponent": "SAC", "home": True},
            {"pts": 26, "reb": 7,  "ast": 9,  "stl": 0, "blk": 0, "min": 34, "fg_pct": 0.420, "ft_pct": 0.700, "opponent": "DEN", "home": False},
            {"pts": 36, "reb": 10, "ast": 11, "stl": 2, "blk": 1, "min": 38, "fg_pct": 0.490, "ft_pct": 0.810, "opponent": "MEM", "home": True},
            {"pts": 30, "reb": 8,  "ast": 7,  "stl": 1, "blk": 0, "min": 36, "fg_pct": 0.460, "ft_pct": 0.760, "opponent": "MIN", "home": False},
            {"pts": 44, "reb": 13, "ast": 13, "stl": 2, "blk": 0, "min": 41, "fg_pct": 0.540, "ft_pct": 0.850, "opponent": "SAS", "home": True},
            {"pts": 29, "reb": 9,  "ast": 8,  "stl": 1, "blk": 1, "min": 35, "fg_pct": 0.450, "ft_pct": 0.770, "opponent": "HOU", "home": False},
        ],
    },
    "jayson_tatum": {
        "name": "Jayson Tatum",
        "team": "BOS",
        "position": "SF/PF",
        "season_avg": {
            "pts": 26.9,
            "reb": 8.1,
            "ast": 4.9,
            "stl": 1.1,
            "blk": 0.6,
            "min": 35.8,
            "fg_pct": 0.470,
            "ft_pct": 0.831,
        },
        "game_log": [
            {"pts": 31, "reb": 9,  "ast": 5, "stl": 1, "blk": 1, "min": 37, "fg_pct": 0.490, "ft_pct": 0.850, "opponent": "NYK", "home": True},
            {"pts": 24, "reb": 7,  "ast": 4, "stl": 0, "blk": 0, "min": 34, "fg_pct": 0.440, "ft_pct": 0.800, "opponent": "MIA", "home": False},
            {"pts": 33, "reb": 10, "ast": 6, "stl": 2, "blk": 1, "min": 38, "fg_pct": 0.510, "ft_pct": 0.833, "opponent": "PHI", "home": True},
            {"pts": 28, "reb": 8,  "ast": 5, "stl": 1, "blk": 0, "min": 36, "fg_pct": 0.460, "ft_pct": 0.810, "opponent": "BKN", "home": False},
            {"pts": 22, "reb": 6,  "ast": 3, "stl": 0, "blk": 1, "min": 33, "fg_pct": 0.420, "ft_pct": 0.778, "opponent": "CLE", "home": True},
            {"pts": 36, "reb": 11, "ast": 7, "stl": 2, "blk": 0, "min": 39, "fg_pct": 0.530, "ft_pct": 0.860, "opponent": "MIL", "home": False},
            {"pts": 25, "reb": 8,  "ast": 4, "stl": 1, "blk": 1, "min": 35, "fg_pct": 0.450, "ft_pct": 0.820, "opponent": "TOR", "home": True},
            {"pts": 29, "reb": 9,  "ast": 5, "stl": 1, "blk": 0, "min": 37, "fg_pct": 0.480, "ft_pct": 0.840, "opponent": "IND", "home": False},
            {"pts": 18, "reb": 5,  "ast": 3, "stl": 0, "blk": 0, "min": 30, "fg_pct": 0.380, "ft_pct": 0.750, "opponent": "DET", "home": True},
            {"pts": 32, "reb": 10, "ast": 6, "stl": 2, "blk": 1, "min": 38, "fg_pct": 0.500, "ft_pct": 0.870, "opponent": "CHI", "home": False},
        ],
    },
    "nikola_jokic": {
        "name": "Nikola Jokic",
        "team": "DEN",
        "position": "C",
        "season_avg": {
            "pts": 26.4,
            "reb": 12.4,
            "ast": 9.0,
            "stl": 1.3,
            "blk": 0.9,
            "min": 34.6,
            "fg_pct": 0.583,
            "ft_pct": 0.815,
        },
        "game_log": [
            {"pts": 28, "reb": 13, "ast": 10, "stl": 2, "blk": 1, "min": 36, "fg_pct": 0.600, "ft_pct": 0.833, "opponent": "LAL", "home": True},
            {"pts": 22, "reb": 11, "ast": 8,  "stl": 1, "blk": 1, "min": 33, "fg_pct": 0.560, "ft_pct": 0.800, "opponent": "GSW", "home": False},
            {"pts": 31, "reb": 15, "ast": 12, "stl": 2, "blk": 0, "min": 37, "fg_pct": 0.610, "ft_pct": 0.840, "opponent": "PHX", "home": True},
            {"pts": 24, "reb": 10, "ast": 9,  "stl": 0, "blk": 2, "min": 34, "fg_pct": 0.570, "ft_pct": 0.790, "opponent": "LAC", "home": False},
            {"pts": 30, "reb": 14, "ast": 11, "stl": 1, "blk": 1, "min": 36, "fg_pct": 0.595, "ft_pct": 0.820, "opponent": "OKC", "home": True},
            {"pts": 18, "reb": 9,  "ast": 7,  "stl": 1, "blk": 0, "min": 31, "fg_pct": 0.530, "ft_pct": 0.750, "opponent": "MIN", "home": False},
            {"pts": 35, "reb": 16, "ast": 13, "stl": 2, "blk": 1, "min": 38, "fg_pct": 0.630, "ft_pct": 0.857, "opponent": "MEM", "home": True},
            {"pts": 25, "reb": 12, "ast": 8,  "stl": 1, "blk": 1, "min": 35, "fg_pct": 0.575, "ft_pct": 0.810, "opponent": "UTA", "home": False},
            {"pts": 29, "reb": 13, "ast": 10, "stl": 0, "blk": 2, "min": 36, "fg_pct": 0.590, "ft_pct": 0.830, "opponent": "SAC", "home": True},
            {"pts": 27, "reb": 11, "ast": 9,  "stl": 1, "blk": 1, "min": 34, "fg_pct": 0.580, "ft_pct": 0.800, "opponent": "DAL", "home": False},
        ],
    },
    "stephen_curry": {
        "name": "Stephen Curry",
        "team": "GSW",
        "position": "PG",
        "season_avg": {
            "pts": 29.4,
            "reb": 6.1,
            "ast": 6.3,
            "stl": 1.2,
            "blk": 0.4,
            "min": 34.5,
            "fg_pct": 0.491,
            "ft_pct": 0.922,
        },
        "game_log": [
            {"pts": 34, "reb": 7,  "ast": 7, "stl": 1, "blk": 0, "min": 36, "fg_pct": 0.510, "ft_pct": 0.933, "opponent": "LAL", "home": True},
            {"pts": 22, "reb": 5,  "ast": 5, "stl": 0, "blk": 1, "min": 31, "fg_pct": 0.430, "ft_pct": 0.900, "opponent": "BOS", "home": False},
            {"pts": 40, "reb": 8,  "ast": 8, "stl": 2, "blk": 0, "min": 38, "fg_pct": 0.550, "ft_pct": 0.944, "opponent": "PHX", "home": True},
            {"pts": 27, "reb": 6,  "ast": 6, "stl": 1, "blk": 0, "min": 34, "fg_pct": 0.480, "ft_pct": 0.917, "opponent": "DEN", "home": False},
            {"pts": 32, "reb": 7,  "ast": 7, "stl": 1, "blk": 0, "min": 35, "fg_pct": 0.500, "ft_pct": 0.929, "opponent": "MIN", "home": True},
            {"pts": 19, "reb": 4,  "ast": 4, "stl": 0, "blk": 0, "min": 29, "fg_pct": 0.400, "ft_pct": 0.875, "opponent": "MEM", "home": False},
            {"pts": 38, "reb": 8,  "ast": 8, "stl": 2, "blk": 1, "min": 38, "fg_pct": 0.540, "ft_pct": 0.950, "opponent": "OKC", "home": True},
            {"pts": 29, "reb": 6,  "ast": 6, "stl": 1, "blk": 0, "min": 35, "fg_pct": 0.490, "ft_pct": 0.923, "opponent": "SAC", "home": False},
            {"pts": 35, "reb": 7,  "ast": 7, "stl": 2, "blk": 0, "min": 37, "fg_pct": 0.520, "ft_pct": 0.938, "opponent": "NOP", "home": True},
            {"pts": 24, "reb": 5,  "ast": 5, "stl": 0, "blk": 1, "min": 32, "fg_pct": 0.460, "ft_pct": 0.900, "opponent": "POR", "home": False},
        ],
    },
    "giannis_antetokounmpo": {
        "name": "Giannis Antetokounmpo",
        "team": "MIL",
        "position": "PF/C",
        "season_avg": {
            "pts": 30.4,
            "reb": 11.5,
            "ast": 6.5,
            "stl": 1.2,
            "blk": 1.1,
            "min": 35.2,
            "fg_pct": 0.611,
            "ft_pct": 0.657,
        },
        "game_log": [
            {"pts": 35, "reb": 13, "ast": 7, "stl": 1, "blk": 1, "min": 37, "fg_pct": 0.630, "ft_pct": 0.667, "opponent": "CHI", "home": True},
            {"pts": 28, "reb": 10, "ast": 5, "stl": 0, "blk": 2, "min": 33, "fg_pct": 0.590, "ft_pct": 0.640, "opponent": "DET", "home": False},
            {"pts": 38, "reb": 14, "ast": 8, "stl": 2, "blk": 1, "min": 39, "fg_pct": 0.650, "ft_pct": 0.680, "opponent": "IND", "home": True},
            {"pts": 30, "reb": 11, "ast": 6, "stl": 1, "blk": 0, "min": 35, "fg_pct": 0.610, "ft_pct": 0.650, "opponent": "ATL", "home": False},
            {"pts": 25, "reb": 9,  "ast": 5, "stl": 0, "blk": 1, "min": 32, "fg_pct": 0.570, "ft_pct": 0.620, "opponent": "BOS", "home": True},
            {"pts": 40, "reb": 15, "ast": 9, "stl": 2, "blk": 2, "min": 40, "fg_pct": 0.670, "ft_pct": 0.700, "opponent": "PHI", "home": False},
            {"pts": 32, "reb": 12, "ast": 7, "stl": 1, "blk": 1, "min": 36, "fg_pct": 0.615, "ft_pct": 0.660, "opponent": "ORL", "home": True},
            {"pts": 27, "reb": 10, "ast": 5, "stl": 0, "blk": 0, "min": 34, "fg_pct": 0.595, "ft_pct": 0.630, "opponent": "WAS", "home": False},
            {"pts": 34, "reb": 13, "ast": 8, "stl": 2, "blk": 2, "min": 38, "fg_pct": 0.635, "ft_pct": 0.675, "opponent": "MIA", "home": True},
            {"pts": 22, "reb": 8,  "ast": 4, "stl": 0, "blk": 1, "min": 30, "fg_pct": 0.555, "ft_pct": 0.600, "opponent": "NYK", "home": False},
        ],
    },
    "kevin_durant": {
        "name": "Kevin Durant",
        "team": "PHX",
        "position": "SF/PF",
        "season_avg": {
            "pts": 27.1,
            "reb": 6.6,
            "ast": 5.0,
            "stl": 0.9,
            "blk": 1.2,
            "min": 35.1,
            "fg_pct": 0.526,
            "ft_pct": 0.856,
        },
        "game_log": [
            {"pts": 30, "reb": 7,  "ast": 5, "stl": 1, "blk": 1, "min": 36, "fg_pct": 0.540, "ft_pct": 0.867, "opponent": "LAL", "home": True},
            {"pts": 24, "reb": 6,  "ast": 4, "stl": 0, "blk": 1, "min": 34, "fg_pct": 0.500, "ft_pct": 0.840, "opponent": "GSW", "home": False},
            {"pts": 33, "reb": 8,  "ast": 6, "stl": 1, "blk": 2, "min": 37, "fg_pct": 0.560, "ft_pct": 0.880, "opponent": "DEN", "home": True},
            {"pts": 27, "reb": 6,  "ast": 5, "stl": 0, "blk": 1, "min": 35, "fg_pct": 0.520, "ft_pct": 0.850, "opponent": "LAC", "home": False},
            {"pts": 22, "reb": 5,  "ast": 3, "stl": 1, "blk": 0, "min": 32, "fg_pct": 0.490, "ft_pct": 0.820, "opponent": "MIN", "home": True},
            {"pts": 35, "reb": 9,  "ast": 7, "stl": 1, "blk": 2, "min": 38, "fg_pct": 0.570, "ft_pct": 0.900, "opponent": "OKC", "home": False},
            {"pts": 28, "reb": 7,  "ast": 5, "stl": 0, "blk": 1, "min": 35, "fg_pct": 0.530, "ft_pct": 0.860, "opponent": "SAC", "home": True},
            {"pts": 25, "reb": 6,  "ast": 4, "stl": 1, "blk": 1, "min": 34, "fg_pct": 0.510, "ft_pct": 0.845, "opponent": "UTA", "home": False},
            {"pts": 31, "reb": 8,  "ast": 6, "stl": 1, "blk": 2, "min": 37, "fg_pct": 0.550, "ft_pct": 0.875, "opponent": "POR", "home": True},
            {"pts": 19, "reb": 4,  "ast": 3, "stl": 0, "blk": 0, "min": 29, "fg_pct": 0.470, "ft_pct": 0.800, "opponent": "DAL", "home": False},
        ],
    },
    "lebron_james": {
        "name": "LeBron James",
        "team": "LAL",
        "position": "SF/PF",
        "season_avg": {
            "pts": 25.7,
            "reb": 7.3,
            "ast": 8.3,
            "stl": 1.3,
            "blk": 0.6,
            "min": 35.3,
            "fg_pct": 0.540,
            "ft_pct": 0.749,
        },
        "game_log": [
            {"pts": 28, "reb": 8,  "ast": 9, "stl": 1, "blk": 1, "min": 36, "fg_pct": 0.560, "ft_pct": 0.760, "opponent": "GSW", "home": True},
            {"pts": 22, "reb": 6,  "ast": 7, "stl": 0, "blk": 0, "min": 33, "fg_pct": 0.510, "ft_pct": 0.720, "opponent": "PHX", "home": False},
            {"pts": 32, "reb": 9,  "ast": 11,"stl": 2, "blk": 1, "min": 38, "fg_pct": 0.580, "ft_pct": 0.780, "opponent": "DEN", "home": True},
            {"pts": 25, "reb": 7,  "ast": 8, "stl": 1, "blk": 0, "min": 35, "fg_pct": 0.535, "ft_pct": 0.750, "opponent": "LAC", "home": False},
            {"pts": 20, "reb": 5,  "ast": 6, "stl": 0, "blk": 0, "min": 31, "fg_pct": 0.490, "ft_pct": 0.700, "opponent": "MIN", "home": True},
            {"pts": 35, "reb": 10, "ast": 12,"stl": 2, "blk": 1, "min": 39, "fg_pct": 0.600, "ft_pct": 0.800, "opponent": "OKC", "home": False},
            {"pts": 27, "reb": 7,  "ast": 9, "stl": 1, "blk": 0, "min": 35, "fg_pct": 0.545, "ft_pct": 0.755, "opponent": "SAC", "home": True},
            {"pts": 23, "reb": 6,  "ast": 7, "stl": 0, "blk": 1, "min": 33, "fg_pct": 0.520, "ft_pct": 0.730, "opponent": "UTA", "home": False},
            {"pts": 30, "reb": 9,  "ast": 10,"stl": 2, "blk": 1, "min": 37, "fg_pct": 0.570, "ft_pct": 0.770, "opponent": "POR", "home": True},
            {"pts": 18, "reb": 4,  "ast": 5, "stl": 0, "blk": 0, "min": 28, "fg_pct": 0.460, "ft_pct": 0.690, "opponent": "BOS", "home": False},
        ],
    },
    "joel_embiid": {
        "name": "Joel Embiid",
        "team": "PHI",
        "position": "C",
        "season_avg": {
            "pts": 34.7,
            "reb": 11.0,
            "ast": 5.6,
            "stl": 1.0,
            "blk": 1.7,
            "min": 34.6,
            "fg_pct": 0.528,
            "ft_pct": 0.876,
        },
        "game_log": [
            {"pts": 38, "reb": 12, "ast": 6, "stl": 1, "blk": 2, "min": 36, "fg_pct": 0.550, "ft_pct": 0.889, "opponent": "BOS", "home": True},
            {"pts": 30, "reb": 10, "ast": 5, "stl": 0, "blk": 1, "min": 33, "fg_pct": 0.510, "ft_pct": 0.860, "opponent": "MIA", "home": False},
            {"pts": 42, "reb": 14, "ast": 7, "stl": 2, "blk": 3, "min": 38, "fg_pct": 0.580, "ft_pct": 0.900, "opponent": "NYK", "home": True},
            {"pts": 34, "reb": 11, "ast": 5, "stl": 1, "blk": 2, "min": 35, "fg_pct": 0.535, "ft_pct": 0.875, "opponent": "BKN", "home": False},
            {"pts": 28, "reb": 9,  "ast": 4, "stl": 0, "blk": 1, "min": 32, "fg_pct": 0.500, "ft_pct": 0.840, "opponent": "CLE", "home": True},
            {"pts": 45, "reb": 15, "ast": 8, "stl": 2, "blk": 2, "min": 39, "fg_pct": 0.600, "ft_pct": 0.920, "opponent": "MIL", "home": False},
            {"pts": 35, "reb": 12, "ast": 6, "stl": 1, "blk": 2, "min": 36, "fg_pct": 0.540, "ft_pct": 0.880, "opponent": "TOR", "home": True},
            {"pts": 29, "reb": 10, "ast": 5, "stl": 0, "blk": 1, "min": 33, "fg_pct": 0.515, "ft_pct": 0.855, "opponent": "IND", "home": False},
            {"pts": 40, "reb": 13, "ast": 7, "stl": 2, "blk": 3, "min": 38, "fg_pct": 0.565, "ft_pct": 0.895, "opponent": "DET", "home": True},
            {"pts": 22, "reb": 8,  "ast": 3, "stl": 0, "blk": 0, "min": 28, "fg_pct": 0.460, "ft_pct": 0.810, "opponent": "CHI", "home": False},
        ],
    },
}


def get_player(player_id: str) -> dict:
    """Return data for a single player by ID key.

    Args:
        player_id: Lowercase underscore key, e.g. 'luka_doncic'.

    Returns:
        Player dictionary.

    Raises:
        KeyError: If the player ID is not found.
    """
    if player_id not in PLAYERS:
        raise KeyError(f"Player '{player_id}' not found. Available: {list(PLAYERS.keys())}")
    return PLAYERS[player_id]


def get_all_players() -> list:
    """Return a list of all player IDs."""
    return list(PLAYERS.keys())
