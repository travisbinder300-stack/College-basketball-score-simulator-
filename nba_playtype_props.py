"""
NBA Playtype Player Prop Generator

Generates NBA player prop recommendations based on:
- Player play-type tendencies (isolation, pick-and-roll, post-up, spot-up, etc.)
- Defensive matchup data against each play type
- Similar player comparisons by position and play-type profile
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Play type constants (based on NBA Synergy categories)
# ---------------------------------------------------------------------------
PLAY_TYPES = [
    "isolation",
    "pnr_ball_handler",
    "pnr_screener",
    "post_up",
    "spot_up",
    "off_screen",
    "hand_off",
    "cut",
    "putback",
    "misc",
]

POSITIONS = ["PG", "SG", "SF", "PF", "C"]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class PlayTypeStats:
    """Per-play-type offensive stats for a player or defensive stats for a team."""
    # frequency: fraction of possessions of this type (0.0 – 1.0)
    frequency: float = 0.0
    # points per possession
    ppp: float = 0.0
    # percentile rank (0–100) vs league
    percentile: float = 50.0


@dataclass
class PlayerProfile:
    """Offensive profile for an NBA player."""
    name: str
    position: str  # one of POSITIONS
    team: str
    # season averages
    avg_points: float = 0.0
    avg_assists: float = 0.0
    avg_rebounds: float = 0.0
    # play-type breakdown; keys are values from PLAY_TYPES
    play_types: Dict[str, PlayTypeStats] = field(default_factory=dict)

    def dominant_play_types(self, top_n: int = 3) -> List[str]:
        """Return the top N play types by frequency."""
        sorted_pts = sorted(
            self.play_types.items(),
            key=lambda kv: kv[1].frequency,
            reverse=True,
        )
        return [pt for pt, _ in sorted_pts[:top_n]]


@dataclass
class DefensiveMatchup:
    """How a team's defense performs against each play type."""
    team: str
    # play-type stats allowed (ppp = points per possession allowed)
    play_types: Dict[str, PlayTypeStats] = field(default_factory=dict)


@dataclass
class DefensiveIsolationStats:
    """Defensive isolation stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game
    freq_pct: float     # frequency % of isolations vs this defense
    ppp: float          # points per possession allowed
    pts: float          # points per game allowed in isolation
    fgm: float          # field goals made allowed per game
    fga: float          # field goals attempted allowed per game
    fg_pct: float       # FG% allowed
    efg_pct: float      # eFG% allowed
    ft_freq_pct: float  # free-throw frequency %
    tov_freq_pct: float # turnover frequency %
    sf_freq_pct: float  # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float   # defensive percentile (higher = better defense)


@dataclass
class TransitionDefensiveStats:
    """Defensive transition stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed in transition
    freq_pct: float     # frequency % of transition possessions allowed
    ppp: float          # points per possession allowed in transition
    pts: float          # points per game allowed in transition
    fgm: float          # field goals made allowed per game
    fga: float          # field goals attempted allowed per game
    fg_pct: float       # FG% allowed
    efg_pct: float      # eFG% allowed
    ft_freq_pct: float  # free-throw frequency %
    tov_freq_pct: float # turnover frequency %
    sf_freq_pct: float  # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float   # NBA Synergy composite defensive percentile (higher = better transition defense)


@dataclass
class DefensivePnrBallHandlerStats:
    """Defensive pick-and-roll ball handler stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs PnR ball handler
    freq_pct: float     # frequency % of PnR ball handler possessions allowed
    ppp: float          # points per possession allowed
    pts: float          # points per game allowed
    fgm: float          # field goals made allowed per game
    fga: float          # field goals attempted allowed per game
    fg_pct: float       # FG% allowed
    efg_pct: float      # eFG% allowed
    ft_freq_pct: float  # free-throw frequency %
    tov_freq_pct: float # turnover frequency %
    sf_freq_pct: float  # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float   # NBA Synergy composite defensive percentile (higher = better PnR ball handler defense)


@dataclass
class DefensivePnrManStats:
    """Defensive pick-and-roll man (screener) stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs PnR man
    freq_pct: float     # frequency % of PnR man possessions allowed
    ppp: float          # points per possession allowed
    pts: float          # points per game allowed
    fgm: float          # field goals made allowed per game
    fga: float          # field goals attempted allowed per game
    fg_pct: float       # FG% allowed
    efg_pct: float      # eFG% allowed
    ft_freq_pct: float  # free-throw frequency %
    tov_freq_pct: float # turnover frequency %
    sf_freq_pct: float  # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float   # NBA Synergy composite defensive percentile (higher = better PnR man defense)


@dataclass
class DefensivePostUpStats:
    """Defensive post-up stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs post-up
    freq_pct: float     # frequency % of post-up possessions allowed
    ppp: float          # points per possession allowed
    pts: float          # points per game allowed
    fgm: float          # field goals made allowed per game
    fga: float          # field goals attempted allowed per game
    fg_pct: float       # FG% allowed
    efg_pct: float      # eFG% allowed
    ft_freq_pct: float  # free-throw frequency %
    tov_freq_pct: float # turnover frequency %
    sf_freq_pct: float  # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float   # NBA Synergy composite defensive percentile (higher = better post-up defense)


@dataclass
class PropRecommendation:
    """A single player-prop recommendation."""
    player_name: str
    prop_type: str          # "points", "assists", or "rebounds"
    line: float             # bookmaker line
    projection: float       # model projection
    edge: float             # projection – line
    confidence: str         # "HIGH", "MEDIUM", or "LOW"
    matchup_notes: str = ""


# ---------------------------------------------------------------------------
# Sample data helpers
# ---------------------------------------------------------------------------

def _make_player_profile(
    name: str,
    position: str,
    team: str,
    avg_points: float,
    avg_assists: float,
    avg_rebounds: float,
    play_type_data: Dict[str, Dict[str, float]],
) -> PlayerProfile:
    """Convenience factory that builds PlayTypeStats objects from plain dicts."""
    play_types = {
        pt: PlayTypeStats(**stats)
        for pt, stats in play_type_data.items()
    }
    return PlayerProfile(
        name=name,
        position=position,
        team=team,
        avg_points=avg_points,
        avg_assists=avg_assists,
        avg_rebounds=avg_rebounds,
        play_types=play_types,
    )


def build_sample_players() -> List[PlayerProfile]:
    """
    Return a small set of illustrative NBA player profiles.
    Frequencies across play types should sum to ~1.0 per player.
    """
    players = [
        _make_player_profile(
            "Shai Gilgeous-Alexander", "PG", "OKC",
            avg_points=32.1, avg_assists=6.4, avg_rebounds=5.0,
            play_type_data={
                "isolation":        {"frequency": 0.32, "ppp": 1.12, "percentile": 88},
                "pnr_ball_handler": {"frequency": 0.28, "ppp": 0.98, "percentile": 72},
                "spot_up":          {"frequency": 0.14, "ppp": 1.05, "percentile": 65},
                "post_up":          {"frequency": 0.10, "ppp": 0.94, "percentile": 60},
                "cut":              {"frequency": 0.08, "ppp": 1.18, "percentile": 70},
                "misc":             {"frequency": 0.08, "ppp": 0.90, "percentile": 50},
            },
        ),
        _make_player_profile(
            "Luka Doncic", "PG", "DAL",
            avg_points=28.5, avg_assists=8.2, avg_rebounds=8.0,
            play_type_data={
                "pnr_ball_handler": {"frequency": 0.35, "ppp": 1.05, "percentile": 80},
                "isolation":        {"frequency": 0.25, "ppp": 1.08, "percentile": 82},
                "post_up":          {"frequency": 0.15, "ppp": 0.99, "percentile": 68},
                "spot_up":          {"frequency": 0.10, "ppp": 1.00, "percentile": 58},
                "hand_off":         {"frequency": 0.08, "ppp": 0.97, "percentile": 55},
                "misc":             {"frequency": 0.07, "ppp": 0.88, "percentile": 48},
            },
        ),
        _make_player_profile(
            "Giannis Antetokounmpo", "PF", "MIL",
            avg_points=30.4, avg_assists=5.8, avg_rebounds=11.5,
            play_type_data={
                "pnr_ball_handler": {"frequency": 0.30, "ppp": 1.15, "percentile": 90},
                "post_up":          {"frequency": 0.22, "ppp": 1.10, "percentile": 85},
                "isolation":        {"frequency": 0.18, "ppp": 1.06, "percentile": 78},
                "cut":              {"frequency": 0.15, "ppp": 1.20, "percentile": 82},
                "spot_up":          {"frequency": 0.08, "ppp": 0.88, "percentile": 40},
                "misc":             {"frequency": 0.07, "ppp": 0.92, "percentile": 52},
            },
        ),
        _make_player_profile(
            "Nikola Jokic", "C", "DEN",
            avg_points=26.4, avg_assists=9.0, avg_rebounds=12.4,
            play_type_data={
                "post_up":          {"frequency": 0.28, "ppp": 1.18, "percentile": 95},
                "pnr_screener":     {"frequency": 0.22, "ppp": 1.22, "percentile": 96},
                "isolation":        {"frequency": 0.15, "ppp": 1.04, "percentile": 70},
                "spot_up":          {"frequency": 0.12, "ppp": 1.08, "percentile": 72},
                "putback":          {"frequency": 0.10, "ppp": 1.25, "percentile": 88},
                "misc":             {"frequency": 0.13, "ppp": 0.95, "percentile": 55},
            },
        ),
        _make_player_profile(
            "Jayson Tatum", "SF", "BOS",
            avg_points=27.1, avg_assists=4.5, avg_rebounds=8.1,
            play_type_data={
                "isolation":        {"frequency": 0.28, "ppp": 1.07, "percentile": 80},
                "spot_up":          {"frequency": 0.22, "ppp": 1.10, "percentile": 78},
                "pnr_ball_handler": {"frequency": 0.20, "ppp": 0.96, "percentile": 65},
                "post_up":          {"frequency": 0.12, "ppp": 0.98, "percentile": 62},
                "off_screen":       {"frequency": 0.10, "ppp": 1.05, "percentile": 70},
                "misc":             {"frequency": 0.08, "ppp": 0.91, "percentile": 50},
            },
        ),
        _make_player_profile(
            "Stephen Curry", "PG", "GSW",
            avg_points=26.4, avg_assists=5.1, avg_rebounds=4.4,
            play_type_data={
                "spot_up":          {"frequency": 0.30, "ppp": 1.20, "percentile": 96},
                "pnr_ball_handler": {"frequency": 0.25, "ppp": 1.08, "percentile": 82},
                "off_screen":       {"frequency": 0.20, "ppp": 1.15, "percentile": 90},
                "isolation":        {"frequency": 0.12, "ppp": 1.05, "percentile": 74},
                "hand_off":         {"frequency": 0.08, "ppp": 1.12, "percentile": 85},
                "misc":             {"frequency": 0.05, "ppp": 0.92, "percentile": 52},
            },
        ),
    ]
    return players


def build_sample_defenses() -> List[DefensiveMatchup]:
    """Return illustrative defensive matchup data for a handful of teams."""
    teams = [
        ("OKC", {
            "isolation":        {"frequency": 0.0, "ppp": 0.85, "percentile": 92},
            "pnr_ball_handler": {"frequency": 0.0, "ppp": 0.88, "percentile": 90},
            "pnr_screener":     {"frequency": 0.0, "ppp": 0.90, "percentile": 85},
            "post_up":          {"frequency": 0.0, "ppp": 0.87, "percentile": 88},
            "spot_up":          {"frequency": 0.0, "ppp": 0.92, "percentile": 78},
            "off_screen":       {"frequency": 0.0, "ppp": 0.89, "percentile": 82},
            "hand_off":         {"frequency": 0.0, "ppp": 0.91, "percentile": 80},
            "cut":              {"frequency": 0.0, "ppp": 0.95, "percentile": 72},
            "putback":          {"frequency": 0.0, "ppp": 0.93, "percentile": 75},
            "misc":             {"frequency": 0.0, "ppp": 0.90, "percentile": 80},
        }),
        ("BOS", {
            "isolation":        {"frequency": 0.0, "ppp": 0.88, "percentile": 88},
            "pnr_ball_handler": {"frequency": 0.0, "ppp": 0.90, "percentile": 85},
            "pnr_screener":     {"frequency": 0.0, "ppp": 0.92, "percentile": 80},
            "post_up":          {"frequency": 0.0, "ppp": 0.89, "percentile": 86},
            "spot_up":          {"frequency": 0.0, "ppp": 0.95, "percentile": 72},
            "off_screen":       {"frequency": 0.0, "ppp": 0.93, "percentile": 75},
            "hand_off":         {"frequency": 0.0, "ppp": 0.91, "percentile": 78},
            "cut":              {"frequency": 0.0, "ppp": 0.97, "percentile": 68},
            "putback":          {"frequency": 0.0, "ppp": 0.95, "percentile": 70},
            "misc":             {"frequency": 0.0, "ppp": 0.92, "percentile": 76},
        }),
        ("MEM", {
            "isolation":        {"frequency": 0.0, "ppp": 1.05, "percentile": 38},
            "pnr_ball_handler": {"frequency": 0.0, "ppp": 1.02, "percentile": 42},
            "pnr_screener":     {"frequency": 0.0, "ppp": 1.08, "percentile": 30},
            "post_up":          {"frequency": 0.0, "ppp": 1.10, "percentile": 25},
            "spot_up":          {"frequency": 0.0, "ppp": 1.06, "percentile": 35},
            "off_screen":       {"frequency": 0.0, "ppp": 1.04, "percentile": 40},
            "hand_off":         {"frequency": 0.0, "ppp": 1.03, "percentile": 44},
            "cut":              {"frequency": 0.0, "ppp": 1.12, "percentile": 22},
            "putback":          {"frequency": 0.0, "ppp": 1.15, "percentile": 18},
            "misc":             {"frequency": 0.0, "ppp": 1.04, "percentile": 38},
        }),
        ("LAC", {
            "isolation":        {"frequency": 0.0, "ppp": 0.96, "percentile": 68},
            "pnr_ball_handler": {"frequency": 0.0, "ppp": 0.98, "percentile": 62},
            "pnr_screener":     {"frequency": 0.0, "ppp": 1.00, "percentile": 55},
            "post_up":          {"frequency": 0.0, "ppp": 0.97, "percentile": 65},
            "spot_up":          {"frequency": 0.0, "ppp": 1.01, "percentile": 52},
            "off_screen":       {"frequency": 0.0, "ppp": 0.99, "percentile": 58},
            "hand_off":         {"frequency": 0.0, "ppp": 0.97, "percentile": 63},
            "cut":              {"frequency": 0.0, "ppp": 1.03, "percentile": 48},
            "putback":          {"frequency": 0.0, "ppp": 1.02, "percentile": 50},
            "misc":             {"frequency": 0.0, "ppp": 0.98, "percentile": 60},
        }),
    ]

    defenses = []
    for team, data in teams:
        play_types = {pt: PlayTypeStats(**stats) for pt, stats in data.items()}
        defenses.append(DefensiveMatchup(team=team, play_types=play_types))
    return defenses


def build_defensive_isolation_rankings() -> Dict[str, "DefensiveIsolationStats"]:
    """
    Return defensive isolation stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    A higher PERCENTILE indicates better isolation defense (fewer points allowed
    per possession vs. league average).
    """
    raw = [
        # (team_abbr, full_name, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("ATL", "Atlanta Hawks",            59, 8.9, 7.7, 1.05, 9.3, 3.5, 7.2, 48.3, 52.4, 12.8,  9.2, 11.6, 2.9, 48.9,   0.0),
        ("BOS", "Boston Celtics",           57, 6.5, 6.0, 0.91, 5.9, 2.2, 5.2, 41.8, 44.1, 12.5,  8.7, 10.8, 1.6, 43.9,  72.4),
        ("BKN", "Brooklyn Nets",            56, 9.7, 8.9, 0.96, 9.3, 3.3, 7.3, 45.0, 48.0, 14.2, 12.9, 13.4, 2.2, 45.8,  20.7),
        ("CHA", "Charlotte Hornets",        58, 7.0, 6.4, 0.96, 6.7, 2.4, 5.6, 43.2, 48.0, 12.5,  9.3, 11.5, 1.5, 45.0,  17.2),
        ("CHI", "Chicago Bulls",            58, 8.2, 7.1, 0.94, 7.7, 2.8, 6.8, 41.1, 45.0, 12.8,  7.2, 12.2, 2.5, 44.2,  44.8),
        ("CLE", "Cleveland Cavaliers",      58, 9.1, 7.9, 0.94, 8.5, 3.1, 7.4, 42.1, 45.3, 14.2,  7.2, 12.7, 2.7, 44.6,  55.2),
        ("DAL", "Dallas Mavericks",         55, 7.5, 6.5, 0.97, 7.3, 2.9, 6.3, 46.5, 48.8, 11.8,  8.2, 11.8, 2.9, 47.2,  13.8),
        ("DEN", "Denver Nuggets",           58, 7.8, 6.9, 0.94, 7.3, 2.6, 6.1, 42.9, 45.9, 14.2, 10.8, 13.3, 2.9, 44.0,  48.3),
        ("DET", "Detroit Pistons",          55, 8.1, 7.2, 0.91, 7.4, 2.5, 6.1, 41.3, 44.3, 16.3, 12.7, 14.1, 3.6, 42.6,  69.0),
        ("GSW", "Golden State Warriors",    57, 9.0, 7.9, 0.94, 8.4, 3.3, 7.6, 43.6, 47.4, 10.0,  8.6,  9.0, 2.7, 43.8,  51.7),
        ("HOU", "Houston Rockets",          56, 8.6, 7.7, 0.89, 7.6, 2.9, 6.8, 43.3, 45.1, 12.5, 11.5, 12.5, 2.9, 43.3,  79.3),
        ("IND", "Indiana Pacers",           57, 9.0, 7.8, 0.95, 8.5, 3.1, 7.1, 43.2, 45.5, 15.7,  7.2, 14.9, 2.5, 46.6,  34.5),
        ("LAC", "LA Clippers",              55, 7.9, 7.2, 0.98, 7.7, 2.7, 6.3, 43.9, 48.5, 13.8, 10.1, 12.7, 3.2, 45.2,  10.3),
        ("LAL", "Los Angeles Lakers",       55, 9.3, 8.4, 0.95, 8.8, 3.1, 7.5, 40.8, 44.8, 14.6,  7.6, 14.2, 2.7, 44.6,  41.4),
        ("MEM", "Memphis Grizzlies",        55, 7.2, 6.2, 0.96, 6.9, 2.4, 5.5, 43.2, 47.8, 15.4, 10.9, 14.4, 2.3, 44.9,  24.1),
        ("MIA", "Miami Heat",               57, 9.6, 8.1, 0.90, 8.6, 3.1, 7.8, 39.6, 44.1, 11.5,  8.8, 10.8, 1.8, 41.8,  75.9),
        ("MIL", "Milwaukee Bucks",          55, 8.2, 7.4, 0.95, 7.8, 2.7, 6.3, 41.8, 45.3, 16.4,  9.5, 15.3, 3.1, 45.4,  37.9),
        ("MIN", "Minnesota Timberwolves",   57, 8.7, 7.6, 0.87, 7.6, 2.9, 6.9, 42.2, 44.0, 12.2, 11.4, 11.0, 2.6, 42.2,  89.7),
        ("NOP", "New Orleans Pelicans",     58, 8.6, 7.4, 0.92, 7.9, 2.9, 6.8, 42.4, 47.0, 11.6, 12.0, 10.6, 2.6, 41.7,  62.1),
        ("NYK", "New York Knicks",          55, 7.5, 6.7, 0.87, 6.5, 2.3, 5.9, 39.8, 43.1, 14.6,  9.7, 13.6, 3.2, 41.8,  86.2),
        ("OKC", "Oklahoma City Thunder",    56, 6.7, 5.8, 0.82, 5.5, 1.9, 5.2, 37.5, 40.0, 14.1, 11.2, 13.0, 2.7, 40.2,  96.6),
        ("ORL", "Orlando Magic",            53, 9.5, 8.4, 0.95, 9.1, 3.5, 7.9, 43.8, 47.4, 11.9,  7.7, 11.5, 2.4, 45.5,  27.6),
        ("PHI", "Philadelphia 76ers",       56, 6.5, 5.7, 0.93, 6.1, 2.1, 5.3, 40.5, 44.6, 13.1,  9.0, 12.0, 2.5, 43.2,  58.6),
        ("PHX", "Phoenix Suns",             56, 9.8, 8.7, 0.81, 7.9, 2.7, 7.0, 38.5, 41.3, 14.2, 16.4, 13.1, 2.0, 39.7, 100.0),
        ("POR", "Portland Trail Blazers",   58, 6.2, 5.4, 0.95, 5.9, 2.1, 4.7, 45.0, 47.2, 15.5, 11.0, 15.2, 1.4, 47.2,  31.0),
        ("SAC", "Sacramento Kings",         58, 8.6, 7.6, 1.02, 8.7, 3.2, 6.9, 46.7, 49.9, 13.5,  9.0, 12.9, 3.4, 47.6,   3.4),
        ("SAS", "San Antonio Spurs",        54, 6.8, 6.0, 0.92, 6.2, 2.2, 5.2, 42.4, 44.5, 14.4, 10.9, 13.3, 2.2, 44.3,  65.5),
        ("TOR", "Toronto Raptors",          57, 9.0, 8.0, 0.88, 7.9, 2.8, 6.6, 42.8, 45.5, 14.9, 13.7, 13.9, 1.8, 43.2,  82.8),
        ("UTA", "Utah Jazz",                58, 8.0, 6.9, 0.99, 7.9, 2.6, 5.9, 43.6, 46.6, 19.1,  9.7, 17.6, 2.1, 48.5,   6.9),
        ("WAS", "Washington Wizards",       55, 7.4, 6.3, 0.82, 6.1, 2.0, 5.6, 35.8, 38.4, 15.7,  9.6, 15.0, 1.5, 40.8,  93.1),
    ]

    rankings: Dict[str, DefensiveIsolationStats] = {}
    for row in raw:
        (abbr, _name, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensiveIsolationStats(
            team=abbr,
            gp=gp,
            poss=poss,
            freq_pct=freq_pct,
            ppp=ppp,
            pts=pts,
            fgm=fgm,
            fga=fga,
            fg_pct=fg_pct,
            efg_pct=efg_pct,
            ft_freq_pct=ft_freq_pct,
            tov_freq_pct=tov_freq_pct,
            sf_freq_pct=sf_freq_pct,
            and_one_freq_pct=and_one_freq_pct,
            score_freq_pct=score_freq_pct,
            percentile=percentile,
        )
    return rankings


def rank_teams_by_isolation_defense(
    rankings: Optional[Dict[str, "DefensiveIsolationStats"]] = None,
) -> List["DefensiveIsolationStats"]:
    """
    Return all teams sorted from best to worst isolation defense
    (highest percentile first, i.e. lowest PPP allowed).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_defensive_isolation_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def build_transition_defensive_rankings() -> Dict[str, "TransitionDefensiveStats"]:
    """
    Return defensive transition stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger transition defense (limiting both the frequency and efficiency of
    opponent transition possessions).
    """
    raw = [
        # (team_abbr, full_name, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("MIA", "Miami Heat",               57, 29.5, 24.9, 1.08, 31.7, 11.6, 22.9, 50.7, 57.6, 12.7, 12.2, 11.4, 2.7, 48.8,   3.4),
        ("CHI", "Chicago Bulls",            58, 26.5, 23.3, 1.14, 30.3, 11.2, 21.0, 53.2, 61.4, 12.2, 11.8, 11.2, 3.2, 50.8,  65.5),
        ("ATL", "Atlanta Hawks",            59, 25.6, 22.3, 1.14, 29.0, 10.8, 20.6, 52.3, 60.5, 11.7, 10.8, 10.9, 3.1, 50.3,  55.2),
        ("TOR", "Toronto Raptors",          57, 25.5, 22.6, 1.13, 28.8, 10.8, 20.1, 53.5, 60.3, 12.4, 10.9, 11.0, 2.1, 52.0,  41.4),
        ("DAL", "Dallas Mavericks",         55, 23.1, 20.1, 1.19, 27.5, 10.2, 18.1, 56.4, 62.4, 15.8,  9.8, 15.1, 4.0, 55.2,  96.6),
        ("SAS", "San Antonio Spurs",        54, 24.5, 21.6, 1.13, 27.7,  9.8, 18.6, 52.7, 60.3, 15.1, 12.0, 14.2, 3.3, 51.2,  48.3),
        ("NOP", "New Orleans Pelicans",     58, 22.5, 19.5, 1.12, 25.2,  9.6, 17.8, 53.6, 59.8, 12.2, 11.4, 11.5, 3.0, 51.2,  34.5),
        ("MIN", "Minnesota Timberwolves",   57, 21.9, 19.1, 1.15, 25.2,  9.6, 16.4, 58.4, 65.2, 13.5, 15.0, 12.5, 3.6, 52.9,  75.9),
        ("UTA", "Utah Jazz",                58, 21.5, 18.3, 1.14, 24.5,  9.2, 16.6, 55.7, 62.3, 12.7, 13.2, 11.8, 3.0, 52.6,  69.0),
        ("MEM", "Memphis Grizzlies",        55, 23.9, 20.6, 1.08, 25.8,  9.7, 18.6, 52.1, 59.2, 11.3, 13.5, 10.7, 2.6, 48.5,   6.9),
        ("DET", "Detroit Pistons",          55, 22.2, 19.2, 1.16, 25.8,  9.8, 17.0, 57.7, 63.1, 14.8, 12.0, 13.8, 3.4, 54.5,  79.3),
        ("CLE", "Cleveland Cavaliers",      58, 21.3, 18.5, 1.14, 24.1,  9.1, 17.2, 52.7, 60.4, 10.9, 10.4, 10.1, 2.4, 51.0,  58.6),
        ("IND", "Indiana Pacers",           57, 22.0, 19.3, 1.10, 24.2,  8.9, 17.0, 52.1, 59.4, 13.3, 12.0, 12.2, 2.5, 50.2,  24.1),
        ("NYK", "New York Knicks",          55, 21.1, 18.7, 1.19, 25.1,  9.3, 17.2, 54.2, 63.0, 11.1, 10.2, 10.6, 2.8, 52.1,  93.1),
        ("ORL", "Orlando Magic",            53, 22.3, 19.6, 1.15, 25.6,  9.3, 17.4, 53.5, 59.7, 15.0,  9.9, 14.3, 3.0, 52.8,  72.4),
        ("POR", "Portland Trail Blazers",   58, 21.1, 17.9, 1.11, 23.4,  8.4, 15.9, 52.8, 60.8, 13.5, 14.2, 12.1, 3.0, 49.9,  27.6),
        ("PHI", "Philadelphia 76ers",       56, 20.7, 18.0, 1.13, 23.5,  8.7, 16.3, 53.6, 60.3, 12.8, 11.2, 11.9, 2.5, 52.0,  51.7),
        ("HOU", "Houston Rockets",          56, 18.9, 16.5, 1.14, 21.6,  8.1, 14.2, 57.2, 64.0, 13.3, 15.0, 12.2, 3.2, 52.4,  62.1),
        ("SAC", "Sacramento Kings",         58, 18.8, 16.6, 1.10, 20.7,  8.0, 14.1, 56.4, 60.7, 13.5, 13.7, 12.8, 2.2, 53.2,  20.7),
        ("OKC", "Oklahoma City Thunder",    56, 17.9, 16.0, 1.20, 21.4,  7.8, 14.4, 54.0, 61.6, 13.9,  9.1, 12.7, 3.6, 53.6, 100.0),
        ("WAS", "Washington Wizards",       55, 21.4, 18.6, 1.02, 21.8,  8.1, 17.1, 47.3, 55.4, 10.1, 12.8,  9.7, 2.8, 44.4,   0.0),
        ("GSW", "Golden State Warriors",    57, 19.0, 16.7, 1.11, 21.0,  7.8, 14.8, 52.7, 61.7,  9.5, 14.4,  8.7, 2.0, 48.5,  31.0),
        ("DEN", "Denver Nuggets",           58, 17.3, 15.6, 1.18, 20.5,  7.4, 13.4, 54.8, 62.5, 14.4, 11.1, 11.8, 3.1, 53.3,  89.7),
        ("LAL", "Los Angeles Lakers",       55, 19.1, 17.4, 1.13, 21.5,  8.1, 14.2, 57.4, 63.2, 14.2, 14.6, 13.3, 3.1, 53.0,  44.8),
        ("BOS", "Boston Celtics",           57, 17.1, 15.5, 1.18, 20.1,  7.5, 14.1, 53.2, 62.5, 10.2,  9.8,  8.8, 2.7, 51.3,  86.2),
        ("PHX", "Phoenix Suns",             56, 18.1, 16.1, 1.13, 20.4,  7.5, 14.3, 52.5, 61.8, 10.3, 12.7,  9.8, 2.0, 49.5,  37.9),
        ("CHA", "Charlotte Hornets",        58, 17.9, 15.7, 1.08, 19.4,  7.1, 13.6, 52.1, 60.4, 11.6, 14.5, 10.8, 1.9, 49.1,  13.8),
        ("MIL", "Milwaukee Bucks",          55, 17.7, 16.3, 1.08, 19.2,  6.9, 13.4, 51.8, 59.4, 14.2, 12.9, 13.3, 2.8, 49.4,  10.3),
        ("BKN", "Brooklyn Nets",            56, 17.2, 15.6, 1.09, 18.8,  7.0, 13.2, 52.9, 60.6, 12.8, 13.7, 12.2, 3.1, 49.1,  17.2),
        ("LAC", "LA Clippers",              55, 16.2, 15.1, 1.17, 18.9,  6.9, 12.3, 55.8, 63.5, 13.6, 13.7, 12.4, 3.5, 52.2,  82.8),
    ]

    rankings: Dict[str, TransitionDefensiveStats] = {}
    for row in raw:
        (abbr, _name, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = TransitionDefensiveStats(
            team=abbr,
            gp=gp,
            poss=poss,
            freq_pct=freq_pct,
            ppp=ppp,
            pts=pts,
            fgm=fgm,
            fga=fga,
            fg_pct=fg_pct,
            efg_pct=efg_pct,
            ft_freq_pct=ft_freq_pct,
            tov_freq_pct=tov_freq_pct,
            sf_freq_pct=sf_freq_pct,
            and_one_freq_pct=and_one_freq_pct,
            score_freq_pct=score_freq_pct,
            percentile=percentile,
        )
    return rankings


def rank_teams_by_transition_defense(
    rankings: Optional[Dict[str, "TransitionDefensiveStats"]] = None,
) -> List["TransitionDefensiveStats"]:
    """
    Return all teams sorted from best to worst transition defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_transition_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def build_pnr_ball_handler_defensive_rankings() -> Dict[str, "DefensivePnrBallHandlerStats"]:
    """
    Return defensive pick-and-roll ball handler stats for all 30 NBA teams
    (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger pick-and-roll ball handler defense (limiting both the frequency
    and efficiency of opponent PnR ball handler possessions).
    """
    raw = [
        # (team_abbr, full_name, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("BKN", "Brooklyn Nets",            56, 11.8, 10.8, 0.87, 10.3, 3.7,  8.1, 45.3, 50.2, 13.2, 20.9, 10.6, 2.7, 41.1,  69.0),
        ("GSW", "Golden State Warriors",    57, 15.1, 13.3, 0.85, 12.9, 4.8, 10.8, 44.7, 48.9, 10.2, 20.4,  8.7, 2.0, 39.9,  79.3),
        ("UTA", "Utah Jazz",                58, 13.5, 11.5, 0.95, 12.8, 4.4, 10.0, 44.3, 50.9, 12.5, 15.8, 11.4, 2.3, 42.6,   3.4),
        ("PHX", "Phoenix Suns",             56, 15.0, 13.4, 0.89, 13.3, 4.8, 10.9, 44.0, 49.2, 10.7, 18.3,  9.5, 1.9, 40.5,  41.4),
        ("MIL", "Milwaukee Bucks",          55, 15.5, 13.9, 0.89, 13.8, 4.8, 11.5, 41.5, 46.7, 13.2, 14.5, 11.7, 1.9, 41.9,  34.5),
        ("CLE", "Cleveland Cavaliers",      58, 16.1, 14.0, 0.81, 13.1, 4.8, 11.8, 40.6, 46.0,  8.9, 18.7,  7.3, 1.3, 37.1,  93.1),
        ("CHI", "Chicago Bulls",            58, 15.9, 13.8, 0.88, 13.9, 5.2, 12.0, 43.7, 49.2,  9.1, 17.4,  8.6, 2.1, 39.7,  62.1),
        ("NOP", "New Orleans Pelicans",     58, 15.5, 13.3, 0.90, 13.9, 4.9, 11.7, 42.5, 48.3, 11.3, 15.2,  9.9, 1.8, 41.2,  17.2),
        ("LAL", "Los Angeles Lakers",       55, 17.0, 15.3, 0.88, 15.0, 5.7, 13.2, 42.8, 48.3,  9.4, 15.6,  8.8, 2.6, 39.7,  51.7),
        ("DET", "Detroit Pistons",          55, 19.0, 16.7, 0.79, 15.0, 5.1, 13.5, 37.9, 42.1, 11.8, 18.5, 10.4, 1.4, 37.2, 100.0),
        ("WAS", "Washington Wizards",       55, 16.8, 14.4, 0.89, 15.0, 5.2, 12.6, 41.0, 45.8, 13.8, 14.1, 12.9, 3.0, 41.0,  27.6),
        ("LAC", "LA Clippers",              55, 17.4, 15.9, 0.88, 15.2, 5.5, 12.8, 42.8, 48.2, 11.0, 16.8,  9.9, 1.4, 40.7,  65.5),
        ("MEM", "Memphis Grizzlies",        55, 17.7, 15.3, 0.88, 15.5, 5.5, 13.3, 41.4, 46.5, 12.3, 15.3, 11.6, 2.3, 40.2,  58.6),
        ("SAC", "Sacramento Kings",         58, 15.9, 14.0, 0.93, 14.8, 5.6, 12.2, 45.7, 51.6,  9.3, 16.3,  8.9, 2.1, 42.1,  10.3),
        ("ATL", "Atlanta Hawks",            59, 16.8, 14.5, 0.87, 14.6, 5.2, 12.1, 43.5, 49.2, 10.9, 19.6,  9.5, 2.4, 39.4,  72.4),
        ("ORL", "Orlando Magic",            53, 18.5, 16.3, 0.88, 16.2, 6.1, 14.1, 43.3, 47.7, 10.2, 15.8,  9.4, 2.4, 40.7,  55.2),
        ("SAS", "San Antonio Spurs",        54, 19.1, 16.9, 0.84, 16.0, 6.2, 15.2, 41.1, 46.0,  7.6, 15.3,  6.7, 2.1, 37.9,  82.8),
        ("OKC", "Oklahoma City Thunder",    56, 19.0, 16.5, 0.81, 15.4, 5.7, 14.4, 39.2, 44.3,  9.7, 15.7,  8.7, 1.5, 37.4,  96.6),
        ("DAL", "Dallas Mavericks",         55, 17.8, 15.3, 0.90, 15.9, 5.7, 13.8, 41.7, 47.5, 10.5, 14.3, 10.0, 2.1, 40.4,  24.1),
        ("DEN", "Denver Nuggets",           58, 16.9, 15.0, 0.90, 15.1, 5.6, 13.1, 42.5, 47.8, 10.2, 14.2,  9.0, 1.8, 41.1,  20.7),
        ("PHI", "Philadelphia 76ers",       56, 18.8, 16.3, 0.84, 15.7, 5.6, 13.3, 42.5, 46.8, 11.6, 19.5, 10.0, 1.7, 39.5,  86.2),
        ("BOS", "Boston Celtics",           57, 17.5, 16.1, 0.89, 15.6, 5.4, 13.6, 39.5, 45.3, 11.9, 12.6, 10.7, 2.1, 40.1,  37.9),
        ("MIA", "Miami Heat",               57, 17.9, 15.2, 0.87, 15.6, 5.5, 13.8, 40.1, 45.4, 10.2, 14.8,  9.4, 2.1, 38.7,  75.9),
        ("NYK", "New York Knicks",          55, 18.3, 16.5, 0.89, 16.2, 5.9, 13.7, 42.6, 48.9,  9.9, 16.8,  8.9, 1.7, 39.9,  48.3),
        ("HOU", "Houston Rockets",          56, 19.2, 17.3, 0.83, 16.0, 5.8, 14.9, 39.2, 44.4,  9.5, 14.9,  8.3, 2.2, 37.4,  89.7),
        ("TOR", "Toronto Raptors",          57, 18.0, 16.0, 0.89, 16.0, 5.6, 13.5, 41.4, 46.8, 12.0, 14.9, 10.1, 2.0, 40.8,  31.0),
        ("IND", "Indiana Pacers",           57, 18.0, 15.7, 0.94, 16.9, 6.3, 13.4, 47.2, 51.6, 12.0, 16.3, 10.6, 2.5, 44.2,   6.9),
        ("CHA", "Charlotte Hornets",        58, 18.5, 16.8, 0.91, 16.8, 6.3, 14.7, 43.0, 48.5,  8.9, 13.5,  8.1, 2.1, 40.9,  13.8),
        ("MIN", "Minnesota Timberwolves",   57, 20.3, 17.6, 0.89, 17.9, 6.5, 15.6, 41.6, 46.8, 10.6, 14.1,  9.2, 1.8, 40.7,  44.8),
        ("POR", "Portland Trail Blazers",   58, 18.5, 16.0, 0.96, 17.7, 6.6, 14.8, 44.7, 50.5,  9.7, 12.5,  8.6, 2.2, 43.1,   0.0),
    ]

    rankings: Dict[str, DefensivePnrBallHandlerStats] = {}
    for row in raw:
        (abbr, _name, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensivePnrBallHandlerStats(
            team=abbr,
            gp=gp,
            poss=poss,
            freq_pct=freq_pct,
            ppp=ppp,
            pts=pts,
            fgm=fgm,
            fga=fga,
            fg_pct=fg_pct,
            efg_pct=efg_pct,
            ft_freq_pct=ft_freq_pct,
            tov_freq_pct=tov_freq_pct,
            sf_freq_pct=sf_freq_pct,
            and_one_freq_pct=and_one_freq_pct,
            score_freq_pct=score_freq_pct,
            percentile=percentile,
        )
    return rankings


def rank_teams_by_pnr_ball_handler_defense(
    rankings: Optional[Dict[str, "DefensivePnrBallHandlerStats"]] = None,
) -> List["DefensivePnrBallHandlerStats"]:
    """
    Return all teams sorted from best to worst pick-and-roll ball handler defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_pnr_ball_handler_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def build_pnr_man_defensive_rankings() -> Dict[str, "DefensivePnrManStats"]:
    """
    Return defensive pick-and-roll man (screener) stats for all 30 NBA teams
    (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger pick-and-roll man defense (limiting both the frequency and
    efficiency of opponent PnR screener possessions).

    NOTE: Washington Wizards data in the source was truncated after TOV FREQ%.
    The sf_freq_pct, and_one_freq_pct, score_freq_pct, and percentile fields
    for WAS are stored as -1.0 to indicate missing/unavailable data (distinct
    from a legitimate 0.0 percentile such as Portland Trail Blazers).
    """
    raw = [
        # (team_abbr, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("ATL", 59,  7.2, 6.2, 1.05,  7.5, 2.9, 5.9, 48.9, 55.1, 10.1,  9.2, 10.1, 1.9, 48.1,  79.3),
        ("BOS", 57,  5.1, 4.7, 1.17,  5.9, 2.3, 4.5, 51.4, 59.5,  9.0,  5.2,  8.7, 3.1, 50.9,  17.2),
        ("BKN", 56,  6.5, 5.9, 1.11,  7.2, 2.9, 5.6, 51.6, 56.1, 10.5,  5.8, 10.2, 2.5, 51.9,  41.4),
        ("CHA", 58,  5.3, 4.8, 1.13,  5.9, 2.4, 4.8, 50.2, 57.0,  6.2,  4.6,  6.2, 1.6, 50.2,  31.0),
        ("CHI", 58,  6.7, 5.8, 1.21,  8.1, 3.2, 5.8, 54.7, 61.5, 11.1,  3.6, 10.9, 2.3, 56.2,   6.9),
        ("CLE", 58,  6.1, 5.3, 1.11,  6.8, 2.7, 5.4, 50.2, 56.6,  7.9,  6.2,  7.0, 1.4, 50.0,  48.3),
        ("DAL", 55,  6.0, 5.1, 1.07,  6.4, 2.5, 5.1, 49.3, 54.0, 10.3,  6.7, 10.3, 1.2, 50.3,  65.5),
        ("DEN", 58,  5.6, 5.0, 1.02,  5.7, 2.3, 4.8, 48.0, 52.5, 10.1,  6.7,  9.5, 2.5, 48.5,  89.7),
        ("DET", 55,  5.9, 5.2, 1.05,  6.2, 2.3, 4.8, 48.5, 57.6,  9.0, 11.1,  8.0, 1.5, 46.9,  75.9),
        ("GSW", 57,  5.5, 4.9, 1.09,  6.1, 2.4, 4.6, 51.3, 57.0,  9.8,  8.9,  9.5, 2.5, 49.7,  51.7),
        ("HOU", 56,  7.0, 6.3, 0.96,  6.7, 2.6, 5.9, 43.6, 49.8, 10.7,  7.1, 10.7, 2.0, 43.6, 100.0),
        ("IND", 57,  7.5, 6.5, 1.08,  8.1, 3.1, 6.2, 49.4, 54.0, 15.0,  6.3, 14.5, 4.2, 50.6,  62.1),
        ("LAC", 55,  6.1, 5.5, 1.05,  6.4, 2.4, 5.0, 47.8, 53.6, 12.0,  8.4, 11.7, 2.7, 47.7,  72.4),
        ("LAL", 55,  5.0, 4.5, 1.27,  6.3, 2.5, 4.2, 60.0, 68.3, 12.0,  6.9, 12.0, 2.5, 58.2,   0.0),
        ("MEM", 55,  6.1, 5.3, 1.01,  6.2, 2.4, 5.0, 48.5, 54.6, 10.1, 12.1,  9.8, 3.3, 45.3,  93.1),
        ("MIA", 57,  6.2, 5.2, 1.06,  6.6, 2.6, 5.3, 49.3, 55.0,  9.9,  7.4,  9.3, 2.8, 48.4,  69.0),
        ("MIL", 55,  5.6, 5.1, 1.25,  7.1, 2.7, 4.8, 56.9, 64.1, 11.6,  6.1, 11.6, 2.3, 57.1,   3.4),
        ("MIN", 57,  6.6, 5.8, 1.12,  7.4, 2.9, 5.6, 51.2, 58.4, 10.8,  6.3, 10.0, 2.1, 50.7,  37.9),
        ("NOP", 58,  5.4, 4.7, 1.11,  6.0, 2.4, 4.7, 50.9, 55.9, 10.2,  6.1, 10.2, 2.5, 51.6,  44.8),
        ("NYK", 55,  6.1, 5.5, 1.14,  6.9, 2.5, 5.0, 49.5, 57.9, 13.5,  6.0, 13.2, 2.4, 51.5,  27.6),
        ("OKC", 56,  6.1, 5.3, 1.05,  6.4, 2.4, 5.1, 48.2, 54.4, 12.3,  7.3, 12.0, 2.6, 48.5,  82.8),
        ("ORL", 53,  5.9, 5.2, 1.15,  6.7, 2.6, 4.8, 54.4, 59.7, 14.1,  8.4, 13.5, 3.5, 53.4,  24.1),
        ("PHI", 56,  6.2, 5.4, 1.09,  6.8, 2.6, 5.1, 51.9, 57.5, 12.7,  8.9, 11.0, 3.7, 50.1,  55.2),
        ("PHX", 56,  4.8, 4.3, 1.16,  5.6, 2.2, 4.1, 53.7, 59.7, 12.2,  7.4, 10.7, 3.7, 53.0,  20.7),
        ("POR", 58,  5.9, 5.1, 1.12,  6.7, 2.6, 5.1, 50.2, 57.3, 11.6,  6.4, 11.0, 3.5, 50.4,  34.5),
        ("SAC", 58,  6.0, 5.3, 1.19,  7.2, 2.9, 4.9, 58.6, 63.7, 11.1,  8.6,  9.4, 1.1, 57.1,  13.8),
        ("SAS", 54,  6.3, 5.6, 1.00,  6.4, 2.6, 5.6, 46.5, 51.0,  9.4,  5.0,  9.4, 2.9, 46.8,  96.6),
        ("TOR", 57,  6.7, 6.0, 1.08,  7.3, 2.7, 5.5, 48.1, 54.1, 13.8,  7.0, 13.3, 3.1, 49.5,  58.6),
        ("UTA", 58,  6.1, 5.2, 1.21,  7.4, 2.9, 5.3, 55.2, 62.3,  9.6,  5.9,  8.8, 2.5, 54.2,  10.3),
        # Washington Wizards row was truncated in source after TOV FREQ%;
        # sf_freq_pct, and_one_freq_pct, score_freq_pct, and percentile are set to -1.0
        # to indicate missing/unavailable data (distinct from a legitimate 0.0 percentile).
        ("WAS", 55,  6.4, 5.5, 1.05,  6.7, 2.7, 5.5, 47.9, 53.4,  9.1,  6.8, -1.0, -1.0,  -1.0,  -1.0),
    ]

    rankings: Dict[str, DefensivePnrManStats] = {}
    for row in raw:
        (abbr, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensivePnrManStats(
            team=abbr,
            gp=gp,
            poss=poss,
            freq_pct=freq_pct,
            ppp=ppp,
            pts=pts,
            fgm=fgm,
            fga=fga,
            fg_pct=fg_pct,
            efg_pct=efg_pct,
            ft_freq_pct=ft_freq_pct,
            tov_freq_pct=tov_freq_pct,
            sf_freq_pct=sf_freq_pct,
            and_one_freq_pct=and_one_freq_pct,
            score_freq_pct=score_freq_pct,
            percentile=percentile,
        )
    return rankings


def rank_teams_by_pnr_man_defense(
    rankings: Optional[Dict[str, "DefensivePnrManStats"]] = None,
) -> List["DefensivePnrManStats"]:
    """
    Return all teams sorted from best to worst pick-and-roll man defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_pnr_man_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def build_post_up_defensive_rankings() -> Dict[str, "DefensivePostUpStats"]:
    """
    Return defensive post-up stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger post-up defense (limiting both the frequency and efficiency of
    opponent post-up possessions).
    """
    raw = [
        # (team_abbr, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("DET", 55, 2.8, 2.5, 0.74, 2.1, 0.7, 1.9, 35.5, 35.5, 18.1, 15.5, 14.8, 2.6, 39.4, 100.0),
        ("PHI", 56, 2.9, 2.5, 1.00, 2.9, 1.2, 2.2, 53.3, 53.3, 13.8, 13.1, 12.5, 3.1, 50.0,  55.2),
        ("SAS", 54, 3.9, 3.4, 0.78, 3.0, 1.2, 3.0, 41.0, 41.0, 11.9, 12.4, 10.5, 1.0, 40.5,  96.6),
        ("MIL", 55, 3.2, 2.9, 0.95, 3.0, 1.1, 2.3, 46.5, 46.5, 21.0,  9.7, 18.8, 4.0, 50.6,  82.8),
        ("LAL", 55, 3.5, 3.1, 0.93, 3.2, 1.2, 2.4, 49.6, 49.6, 16.8, 17.4, 12.1, 3.2, 47.9,  86.2),
        ("POR", 58, 3.1, 2.7, 0.98, 3.1, 1.2, 2.4, 51.4, 51.4, 15.5,  9.4, 12.7, 2.2, 51.4,  62.1),
        ("MIN", 57, 2.8, 2.4, 1.13, 3.1, 1.3, 2.1, 59.5, 59.5, 16.5, 11.4, 14.6, 4.4, 57.0,   0.0),
        ("DAL", 55, 3.3, 2.8, 1.02, 3.3, 1.3, 2.3, 55.0, 55.0, 15.6, 16.8, 14.5, 4.5, 50.3,  41.4),
        ("TOR", 57, 3.3, 2.9, 1.02, 3.3, 1.1, 2.3, 48.5, 48.5, 22.6, 12.4, 17.2, 4.8, 51.6,  44.8),
        ("LAC", 55, 3.2, 2.9, 1.11, 3.5, 1.5, 2.6, 56.6, 56.6, 14.9,  7.5, 13.8, 4.6, 56.3,   3.4),
        ("DEN", 58, 3.6, 3.2, 0.95, 3.4, 1.3, 2.6, 49.3, 49.3, 19.3, 12.1, 16.4, 3.9, 49.8,  79.3),
        ("HOU", 56, 3.8, 3.4, 0.98, 3.7, 1.5, 2.9, 50.3, 50.3, 16.4,  9.4, 12.7, 2.3, 51.6,  69.0),
        ("GSW", 57, 3.9, 3.4, 0.98, 3.8, 1.4, 3.0, 47.4, 47.4, 16.6, 10.3, 16.6, 3.6, 48.9,  65.5),
        ("OKC", 56, 4.3, 3.7, 0.92, 3.9, 1.5, 3.3, 46.2, 46.2, 16.4, 10.1, 14.7, 2.9, 46.6,  89.7),
        ("NYK", 55, 4.0, 3.6, 1.02, 4.1, 1.4, 2.8, 51.3, 51.3, 20.5, 11.9, 18.3, 2.7, 52.5,  37.9),
        ("BOS", 57, 4.7, 4.4, 0.85, 4.0, 1.6, 3.5, 44.5, 44.5, 10.7, 16.3,  8.5, 1.1, 42.6,  93.1),
        ("UTA", 58, 3.9, 3.4, 1.03, 4.1, 1.4, 2.6, 55.3, 55.3, 21.5, 15.8, 16.7, 3.9, 53.1,  27.6),
        ("BKN", 56, 3.9, 3.6, 1.10, 4.3, 1.6, 2.9, 55.0, 55.0, 21.2,  8.8, 16.1, 3.7, 57.1,  10.7),
        ("MEM", 55, 4.4, 3.8, 1.01, 4.5, 1.7, 3.4, 50.3, 50.3, 16.8,  9.4, 14.8, 3.7, 51.6,  48.3),
        ("ATL", 59, 4.6, 4.0, 0.95, 4.4, 1.7, 3.5, 50.0, 50.0, 13.9, 14.6, 10.6, 3.6, 47.8,  75.9),
        ("MIA", 57, 4.4, 3.7, 1.06, 4.6, 1.8, 3.2, 55.7, 55.7, 17.3, 12.4, 14.9, 3.2, 54.2,  17.2),
        ("ORL", 53, 4.8, 4.2, 1.05, 5.0, 2.0, 3.7, 52.8, 52.8, 16.3, 10.3, 15.1, 4.8, 52.8,  24.1),
        ("WAS", 55, 5.0, 4.3, 0.96, 4.8, 1.9, 4.0, 49.1, 49.1, 13.4, 10.5, 11.6, 2.9, 48.9,  72.4),
        ("CHA", 58, 4.6, 4.2, 1.00, 4.6, 2.0, 3.9, 50.7, 50.7, 10.8,  8.2,  9.7, 3.0, 50.4,  51.7),
        ("IND", 57, 4.4, 3.8, 1.10, 4.8, 1.9, 3.2, 58.5, 58.5, 16.9, 10.9, 16.1, 1.6, 56.0,  10.7),
        ("NOP", 58, 4.5, 3.9, 1.05, 4.8, 1.8, 3.2, 54.5, 54.5, 17.6, 13.4, 15.6, 2.3, 54.2,  20.7),
        ("PHX", 56, 4.8, 4.3, 1.03, 5.0, 1.9, 3.6, 53.2, 53.2, 18.5, 11.5, 14.8, 4.4, 52.6,  31.0),
        ("CLE", 58, 5.1, 4.4, 0.99, 5.0, 1.7, 3.4, 50.0, 50.0, 19.7, 16.7, 17.0, 3.7, 49.3,  58.6),
        ("CHI", 58, 5.4, 4.7, 1.03, 5.6, 2.2, 4.1, 53.6, 53.6, 15.6, 11.5, 14.0, 3.2, 52.5,  34.5),
        ("SAC", 58, 5.3, 4.6, 1.11, 5.8, 2.4, 4.0, 59.2, 59.2, 16.7, 11.8, 16.0, 4.6, 56.2,   6.9),
    ]

    rankings: Dict[str, DefensivePostUpStats] = {}
    for row in raw:
        (abbr, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensivePostUpStats(
            team=abbr,
            gp=gp,
            poss=poss,
            freq_pct=freq_pct,
            ppp=ppp,
            pts=pts,
            fgm=fgm,
            fga=fga,
            fg_pct=fg_pct,
            efg_pct=efg_pct,
            ft_freq_pct=ft_freq_pct,
            tov_freq_pct=tov_freq_pct,
            sf_freq_pct=sf_freq_pct,
            and_one_freq_pct=and_one_freq_pct,
            score_freq_pct=score_freq_pct,
            percentile=percentile,
        )
    return rankings


def rank_teams_by_post_up_defense(
    rankings: Optional[Dict[str, "DefensivePostUpStats"]] = None,
) -> List["DefensivePostUpStats"]:
    """
    Return all teams sorted from best to worst post-up defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_post_up_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


# ---------------------------------------------------------------------------
# Similarity engine
# ---------------------------------------------------------------------------

def _play_type_vector(player: PlayerProfile) -> Dict[str, float]:
    """Return a dict mapping each play type to the player's frequency."""
    return {pt: player.play_types.get(pt, PlayTypeStats()).frequency for pt in PLAY_TYPES}


def compute_similarity(player_a: PlayerProfile, player_b: PlayerProfile) -> float:
    """
    Compute a 0–1 similarity score between two players based on:
    - Matching position (binary bonus)
    - Cosine similarity of play-type frequency vectors
    """
    # Position bonus: same position → 1.0, adjacent position → 0.5, else 0.0
    pos_order = {p: i for i, p in enumerate(POSITIONS)}
    pos_diff = abs(pos_order.get(player_a.position, 0) - pos_order.get(player_b.position, 0))
    position_score = 1.0 if pos_diff == 0 else (0.5 if pos_diff == 1 else 0.0)

    # Cosine similarity of play-type vectors
    vec_a = _play_type_vector(player_a)
    vec_b = _play_type_vector(player_b)

    dot = sum(vec_a[pt] * vec_b[pt] for pt in PLAY_TYPES)
    mag_a = sum(v ** 2 for v in vec_a.values()) ** 0.5
    mag_b = sum(v ** 2 for v in vec_b.values()) ** 0.5

    if mag_a == 0 or mag_b == 0:
        cosine = 0.0
    else:
        cosine = dot / (mag_a * mag_b)

    # Weighted combination: 40% position, 60% play-type
    return 0.40 * position_score + 0.60 * cosine


def find_similar_players(
    player: PlayerProfile,
    all_players: List[PlayerProfile],
    top_n: int = 3,
) -> List[tuple]:
    """
    Return the top_n most similar players (excluding the player themselves).
    Each result is a (PlayerProfile, similarity_score) tuple.
    """
    scores = [
        (other, compute_similarity(player, other))
        for other in all_players
        if other.name != player.name
    ]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]


# ---------------------------------------------------------------------------
# Prop projection engine
# ---------------------------------------------------------------------------

def _matchup_multiplier(
    player: PlayerProfile,
    defense: DefensiveMatchup,
    league_avg_ppp: float = 1.00,
) -> float:
    """
    Compute a scoring multiplier based on how the opposing defense performs
    against the player's dominant play types.

    multiplier > 1.0 → favorable matchup (defense struggles)
    multiplier < 1.0 → tough matchup (defense is elite)
    """
    total_freq = 0.0
    weighted_def_ppp = 0.0

    for pt, pt_stats in player.play_types.items():
        def_stats = defense.play_types.get(pt)
        if def_stats is None:
            continue
        weighted_def_ppp += pt_stats.frequency * def_stats.ppp
        total_freq += pt_stats.frequency

    if total_freq == 0:
        return 1.0

    weighted_def_ppp /= total_freq
    return weighted_def_ppp / league_avg_ppp


def project_props(
    player: PlayerProfile,
    defense: DefensiveMatchup,
    lines: Optional[Dict[str, float]] = None,
) -> List[PropRecommendation]:
    """
    Project points, assists, and rebounds for *player* against *defense*,
    then compare to bookmaker *lines* to generate recommendations.

    lines: dict with optional keys "points", "assists", "rebounds"
    """
    if lines is None:
        lines = {}

    multiplier = _matchup_multiplier(player, defense)

    # Applies matchup multiplier mainly to points; assists/rebounds scale less
    projected_pts = round(player.avg_points * multiplier, 1)
    projected_ast = round(player.avg_assists * (1 + (multiplier - 1) * 0.4), 1)
    projected_reb = round(player.avg_rebounds * (1 + (multiplier - 1) * 0.2), 1)

    # Build descriptive matchup note
    dom_types = player.dominant_play_types(top_n=2)
    dom_def_ppps = [
        f"{pt.replace('_', ' ')} ({defense.play_types[pt].ppp:.2f} PPP allowed)"
        for pt in dom_types
        if pt in defense.play_types
    ]
    matchup_note = (
        f"{defense.team} defense vs {player.position} dominant play types: "
        + ", ".join(dom_def_ppps)
        + f" | multiplier={multiplier:.3f}"
    )

    recs = []
    prop_map = {
        "points":   (projected_pts,  player.avg_points),
        "assists":  (projected_ast,  player.avg_assists),
        "rebounds": (projected_reb,  player.avg_rebounds),
    }

    for prop_type, (projection, season_avg) in prop_map.items():
        line = lines.get(prop_type, season_avg)
        edge = round(projection - line, 1)
        abs_edge = abs(edge)

        if abs_edge >= 2.5:
            confidence = "HIGH"
        elif abs_edge >= 1.0:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        recs.append(PropRecommendation(
            player_name=player.name,
            prop_type=prop_type,
            line=line,
            projection=projection,
            edge=edge,
            confidence=confidence,
            matchup_notes=matchup_note,
        ))

    return recs


# ---------------------------------------------------------------------------
# Full analysis pipeline
# ---------------------------------------------------------------------------

def analyze_matchup(
    player: PlayerProfile,
    defense: DefensiveMatchup,
    all_players: List[PlayerProfile],
    lines: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Run the full analysis pipeline for a player vs. a specific defense:
    1. Find similar players by position + play type
    2. Project props using defensive matchup data
    3. Return a structured result dict
    """
    similar = find_similar_players(player, all_players, top_n=3)
    props = project_props(player, defense, lines)

    return {
        "player": player.name,
        "position": player.position,
        "opponent": defense.team,
        "dominant_play_types": player.dominant_play_types(top_n=3),
        "similar_players": [
            {"name": p.name, "position": p.position, "similarity": round(s, 3)}
            for p, s in similar
        ],
        "prop_recommendations": [
            {
                "prop":       r.prop_type,
                "line":       r.line,
                "projection": r.projection,
                "edge":       r.edge,
                "confidence": r.confidence,
                "notes":      r.matchup_notes,
            }
            for r in props
        ],
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _print_analysis(result: Dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Player : {result['player']} ({result['position']})")
    print(f"  Opponent: {result['opponent']}")
    print(f"  Dominant play types: {', '.join(result['dominant_play_types'])}")
    print(f"\n  Similar players (by position + play-type profile):")
    for sp in result["similar_players"]:
        print(f"    • {sp['name']} ({sp['position']}) — similarity: {sp['similarity']}")
    print(f"\n  Prop Recommendations:")
    for rec in result["prop_recommendations"]:
        direction = "OVER" if rec["edge"] > 0 else "UNDER"
        print(
            f"    [{rec['confidence']:6s}] {rec['prop'].capitalize():9s} "
            f"Line={rec['line']:.1f}  Proj={rec['projection']:.1f}  "
            f"Edge={rec['edge']:+.1f}  → {direction}"
        )
        print(f"            {rec['notes']}")
    print(f"{'=' * 60}\n")


def main() -> None:
    players = build_sample_players()
    defenses = build_sample_defenses()

    # Index for quick lookup
    defense_map = {d.team: d for d in defenses}

    # Example 1: SGA vs Memphis (weak defense vs isolation & PnR)
    sga = next(p for p in players if "Gilgeous" in p.name)
    result = analyze_matchup(sga, defense_map["MEM"], players)
    _print_analysis(result)

    # Example 2: Nikola Jokic vs Boston (strong defense vs post & screener)
    jokic = next(p for p in players if "Jokic" in p.name)
    result = analyze_matchup(jokic, defense_map["BOS"], players)
    _print_analysis(result)

    # Example 3: Stephen Curry vs OKC (elite defense vs spot-up & off-screen)
    curry = next(p for p in players if "Curry" in p.name)
    result = analyze_matchup(curry, defense_map["OKC"], players)
    _print_analysis(result)


if __name__ == "__main__":
    main()
