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
class DefensiveSpotUpStats:
    """Defensive spot-up stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs spot-up
    freq_pct: float     # frequency % of spot-up possessions allowed
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
    percentile: float   # NBA Synergy composite defensive percentile (higher = better spot-up defense)


@dataclass
class DefensiveHandoffStats:
    """Defensive handoff stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs handoff
    freq_pct: float     # frequency % of handoff possessions allowed
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
    percentile: float   # NBA Synergy composite defensive percentile (higher = better handoff defense)


@dataclass
class DefensiveOffScreenStats:
    """Defensive off-screen stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs off-screen
    freq_pct: float     # frequency % of off-screen possessions allowed
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
    percentile: float   # NBA Synergy composite defensive percentile (higher = better off-screen defense)


@dataclass
class DefensivePutbackStats:
    """Defensive putback stats for a single NBA team (NBA Synergy)."""
    team: str
    gp: int             # games played
    poss: float         # possessions per game allowed vs putback
    freq_pct: float     # frequency % of putback possessions allowed
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
    percentile: float   # NBA Synergy composite defensive percentile (higher = better putback defense)


@dataclass
class OffensiveTransitionStats:
    """Offensive transition stats for a single NBA player (NBA Synergy)."""
    player: str
    team: str
    gp: int              # games played
    poss: float          # transition possessions per game
    freq_pct: float      # frequency % of total possessions
    ppp: float           # points per possession
    pts: float           # transition points per game
    fgm: float           # field goals made per game
    fga: float           # field goals attempted per game
    fg_pct: float        # FG%
    efg_pct: float       # eFG%
    ft_freq_pct: float   # free-throw frequency %
    tov_freq_pct: float  # turnover frequency %
    sf_freq_pct: float   # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float    # NBA Synergy composite offensive percentile (higher = better transition scorer)


@dataclass
class OffensiveIsolationStats:
    """Offensive isolation stats for a single NBA player (NBA Synergy)."""
    player: str
    team: str
    gp: int              # games played
    poss: float          # isolation possessions per game
    freq_pct: float      # frequency % of total possessions
    ppp: float           # points per possession
    pts: float           # isolation points per game
    fgm: float           # field goals made per game
    fga: float           # field goals attempted per game
    fg_pct: float        # FG%
    efg_pct: float       # eFG%
    ft_freq_pct: float   # free-throw frequency %
    tov_freq_pct: float  # turnover frequency %
    sf_freq_pct: float   # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float    # NBA Synergy composite offensive percentile (higher = better isolation scorer)


@dataclass
class OffensivePnrBallHandlerStats:
    """Offensive pick-and-roll ball handler stats for a single NBA player (NBA Synergy)."""
    player: str
    team: str
    gp: int              # games played
    poss: float          # PnR ball handler possessions per game
    freq_pct: float      # frequency % of total possessions
    ppp: float           # points per possession
    pts: float           # PnR ball handler points per game
    fgm: float           # field goals made per game
    fga: float           # field goals attempted per game
    fg_pct: float        # FG%
    efg_pct: float       # eFG%
    ft_freq_pct: float   # free-throw frequency %
    tov_freq_pct: float  # turnover frequency %
    sf_freq_pct: float   # shooting-foul frequency %
    and_one_freq_pct: float  # and-one frequency %
    score_freq_pct: float    # score frequency %
    percentile: float    # NBA Synergy composite offensive percentile (higher = better PnR ball handler)


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
        _make_player_profile(
            "Josh Hart", "SF", "NYK",
            avg_points=9.7, avg_assists=5.0, avg_rebounds=8.2,
            play_type_data={
                "cut":              {"frequency": 0.30, "ppp": 1.18, "percentile": 75},
                "spot_up":          {"frequency": 0.25, "ppp": 1.02, "percentile": 58},
                "pnr_ball_handler": {"frequency": 0.18, "ppp": 0.92, "percentile": 48},
                "putback":          {"frequency": 0.12, "ppp": 1.10, "percentile": 65},
                "misc":             {"frequency": 0.15, "ppp": 0.85, "percentile": 42},
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
        ("SAS", {
            "isolation":        {"frequency": 0.0, "ppp": 0.92, "percentile": 66},
            "pnr_ball_handler": {"frequency": 0.0, "ppp": 0.96, "percentile": 58},
            "pnr_screener":     {"frequency": 0.0, "ppp": 0.98, "percentile": 54},
            "post_up":          {"frequency": 0.0, "ppp": 0.95, "percentile": 60},
            "spot_up":          {"frequency": 0.0, "ppp": 0.99, "percentile": 52},
            "off_screen":       {"frequency": 0.0, "ppp": 0.97, "percentile": 56},
            "hand_off":         {"frequency": 0.0, "ppp": 0.96, "percentile": 58},
            "cut":              {"frequency": 0.0, "ppp": 1.02, "percentile": 46},
            "putback":          {"frequency": 0.0, "ppp": 1.00, "percentile": 50},
            "misc":             {"frequency": 0.0, "ppp": 0.97, "percentile": 56},
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


def build_spot_up_defensive_rankings() -> Dict[str, "DefensiveSpotUpStats"]:
    """
    Return defensive spot-up stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger spot-up defense (limiting both the frequency and efficiency of
    opponent spot-up possessions).
    """
    raw = [
        # (team_abbr, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("ORL", 53, 24.6, 21.8, 1.06, 26.1,  8.7, 21.8, 39.8, 53.0,  7.3, 5.4, 6.8, 1.1, 41.1,  20.7),
        ("HOU", 56, 23.7, 21.3, 1.05, 24.9,  8.7, 22.0, 39.5, 53.0,  4.5, 3.6, 4.5, 1.1, 40.1,  51.7),
        ("DET", 55, 26.5, 23.3, 0.97, 25.7,  8.5, 23.4, 36.2, 49.3,  6.6, 6.2, 5.6, 1.1, 37.1, 100.0),
        ("MIN", 57, 24.3, 21.1, 1.04, 25.2,  8.6, 21.8, 39.6, 52.9,  5.9, 5.2, 5.3, 0.9, 40.3,  58.6),
        ("IND", 57, 24.2, 21.1, 1.05, 25.6,  8.9, 22.1, 40.1, 53.6,  5.4, 4.9, 4.9, 1.5, 40.4,  34.5),
        ("CHA", 58, 25.0, 22.8, 1.03, 25.9,  8.9, 22.8, 39.3, 53.0,  4.5, 5.2, 4.1, 0.8, 39.4,  65.5),
        ("DAL", 55, 27.4, 23.5, 1.00, 27.5,  9.7, 25.1, 38.5, 50.3,  5.4, 4.6, 5.3, 1.4, 39.1,  89.7),
        ("SAS", 54, 26.6, 23.5, 1.06, 28.1,  9.7, 24.4, 39.8, 53.8,  5.1, 4.4, 4.9, 1.0, 40.2,  24.1),
        ("NYK", 55, 27.5, 24.7, 1.02, 27.9,  9.4, 24.7, 38.0, 51.4,  5.8, 5.0, 5.2, 0.9, 38.9,  82.8),
        ("PHX", 56, 27.0, 24.0, 1.02, 27.5,  9.5, 24.6, 38.6, 51.7,  5.2, 4.8, 4.8, 1.3, 39.0,  79.3),
        ("LAC", 55, 27.3, 24.8, 1.03, 28.2,  9.7, 24.9, 38.7, 52.5,  4.7, 5.0, 4.7, 1.2, 39.0,  69.0),
        ("POR", 58, 26.0, 22.5, 1.03, 26.9,  9.3, 23.6, 39.4, 53.1,  5.1, 5.2, 4.6, 1.0, 39.5,  62.1),
        ("LAL", 55, 27.3, 24.5, 1.05, 28.7, 10.1, 24.7, 40.8, 54.6,  4.5, 6.0, 4.3, 1.0, 40.2,  44.8),
        ("MIA", 57, 28.7, 24.3, 0.98, 28.2,  9.6, 25.8, 37.1, 50.2,  4.9, 5.8, 4.8, 0.7, 37.5,  96.6),
        ("BOS", 57, 28.0, 25.8, 1.01, 28.4,  9.7, 26.0, 37.2, 51.5,  3.9, 4.4, 3.8, 1.1, 37.2,  86.2),
        ("SAC", 58, 27.1, 23.9, 1.05, 28.6,  9.7, 24.5, 39.7, 53.5,  5.5, 5.1, 5.3, 1.0, 40.2,  37.9),
        ("ATL", 59, 28.2, 24.4, 1.00, 28.2,  9.7, 25.7, 37.6, 50.5,  5.5, 5.0, 5.4, 1.3, 38.4,  93.1),
        ("PHI", 56, 28.9, 25.1, 1.03, 29.7,  9.9, 25.5, 39.0, 52.8,  6.5, 6.4, 6.0, 1.0, 39.6,  72.4),
        ("WAS", 55, 27.1, 23.1, 1.13, 30.5, 10.3, 24.7, 41.6, 56.8,  6.1, 3.6, 5.6, 1.1, 42.8,   0.0),
        ("MEM", 55, 29.5, 25.5, 1.05, 31.0, 10.6, 26.9, 39.3, 53.6,  5.5, 5.0, 5.0, 1.6, 39.3,  48.3),
        ("GSW", 57, 27.6, 24.3, 1.08, 29.9, 10.2, 24.9, 40.8, 54.9,  5.6, 5.0, 5.2, 0.8, 41.5,   6.9),
        ("CLE", 58, 28.4, 24.7, 1.05, 29.8, 10.2, 25.8, 39.7, 54.4,  4.2, 5.8, 3.9, 1.0, 39.3,  41.4),
        ("CHI", 58, 28.5, 24.8, 1.06, 30.3, 10.5, 26.0, 40.3, 54.0,  5.4, 4.7, 5.1, 1.3, 40.7,  17.2),
        ("TOR", 57, 29.6, 26.3, 1.04, 30.9, 10.4, 26.6, 38.9, 52.2,  6.9, 5.2, 6.2, 1.8, 40.0,  55.2),
        ("MIL", 55, 30.1, 27.0, 1.07, 32.1, 10.9, 27.2, 40.1, 54.4,  5.3, 5.3, 4.9, 0.9, 40.4,  13.8),
        ("BKN", 56, 29.1, 26.7, 1.09, 31.6, 11.2, 26.4, 42.2, 55.7,  4.9, 5.1, 4.5, 0.9, 42.2,   3.4),
        ("NOP", 58, 29.1, 25.0, 1.06, 30.7, 10.5, 26.5, 39.6, 53.8,  5.5, 4.7, 5.2, 1.4, 39.6,  27.6),
        ("DEN", 58, 30.4, 27.0, 1.03, 31.2, 10.5, 27.5, 38.1, 51.6,  6.0, 4.6, 5.7, 1.2, 39.0,  75.9),
        ("OKC", 56, 30.7, 26.7, 1.06, 32.4, 11.2, 28.1, 39.7, 54.6,  3.5, 5.7, 3.1, 0.7, 39.1,  31.0),
        ("UTA", 58, 31.7, 27.1, 1.08, 34.3, 11.5, 28.3, 40.7, 55.1,  6.8, 5.5, 6.4, 1.5, 41.3,  10.3),
    ]

    rankings: Dict[str, DefensiveSpotUpStats] = {}
    for row in raw:
        (abbr, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensiveSpotUpStats(
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


def rank_teams_by_spot_up_defense(
    rankings: Optional[Dict[str, "DefensiveSpotUpStats"]] = None,
) -> List["DefensiveSpotUpStats"]:
    """
    Return all teams sorted from best to worst spot-up defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_spot_up_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def find_spot_up_beneficiaries(
    players: List[PlayerProfile],
    opponent_team: str,
    spot_up_rankings: Optional[Dict[str, "DefensiveSpotUpStats"]] = None,
    min_spot_up_freq: float = 0.10,
    ppp_threshold: float = 1.03,
) -> List[Dict]:
    """
    Identify players who are likely to benefit from a weak spot-up defense.

    A player is flagged as a beneficiary when:
    - Their spot-up play frequency is at least *min_spot_up_freq*
    - The opposing team's spot-up defensive PPP allowed is >= *ppp_threshold*
      (meaning the defense struggles to contain spot-up shooters)

    Returns a list of dicts sorted by spot-up frequency (highest first), each
    containing:
      - "player"        : player name
      - "position"      : player position
      - "spot_up_freq"  : player's spot-up frequency (0–1)
      - "spot_up_ppp"   : player's historical spot-up PPP
      - "def_ppp"       : opponent's spot-up defensive PPP allowed
      - "def_percentile": opponent's spot-up defensive percentile (lower = weaker)
      - "edge"          : player spot-up PPP minus opponent defensive PPP
    """
    if spot_up_rankings is None:
        spot_up_rankings = build_spot_up_defensive_rankings()

    def_stats = spot_up_rankings.get(opponent_team)
    if def_stats is None:
        return []

    results = []
    for player in players:
        su_stats = player.play_types.get("spot_up")
        if su_stats is None:
            continue
        if su_stats.frequency < min_spot_up_freq:
            continue
        if def_stats.ppp < ppp_threshold:
            continue
        results.append({
            "player":         player.name,
            "position":       player.position,
            "spot_up_freq":   su_stats.frequency,
            "spot_up_ppp":    su_stats.ppp,
            "def_ppp":        def_stats.ppp,
            "def_percentile": def_stats.percentile,
            "edge":           round(su_stats.ppp - def_stats.ppp, 3),
        })

    results.sort(key=lambda r: r["spot_up_freq"], reverse=True)
    return results


def build_handoff_defensive_rankings() -> Dict[str, "DefensiveHandoffStats"]:
    """
    Return defensive handoff stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger handoff defense (limiting both the frequency and efficiency of
    opponent handoff possessions).
    """
    raw = [
        # (team_abbr, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("BKN", 56, 4.1, 3.7, 0.82, 3.3, 1.1, 3.1, 36.4, 44.9,  8.3, 15.8,  7.0, 1.3, 34.6,  96.6),
        ("MIA", 57, 4.8, 4.0, 0.82, 3.9, 1.4, 3.7, 36.2, 42.7,  9.2, 14.7,  8.8, 2.2, 35.3, 100.0),
        ("GSW", 57, 4.7, 4.2, 0.86, 4.1, 1.5, 3.7, 40.6, 46.0, 10.0, 13.8,  9.7, 2.6, 39.0,  86.2),
        ("TOR", 57, 4.6, 4.1, 0.88, 4.1, 1.3, 3.8, 34.4, 43.1, 10.2,  8.7,  8.0, 1.5, 37.1,  79.3),
        ("SAC", 58, 4.2, 3.7, 0.96, 4.0, 1.5, 3.5, 42.4, 50.7,  7.0,  9.9,  6.2, 1.7, 41.3,  37.9),
        ("OKC", 56, 4.9, 4.3, 0.86, 4.2, 1.4, 3.8, 35.8, 43.9, 11.2, 13.0, 10.1, 0.7, 37.2,  89.7),
        ("UTA", 58, 3.9, 3.3, 1.07, 4.1, 1.5, 3.2, 47.0, 58.2,  8.4, 12.0,  7.6, 1.8, 44.9,   6.9),
        ("LAL", 55, 4.1, 3.7, 1.09, 4.5, 1.6, 3.5, 45.9, 56.2,  8.4,  8.4,  7.5, 2.2, 44.9,   3.4),
        ("DEN", 58, 4.5, 4.0, 0.95, 4.3, 1.4, 3.5, 39.5, 47.6, 11.5, 11.2, 11.2, 1.5, 41.2,  44.8),
        ("PHI", 56, 4.6, 4.0, 0.96, 4.4, 1.5, 3.6, 41.3, 47.8, 13.5, 10.8, 11.2, 1.9, 43.2,  27.6),
        ("BOS", 57, 4.6, 4.3, 0.96, 4.4, 1.5, 3.8, 39.9, 48.9,  8.7,  9.8,  8.7, 1.1, 40.2,  41.4),
        ("NYK", 55, 5.1, 4.6, 0.91, 4.6, 1.6, 4.4, 37.3, 44.6,  9.6,  6.8,  9.6, 2.5, 38.9,  72.4),
        ("LAC", 55, 5.4, 5.0, 0.89, 4.8, 1.7, 4.0, 42.1, 50.7,  8.4, 18.7,  7.7, 1.0, 38.1,  75.9),
        ("NOP", 58, 4.7, 4.0, 0.98, 4.6, 1.6, 3.8, 41.9, 52.7,  8.1, 11.0,  7.4, 0.7, 41.5,  20.7),
        ("MEM", 55, 5.7, 4.9, 0.85, 4.9, 1.7, 4.7, 36.2, 43.4,  9.2, 11.1,  8.3, 1.9, 36.8,  93.1),
        ("PHX", 56, 5.2, 4.6, 0.94, 4.9, 1.7, 4.1, 40.1, 48.7,  8.6, 12.4,  7.2, 1.0, 39.7,  55.2),
        ("DET", 55, 5.4, 4.7, 0.93, 5.0, 1.6, 4.0, 39.8, 48.6, 13.2, 13.6, 12.2, 1.7, 40.3,  58.6),
        ("CLE", 58, 5.0, 4.4, 0.94, 4.7, 1.7, 4.0, 41.0, 48.9,  8.6, 12.0,  7.9, 1.0, 40.5,  51.7),
        ("MIL", 55, 4.8, 4.3, 1.04, 5.0, 1.7, 3.8, 43.1, 53.3, 12.5, 10.9, 12.5, 3.0, 43.4,  10.3),
        ("HOU", 56, 5.2, 4.6, 0.97, 5.0, 1.9, 4.4, 43.1, 49.8,  9.0,  8.0,  8.3, 2.1, 42.2,  24.1),
        ("CHA", 58, 5.6, 5.1, 0.87, 4.9, 1.7, 4.7, 37.3, 43.9,  8.9,  9.2,  7.7, 1.2, 38.7,  82.8),
        ("ORL", 53, 5.6, 5.0, 1.00, 5.6, 2.0, 4.7, 43.5, 52.0,  8.1, 10.4,  7.4, 2.0, 42.4,  17.2),
        ("POR", 58, 5.7, 4.9, 0.91, 5.2, 1.8, 4.7, 39.6, 47.2,  8.8, 11.2,  7.9, 1.5, 39.3,  69.0),
        ("ATL", 59, 5.6, 4.8, 0.92, 5.1, 1.8, 4.6, 39.6, 47.0,  9.4, 10.3,  8.5, 1.5, 40.0,  65.5),
        ("MIN", 57, 5.7, 4.9, 0.96, 5.4, 2.1, 4.8, 43.6, 50.0,  8.0,  9.6,  7.4, 2.2, 42.7,  34.5),
        ("DAL", 55, 6.0, 5.2, 0.96, 5.8, 2.3, 5.3, 43.6, 49.7,  6.0,  8.5,  6.0, 1.8, 42.0,  31.0),
        ("WAS", 55, 5.3, 4.6, 1.09, 5.8, 2.0, 4.2, 48.3, 57.2, 11.9, 11.3, 10.6, 1.7, 47.4,   0.0),
        ("IND", 57, 5.9, 5.1, 0.95, 5.6, 2.1, 4.5, 46.5, 52.8, 11.3, 16.3, 10.7, 3.0, 43.3,  48.3),
        ("CHI", 58, 5.6, 4.8, 1.00, 5.6, 1.9, 4.5, 41.1, 49.8, 11.5,  9.6, 10.9, 2.8, 41.6,  13.8),
        ("SAS", 54, 6.8, 6.0, 0.93, 6.3, 2.4, 5.6, 42.1, 47.8,  8.7, 10.1,  8.2, 1.4, 41.0,  62.1),
    ]

    rankings: Dict[str, DefensiveHandoffStats] = {}
    for row in raw:
        (abbr, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensiveHandoffStats(
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


def rank_teams_by_handoff_defense(
    rankings: Optional[Dict[str, "DefensiveHandoffStats"]] = None,
) -> List["DefensiveHandoffStats"]:
    """
    Return all teams sorted from best to worst handoff defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_handoff_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def find_handoff_beneficiaries(
    players: List[PlayerProfile],
    opponent_team: str,
    handoff_rankings: Optional[Dict[str, "DefensiveHandoffStats"]] = None,
    min_handoff_freq: float = 0.05,
    ppp_threshold: float = 1.00,
) -> List[Dict]:
    """
    Identify players who are likely to benefit from a weak handoff defense.

    A player is flagged as a beneficiary when:
    - Their handoff play frequency is at least *min_handoff_freq*
    - The opposing team's handoff defensive PPP allowed is >= *ppp_threshold*
      (meaning the defense struggles to contain handoff actions)

    Returns a list of dicts sorted by handoff frequency (highest first), each
    containing:
      - "player"         : player name
      - "position"       : player position
      - "handoff_freq"   : player's handoff frequency (0–1)
      - "handoff_ppp"    : player's historical handoff PPP
      - "def_ppp"        : opponent's handoff defensive PPP allowed
      - "def_percentile" : opponent's handoff defensive percentile (lower = weaker)
      - "edge"           : player handoff PPP minus opponent defensive PPP
    """
    if handoff_rankings is None:
        handoff_rankings = build_handoff_defensive_rankings()

    def_stats = handoff_rankings.get(opponent_team)
    if def_stats is None:
        return []

    results = []
    for player in players:
        ho_stats = player.play_types.get("handoff")
        if ho_stats is None:
            continue
        if ho_stats.frequency < min_handoff_freq:
            continue
        if def_stats.ppp < ppp_threshold:
            continue
        results.append({
            "player":         player.name,
            "position":       player.position,
            "handoff_freq":   ho_stats.frequency,
            "handoff_ppp":    ho_stats.ppp,
            "def_ppp":        def_stats.ppp,
            "def_percentile": def_stats.percentile,
            "edge":           round(ho_stats.ppp - def_stats.ppp, 3),
        })

    results.sort(key=lambda r: r["handoff_freq"], reverse=True)
    return results


def build_off_screen_defensive_rankings() -> Dict[str, "DefensiveOffScreenStats"]:
    """
    Return defensive off-screen stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger off-screen defense (limiting both the frequency and efficiency of
    opponent off-screen possessions).
    """
    raw = [
        # (team_abbr, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("UTA", 58, 9.1, 7.7, 0.94, 8.5, 2.9, 7.7, 38.0, 46.9,  9.1,  8.2,  8.6, 2.1, 38.7,  27.6),
        ("ATL", 59, 6.6, 5.7, 0.99, 6.5, 2.3, 5.6, 40.4, 51.8,  7.2,  9.3,  6.4, 1.0, 40.1,  55.2),
        ("GSW", 57, 7.4, 6.5, 0.91, 6.7, 2.2, 6.6, 33.7, 46.1,  4.3,  6.7,  4.3, 0.2, 34.1,  17.2),
        ("DEN", 58, 4.8, 4.4, 1.23, 5.9, 1.8, 4.1, 44.6, 59.0, 11.4,  4.3, 10.7, 1.4, 48.2, 100.0),
        ("LAL", 55, 5.6, 5.1, 1.11, 6.2, 2.3, 4.9, 46.5, 55.9,  9.7,  4.9,  9.4, 2.3, 47.6,  96.6),
        ("MIN", 57, 5.7, 5.0, 1.04, 5.9, 2.0, 4.8, 41.7, 53.8,  7.7,  8.0,  6.8, 1.2, 42.1,  75.9),
        ("BOS", 57, 5.6, 5.1, 0.96, 5.4, 1.9, 5.0, 37.8, 47.6,  6.6,  4.7,  6.3, 0.9, 39.2,  51.7),
        ("DAL", 55, 5.5, 4.8, 0.96, 5.3, 2.0, 4.8, 41.7, 50.6,  4.9,  9.2,  4.6, 0.7, 40.3,  48.3),
        ("TOR", 57, 4.8, 4.3, 1.05, 5.1, 1.9, 4.3, 44.9, 52.4,  8.7,  4.4,  8.0, 2.2, 45.8,  86.2),
        ("SAS", 54, 5.5, 4.8, 0.94, 5.1, 1.9, 4.8, 40.0, 47.5,  7.1,  6.4,  6.4, 1.7, 40.3,  34.5),
        ("SAC", 58, 3.7, 3.3, 1.10, 4.1, 1.5, 3.3, 46.6, 54.5, 10.1,  5.1,  9.7, 2.3, 48.4,  93.1),
        ("IND", 57, 4.6, 4.0, 0.89, 4.1, 1.5, 4.1, 35.9, 45.2,  6.5,  7.6,  6.1, 1.9, 36.1,  10.3),
        ("WAS", 55, 4.1, 3.6, 1.00, 4.1, 1.5, 3.5, 44.0, 52.6,  7.1,  9.3,  6.6, 1.8, 41.6,  63.0),
        ("MIA", 57, 4.2, 3.5, 0.95, 4.0, 1.3, 3.5, 37.9, 46.2, 12.2,  6.7, 10.1, 2.1, 41.2,  44.8),
        ("PHI", 56, 4.0, 3.5, 1.00, 4.0, 1.4, 3.5, 39.1, 49.0,  7.6,  5.8,  6.3, 1.3, 40.2,  63.0),
        ("BKN", 56, 3.9, 3.5, 0.94, 3.7, 1.3, 3.4, 37.9, 50.0,  6.4, 10.0,  5.9, 3.2, 36.1,  37.9),
        ("DET", 55, 4.3, 3.7, 0.84, 3.7, 1.3, 3.7, 34.7, 42.8,  7.1,  8.8,  5.5, 0.8, 35.3,   3.4),
        ("PHX", 56, 4.0, 3.5, 0.89, 3.6, 1.3, 3.4, 37.4, 46.8,  7.1, 10.7,  6.7, 2.7, 35.7,  13.8),
        ("MEM", 55, 3.4, 2.9, 1.05, 3.6, 1.2, 2.8, 43.6, 54.8,  9.6,  9.6,  9.0, 2.1, 43.1,  82.8),
        ("ORL", 53, 3.9, 3.4, 0.95, 3.7, 1.3, 3.3, 38.9, 45.1, 13.1,  5.3, 12.1, 3.4, 42.7,  41.4),
        ("CHA", 58, 3.0, 2.7, 1.02, 3.1, 1.0, 2.7, 38.2, 51.0,  6.9,  6.9,  6.9, 3.4, 37.7,  72.4),
        ("CLE", 58, 3.0, 2.6, 1.01, 3.0, 1.2, 2.6, 45.4, 55.6,  2.3,  9.3,  1.7, 0.0, 42.4,  69.0),
        ("NOP", 58, 3.0, 2.6, 0.91, 2.7, 1.0, 2.6, 40.0, 47.0,  7.5,  8.6,  6.9, 2.3, 39.1,  20.7),
        ("OKC", 56, 2.5, 2.2, 1.09, 2.7, 1.0, 2.2, 45.1, 54.1,  9.4,  5.0,  7.9, 2.2, 46.0,  89.7),
        ("NYK", 55, 2.7, 2.4, 1.00, 2.7, 1.0, 2.4, 40.6, 49.2,  6.8,  4.1,  6.1, 1.4, 42.2,  63.0),
        ("LAC", 55, 2.5, 2.3, 1.05, 2.6, 0.9, 2.2, 42.9, 52.1,  8.9,  5.9,  8.9, 3.0, 43.0,  79.3),
        ("HOU", 56, 2.9, 2.6, 0.85, 2.5, 1.0, 2.6, 37.8, 43.2,  4.9,  6.1,  4.9, 1.2, 37.2,   6.9),
        ("POR", 58, 2.6, 2.2, 0.80, 2.1, 0.7, 2.2, 33.3, 40.9,  8.7, 10.1,  8.1, 3.4, 32.9,   0.0),
        ("MIL", 55, 2.2, 2.0, 0.94, 2.1, 0.7, 2.0, 36.1, 49.1,  3.3,  7.4,  2.5, 0.0, 35.5,  31.0),
        ("CHI", 58, 2.1, 1.8, 0.93, 2.0, 0.7, 1.8, 37.4, 48.1,  7.4,  8.2,  6.6, 3.3, 36.9,  24.1),
    ]

    rankings: Dict[str, DefensiveOffScreenStats] = {}
    for row in raw:
        (abbr, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensiveOffScreenStats(
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


def rank_teams_by_off_screen_defense(
    rankings: Optional[Dict[str, "DefensiveOffScreenStats"]] = None,
) -> List["DefensiveOffScreenStats"]:
    """
    Return all teams sorted from best to worst off-screen defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_off_screen_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def find_off_screen_beneficiaries(
    players: List[PlayerProfile],
    opponent_team: str,
    off_screen_rankings: Optional[Dict[str, "DefensiveOffScreenStats"]] = None,
    min_off_screen_freq: float = 0.05,
    ppp_threshold: float = 1.00,
) -> List[Dict]:
    """
    Identify players who are likely to benefit from a weak off-screen defense.

    A player is flagged as a beneficiary when:
    - Their off-screen play frequency is at least *min_off_screen_freq*
    - The opposing team's off-screen defensive PPP allowed is >= *ppp_threshold*
      (meaning the defense struggles to contain off-screen actions)

    Returns a list of dicts sorted by off-screen frequency (highest first), each
    containing:
      - "player"            : player name
      - "position"          : player position
      - "off_screen_freq"   : player's off-screen frequency (0–1)
      - "off_screen_ppp"    : player's historical off-screen PPP
      - "def_ppp"           : opponent's off-screen defensive PPP allowed
      - "def_percentile"    : opponent's off-screen defensive percentile (lower = weaker)
      - "edge"              : player off-screen PPP minus opponent defensive PPP
    """
    if off_screen_rankings is None:
        off_screen_rankings = build_off_screen_defensive_rankings()

    def_stats = off_screen_rankings.get(opponent_team)
    if def_stats is None:
        return []

    results = []
    for player in players:
        os_stats = player.play_types.get("off_screen")
        if os_stats is None:
            continue
        if os_stats.frequency < min_off_screen_freq:
            continue
        if def_stats.ppp < ppp_threshold:
            continue
        results.append({
            "player":           player.name,
            "position":         player.position,
            "off_screen_freq":  os_stats.frequency,
            "off_screen_ppp":   os_stats.ppp,
            "def_ppp":          def_stats.ppp,
            "def_percentile":   def_stats.percentile,
            "edge":             round(os_stats.ppp - def_stats.ppp, 3),
        })

    results.sort(key=lambda r: r["off_screen_freq"], reverse=True)
    return results


def build_putback_defensive_rankings() -> Dict[str, "DefensivePutbackStats"]:
    """
    Return defensive putback stats for all 30 NBA teams (NBA Synergy data).

    Columns: GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    stronger putback defense (limiting both the frequency and efficiency of
    opponent putback possessions).
    """
    raw = [
        # (team_abbr, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("BKN", 56, 5.1, 4.7, 1.04, 5.4, 2.2, 4.2, 53.0, 53.2, 12.8,  6.9, 10.8, 1.7, 52.8,  89.7),
        ("ORL", 53, 5.5, 4.9, 1.07, 5.9, 2.5, 4.5, 56.0, 57.3, 12.3,  8.5, 11.9, 3.1, 53.6,  72.4),
        ("NYK", 55, 5.5, 5.0, 1.05, 5.8, 2.4, 4.5, 54.1, 54.5, 11.9,  9.6, 11.2, 2.6, 52.5,  86.2),
        ("SAS", 54, 5.4, 4.7, 1.10, 5.9, 2.5, 4.6, 54.6, 55.6, 10.3,  5.9, 10.3, 2.1, 54.8,  55.2),
        ("LAC", 55, 5.6, 5.1, 1.06, 5.9, 2.3, 4.6, 51.2, 51.6, 12.7,  6.5, 11.8, 1.6, 52.9,  79.3),
        ("MIL", 55, 5.5, 5.0, 1.08, 6.0, 2.4, 4.5, 54.3, 54.5, 13.8,  7.9, 12.8, 2.3, 54.9,  69.0),
        ("CHA", 58, 5.4, 4.9, 1.06, 5.7, 2.4, 4.2, 57.0, 58.5, 12.7, 12.4, 12.1, 2.2, 53.2,  75.9),
        ("MIN", 57, 5.8, 5.0, 1.01, 5.9, 2.5, 4.8, 52.8, 53.3, 12.4,  7.9, 11.8, 2.1, 51.7,  96.6),
        ("LAL", 55, 5.5, 4.9, 1.13, 6.2, 2.7, 4.6, 59.4, 60.0,  9.9,  8.6,  8.9, 1.7, 57.0,  37.9),
        ("CLE", 58, 6.1, 5.3, 1.01, 6.1, 2.4, 4.9, 49.3, 50.2, 13.4,  7.7, 11.7, 2.0, 51.0, 100.0),
        ("TOR", 57, 6.0, 5.3, 1.05, 6.3, 2.7, 5.0, 54.8, 54.9, 10.6,  8.5, 10.0, 2.1, 53.1,  82.8),
        ("OKC", 56, 6.3, 5.5, 1.02, 6.4, 2.6, 4.9, 54.0, 54.0, 15.6,  8.5, 14.4, 1.1, 54.7,  93.1),
        ("DET", 55, 6.0, 5.3, 1.09, 6.6, 2.7, 4.8, 56.4, 57.1, 14.2,  9.1, 13.6, 3.6, 54.7,  65.5),
        ("GSW", 57, 6.0, 5.3, 1.10, 6.6, 2.8, 5.1, 55.7, 56.5, 12.5,  5.5, 12.5, 2.9, 56.0,  48.3),
        ("HOU", 56, 5.8, 5.2, 1.17, 6.8, 2.9, 4.9, 60.0, 60.5, 10.4,  7.4,  9.2, 2.1, 58.6,  17.2),
        ("PHI", 56, 5.8, 5.1, 1.17, 6.8, 2.9, 4.9, 59.5, 60.0, 11.3,  7.0, 10.4, 2.1, 59.0,  20.7),
        ("DEN", 58, 6.1, 5.5, 1.10, 6.8, 2.9, 5.2, 54.6, 55.3, 11.8,  5.3, 11.2, 2.5, 55.1,  51.7),
        ("BOS", 57, 6.1, 5.6, 1.13, 6.9, 2.8, 4.9, 56.4, 56.6, 15.2,  8.0, 14.7, 4.3, 56.0,  34.5),
        ("MEM", 55, 6.6, 5.7, 1.11, 7.3, 3.3, 5.4, 59.9, 60.4,  9.4, 10.8,  8.6, 3.0, 54.8,  44.8),
        ("CHI", 58, 6.0, 5.2, 1.17, 6.9, 2.9, 4.9, 58.9, 59.2, 14.2,  7.2, 14.2, 2.9, 58.7,  24.1),
        ("IND", 57, 5.9, 5.1, 1.20, 7.1, 2.9, 4.7, 62.2, 62.8, 13.7,  7.7, 13.7, 1.8, 61.0,   3.4),
        ("POR", 58, 6.4, 5.6, 1.09, 7.0, 2.9, 5.0, 57.4, 57.8, 13.1, 10.7, 11.2, 1.1, 55.6,  62.1),
        ("ATL", 59, 5.9, 5.1, 1.17, 6.9, 2.8, 4.7, 60.5, 61.1, 17.4,  7.7, 16.9, 4.0, 60.3,  13.8),
        ("WAS", 55, 6.8, 5.8, 1.10, 7.5, 3.2, 5.6, 56.1, 56.5, 11.7,  7.2, 10.6, 1.3, 55.6,  58.6),
        ("SAC", 58, 5.7, 5.0, 1.25, 7.1, 3.1, 4.9, 63.4, 63.7, 12.4,  5.7, 12.1, 3.9, 61.9,   0.0),
        ("MIA", 57, 6.3, 5.3, 1.18, 7.4, 3.2, 5.2, 60.4, 61.4, 11.5,  9.0, 10.1, 3.9, 57.4,  10.3),
        ("UTA", 58, 6.3, 5.4, 1.16, 7.3, 3.2, 5.2, 61.1, 61.9, 11.7,  8.4, 10.9, 2.4, 58.2,  27.6),
        ("DAL", 55, 7.0, 6.0, 1.12, 7.9, 3.4, 5.7, 59.6, 60.0, 11.6,  8.5, 10.9, 1.3, 57.6,  41.4),
        ("PHX", 56, 6.6, 5.8, 1.19, 7.8, 3.3, 5.4, 60.7, 61.1, 13.0,  6.5, 11.4, 2.4, 60.1,   6.9),
        ("NOP", 58, 7.2, 6.2, 1.15, 8.3, 3.5, 6.0, 58.1, 58.7, 12.4,  7.9, 11.9, 2.9, 57.3,  31.0),
    ]

    rankings: Dict[str, DefensivePutbackStats] = {}
    for row in raw:
        (abbr, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        rankings[abbr] = DefensivePutbackStats(
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


def rank_teams_by_putback_defense(
    rankings: Optional[Dict[str, "DefensivePutbackStats"]] = None,
) -> List["DefensivePutbackStats"]:
    """
    Return all teams sorted from best to worst putback defense
    (highest percentile first).

    If *rankings* is not provided, the full league data is used.
    """
    if rankings is None:
        rankings = build_putback_defensive_rankings()
    return sorted(rankings.values(), key=lambda s: s.percentile, reverse=True)


def find_putback_beneficiaries(
    players: List[PlayerProfile],
    opponent_team: str,
    putback_rankings: Optional[Dict[str, "DefensivePutbackStats"]] = None,
    min_putback_freq: float = 0.05,
    ppp_threshold: float = 1.00,
) -> List[Dict]:
    """
    Identify players who are likely to benefit from a weak putback defense.

    A player is flagged as a beneficiary when:
    - Their putback play frequency is at least *min_putback_freq*
    - The opposing team's putback defensive PPP allowed is >= *ppp_threshold*
      (meaning the defense struggles to contain putback actions)

    Returns a list of dicts sorted by putback frequency (highest first), each
    containing:
      - "player"          : player name
      - "position"        : player position
      - "putback_freq"    : player's putback frequency (0–1)
      - "putback_ppp"     : player's historical putback PPP
      - "def_ppp"         : opponent's putback defensive PPP allowed
      - "def_percentile"  : opponent's putback defensive percentile (lower = weaker)
      - "edge"            : player putback PPP minus opponent defensive PPP
    """
    if putback_rankings is None:
        putback_rankings = build_putback_defensive_rankings()

    def_stats = putback_rankings.get(opponent_team)
    if def_stats is None:
        return []

    results = []
    for player in players:
        pb_stats = player.play_types.get("putback")
        if pb_stats is None:
            continue
        if pb_stats.frequency < min_putback_freq:
            continue
        if def_stats.ppp < ppp_threshold:
            continue
        results.append({
            "player":         player.name,
            "position":       player.position,
            "putback_freq":   pb_stats.frequency,
            "putback_ppp":    pb_stats.ppp,
            "def_ppp":        def_stats.ppp,
            "def_percentile": def_stats.percentile,
            "edge":           round(pb_stats.ppp - def_stats.ppp, 3),
        })

    results.sort(key=lambda r: r["putback_freq"], reverse=True)
    return results


def build_offensive_transition_stats() -> List["OffensiveTransitionStats"]:
    """
    Return offensive transition stats for 196 NBA players (NBA Synergy data).

    Columns: PLAYER, TEAM, GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking. Higher values indicate a
    more efficient/frequent transition scorer.
    """
    raw = [
        # (player, team, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("Brandon Williams",       "DAL", 47,  1.4, 10.7, 1.06,  1.5, 0.6, 1.1, 52.8, 53.8, 16.2, 10.3, 14.7, 4.4, 52.9,  82.9),
        ("Giannis Antetokounmpo", "MIL", 28,  2.6, 10.9, 0.97,  2.5, 1.0, 2.0, 47.4, 48.2, 16.4,  9.6, 15.1, 4.1, 47.9,  67.3),
        ("Cam Thomas",             "BKN", 24,  2.9, 17.2, 1.01,  2.9, 1.0, 2.3, 41.1, 44.6, 17.4,  5.8, 15.9, 4.3, 46.4,  75.9),
        ("Michael Porter Jr.",     "BKN", 45,  1.6,  7.2, 0.96,  1.5, 0.6, 1.3, 47.4, 55.3,  4.2, 16.7,  4.2, 0.0, 41.7,  63.9),
        ("Jalen Duren",            "DET", 46,  1.4,  8.8, 1.08,  1.5, 0.5, 1.1, 50.0, 50.0, 20.6,  3.2, 19.0, 3.2, 57.1,  84.5),
        ("Nikola Jokić",           "DEN", 42,  1.6,  6.5, 1.00,  1.6, 0.7, 1.3, 51.9, 53.7, 10.3, 13.2, 10.3, 2.9, 48.5,  73.0),
        ("Brandon Miller",         "CHA", 42,  2.0,  9.3, 0.81,  1.6, 0.6, 1.7, 35.2, 36.6, 11.9,  6.0, 11.9, 2.4, 39.3,  36.9),
        ("Karl-Anthony Towns",     "NYK", 51,  1.8,  9.5, 0.74,  1.3, 0.4, 1.2, 35.6, 35.6, 19.6, 17.4, 19.6, 1.1, 40.2,  27.3),
        ("Jalen Johnson",          "ATL", 52,  1.9,  8.1, 0.70,  1.3, 0.5, 1.5, 32.5, 33.1, 12.4,  9.3, 11.3, 4.1, 34.0,  19.2),
        ("Ryan Rollins",           "MIL", 53,  1.5,  8.5, 0.86,  1.3, 0.5, 1.2, 36.4, 43.9,  9.0,  9.0,  7.7, 2.6, 37.2,  48.6),
        ("Aaron Gordon",           "DEN", 22,  2.5, 16.0, 1.20,  3.0, 0.9, 1.9, 45.2, 53.6, 24.1,  1.9, 22.2, 3.7, 55.6,  92.2),
        ("Andrew Wiggins",         "MIA", 52,  1.5,  9.8, 0.83,  1.3, 0.5, 1.2, 40.6, 41.4,  9.0, 10.3,  6.4, 1.3, 41.0,  40.7),
        ("Chet Holmgren",          "OKC", 48,  1.3,  8.8, 0.98,  1.3, 0.4, 0.9, 45.5, 48.9, 22.2, 11.1, 20.6, 3.2, 50.8,  68.6),
        ("Kelly Oubre Jr.",        "PHI", 36,  1.6, 11.5, 1.05,  1.7, 0.6, 1.3, 48.9, 48.9, 15.8,  7.0, 15.8, 5.3, 50.9,  81.6),
        ("Jrue Holiday",           "POR", 31,  2.0, 11.7, 0.97,  1.9, 0.8, 1.6, 49.0, 56.1,  3.3, 16.4,  1.6, 0.0, 42.6,  66.5),
        ("Jalen Williams",         "OKC", 23,  2.7, 15.0, 0.95,  2.6, 1.0, 2.3, 42.6, 43.5, 11.3,  3.2, 11.3, 1.6, 46.8,  62.0),
        ("Naji Marshall",          "DAL", 54,  0.9,  6.4, 1.17,  1.0, 0.4, 0.7, 57.5, 57.5, 14.6,  4.2, 12.5, 2.1, 60.4,  91.0),
        ("Jeremiah Fears",         "NOP", 58,  1.2,  7.6, 0.81,  0.9, 0.4, 0.9, 43.4, 45.3,  6.0, 17.9,  3.0, 3.0, 37.3,  36.3),
        ("Kevin Porter Jr.",       "MIL", 33,  1.8,  9.9, 0.87,  1.6, 0.5, 1.4, 36.2, 39.4, 14.8, 11.5, 14.8, 3.3, 39.3,  49.4),
        ("Andrew Nembhard",        "IND", 45,  1.4,  8.0, 0.81,  1.2, 0.4, 1.1, 35.3, 39.2, 10.8, 10.8,  9.2, 0.0, 38.5,  38.4),
        ("Ajay Mitchell",          "OKC", 38,  1.3,  8.9, 1.06,  1.3, 0.5, 0.9, 50.0, 52.8, 18.8, 10.4, 16.7, 4.2, 52.1,  83.7),
        ("Saddiq Bey",             "NOP", 51,  1.2,  7.8, 0.81,  1.0, 0.3, 1.1, 31.5, 33.3, 15.9,  1.6, 15.9, 3.2, 39.7,  36.9),
        ("Stephon Castle",         "SAS", 46,  1.4,  8.0, 0.77,  1.1, 0.4, 1.1, 34.6, 34.6, 15.2,  9.1, 15.2, 3.0, 39.4,  31.8),
        ("Dru Smith",              "MIA", 55,  0.7, 10.3, 1.39,  0.9, 0.3, 0.5, 69.2, 69.2, 30.6,  8.3, 27.8, 11.1, 69.4,  97.1),
        ("Bam Adebayo",            "MIA", 50,  1.4,  7.5, 0.67,  0.9, 0.3, 1.1, 28.3, 29.2, 17.1, 11.4, 17.1, 4.3, 32.9,  14.7),
        ("James Harden",           "CLE",  7,  4.7, 26.8, 1.39,  6.6, 2.0, 3.3, 60.9, 71.7, 21.2, 12.1, 21.2, 3.0, 60.6,  97.6),
        ("Kyshawn George",         "WAS", 45,  1.1,  6.6, 0.96,  1.0, 0.4, 1.0, 39.5, 46.5, 10.4,  4.2, 10.4, 4.2, 41.7,  63.9),
        ("Zach LaVine",            "SAC", 36,  1.5,  9.0, 0.84,  1.3, 0.4, 1.2, 37.2, 39.5, 12.7,  9.1, 12.7, 0.0, 41.8,  41.8),
        ("Immanuel Quickley",      "TOR", 55,  1.0,  6.1, 0.84,  0.8, 0.2, 0.7, 30.0, 32.5, 20.0,  7.3, 20.0, 0.0, 41.8,  41.8),
        ("Quentin Grimes",         "PHI", 50,  1.2,  9.6, 0.78,  0.9, 0.3, 0.8, 33.3, 41.0, 15.3, 22.0, 13.6, 3.4, 33.9,  32.7),
        ("Ja Morant",              "MEM", 19,  3.1, 14.1, 0.76,  2.4, 0.7, 2.4, 30.4, 31.5, 16.9,  8.5, 15.3, 3.4, 37.3,  30.2),
        ("Brandin Podziemski",     "GSW", 57,  0.8,  6.1, 1.02,  0.8, 0.3, 0.6, 43.2, 48.6, 11.6,  4.7, 11.6, 2.3, 46.5,  76.6),
        ("Jerami Grant",           "POR", 42,  1.6,  9.3, 0.64,  1.0, 0.4, 1.1, 31.9, 33.0, 13.0, 18.8, 13.0, 0.0, 33.3,   9.4),
        ("Ausar Thompson",         "DET", 52,  0.9,  7.9, 0.96,  0.8, 0.3, 0.7, 50.0, 50.0, 13.3, 11.1, 13.3, 0.0, 51.1,  62.4),
        ("Tre Johnson",            "WAS", 44,  0.7,  5.7, 1.31,  1.0, 0.4, 0.6, 57.1, 64.3, 12.5,  0.0,  6.3, 0.0, 62.5,  96.7),
        ("Coby White",             "CHA", 28,  1.4,  7.5, 1.05,  1.5, 0.4, 1.0, 44.4, 48.1, 20.5, 10.3, 17.9, 0.0, 51.3,  81.2),
        ("Tyler Herro",            "MIA", 14,  2.3, 12.0, 1.25,  2.9, 1.1, 1.9, 61.5, 65.4, 15.6,  9.4, 15.6, 6.3, 59.4,  94.7),
        ("Jordan Poole",           "NOP", 33,  1.1,  7.5, 1.11,  1.2, 0.4, 0.9, 43.3, 53.3, 13.9,  8.3, 13.9, 5.6, 44.4,  87.7),
        ("Daniss Jenkins",         "DET", 46,  1.0, 10.6, 0.91,  0.9, 0.4, 0.8, 48.6, 48.6, 11.4, 13.6, 11.4, 4.5, 45.5,  56.4),
        ("Trey Murphy III",        "NOP", 49,  1.2,  6.4, 0.64,  0.8, 0.2, 0.9, 26.1, 31.5,  9.8, 14.8,  8.2, 0.0, 29.5,   9.8),
        ("Pelle Larsson",          "MIA", 46,  0.8,  8.0, 1.03,  0.8, 0.3, 0.5, 56.5, 58.7, 21.6, 16.2, 21.6, 0.0, 56.8,  77.1),
        ("Caleb Love",             "POR", 42,  1.1,  8.4, 0.84,  0.9, 0.4, 0.9, 43.2, 45.9,  6.7, 11.1,  6.7, 0.0, 42.2,  44.5),
        ("Harrison Barnes",        "SAS", 54,  0.6,  6.4, 1.16,  0.7, 0.3, 0.5, 57.7, 57.7, 12.5,  6.3, 12.5, 0.0, 59.4,  90.2),
        ("Evan Mobley",            "CLE", 43,  0.9,  5.1, 1.00,  0.9, 0.4, 0.7, 53.1, 53.1,  8.1,  8.1,  5.4, 2.7, 51.4,  73.0),
        ("Grayson Allen",          "PHX", 37,  0.9,  5.0, 1.13,  1.0, 0.3, 0.6, 52.4, 61.9, 25.0, 12.5, 25.0, 3.1, 53.1,  88.6),
        ("De'Andre Hunter",        "CLE", 40,  1.1,  7.9, 0.80,  0.9, 0.3, 0.8, 38.7, 45.2, 11.1, 20.0, 11.1, 0.0, 37.8,  34.8),
        ("Peyton Watson",          "DEN", 47,  1.1,  7.7, 0.69,  0.8, 0.3, 0.9, 34.1, 34.1, 11.5,  9.6, 11.5, 0.0, 38.5,  16.5),
        ("Bones Hyland",           "MIN", 50,  0.8, 11.3, 0.85,  0.7, 0.2, 0.6, 41.4, 44.8, 17.9, 10.3, 15.4, 2.6, 41.0,  45.5),
        ("Jordan Miller",          "LAC", 36,  1.1, 13.1, 0.81,  0.9, 0.3, 0.7, 38.5, 40.4, 17.1, 19.5, 17.1, 0.0, 41.5,  35.9),
        ("Kyle Kuzma",             "MIL", 52,  0.6,  4.7, 1.03,  0.6, 0.2, 0.4, 47.8, 47.8, 22.6,  6.5, 22.6, 3.2, 54.8,  77.6),
        # --- second batch ---
        ("Jabari Smith Jr.",        "HOU", 54,  0.8,  5.7, 0.71,  0.6, 0.2, 0.7, 33.3, 37.5,  8.9, 11.1,  8.9, 0.0, 35.6,  21.6),
        ("Anthony Davis",           "DAL", 19,  2.4, 11.5, 0.70,  1.7, 0.7, 2.1, 35.9, 35.9,  8.7,  8.7,  8.7, 2.2, 34.8,  17.6),
        ("Ty Jerome",               "MEM",  8,  2.8, 17.1, 1.41,  3.9, 1.3, 2.3, 55.6, 66.7, 22.7,  4.5, 22.7, 9.1, 59.1,  98.0),
        ("Nickeil Alexander-Walker","ATL", 56,  0.7,  3.6, 0.80,  0.6, 0.2, 0.6, 35.5, 37.1, 12.8, 10.3, 12.8, 2.6, 38.5,  34.3),
        ("Bennedict Mathurin",      "IND", 25,  1.7,  9.9, 0.74,  1.2, 0.4, 1.3, 31.3, 34.4, 16.7, 11.9, 16.7, 4.8, 35.7,  26.9),
        ("Toumani Camara",          "POR", 58,  0.9,  6.5, 0.62,  0.5, 0.2, 0.6, 34.4, 39.1, 10.0, 26.0, 10.0, 0.0, 30.0,   7.8),
        ("Josh Giddey",             "CHI", 37,  1.0,  5.0, 0.83,  0.8, 0.2, 0.8, 30.0, 33.3, 16.7,  0.0, 16.7, 0.0, 41.7,  40.7),
        ("Jarace Walker",           "IND", 56,  0.8,  6.1, 0.71,  0.5, 0.2, 0.6, 32.3, 35.5,  9.5, 16.7,  9.5, 0.0, 33.3,  22.3),
        ("Darius Garland",          "CLE", 23,  1.3,  7.0, 0.97,  1.3, 0.4, 0.8, 52.6, 60.5, 13.3, 23.3, 10.0, 0.0, 43.3,  66.1),
        ("Lauri Markkanen",         "UTA", 40,  0.9,  3.6, 0.85,  0.7, 0.3, 0.8, 40.6, 43.8,  2.9,  5.9,  2.9, 2.9, 38.2,  46.9),
        ("CJ McCollum",             "ATL", 21,  1.8,  9.5, 0.78,  1.4, 0.5, 1.4, 34.5, 36.2, 16.2,  5.4, 16.2, 0.0, 40.5,  33.5),
        ("Malik Monk",              "SAC", 45,  1.0,  7.6, 0.67,  0.6, 0.2, 0.9, 27.5, 33.8,  2.3,  4.7,  2.3, 0.0, 27.9,  15.1),
        ("Jalen Suggs",             "ORL", 30,  0.8,  5.6, 1.17,  0.9, 0.2, 0.6, 41.2, 47.1, 29.2,  0.0, 16.7, 0.0, 54.2,  91.0),
        ("Cedric Coward",           "MEM", 45,  0.5,  3.5, 1.29,  0.6, 0.2, 0.4, 55.0, 60.0, 14.3,  0.0, 14.3, 9.5, 57.1,  95.5),
        ("Marvin Bagley III",       "WAS", 37,  0.7,  7.6, 1.08,  0.7, 0.3, 0.5, 58.8, 58.8, 36.0, 12.0, 36.0, 16.0, 52.0, 85.3),
        ("Matas Buzelis",           "CHI", 58,  0.5,  3.3, 0.93,  0.5, 0.2, 0.3, 57.9, 57.9, 17.2, 24.1, 17.2, 6.9, 44.8,  59.6),
        ("De'Anthony Melton",       "GSW", 32,  1.2,  8.6, 0.73,  0.8, 0.2, 0.8, 28.0, 30.0, 16.2, 16.2, 13.5, 0.0, 35.1,  25.1),
        ("Dylan Harper",            "SAS", 44,  0.8,  7.2, 0.73,  0.6, 0.3, 0.7, 41.4, 41.4,  8.1, 13.5,  8.1, 0.0, 40.5,  25.1),
        ("Max Christie",            "DAL", 50,  0.7,  6.3, 0.73,  0.5, 0.2, 0.6, 30.0, 31.7, 13.5,  5.4, 13.5, 0.0, 37.8,  25.1),
        ("Derrick White",           "BOS", 55,  1.0,  5.5, 0.50,  0.5, 0.2, 0.8, 23.9, 27.2,  1.9, 13.0,  1.9, 0.0, 22.2,   3.7),
        ("Reed Sheppard",           "HOU", 56,  0.6,  4.4, 0.84,  0.5, 0.1, 0.4, 32.0, 36.0, 16.1,  6.5, 12.9, 3.2, 38.7,  43.0),
        ("Alex Sarr",               "WAS", 38,  0.9,  5.3, 0.77,  0.7, 0.3, 0.7, 37.0, 37.0, 11.8,  8.8, 11.8, 0.0, 41.2,  30.7),
        ("Jamal Shead",             "TOR", 57,  0.6,  7.3, 0.74,  0.5, 0.1, 0.5, 25.9, 27.8, 20.0,  2.9, 14.3, 0.0, 40.0,  27.8),
        ("Bub Carrington",          "WAS", 55,  0.7,  5.6, 0.72,  0.5, 0.2, 0.6, 32.3, 37.1,  8.3,  5.6,  5.6, 0.0, 33.3,  23.7),
        ("OG Anunoby",              "NYK", 43,  0.9,  5.6, 0.68,  0.6, 0.2, 0.8, 30.3, 30.3,  7.9,  5.3,  7.9, 0.0, 34.2,  15.6),
        ("CJ McCollum",             "WAS", 31,  1.5,  8.4, 0.56,  0.8, 0.4, 1.2, 28.9, 28.9,  8.7, 10.9,  8.7, 2.2, 28.3,   5.7),
        ("Ryan Nembhard",           "DAL", 36,  0.7,  8.3, 1.04,  0.7, 0.3, 0.6, 50.0, 52.3,  4.2,  4.2,  0.0, 0.0, 50.0,  78.8),
        ("Collin Sexton",           "CHA", 39,  0.6,  4.7, 1.00,  0.6, 0.2, 0.4, 47.1, 50.0, 20.0, 16.0, 20.0, 4.0, 48.0,  73.0),
        ("Noah Clowney",            "BKN", 50,  0.5,  4.2, 0.93,  0.5, 0.1, 0.3, 41.2, 41.2, 29.6, 14.8, 25.9, 7.4, 44.4,  59.2),
        ("Anthony Black",           "ORL", 53,  0.7,  4.1, 0.71,  0.5, 0.1, 0.5, 26.9, 30.8, 14.3, 11.4, 14.3, 0.0, 34.3,  22.3),
        ("Kris Dunn",               "LAC", 55,  0.3,  4.4, 1.26,  0.4, 0.2, 0.2, 69.2, 69.2, 26.3, 15.8, 26.3, 10.5, 63.2, 95.1),
        ("Bobby Portis",            "MIL", 53,  0.5,  3.8, 0.96,  0.5, 0.2, 0.5, 48.0, 48.0,  0.0,  0.0,  0.0, 0.0, 48.0,  64.5),
        ("Tre Mann",                "CHA", 37,  0.7,  8.7, 0.92,  0.6, 0.2, 0.5, 45.0, 50.0,  7.7, 15.4,  7.7, 0.0, 42.3,  58.6),
        ("P.J. Washington",         "DAL", 39,  0.7,  4.6, 0.89,  0.6, 0.2, 0.5, 45.0, 45.0, 18.5, 11.1, 18.5, 3.7, 44.4,  51.8),
        ("Jonathan Kuminga",        "GSW", 20,  1.7, 12.6, 0.71,  1.2, 0.4, 1.1, 31.8, 31.8, 20.6, 20.6, 20.6, 5.9, 35.3,  19.8),
        ("Aaron Wiggins",           "OKC", 44,  0.8,  6.9, 0.71,  0.5, 0.2, 0.6, 38.5, 44.2,  5.9, 17.6,  5.9, 0.0, 32.4,  19.8),
        ("Dyson Daniels",           "ATL", 56,  0.6,  5.0, 0.67,  0.4, 0.2, 0.5, 33.3, 33.3, 11.1,  8.3, 11.1, 2.8, 33.3,  12.9),
        ("Franz Wagner",            "ORL", 25,  1.5,  7.5, 0.65,  1.0, 0.3, 1.1, 25.0, 30.4, 16.2,  8.1, 13.5, 0.0, 32.4,  11.8),
        ("Cam Thomas",              "MIL",  8,  1.3,  9.1, 2.30,  2.9, 1.1, 1.3, 90.0, 115.0, 0.0,  0.0,  0.0, 0.0, 90.0, 100.0),
        ("Kenrich Williams",        "OKC", 37,  0.5,  7.7, 1.21,  0.6, 0.2, 0.4, 56.3, 62.5, 10.5, 10.5, 10.5, 5.3, 52.6,  92.7),
        ("D'Angelo Russell",        "DAL", 25,  0.9,  8.7, 1.00,  0.9, 0.3, 0.8, 42.1, 50.0,  8.7,  8.7,  8.7, 0.0, 43.5,  73.0),
        ("Moses Moody",             "GSW", 55,  0.5,  4.7, 0.82,  0.4, 0.1, 0.4, 35.0, 40.0, 17.9, 10.7, 17.9, 0.0, 42.9,  39.2),
        ("Gui Santos",              "GSW", 48,  0.3,  4.9, 1.47,  0.5, 0.2, 0.2, 90.0, 90.0, 26.7, 20.0, 26.7, 13.3, 73.3, 98.8),
        ("Rui Hachimura",           "LAL", 43,  0.4,  3.8, 1.29,  0.5, 0.2, 0.3, 58.3, 58.3, 23.5,  5.9, 23.5, 0.0, 64.7,  95.9),
        ("Sharife Cooper",          "WAS", 16,  1.3, 16.2, 1.05,  1.4, 0.5, 1.0, 50.0, 59.4,  9.5, 14.3,  9.5, 0.0, 47.6,  80.4),
        ("Drake Powell",            "BKN", 44,  0.5,  8.0, 0.96,  0.5, 0.2, 0.3, 57.1, 64.3,  8.7, 30.4,  8.7, 0.0, 43.5,  62.9),
        ("Keldon Johnson",          "SAS", 54,  0.5,  4.0, 0.88,  0.4, 0.2, 0.4, 40.9, 40.9, 12.0,  0.0, 12.0, 0.0, 48.0,  50.6),
        ("Brice Sensabaugh",        "UTA", 55,  0.5,  4.0, 0.81,  0.4, 0.1, 0.4, 35.0, 37.5, 14.8, 11.1, 14.8, 0.0, 40.7,  38.0),
        ("Cason Wallace",           "OKC", 53,  0.5,  5.8, 0.76,  0.4, 0.2, 0.5, 38.5, 38.5,  3.4,  6.9,  3.4, 0.0, 37.9,  29.4),
        ("Ace Bailey",              "UTA", 51,  0.6,  5.0, 0.67,  0.4, 0.2, 0.5, 35.7, 39.3,  0.0, 15.2,  0.0, 0.0, 30.3,  12.9),
        # --- third batch ---
        ("Dennis Schröder",         "CLE", 10,  1.7, 13.3, 1.24,  2.1, 0.8, 1.4, 57.1, 57.1, 17.6,  0.0, 17.6, 0.0, 64.7,  93.5),
        ("Caris LeVert",            "DET", 38,  0.6,  7.3, 0.91,  0.6, 0.2, 0.5, 47.4, 52.6,  8.7, 13.0,  4.3, 4.3, 43.5,  57.6),
        ("Day'Ron Sharpe",          "BKN", 54,  0.3,  3.9, 1.11,  0.4, 0.1, 0.2, 72.7, 72.7, 16.7, 22.2, 11.1, 0.0, 55.6,  87.7),
        ("Bruce Brown",             "DEN", 58,  0.3,  3.8, 1.11,  0.3, 0.2, 0.3, 60.0, 60.0, 11.1, 16.7, 11.1, 11.1, 50.0, 87.7),
        ("Marcus Smart",            "LAL", 46,  0.4,  3.9, 1.06,  0.4, 0.2, 0.3, 57.1, 60.7, 16.7, 22.2, 16.7, 16.7, 44.4, 82.0),
        ("Jaden McDaniels",         "MIN", 55,  0.4,  2.7, 0.91,  0.3, 0.1, 0.3, 40.0, 40.0, 19.0,  9.5, 19.0, 0.0, 47.6,  55.1),
        ("Jalen Green",             "PHX", 12,  2.1, 12.9, 0.76,  1.6, 0.7, 1.9, 34.8, 39.1,  4.0,  4.0,  4.0, 0.0, 36.0,  29.8),
        ("Will Riley",              "WAS", 47,  0.4,  4.8, 0.95,  0.4, 0.1, 0.3, 58.3, 58.3, 15.8, 21.1, 15.8, 0.0, 47.4,  61.6),
        ("Jaylen Wells",            "MEM", 54,  0.4,  3.0, 0.90,  0.3, 0.1, 0.3, 50.0, 50.0, 20.0, 15.0, 20.0, 5.0, 45.0,  54.5),
        ("Jordan Clarkson",         "NYK", 49,  0.4,  5.1, 0.82,  0.4, 0.2, 0.4, 42.1, 44.7,  4.5, 13.6,  4.5, 4.5, 36.4,  38.8),
        ("Collin Gillespie",        "PHX", 55,  0.4,  3.3, 0.78,  0.3, 0.1, 0.4, 35.0, 37.5,  8.7,  4.3,  8.7, 0.0, 39.1,  33.1),
        ("Oso Ighodaro",            "PHX", 56,  0.5,  7.9, 0.69,  0.3, 0.2, 0.3, 52.9, 52.9, 11.5, 30.8, 11.5, 7.7, 34.6,  16.5),
        ("Scoot Henderson",         "POR",  9,  1.3,  8.5, 1.42,  1.9, 0.4, 0.9, 50.0, 50.0, 33.3,  0.0, 16.7, 0.0, 66.7,  98.4),
        ("Jose Alvarado",           "NOP", 38,  0.3,  4.3, 1.31,  0.4, 0.2, 0.3, 54.5, 68.2,  7.7,  7.7,  7.7, 0.0, 53.8,  96.3),
        ("Jaden Ivey",              "DET", 31,  0.5,  5.5, 1.21,  0.5, 0.2, 0.3, 70.0, 80.0,  7.1, 28.6,  7.1, 7.1, 50.0,  93.1),
        ("Kobe Sanders",            "LAC", 45,  0.4,  4.9, 1.00,  0.4, 0.2, 0.3, 53.3, 53.3,  5.9,  5.9,  0.0, 0.0, 52.9,  73.0),
        ("Mikal Bridges",           "NYK", 55,  0.3,  2.2, 1.00,  0.3, 0.1, 0.3, 46.7, 46.7, 11.8,  0.0, 11.8, 0.0, 52.9,  73.0),
        ("Khris Middleton",         "WAS", 30,  0.8,  6.9, 0.71,  0.6, 0.3, 0.7, 38.1, 38.1,  4.2,  8.3,  4.2, 0.0, 37.5,  21.2),
        ("Naz Reid",                "MIN", 56,  0.5,  3.5, 0.63,  0.3, 0.1, 0.3, 29.4, 32.4, 14.8, 25.9, 14.8, 3.7, 29.6,   8.6),
        ("Bilal Coulibaly",         "WAS", 36,  0.8,  6.9, 0.61,  0.5, 0.2, 0.6, 36.4, 36.4,  7.1, 14.3,  7.1, 0.0, 32.1,   7.3),
        ("Anfernee Simons",         "CHI",  6,  2.3, 15.1, 1.14,  2.7, 1.2, 2.0, 58.3, 62.5,  7.1, 14.3,  7.1, 7.1, 50.0,  89.8),
        ("Tristan Vukcevic",        "WAS", 34,  0.4,  5.0, 1.14,  0.5, 0.2, 0.4, 46.2, 53.8,  7.1,  0.0,  7.1, 0.0, 50.0,  89.8),
        ("Ousmane Dieng",           "OKC", 25,  0.7, 18.1, 0.94,  0.6, 0.3, 0.7, 41.2, 47.1,  0.0,  0.0,  0.0, 0.0, 41.2,  61.2),
        ("Kyle Anderson",           "UTA", 20,  1.0, 13.3, 0.84,  0.8, 0.2, 0.7, 30.8, 30.8, 31.6,  0.0, 31.6, 0.0, 52.6,  43.9),
        ("Miles McBride",           "NYK", 32,  0.6,  5.0, 0.84,  0.5, 0.2, 0.6, 38.9, 44.4,  0.0,  5.3,  0.0, 0.0, 36.8,  43.9),
        ("Trae Young",              "ATL", 10,  2.3, 12.0, 0.70,  1.6, 0.4, 2.0, 20.0, 22.5, 17.4,  0.0, 13.0, 4.3, 30.4,  17.6),
        ("Tobias Harris",           "DET", 40,  0.7,  5.7, 0.55,  0.4, 0.1, 0.6, 20.8, 20.8, 17.2,  6.9, 17.2, 6.9, 27.6,   5.3),
        ("Collin Sexton",           "CHI",  8,  1.3,  9.3, 1.50,  1.9, 0.8, 1.1, 66.7, 72.2, 10.0,  0.0, 10.0, 0.0, 70.0,  99.6),
        ("Josh Hart",               "NYK", 43,  0.2,  2.0, 1.50,  0.3, 0.1, 0.2, 55.6, 66.7, 20.0,  0.0, 10.0, 10.0, 60.0, 99.6),
        ("Buddy Hield",             "GSW", 41,  0.3,  3.5, 1.25,  0.4, 0.2, 0.3, 58.3, 62.5,  0.0,  0.0,  0.0, 0.0, 58.3,  94.7),
        ("Jalen Pickett",           "DEN", 39,  0.4,  7.5, 0.88,  0.4, 0.2, 0.4, 40.0, 50.0,  0.0, 11.8,  0.0, 0.0, 35.3,  51.0),
        ("Devin Carter",            "SAC", 23,  0.8, 10.3, 0.79,  0.7, 0.1, 0.5, 16.7, 16.7, 31.6,  5.3, 31.6, 0.0, 42.1,  33.9),
        ("Rob Dillingham",          "CHI", 32,  0.9, 17.5, 0.50,  0.5, 0.2, 0.8, 23.1, 25.0,  3.3, 10.0,  3.3, 0.0, 23.3,   3.7),
        ("Kentavious Caldwell-Pope","MEM", 48,  0.3,  3.2, 1.00,  0.3, 0.1, 0.2, 36.4, 36.4, 21.4,  0.0, 21.4, 0.0, 50.0,  73.0),
        ("Isaac Okoro",             "CHI", 50,  0.3,  3.9, 0.82,  0.3, 0.1, 0.2, 54.5, 54.5, 11.8, 23.5, 11.8, 0.0, 47.1,  39.8),
        ("RJ Barrett",              "TOR", 35,  0.5,  2.8, 0.82,  0.4, 0.2, 0.4, 42.9, 42.9,  5.9, 11.8,  5.9, 0.0, 41.2,  39.8),
        ("Nolan Traore",            "BKN", 37,  0.5,  4.8, 0.78,  0.4, 0.2, 0.4, 46.2, 46.2, 11.1, 16.7,  5.6, 0.0, 44.4,  32.2),
        ("Herbert Jones",           "NOP", 36,  0.5,  5.1, 0.74,  0.4, 0.2, 0.5, 33.3, 38.9,  0.0,  5.3,  0.0, 0.0, 31.6,  26.5),
        ("T.J. McConnell",          "IND", 40,  0.5,  5.5, 0.67,  0.4, 0.2, 0.4, 40.0, 40.0,  4.8, 23.8,  4.8, 0.0, 33.3,  12.9),
        ("Jonas Valančiūnas",       "DEN", 46,  0.3,  3.1, 1.08,  0.3, 0.1, 0.2, 60.0, 65.0,  0.0, 16.7,  0.0, 0.0, 50.0,  86.1),
        ("Onyeka Okongwu",          "ATL", 53,  0.2,  1.5, 1.08,  0.2, 0.1, 0.2, 50.0, 50.0, 25.0,  8.3, 25.0, 0.0, 58.3,  86.1),
        ("Ronald Holland II",       "DET", 51,  0.3,  3.4, 0.81,  0.3, 0.1, 0.3, 35.7, 35.7, 12.5,  6.3, 12.5, 6.3, 37.5,  37.6),
        ("Nique Clifford",          "SAC", 54,  0.3,  3.6, 0.77,  0.2, 0.1, 0.2, 44.4, 50.0, 11.8, 35.3, 11.8, 0.0, 35.3,  30.7),
        ("Cole Anthony",            "MIL", 32,  0.6,  6.7, 0.68,  0.4, 0.2, 0.6, 33.3, 36.1,  0.0,  5.3,  0.0, 0.0, 31.6,  15.6),
        ("Cam Spencer",             "MEM", 53,  0.4,  3.8, 0.65,  0.2, 0.1, 0.2, 30.8, 34.6, 10.0, 25.0, 10.0, 0.0, 30.0,  12.2),
        ("Pat Spencer",             "GSW", 43,  0.5,  6.9, 0.59,  0.3, 0.1, 0.5, 30.0, 30.0,  4.5,  4.5,  4.5, 0.0, 31.8,   6.5),
        ("Ayo Dosunmu",             "CHI", 43,  0.3,  2.1, 1.00,  0.3, 0.1, 0.2, 55.6, 61.1,  8.3, 25.0,  8.3, 8.3, 41.7,  73.0),
        ("Myles Turner",            "MIL", 51,  0.3,  2.2, 0.92,  0.2, 0.1, 0.2, 40.0, 40.0, 23.1,  7.7, 23.1, 7.7, 46.2,  58.6),
        ("Jamaree Bouyea",          "PHX", 30,  0.5,  7.3, 0.86,  0.4, 0.2, 0.4, 46.2, 46.2,  0.0,  7.1,  0.0, 0.0, 42.9,  47.7),
        ("Jarrett Allen",           "CLE", 47,  0.3,  2.3, 0.86,  0.3, 0.1, 0.2, 50.0, 50.0, 14.3, 28.6, 14.3, 0.0, 42.9,  47.7),
        # --- fourth batch ---
        ("Tim Hardaway Jr.",        "DEN", 57,  0.2,  2.1, 0.86,  0.2, 0.1, 0.2, 25.0, 33.3, 14.3,  0.0, 14.3, 0.0, 35.7,  47.7),
        ("Patrick Williams",        "CHI", 53,  0.3,  3.9, 0.75,  0.2, 0.1, 0.2, 38.5, 38.5,  6.3, 12.5,  0.0, 0.0, 37.5,  28.4),
        ("Tyrese Proctor",          "CLE", 40,  0.4,  8.2, 0.71,  0.3, 0.1, 0.3, 23.1, 23.1, 17.6,  5.9, 11.8, 0.0, 35.3,  19.8),
        ("Trendon Watford",         "PHI", 34,  0.5,  7.9, 0.71,  0.4, 0.1, 0.3, 27.3, 27.3, 23.5, 17.6, 23.5, 5.9, 35.3,  19.8),
        ("Tre Jones",               "CHI", 41,  0.6,  5.1, 0.52,  0.3, 0.1, 0.4, 18.8, 18.8, 17.4, 13.0, 17.4, 0.0, 30.4,   4.5),
        ("Jaden Hardy",             "DAL", 31,  0.4,  4.9, 1.00,  0.4, 0.1, 0.3, 50.0, 50.0, 18.2,  9.1, 18.2, 0.0, 54.5,  73.0),
        ("Ousmane Dieng",           "MIL",  8,  1.6, 21.3, 0.85,  1.4, 0.5, 1.4, 36.4, 45.5,  7.7,  7.7,  7.7, 0.0, 38.5,  45.5),
        ("Noah Penda",              "ORL", 39,  0.3,  6.7, 0.85,  0.3, 0.1, 0.2, 44.4, 50.0, 15.4, 23.1, 15.4, 7.7, 38.5,  45.5),
        ("Caleb Martin",            "DAL", 46,  0.3,  6.4, 0.85,  0.2, 0.1, 0.2, 44.4, 44.4, 15.4, 23.1, 15.4, 7.7, 38.5,  45.5),
        ("Keaton Wallace",          "ATL", 41,  0.4,  8.8, 0.73,  0.3, 0.1, 0.4, 33.3, 36.7,  0.0,  0.0,  0.0, 0.0, 33.3,  26.1),
        ("Tari Eason",              "HOU", 36,  0.5,  3.9, 0.65,  0.3, 0.1, 0.4, 38.5, 38.5,  5.9, 23.5,  5.9, 5.9, 29.4,  11.4),
        ("Jared McCain",            "PHI", 35,  0.6,  8.7, 0.52,  0.3, 0.1, 0.4, 35.7, 35.7,  4.8, 33.3,  4.8, 4.8, 23.8,   4.9),
        ("Craig Porter Jr.",        "CLE", 51,  0.2,  4.0, 0.91,  0.2, 0.1, 0.2, 36.4, 40.9, 18.2,  0.0, 18.2, 18.2, 36.4, 56.4),
        ("Walter Clayton Jr.",      "UTA", 43,  0.3,  3.3, 0.91,  0.2, 0.1, 0.2, 44.4, 44.4, 18.2, 18.2, 18.2, 18.2, 36.4, 56.4),
        ("Svi Mykhailiuk",          "UTA", 46,  0.2,  3.1, 0.91,  0.2, 0.1, 0.2, 36.4, 45.5,  0.0,  0.0,  0.0, 0.0, 36.4,  56.4),
        ("Wendell Carter Jr.",      "ORL", 51,  0.2,  1.9, 0.91,  0.2, 0.1, 0.2, 40.0, 40.0,  9.1,  0.0,  9.1, 0.0, 45.5,  56.4),
        ("GG Jackson",              "MEM", 37,  0.3,  3.2, 0.83,  0.3, 0.1, 0.2, 33.3, 38.9, 16.7, 16.7, 16.7, 8.3, 33.3,  40.7),
        ("Blake Wesley",            "POR", 17,  0.8, 11.8, 0.77,  0.6, 0.3, 0.5, 55.6, 55.6,  7.7, 30.8,  7.7, 7.7, 38.5,  31.4),
        ("John Collins",            "LAC", 50,  0.3,  2.4, 0.71,  0.2, 0.1, 0.2, 40.0, 40.0, 14.3, 21.4, 14.3, 7.1, 35.7,  22.3),
        ("Kon Knueppel",            "CHA", 57,  0.2,  1.5, 0.71,  0.2, 0.1, 0.2, 30.0, 30.0, 14.3, 14.3, 14.3, 0.0, 35.7,  22.3),
        ("Kasparas Jakučionis",     "MIA", 34,  0.5,  8.5, 0.63,  0.3, 0.1, 0.3, 22.2, 22.2, 25.0, 18.8, 18.8, 0.0, 37.5,   8.2),
        ("Bennedict Mathurin",      "LAC",  6,  2.0,  9.2, 0.75,  1.5, 0.5, 1.8, 27.3, 31.8,  8.3,  0.0,  8.3, 0.0, 33.3,  28.4),
        ("Dalton Knecht",           "LAL", 42,  0.3,  6.2, 0.75,  0.2, 0.1, 0.3, 33.3, 37.5,  0.0,  0.0,  0.0, 0.0, 33.3,  28.4),
        ("Donte DiVincenzo",        "MIN", 57,  0.2,  1.8, 0.69,  0.2, 0.1, 0.2, 33.3, 33.3, 15.4, 15.4, 15.4, 0.0, 38.5,  16.5),
        ("Khris Middleton",         "DAL",  7,  2.0, 15.4, 0.64,  1.3, 0.4, 1.4, 30.0, 30.0, 14.3, 21.4, 14.3, 7.1, 28.6,  10.3),
        ("Keegan Murray",           "SAC", 21,  0.7,  4.5, 0.64,  0.4, 0.1, 0.6, 23.1, 26.9,  7.1,  0.0,  7.1, 0.0, 28.6,  10.3),
        ("Nikola Jović",            "MIA", 44,  0.3,  3.4, 0.64,  0.2, 0.1, 0.2, 33.3, 33.3, 21.4, 21.4, 14.3, 7.1, 35.7,  10.3),
        ("Ben Saraf",               "BKN", 23,  0.7,  8.8, 0.60,  0.4, 0.2, 0.6, 30.8, 30.8,  6.7,  6.7,  6.7, 0.0, 33.3,   6.9),
        ("Aaron Holiday",           "HOU", 35,  0.3,  5.6, 0.80,  0.2, 0.1, 0.2, 57.1, 57.1,  0.0, 30.0,  0.0, 0.0, 40.0,  34.8),
        ("Bryce McGowens",          "NOP", 36,  0.3,  4.2, 0.73,  0.2, 0.1, 0.3, 30.0, 30.0, 18.2,  9.1, 18.2, 18.2, 27.3, 24.2),
        ("Nikola Vučević",          "CHI", 46,  0.2,  1.5, 0.73,  0.2, 0.1, 0.2, 40.0, 40.0,  0.0,  9.1,  0.0, 0.0, 36.4,  24.2),
        ("Brook Lopez",             "LAC", 50,  0.2,  3.1, 0.67,  0.2, 0.1, 0.2, 36.4, 36.4,  0.0,  8.3,  0.0, 0.0, 33.3,  12.9),
        ("Jake LaRavia",            "LAL", 55,  0.2,  2.3, 0.67,  0.1, 0.0, 0.1, 25.0, 25.0, 16.7, 16.7, 16.7, 0.0, 33.3,  12.9),
        ("Alex Caruso",             "OKC", 35,  0.3,  4.2, 0.70,  0.2, 0.1, 0.3, 30.0, 35.0,  0.0,  0.0,  0.0, 0.0, 30.0,  18.4),
        ("Tyler Kolek",             "NYK", 46,  0.2,  3.7, 0.70,  0.2, 0.0, 0.2, 25.0, 31.3, 10.0, 10.0, 10.0, 0.0, 30.0,  18.4),
        ("Cam Whitmore",            "WAS", 17,  0.6,  6.3, 0.64,  0.4, 0.2, 0.6, 30.0, 35.0,  0.0,  9.1,  0.0, 0.0, 27.3,   9.0),
        ("Aaron Nesmith",           "IND", 33,  0.4,  2.6, 0.58,  0.2, 0.1, 0.2, 50.0, 58.3,  0.0, 50.0,  0.0, 0.0, 25.0,   6.1),
        ("Precious Achiuwa",        "SAC", 50,  0.3,  3.6, 0.47,  0.1, 0.1, 0.2, 27.3, 27.3,  6.7, 20.0,  6.7, 0.0, 26.7,   3.3),
        ("Egor Dëmin",              "BKN", 49,  0.3,  3.3, 0.35,  0.1, 0.0, 0.3, 11.8, 17.6,  0.0,  0.0,  0.0, 0.0, 11.8,   2.0),
        ("Devin Vassell",           "SAS", 41,  0.3,  2.4, 0.39,  0.1, 0.0, 0.2, 20.0, 20.0,  7.7, 15.4,  7.7, 0.0, 23.1,   2.9),
        ("Nick Smith Jr.",          "LAL", 25,  0.7, 10.9, 0.29,  0.2, 0.1, 0.5, 15.4, 19.2,  0.0, 23.5,  0.0, 0.0, 11.8,   1.2),
        ("Danny Wolf",              "BKN", 44,  0.3,  2.6, 0.36,  0.1, 0.0, 0.2, 11.1, 11.1, 18.2,  0.0, 18.2, 0.0, 18.2,   2.4),
        ("Terance Mann",            "BKN", 48,  0.2,  2.7, 0.30,  0.1, 0.0, 0.2, 12.5, 18.8, 10.0, 10.0, 10.0, 0.0, 10.0,   1.6),
        ("Luguentz Dort",           "OKC", 45,  0.2,  2.4, 0.20,  0.0, 0.0, 0.2, 11.1, 11.1,  0.0, 10.0,  0.0, 0.0, 10.0,   0.4),
        ("Klay Thompson",           "DAL", 49,  0.2,  1.7, 0.20,  0.0, 0.0, 0.2, 12.5, 12.5,  0.0, 20.0,  0.0, 0.0, 10.0,   0.4),
        ("Jordan Goodwin",          "PHX", 50,  0.2,  2.3, 0.18,  0.0, 0.0, 0.2,  9.1,  9.1,  0.0,  0.0,  0.0, 0.0,  9.1,   0.0),
    ]

    stats: List[OffensiveTransitionStats] = []
    for row in raw:
        (player, team, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        stats.append(OffensiveTransitionStats(
            player=player,
            team=team,
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
        ))
    return stats


def rank_players_by_offensive_transition(
    stats: Optional[List["OffensiveTransitionStats"]] = None,
) -> List["OffensiveTransitionStats"]:
    """
    Return all players sorted from best to worst offensive transition scorer
    (highest percentile first).

    If *stats* is not provided, the full dataset is used.
    """
    if stats is None:
        stats = build_offensive_transition_stats()
    return sorted(stats, key=lambda s: s.percentile, reverse=True)


def find_transition_scorers(
    transition_stats: Optional[List["OffensiveTransitionStats"]] = None,
    opponent_team: Optional[str] = None,
    transition_defensive_rankings: Optional[Dict[str, "TransitionDefensiveStats"]] = None,
    min_freq_pct: float = 10.0,
    min_ppp: float = 1.00,
) -> List[Dict]:
    """
    Identify players who are high-volume, efficient transition scorers.

    When *opponent_team* and *transition_defensive_rankings* are provided the
    results are further filtered to only players whose opponent allows an above-
    average transition PPP (weak transition defense).

    Returns a list of dicts sorted by transition frequency % (highest first),
    each containing:
      - "player"        : player name
      - "team"          : player's team
      - "freq_pct"      : transition frequency %
      - "ppp"           : player's transition PPP
      - "pts"           : transition points per game
      - "percentile"    : player's offensive transition percentile
      - "def_ppp"       : opponent's transition defensive PPP (if opponent supplied)
      - "def_percentile": opponent's transition defensive percentile (if supplied)
    """
    if transition_stats is None:
        transition_stats = build_offensive_transition_stats()

    def_stats = None
    if opponent_team and transition_defensive_rankings:
        def_stats = transition_defensive_rankings.get(opponent_team)

    results = []
    for s in transition_stats:
        if s.freq_pct < min_freq_pct:
            continue
        if s.ppp < min_ppp:
            continue
        entry: Dict = {
            "player":     s.player,
            "team":       s.team,
            "freq_pct":   s.freq_pct,
            "ppp":        s.ppp,
            "pts":        s.pts,
            "percentile": s.percentile,
            "def_ppp":        def_stats.ppp if def_stats else None,
            "def_percentile": def_stats.percentile if def_stats else None,
        }
        results.append(entry)

    results.sort(key=lambda r: r["freq_pct"], reverse=True)
    return results


def find_transition_beneficiaries(
    transition_stats: Optional[List["OffensiveTransitionStats"]] = None,
    opponent_team: str = "",
    transition_defensive_rankings: Optional[Dict[str, "TransitionDefensiveStats"]] = None,
    min_freq_pct: float = 10.0,
    min_ppp: float = 1.00,
    max_def_percentile: float = 40.0,
) -> List[Dict]:
    """
    Identify players likely to benefit from a weak opponent transition defense.

    A player is flagged as a beneficiary when:
    - Their transition frequency % is at least *min_freq_pct*
    - Their transition PPP is at least *min_ppp*
    - The opposing team's transition defensive percentile is at most
      *max_def_percentile* (low percentile = weak transition defense that
      allows many transition opportunities)

    Returns a list of dicts sorted by transition frequency % (highest first),
    each containing:
      - "player"          : player name
      - "team"            : player's team
      - "freq_pct"        : player's transition frequency %
      - "ppp"             : player's transition PPP
      - "pts"             : player's transition points per game
      - "percentile"      : player's offensive transition percentile
      - "def_ppp"         : opponent's transition defensive PPP allowed
      - "def_percentile"  : opponent's transition defensive percentile (lower = weaker)
      - "edge"            : player transition PPP minus opponent's defensive PPP
    """
    if transition_stats is None:
        transition_stats = build_offensive_transition_stats()
    if transition_defensive_rankings is None:
        transition_defensive_rankings = build_transition_defensive_rankings()

    def_stats = transition_defensive_rankings.get(opponent_team)
    if def_stats is None:
        return []

    if def_stats.percentile > max_def_percentile:
        return []

    results = []
    for s in transition_stats:
        if s.freq_pct < min_freq_pct:
            continue
        if s.ppp < min_ppp:
            continue
        results.append({
            "player":         s.player,
            "team":           s.team,
            "freq_pct":       s.freq_pct,
            "ppp":            s.ppp,
            "pts":            s.pts,
            "percentile":     s.percentile,
            "def_ppp":        def_stats.ppp,
            "def_percentile": def_stats.percentile,
            "edge":           round(s.ppp - def_stats.ppp, 3),
        })

    results.sort(key=lambda r: r["freq_pct"], reverse=True)
    return results


def match_all_transition_matchups(
    offensive_stats: Optional[List["OffensiveTransitionStats"]] = None,
    defensive_rankings: Optional[Dict[str, "TransitionDefensiveStats"]] = None,
    top_n: int = 50,
    max_def_percentile: float = 40.0,
    min_off_percentile: float = 0.0,
) -> List[Dict]:
    """
    Cross-reference all offensive transition players with all defensive teams
    to identify the highest-edge matchups.

    For every (player, opponent) pair where the player's own team differs from
    the opponent and the opponent's transition defensive percentile is at most
    *max_def_percentile*, compute::

        edge = player PPP − opponent defensive PPP allowed

    The *top_n* pairs with the largest edge are returned, sorted by edge
    descending (ties broken by the player's offensive percentile, also
    descending).

    Parameters
    ----------
    offensive_stats:
        Pre-built offensive stats list; defaults to the full 196-player dataset.
    defensive_rankings:
        Pre-built ``{team: TransitionDefensiveStats}`` mapping; defaults to the
        full 30-team dataset.
    top_n:
        Maximum number of matchup records to return (default 50).
    max_def_percentile:
        Upper bound on the opponent's transition defensive percentile.
        A low percentile means a weak transition defense, so setting this to
        40 (default) restricts results to the bottom 40 % of defenses.
        Pass ``100.0`` to include all teams.
    min_off_percentile:
        Lower bound on the player's offensive transition percentile (default 0).

    Returns
    -------
    list of dict, each containing:
      - ``"player"``         : player name
      - ``"team"``           : player's team abbreviation
      - ``"off_percentile"`` : player's offensive transition percentile
      - ``"ppp"``            : player's transition PPP
      - ``"freq_pct"``       : player's transition frequency %
      - ``"opponent"``       : opponent team abbreviation
      - ``"def_ppp"``        : opponent's transition defensive PPP allowed
      - ``"def_percentile"`` : opponent's transition defensive percentile
      - ``"edge"``           : player PPP − opponent defensive PPP (higher = better)
    """
    if offensive_stats is None:
        offensive_stats = build_offensive_transition_stats()
    if defensive_rankings is None:
        defensive_rankings = build_transition_defensive_rankings()

    results: List[Dict] = []
    for player in offensive_stats:
        if player.percentile < min_off_percentile:
            continue
        for def_team, d in defensive_rankings.items():
            if def_team == player.team:
                continue
            if d.percentile > max_def_percentile:
                continue
            results.append({
                "player":         player.player,
                "team":           player.team,
                "off_percentile": player.percentile,
                "ppp":            player.ppp,
                "freq_pct":       player.freq_pct,
                "opponent":       def_team,
                "def_ppp":        d.ppp,
                "def_percentile": d.percentile,
                "edge":           round(player.ppp - d.ppp, 3),
            })

    results.sort(key=lambda r: (r["edge"], r["off_percentile"]), reverse=True)
    return results[:top_n]


def predict_transition_matchup(
    player_name: str,
    opponent_team: str,
    offensive_stats: Optional[List["OffensiveTransitionStats"]] = None,
    defensive_rankings: Optional[Dict[str, "TransitionDefensiveStats"]] = None,
) -> Optional[Dict]:
    """
    Return a head-to-head transition matchup prediction for *player_name*
    against *opponent_team*'s transition defense.

    Unlike :func:`find_transition_beneficiaries`, this function performs a
    direct lookup with **no frequency or PPP thresholds**, making it suitable
    for on-demand matchup queries regardless of sample size.

    Parameters
    ----------
    player_name:
        Exact player name as it appears in the offensive transition dataset
        (e.g. ``"Josh Hart"``).
    opponent_team:
        Three-letter team abbreviation for the defending team (e.g. ``"SAS"``).
    offensive_stats:
        Pre-built offensive stats list; defaults to the full dataset.
    defensive_rankings:
        Pre-built ``{team: TransitionDefensiveStats}`` mapping; defaults to
        the full 30-team dataset.

    Returns
    -------
    dict or None
        ``None`` when the player or team cannot be found.  Otherwise a dict
        containing:

        - ``"player"``         : player name
        - ``"team"``           : player's team abbreviation
        - ``"gp"``             : games played
        - ``"freq_pct"``       : player's transition frequency %
        - ``"ppp"``            : player's transition PPP
        - ``"pts"``            : player's transition points per game
        - ``"off_percentile"`` : player's offensive transition percentile
        - ``"opponent"``       : opponent team abbreviation
        - ``"def_ppp"``        : opponent's transition PPP allowed
        - ``"def_freq_pct"``   : opponent's transition frequency allowed %
        - ``"def_percentile"`` : opponent's transition defensive percentile
        - ``"edge"``           : player PPP − opponent defensive PPP
        - ``"verdict"``        : short human-readable label (``"FAVORABLE"``,
                                 ``"NEUTRAL"``, or ``"TOUGH"``)
    """
    if offensive_stats is None:
        offensive_stats = build_offensive_transition_stats()
    if defensive_rankings is None:
        defensive_rankings = build_transition_defensive_rankings()

    player_stat = next(
        (s for s in offensive_stats if s.player.lower() == player_name.lower()),
        None,
    )
    if player_stat is None:
        return None

    def_stat = defensive_rankings.get(opponent_team.upper())
    if def_stat is None:
        return None

    edge = round(player_stat.ppp - def_stat.ppp, 3)
    if edge >= 0.15:
        verdict = "FAVORABLE"
    elif edge <= -0.15:
        verdict = "TOUGH"
    else:
        verdict = "NEUTRAL"

    return {
        "player":         player_stat.player,
        "team":           player_stat.team,
        "gp":             player_stat.gp,
        "freq_pct":       player_stat.freq_pct,
        "ppp":            player_stat.ppp,
        "pts":            player_stat.pts,
        "off_percentile": player_stat.percentile,
        "opponent":       def_stat.team,
        "def_ppp":        def_stat.ppp,
        "def_freq_pct":   def_stat.freq_pct,
        "def_percentile": def_stat.percentile,
        "edge":           edge,
        "verdict":        verdict,
    }



# ---------------------------------------------------------------------------
# Offensive isolation analytics
# ---------------------------------------------------------------------------

def build_offensive_isolation_stats() -> List["OffensiveIsolationStats"]:
    """
    Return offensive isolation stats for 150 NBA players (NBA Synergy data).

    Columns: PLAYER, TEAM, GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking.  Higher values indicate a
    more efficient/frequent isolation scorer.
    """
    raw = [
        # (player, team, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("James Harden",             "CLE", 41, 10.2, 42.1, 1.06, 10.8, 2.9, 7.5, 38.2, 43.5, 22.4,  6.9, 22.0, 3.1, 47.3,  82.4),
        ("Shai Gilgeous-Alexander",  "OKC", 45,  6.9, 26.6, 1.17,  8.1, 2.7, 5.3, 50.4, 55.7, 17.7,  7.7, 16.5, 2.3, 54.2,  91.4),
        ("Anthony Edwards",          "MIN", 47,  6.4, 24.2, 1.05,  6.7, 2.4, 5.3, 45.6, 51.6, 13.0,  6.6, 12.3, 2.0, 48.5,  80.8),
        ("Jaylen Brown",             "BOS", 51,  5.6, 19.5, 0.96,  5.4, 2.0, 4.4, 44.6, 48.0, 15.0, 10.1, 14.7, 3.5, 45.5,  64.9),
        ("Kevin Durant",             "HOU", 54,  4.6, 19.3, 0.98,  4.5, 1.7, 3.7, 46.5, 50.3, 11.2, 11.2, 10.0, 2.0, 46.2,  68.2),
        ("Luka Dončić",              "LAL", 43,  4.8, 15.6, 1.14,  5.4, 1.7, 3.8, 44.5, 54.3, 16.1,  7.3, 14.6, 3.4, 48.3,  89.0),
        ("Zion Williamson",          "NOP", 43,  4.6, 23.8, 1.06,  4.8, 1.8, 3.3, 54.3, 54.3, 22.4, 11.7, 21.9, 5.6, 54.1,  83.3),
        ("Tyrese Maxey",             "PHI", 54,  4.3, 15.8, 0.90,  3.8, 1.5, 3.9, 37.8, 41.1, 10.4,  3.5,  9.1, 4.8, 40.0,  53.5),
        ("Jalen Brunson",            "NYK", 51,  3.7, 15.3, 0.98,  3.7, 1.4, 3.1, 44.9, 48.1, 11.0,  8.4,  9.9, 2.1, 46.1,  67.8),
        ("Jamal Murray",             "DEN", 53,  3.3, 14.6, 1.05,  3.4, 1.3, 2.8, 47.3, 52.7,  8.0,  7.5,  6.9, 1.7, 47.1,  80.0),
        ("DeMar DeRozan",            "SAC", 58,  3.1, 18.9, 1.00,  3.1, 1.1, 2.5, 43.8, 44.5, 18.8,  6.1, 18.8, 5.5, 48.6,  73.0),
        ("Julius Randle",            "MIN", 57,  3.2, 15.2, 0.99,  3.1, 1.2, 2.5, 46.2, 48.6, 13.9, 10.6, 13.3, 3.9, 46.1,  69.0),
        ("Kawhi Leonard",            "LAC", 42,  4.5, 18.3, 0.90,  4.1, 1.4, 3.7, 38.2, 41.1, 12.6,  6.8, 10.5, 2.1, 42.1,  54.5),
        ("Donovan Mitchell",         "CLE", 52,  3.0, 11.6, 1.00,  3.0, 1.1, 2.5, 42.3, 50.4,  8.9,  8.9,  7.6, 0.6, 43.3,  73.0),
        ("Alperen Sengun",           "HOU", 49,  3.6, 16.3, 0.89,  3.2, 1.3, 2.8, 46.0, 46.0, 12.1, 11.5, 11.5, 2.3, 44.3,  52.2),
        ("Payton Pritchard",         "BOS", 56,  2.2, 13.6, 1.24,  2.7, 1.1, 1.9, 59.4, 65.1,  6.5,  7.3,  4.9, 0.0, 57.7,  93.9),
        ("Cade Cunningham",          "DET", 50,  3.0, 11.8, 1.01,  3.0, 1.2, 2.5, 46.4, 50.0, 12.0,  6.7, 12.0, 2.0, 48.7,  74.7),
        ("Devin Booker",             "PHX", 41,  3.4, 13.8, 1.08,  3.6, 1.3, 2.6, 51.4, 54.3, 16.7, 10.9, 15.2, 3.6, 52.2,  84.9),
        ("Brandon Ingram",           "TOR", 55,  3.0, 14.1, 0.87,  2.7, 1.1, 2.3, 45.7, 46.5, 11.4, 13.8, 11.4, 1.2, 43.7,  49.8),
        ("Pascal Siakam",            "IND", 49,  3.1, 12.9, 0.93,  2.9, 1.1, 2.5, 43.8, 45.5, 16.0,  8.0, 16.0, 4.7, 46.7,  60.0),
        ("Paolo Banchero",           "ORL", 46,  3.4, 15.5, 0.87,  3.0, 1.0, 2.6, 37.3, 39.4, 20.9,  7.0, 19.0, 2.5, 44.3,  49.0),
        ("Deni Avdija",              "POR", 45,  3.2, 13.3, 0.96,  3.0, 0.8, 2.1, 35.8, 42.1, 23.9, 12.7, 21.1, 3.5, 44.4,  63.3),
        ("Derik Queen",              "NOP", 57,  2.2, 16.4, 1.00,  2.2, 0.8, 1.6, 50.0, 50.6, 17.1, 11.4, 13.0, 1.6, 51.2,  73.0),
        ("Shaedon Sharpe",           "POR", 46,  2.8, 12.3, 0.97,  2.7, 1.0, 2.4, 42.3, 50.0,  7.1,  7.9,  5.5, 2.4, 41.7,  66.9),
        ("Keyonte George",           "UTA", 47,  2.8, 12.6, 0.92,  2.6, 0.9, 2.2, 38.5, 42.8, 14.3,  9.8, 13.5, 2.3, 42.1,  58.0),
        ("Cooper Flagg",             "DAL", 45,  2.8, 13.7, 0.94,  2.7, 1.0, 2.3, 43.3, 44.2, 14.1,  7.8, 12.5, 3.1, 46.1,  60.8),
        ("Joel Embiid",              "PHI", 33,  3.5, 13.8, 1.04,  3.6, 1.3, 2.6, 51.8, 53.5, 15.8, 12.3, 14.0, 2.6, 51.8,  79.2),
        ("Anfernee Simons",          "BOS", 47,  2.4, 18.1, 1.04,  2.5, 1.0, 2.1, 44.6, 53.0,  7.1,  5.3,  7.1, 1.8, 45.1,  79.6),
        ("Davion Mitchell",          "MIA", 46,  2.7, 28.2, 0.89,  2.4, 1.0, 2.3, 44.9, 47.2,  6.4,  9.6,  4.8, 1.6, 43.2,  51.4),
        ("Norman Powell",            "MIA", 45,  2.1, 10.3, 1.18,  2.4, 0.9, 1.6, 54.8, 57.5, 19.4, 10.8, 18.3, 8.6, 53.8,  91.8),
        ("Dillon Brooks",            "PHX", 46,  2.4, 11.3, 1.01,  2.4, 1.0, 2.1, 46.9, 50.5,  6.4,  4.6,  5.5, 0.9, 47.7,  75.1),
        ("Jaime Jaquez Jr.",         "MIA", 52,  2.5, 15.8, 0.85,  2.1, 0.9, 1.9, 46.5, 46.5, 10.1, 13.2,  9.3, 1.6, 44.2,  46.5),
        ("LaMelo Ball",              "CHA", 48,  2.6, 12.3, 0.88,  2.3, 0.8, 2.2, 38.1, 44.3,  7.3,  8.9,  5.7, 1.6, 38.2,  50.2),
        ("Austin Reaves",            "LAL", 29,  3.2, 15.2, 1.08,  3.5, 1.2, 2.7, 43.6, 46.8, 20.2,  3.2, 19.1, 6.4, 48.9,  86.5),
        ("Jimmy Butler III",         "GSW", 35,  3.0, 17.7, 0.96,  2.9, 0.8, 2.0, 40.6, 42.0, 24.8, 12.4, 22.9, 2.9, 47.6,  65.3),
        ("Victor Wembanyama",        "SAS", 43,  2.7, 12.5, 0.84,  2.3, 0.8, 2.0, 39.1, 40.2, 15.4, 12.8, 14.5, 2.6, 41.0,  42.4),
        ("Russell Westbrook",        "SAC", 53,  2.3, 13.0, 0.80,  1.8, 0.6, 1.7, 35.2, 39.0, 16.4, 10.7, 16.4, 1.6, 38.5,  35.5),
        ("LeBron James",             "LAL", 38,  2.7, 12.3, 0.89,  2.4, 0.9, 2.2, 41.5, 46.3,  8.9, 10.9,  8.9, 1.0, 40.6,  52.7),
        ("Stephen Curry",            "GSW", 36,  2.3,  9.6, 1.07,  2.4, 0.8, 1.8, 46.9, 51.6, 15.9,  9.8, 14.6, 3.7, 48.8,  84.1),
        ("Scottie Barnes",           "TOR", 55,  1.6,  8.1, 1.02,  1.6, 0.6, 1.1, 51.7, 52.5, 22.1,  9.3, 19.8, 1.2, 54.7,  76.6),
        ("De'Aaron Fox",             "SAS", 45,  1.8, 10.0, 1.04,  1.9, 0.7, 1.5, 48.5, 52.3, 13.4,  6.1, 12.2, 0.0, 50.0,  78.0),
        ("Dennis Schröder",          "SAC", 39,  2.0, 14.5, 1.04,  2.1, 0.7, 1.5, 43.3, 45.8, 21.5,  3.8, 21.5, 1.3, 53.2,  78.4),
        ("Amen Thompson",            "HOU", 54,  1.6,  8.9, 0.96,  1.5, 0.6, 1.1, 49.2, 49.2, 17.6, 15.3, 17.6, 4.7, 48.2,  65.7),
        ("Isaiah Collier",           "UTA", 50,  1.7, 14.2, 0.90,  1.6, 0.6, 1.3, 47.0, 47.0, 11.5, 13.8, 11.5, 1.1, 46.0,  53.9),
        ("Jaren Jackson Jr.",        "MEM", 42,  2.2, 11.7, 0.84,  1.9, 0.7, 1.6, 45.6, 45.6, 12.9, 17.2, 12.9, 3.2, 41.9,  43.0),
        ("Nic Claxton",              "BKN", 51,  1.4, 11.8, 1.12,  1.5, 0.6, 1.0, 56.6, 56.6, 20.3,  8.7, 15.9, 5.8, 56.5,  88.2),
        ("Miles Bridges",            "CHA", 53,  1.5,  8.5, 1.00,  1.5, 0.4, 1.0, 39.6, 41.5, 23.4,  9.1, 23.4, 1.3, 49.4,  73.0),
        ("Desmond Bane",             "ORL", 53,  1.4,  7.6, 1.01,  1.4, 0.5, 1.1, 47.4, 53.5, 10.8, 13.5,  8.1, 1.4, 45.9,  75.5),
        ("Paul George",              "PHI", 26,  3.0, 18.9, 0.94,  2.8, 1.2, 2.7, 44.9, 47.8,  8.9,  6.3,  7.6, 2.5, 45.6,  60.4),
        ("VJ Edgecombe",             "PHI", 54,  1.5,  9.6, 0.89,  1.4, 0.6, 1.4, 42.5, 47.3,  6.0,  9.6,  6.0, 3.6, 39.8,  53.1),
        # --- next batch ---
        ("Brandon Williams",         "DAL", 47,  1.4, 10.7, 1.06,  1.5, 0.6, 1.1, 52.8, 53.8, 16.2, 10.3, 14.7, 4.4, 52.9,  82.9),
        ("Giannis Antetokounmpo",    "MIL", 28,  2.6, 10.9, 0.97,  2.5, 1.0, 2.0, 47.4, 48.2, 16.4,  9.6, 15.1, 4.1, 47.9,  67.3),
        ("Cam Thomas",               "BKN", 24,  2.9, 17.2, 1.01,  2.9, 1.0, 2.3, 41.1, 44.6, 17.4,  5.8, 15.9, 4.3, 46.4,  75.9),
        ("Michael Porter Jr.",       "BKN", 45,  1.6,  7.2, 0.96,  1.5, 0.6, 1.3, 47.4, 55.3,  4.2, 16.7,  4.2, 0.0, 41.7,  63.9),
        ("Jalen Duren",              "DET", 46,  1.4,  8.8, 1.08,  1.5, 0.5, 1.1, 50.0, 50.0, 20.6,  3.2, 19.0, 3.2, 57.1,  84.5),
        ("Nikola Jokić",             "DEN", 42,  1.6,  6.5, 1.00,  1.6, 0.7, 1.3, 51.9, 53.7, 10.3, 13.2, 10.3, 2.9, 48.5,  73.0),
        ("Brandon Miller",           "CHA", 42,  2.0,  9.3, 0.81,  1.6, 0.6, 1.7, 35.2, 36.6, 11.9,  6.0, 11.9, 2.4, 39.3,  36.9),
        ("Karl-Anthony Towns",       "NYK", 51,  1.8,  9.5, 0.74,  1.3, 0.4, 1.2, 35.6, 35.6, 19.6, 17.4, 19.6, 1.1, 40.2,  27.3),
        ("Jalen Johnson",            "ATL", 52,  1.9,  8.1, 0.70,  1.3, 0.5, 1.5, 32.5, 33.1, 12.4,  9.3, 11.3, 4.1, 34.0,  19.2),
        ("Ryan Rollins",             "MIL", 53,  1.5,  8.5, 0.86,  1.3, 0.5, 1.2, 36.4, 43.9,  9.0,  9.0,  7.7, 2.6, 37.2,  48.6),
        ("Aaron Gordon",             "DEN", 22,  2.5, 16.0, 1.20,  3.0, 0.9, 1.9, 45.2, 53.6, 24.1,  1.9, 22.2, 3.7, 55.6,  92.2),
        ("Andrew Wiggins",           "MIA", 52,  1.5,  9.8, 0.83,  1.3, 0.5, 1.2, 40.6, 41.4,  9.0, 10.3,  6.4, 1.3, 41.0,  40.7),
        ("Chet Holmgren",            "OKC", 48,  1.3,  8.8, 0.98,  1.3, 0.4, 0.9, 45.5, 48.9, 22.2, 11.1, 20.6, 3.2, 50.8,  68.6),
        ("Kelly Oubre Jr.",          "PHI", 36,  1.6, 11.5, 1.05,  1.7, 0.6, 1.3, 48.9, 48.9, 15.8,  7.0, 15.8, 5.3, 50.9,  81.6),
        ("Jrue Holiday",             "POR", 31,  2.0, 11.7, 0.97,  1.9, 0.8, 1.6, 49.0, 56.1,  3.3, 16.4,  1.6, 0.0, 42.6,  66.5),
        ("Jalen Williams",           "OKC", 23,  2.7, 15.0, 0.95,  2.6, 1.0, 2.3, 42.6, 43.5, 11.3,  3.2, 11.3, 1.6, 46.8,  62.0),
        ("Naji Marshall",            "DAL", 54,  0.9,  6.4, 1.17,  1.0, 0.4, 0.7, 57.5, 57.5, 14.6,  4.2, 12.5, 2.1, 60.4,  91.0),
        ("Jeremiah Fears",           "NOP", 58,  1.2,  7.6, 0.81,  0.9, 0.4, 0.9, 43.4, 45.3,  6.0, 17.9,  3.0, 3.0, 37.3,  36.3),
        ("Kevin Porter Jr.",         "MIL", 33,  1.8,  9.9, 0.87,  1.6, 0.5, 1.4, 36.2, 39.4, 14.8, 11.5, 14.8, 3.3, 39.3,  49.4),
        ("Andrew Nembhard",          "IND", 45,  1.4,  8.0, 0.81,  1.2, 0.4, 1.1, 35.3, 39.2, 10.8, 10.8,  9.2, 0.0, 38.5,  38.4),
        ("Ajay Mitchell",            "OKC", 38,  1.3,  8.9, 1.06,  1.3, 0.5, 0.9, 50.0, 52.8, 18.8, 10.4, 16.7, 4.2, 52.1,  83.7),
        ("Saddiq Bey",               "NOP", 51,  1.2,  7.8, 0.81,  1.0, 0.3, 1.1, 31.5, 33.3, 15.9,  1.6, 15.9, 3.2, 39.7,  36.9),
        ("Stephon Castle",           "SAS", 46,  1.4,  8.0, 0.77,  1.1, 0.4, 1.1, 34.6, 34.6, 15.2,  9.1, 15.2, 3.0, 39.4,  31.8),
        ("Dru Smith",                "MIA", 55,  0.7, 10.3, 1.39,  0.9, 0.3, 0.5, 69.2, 69.2, 30.6,  8.3, 27.8, 11.1, 69.4, 97.1),
        ("Bam Adebayo",              "MIA", 50,  1.4,  7.5, 0.67,  0.9, 0.3, 1.1, 28.3, 29.2, 17.1, 11.4, 17.1, 4.3, 32.9,  14.7),
        ("James Harden",             "CLE",  7,  4.7, 26.8, 1.39,  6.6, 2.0, 3.3, 60.9, 71.7, 21.2, 12.1, 21.2, 3.0, 60.6,  97.6),
        ("Kyshawn George",           "WAS", 45,  1.1,  6.6, 0.96,  1.0, 0.4, 1.0, 39.5, 46.5, 10.4,  4.2, 10.4, 4.2, 41.7,  63.9),
        ("Zach LaVine",              "SAC", 36,  1.5,  9.0, 0.84,  1.3, 0.4, 1.2, 37.2, 39.5, 12.7,  9.1, 12.7, 0.0, 41.8,  41.8),
        ("Immanuel Quickley",        "TOR", 55,  1.0,  6.1, 0.84,  0.8, 0.2, 0.7, 30.0, 32.5, 20.0,  7.3, 20.0, 0.0, 41.8,  41.8),
        ("Quentin Grimes",           "PHI", 50,  1.2,  9.6, 0.78,  0.9, 0.3, 0.8, 33.3, 41.0, 15.3, 22.0, 13.6, 3.4, 33.9,  32.7),
        ("Ja Morant",                "MEM", 19,  3.1, 14.1, 0.76,  2.4, 0.7, 2.4, 30.4, 31.5, 16.9,  8.5, 15.3, 3.4, 37.3,  30.2),
        ("Brandin Podziemski",       "GSW", 57,  0.8,  6.1, 1.02,  0.8, 0.3, 0.6, 43.2, 48.6, 11.6,  4.7, 11.6, 2.3, 46.5,  76.6),
        ("Jerami Grant",             "POR", 42,  1.6,  9.3, 0.64,  1.0, 0.4, 1.1, 31.9, 33.0, 13.0, 18.8, 13.0, 0.0, 33.3,   9.4),
        ("Ausar Thompson",           "DET", 52,  0.9,  7.9, 0.96,  0.8, 0.3, 0.7, 50.0, 50.0, 13.3, 11.1, 13.3, 0.0, 51.1,  62.4),
        ("Tre Johnson",              "WAS", 44,  0.7,  5.7, 1.31,  1.0, 0.4, 0.6, 57.1, 64.3, 12.5,  0.0,  6.3, 0.0, 62.5,  96.7),
        ("Coby White",               "CHI", 28,  1.4,  7.5, 1.05,  1.5, 0.4, 1.0, 44.4, 48.1, 20.5, 10.3, 17.9, 0.0, 51.3,  81.2),
        ("Tyler Herro",              "MIA", 14,  2.3, 12.0, 1.25,  2.9, 1.1, 1.9, 61.5, 65.4, 15.6,  9.4, 15.6, 6.3, 59.4,  94.7),
        ("Jordan Poole",             "NOP", 33,  1.1,  7.5, 1.11,  1.2, 0.4, 0.9, 43.3, 53.3, 13.9,  8.3, 13.9, 5.6, 44.4,  87.7),
        ("Daniss Jenkins",           "DET", 46,  1.0, 10.6, 0.91,  0.9, 0.4, 0.8, 48.6, 48.6, 11.4, 13.6, 11.4, 4.5, 45.5,  56.4),
        ("Trey Murphy III",          "NOP", 49,  1.2,  6.4, 0.64,  0.8, 0.2, 0.9, 26.1, 31.5,  9.8, 14.8,  8.2, 0.0, 29.5,   9.8),
        ("Pelle Larsson",            "MIA", 46,  0.8,  8.0, 1.03,  0.8, 0.3, 0.5, 56.5, 58.7, 21.6, 16.2, 21.6, 0.0, 56.8,  77.1),
        ("Caleb Love",               "POR", 42,  1.1,  8.4, 0.84,  0.9, 0.4, 0.9, 43.2, 45.9,  6.7, 11.1,  6.7, 0.0, 42.2,  44.5),
        ("Harrison Barnes",          "SAS", 54,  0.6,  6.4, 1.16,  0.7, 0.3, 0.5, 57.7, 57.7, 12.5,  6.3, 12.5, 0.0, 59.4,  90.2),
        ("Evan Mobley",              "CLE", 43,  0.9,  5.1, 1.00,  0.9, 0.4, 0.7, 53.1, 53.1,  8.1,  8.1,  5.4, 2.7, 51.4,  73.0),
        ("Grayson Allen",            "PHX", 37,  0.9,  5.0, 1.13,  1.0, 0.3, 0.6, 52.4, 61.9, 25.0, 12.5, 25.0, 3.1, 53.1,  88.6),
        ("De'Andre Hunter",          "CLE", 40,  1.1,  7.9, 0.80,  0.9, 0.3, 0.8, 38.7, 45.2, 11.1, 20.0, 11.1, 0.0, 37.8,  34.8),
        ("Peyton Watson",            "DEN", 47,  1.1,  7.7, 0.69,  0.8, 0.3, 0.9, 34.1, 34.1, 11.5,  9.6, 11.5, 0.0, 38.5,  16.5),
        ("Bones Hyland",             "MIN", 50,  0.8, 11.3, 0.85,  0.7, 0.2, 0.6, 41.4, 44.8, 17.9, 10.3, 15.4, 2.6, 41.0,  45.5),
        ("Jordan Miller",            "LAC", 36,  1.1, 13.1, 0.81,  0.9, 0.3, 0.7, 38.5, 40.4, 17.1, 19.5, 17.1, 0.0, 41.5,  35.9),
        ("Kyle Kuzma",               "MIL", 52,  0.6,  4.7, 1.03,  0.6, 0.2, 0.4, 47.8, 47.8, 22.6,  6.5, 22.6, 3.2, 54.8,  77.6),
        # --- next batch ---
        ("Jabari Smith Jr.",          "HOU", 54,  0.8,  5.7, 0.71,  0.6, 0.2, 0.7, 33.3, 37.5,  8.9, 11.1,  8.9, 0.0, 35.6,  21.6),
        ("Anthony Davis",             "DAL", 19,  2.4, 11.5, 0.70,  1.7, 0.7, 2.1, 35.9, 35.9,  8.7,  8.7,  8.7, 2.2, 34.8,  17.6),
        ("Ty Jerome",                 "MEM",  8,  2.8, 17.1, 1.41,  3.9, 1.3, 2.3, 55.6, 66.7, 22.7,  4.5, 22.7, 9.1, 59.1,  98.0),
        ("Nickeil Alexander-Walker",  "ATL", 56,  0.7,  3.6, 0.80,  0.6, 0.2, 0.6, 35.5, 37.1, 12.8, 10.3, 12.8, 2.6, 38.5,  34.3),
        ("Bennedict Mathurin",        "IND", 25,  1.7,  9.9, 0.74,  1.2, 0.4, 1.3, 31.3, 34.4, 16.7, 11.9, 16.7, 4.8, 35.7,  26.9),
        ("Toumani Camara",            "POR", 58,  0.9,  6.5, 0.62,  0.5, 0.2, 0.6, 34.4, 39.1, 10.0, 26.0, 10.0, 0.0, 30.0,   7.8),
        ("Josh Giddey",               "CHI", 37,  1.0,  5.0, 0.83,  0.8, 0.2, 0.8, 30.0, 33.3, 16.7,  0.0, 16.7, 0.0, 41.7,  40.7),
        ("Jarace Walker",             "IND", 56,  0.8,  6.1, 0.71,  0.5, 0.2, 0.6, 32.3, 35.5,  9.5, 16.7,  9.5, 0.0, 33.3,  22.3),
        ("Darius Garland",            "CLE", 23,  1.3,  7.0, 0.97,  1.3, 0.4, 0.8, 52.6, 60.5, 13.3, 23.3, 10.0, 0.0, 43.3,  66.1),
        ("Lauri Markkanen",           "UTA", 40,  0.9,  3.6, 0.85,  0.7, 0.3, 0.8, 40.6, 43.8,  2.9,  5.9,  2.9, 2.9, 38.2,  46.9),
        ("CJ McCollum",               "ATL", 21,  1.8,  9.5, 0.78,  1.4, 0.5, 1.4, 34.5, 36.2, 16.2,  5.4, 16.2, 0.0, 40.5,  33.5),
        ("Malik Monk",                "SAC", 45,  1.0,  7.6, 0.67,  0.6, 0.2, 0.9, 27.5, 33.8,  2.3,  4.7,  2.3, 0.0, 27.9,  15.1),
        ("Jalen Suggs",               "ORL", 30,  0.8,  5.6, 1.17,  0.9, 0.2, 0.6, 41.2, 47.1, 29.2,  0.0, 16.7, 0.0, 54.2,  91.0),
        ("Cedric Coward",             "MEM", 45,  0.5,  3.5, 1.29,  0.6, 0.2, 0.4, 55.0, 60.0, 14.3,  0.0, 14.3, 9.5, 57.1,  95.5),
        ("Marvin Bagley III",         "WAS", 37,  0.7,  7.6, 1.08,  0.7, 0.3, 0.5, 58.8, 58.8, 36.0, 12.0, 36.0, 16.0, 52.0,  85.3),
        ("Matas Buzelis",             "CHI", 58,  0.5,  3.3, 0.93,  0.5, 0.2, 0.3, 57.9, 57.9, 17.2, 24.1, 17.2, 6.9, 44.8,  59.6),
        ("De'Anthony Melton",         "GSW", 32,  1.2,  8.6, 0.73,  0.8, 0.2, 0.8, 28.0, 30.0, 16.2, 16.2, 13.5, 0.0, 35.1,  25.1),
        ("Dylan Harper",              "SAS", 44,  0.8,  7.2, 0.73,  0.6, 0.3, 0.7, 41.4, 41.4,  8.1, 13.5,  8.1, 0.0, 40.5,  25.1),
        ("Max Christie",              "DAL", 50,  0.7,  6.3, 0.73,  0.5, 0.2, 0.6, 30.0, 31.7, 13.5,  5.4, 13.5, 0.0, 37.8,  25.1),
        ("Derrick White",             "BOS", 55,  1.0,  5.5, 0.50,  0.5, 0.2, 0.8, 23.9, 27.2,  1.9, 13.0,  1.9, 0.0, 22.2,   3.7),
        ("Reed Sheppard",             "HOU", 56,  0.6,  4.4, 0.84,  0.5, 0.1, 0.4, 32.0, 36.0, 16.1,  6.5, 12.9, 3.2, 38.7,  43.0),
        ("Alex Sarr",                 "WAS", 38,  0.9,  5.3, 0.77,  0.7, 0.3, 0.7, 37.0, 37.0, 11.8,  8.8, 11.8, 0.0, 41.2,  30.7),
        ("Jamal Shead",               "TOR", 57,  0.6,  7.3, 0.74,  0.5, 0.1, 0.5, 25.9, 27.8, 20.0,  2.9, 14.3, 0.0, 40.0,  27.8),
        ("Bub Carrington",            "WAS", 55,  0.7,  5.6, 0.72,  0.5, 0.2, 0.6, 32.3, 37.1,  8.3,  5.6,  5.6, 0.0, 33.3,  23.7),
        ("OG Anunoby",                "NYK", 43,  0.9,  5.6, 0.68,  0.6, 0.2, 0.8, 30.3, 30.3,  7.9,  5.3,  7.9, 0.0, 34.2,  15.6),
        ("CJ McCollum",               "WAS", 31,  1.5,  8.4, 0.56,  0.8, 0.4, 1.2, 28.9, 28.9,  8.7, 10.9,  8.7, 2.2, 28.3,   5.7),
        ("Ryan Nembhard",             "DAL", 36,  0.7,  8.3, 1.04,  0.7, 0.3, 0.6, 50.0, 52.3,  4.2,  4.2,  0.0, 0.0, 50.0,  78.8),
        ("Collin Sexton",             "CHA", 39,  0.6,  4.7, 1.00,  0.6, 0.2, 0.4, 47.1, 50.0, 20.0, 16.0, 20.0, 4.0, 48.0,  73.0),
        ("Noah Clowney",              "BKN", 50,  0.5,  4.2, 0.93,  0.5, 0.1, 0.3, 41.2, 41.2, 29.6, 14.8, 25.9, 7.4, 44.4,  59.2),
        ("Anthony Black",             "ORL", 53,  0.7,  4.1, 0.71,  0.5, 0.1, 0.5, 26.9, 30.8, 14.3, 11.4, 14.3, 0.0, 34.3,  22.3),
        ("Kris Dunn",                 "LAC", 55,  0.3,  4.4, 1.26,  0.4, 0.2, 0.2, 69.2, 69.2, 26.3, 15.8, 26.3, 10.5, 63.2,  95.1),
        ("Bobby Portis",              "MIL", 53,  0.5,  3.8, 0.96,  0.5, 0.2, 0.5, 48.0, 48.0,  0.0,  0.0,  0.0, 0.0, 48.0,  64.5),
        ("Tre Mann",                  "CHA", 37,  0.7,  8.7, 0.92,  0.6, 0.2, 0.5, 45.0, 50.0,  7.7, 15.4,  7.7, 0.0, 42.3,  58.6),
        ("P.J. Washington",           "DAL", 39,  0.7,  4.6, 0.89,  0.6, 0.2, 0.5, 45.0, 45.0, 18.5, 11.1, 18.5, 3.7, 44.4,  51.8),
        ("Jonathan Kuminga",          "GSW", 20,  1.7, 12.6, 0.71,  1.2, 0.4, 1.1, 31.8, 31.8, 20.6, 20.6, 20.6, 5.9, 35.3,  19.8),
        ("Aaron Wiggins",             "OKC", 44,  0.8,  6.9, 0.71,  0.5, 0.2, 0.6, 38.5, 44.2,  5.9, 17.6,  5.9, 0.0, 32.4,  19.8),
        ("Dyson Daniels",             "ATL", 56,  0.6,  5.0, 0.67,  0.4, 0.2, 0.5, 33.3, 33.3, 11.1,  8.3, 11.1, 2.8, 33.3,  12.9),
        ("Franz Wagner",              "ORL", 25,  1.5,  7.5, 0.65,  1.0, 0.3, 1.1, 25.0, 30.4, 16.2,  8.1, 13.5, 0.0, 32.4,  11.8),
        ("Cam Thomas",                "MIL",  8,  1.3,  9.1, 2.30,  2.9, 1.1, 1.3, 90.0, 115.0,  0.0,  0.0,  0.0, 0.0, 90.0, 100.0),
        ("Kenrich Williams",          "OKC", 37,  0.5,  7.7, 1.21,  0.6, 0.2, 0.4, 56.3, 62.5, 10.5, 10.5, 10.5, 5.3, 52.6,  92.7),
        ("D'Angelo Russell",          "DAL", 25,  0.9,  8.7, 1.00,  0.9, 0.3, 0.8, 42.1, 50.0,  8.7,  8.7,  8.7, 0.0, 43.5,  73.0),
        ("Moses Moody",               "GSW", 55,  0.5,  4.7, 0.82,  0.4, 0.1, 0.4, 35.0, 40.0, 17.9, 10.7, 17.9, 0.0, 42.9,  39.2),
        ("Gui Santos",                "GSW", 48,  0.3,  4.9, 1.47,  0.5, 0.2, 0.2, 90.0, 90.0, 26.7, 20.0, 26.7, 13.3, 73.3,  98.8),
        ("Rui Hachimura",             "LAL", 43,  0.4,  3.8, 1.29,  0.5, 0.2, 0.3, 58.3, 58.3, 23.5,  5.9, 23.5, 0.0, 64.7,  95.9),
        ("Sharife Cooper",            "WAS", 16,  1.3, 16.2, 1.05,  1.4, 0.5, 1.0, 50.0, 59.4,  9.5, 14.3,  9.5, 0.0, 47.6,  80.4),
        ("Drake Powell",              "BKN", 44,  0.5,  8.0, 0.96,  0.5, 0.2, 0.3, 57.1, 64.3,  8.7, 30.4,  8.7, 0.0, 43.5,  62.9),
        ("Keldon Johnson",            "SAS", 54,  0.5,  4.0, 0.88,  0.4, 0.2, 0.4, 40.9, 40.9, 12.0,  0.0, 12.0, 0.0, 48.0,  50.6),
        ("Brice Sensabaugh",          "UTA", 55,  0.5,  4.0, 0.81,  0.4, 0.1, 0.4, 35.0, 37.5, 14.8, 11.1, 14.8, 0.0, 40.7,  38.0),
        ("Cason Wallace",             "OKC", 53,  0.5,  5.8, 0.76,  0.4, 0.2, 0.5, 38.5, 38.5,  3.4,  6.9,  3.4, 0.0, 37.9,  29.4),
        ("Ace Bailey",                "UTA", 51,  0.6,  5.0, 0.67,  0.4, 0.2, 0.5, 35.7, 39.3,  0.0, 15.2,  0.0, 0.0, 30.3,  12.9),
        # --- next batch ---
        ("Dennis Schröder",          "CLE", 10,  1.7, 13.3, 1.24,  2.1, 0.8, 1.4, 57.1, 57.1, 17.6,  0.0, 17.6, 0.0, 64.7,  93.5),
        ("Caris LeVert",             "DET", 38,  0.6,  7.3, 0.91,  0.6, 0.2, 0.5, 47.4, 52.6,  8.7, 13.0,  4.3, 4.3, 43.5,  57.6),
        ("Day'Ron Sharpe",           "BKN", 54,  0.3,  3.9, 1.11,  0.4, 0.1, 0.2, 72.7, 72.7, 16.7, 22.2, 11.1, 0.0, 55.6,  87.7),
        ("Bruce Brown",              "DEN", 58,  0.3,  3.8, 1.11,  0.3, 0.2, 0.3, 60.0, 60.0, 11.1, 16.7, 11.1, 11.1, 50.0,  87.7),
        ("Marcus Smart",             "LAL", 46,  0.4,  3.9, 1.06,  0.4, 0.2, 0.3, 57.1, 60.7, 16.7, 22.2, 16.7, 16.7, 44.4,  82.0),
        ("Jaden McDaniels",          "MIN", 55,  0.4,  2.7, 0.91,  0.3, 0.1, 0.3, 40.0, 40.0, 19.0,  9.5, 19.0, 0.0, 47.6,  55.1),
        ("Jalen Green",              "PHX", 12,  2.1, 12.9, 0.76,  1.6, 0.7, 1.9, 34.8, 39.1,  4.0,  4.0,  4.0, 0.0, 36.0,  29.8),
        ("Will Riley",               "WAS", 47,  0.4,  4.8, 0.95,  0.4, 0.1, 0.3, 58.3, 58.3, 15.8, 21.1, 15.8, 0.0, 47.4,  61.6),
        ("Jaylen Wells",             "MEM", 54,  0.4,  3.0, 0.90,  0.3, 0.1, 0.3, 50.0, 50.0, 20.0, 15.0, 20.0, 5.0, 45.0,  54.5),
        ("Jordan Clarkson",          "NYK", 49,  0.4,  5.1, 0.82,  0.4, 0.2, 0.4, 42.1, 44.7,  4.5, 13.6,  4.5, 4.5, 36.4,  38.8),
        ("Collin Gillespie",         "PHX", 55,  0.4,  3.3, 0.78,  0.3, 0.1, 0.4, 35.0, 37.5,  8.7,  4.3,  8.7, 0.0, 39.1,  33.1),
        ("Oso Ighodaro",             "PHX", 56,  0.5,  7.9, 0.69,  0.3, 0.2, 0.3, 52.9, 52.9, 11.5, 30.8, 11.5, 7.7, 34.6,  16.5),
        ("Scoot Henderson",          "POR",  9,  1.3,  8.5, 1.42,  1.9, 0.4, 0.9, 50.0, 50.0, 33.3,  0.0, 16.7, 0.0, 66.7,  98.4),
        ("Jose Alvarado",            "NOP", 38,  0.3,  4.3, 1.31,  0.4, 0.2, 0.3, 54.5, 68.2,  7.7,  7.7,  7.7, 0.0, 53.8,  96.3),
        ("Jaden Ivey",               "DET", 31,  0.5,  5.5, 1.21,  0.5, 0.2, 0.3, 70.0, 80.0,  7.1, 28.6,  7.1, 7.1, 50.0,  93.1),
        ("Kobe Sanders",             "LAC", 45,  0.4,  4.9, 1.00,  0.4, 0.2, 0.3, 53.3, 53.3,  5.9,  5.9,  0.0, 0.0, 52.9,  73.0),
        ("Mikal Bridges",            "NYK", 55,  0.3,  2.2, 1.00,  0.3, 0.1, 0.3, 46.7, 46.7, 11.8,  0.0, 11.8, 0.0, 52.9,  73.0),
        ("Khris Middleton",          "WAS", 30,  0.8,  6.9, 0.71,  0.6, 0.3, 0.7, 38.1, 38.1,  4.2,  8.3,  4.2, 0.0, 37.5,  21.2),
        ("Naz Reid",                 "MIN", 56,  0.5,  3.5, 0.63,  0.3, 0.1, 0.3, 29.4, 32.4, 14.8, 25.9, 14.8, 3.7, 29.6,   8.6),
        ("Bilal Coulibaly",          "WAS", 36,  0.8,  6.9, 0.61,  0.5, 0.2, 0.6, 36.4, 36.4,  7.1, 14.3,  7.1, 0.0, 32.1,   7.3),
        ("Anfernee Simons",          "CHI",  6,  2.3, 15.1, 1.14,  2.7, 1.2, 2.0, 58.3, 62.5,  7.1, 14.3,  7.1, 7.1, 50.0,  89.8),
        ("Tristan Vukcevic",         "WAS", 34,  0.4,  5.0, 1.14,  0.5, 0.2, 0.4, 46.2, 53.8,  7.1,  0.0,  7.1, 0.0, 50.0,  89.8),
        ("Ousmane Dieng",            "OKC", 25,  0.7, 18.1, 0.94,  0.6, 0.3, 0.7, 41.2, 47.1,  0.0,  0.0,  0.0, 0.0, 41.2,  61.2),
        ("Kyle Anderson",            "UTA", 20,  1.0, 13.3, 0.84,  0.8, 0.2, 0.7, 30.8, 30.8, 31.6,  0.0, 31.6, 0.0, 52.6,  43.9),
        ("Miles McBride",            "NYK", 32,  0.6,  5.0, 0.84,  0.5, 0.2, 0.6, 38.9, 44.4,  0.0,  5.3,  0.0, 0.0, 36.8,  43.9),
        ("Trae Young",               "ATL", 10,  2.3, 12.0, 0.70,  1.6, 0.4, 2.0, 20.0, 22.5, 17.4,  0.0, 13.0, 4.3, 30.4,  17.6),
        ("Tobias Harris",            "DET", 40,  0.7,  5.7, 0.55,  0.4, 0.1, 0.6, 20.8, 20.8, 17.2,  6.9, 17.2, 6.9, 27.6,   5.3),
        ("Collin Sexton",            "CHI",  8,  1.3,  9.3, 1.50,  1.9, 0.8, 1.1, 66.7, 72.2, 10.0,  0.0, 10.0, 0.0, 70.0,  99.6),
        ("Josh Hart",                "NYK", 43,  0.2,  2.0, 1.50,  0.3, 0.1, 0.2, 55.6, 66.7, 20.0,  0.0, 10.0, 10.0, 60.0,  99.6),
        ("Buddy Hield",              "GSW", 41,  0.3,  3.5, 1.25,  0.4, 0.2, 0.3, 58.3, 62.5,  0.0,  0.0,  0.0, 0.0, 58.3,  94.7),
        ("Jalen Pickett",            "DEN", 39,  0.4,  7.5, 0.88,  0.4, 0.2, 0.4, 40.0, 50.0,  0.0, 11.8,  0.0, 0.0, 35.3,  51.0),
        ("Devin Carter",             "SAC", 23,  0.8, 10.3, 0.79,  0.7, 0.1, 0.5, 16.7, 16.7, 31.6,  5.3, 31.6, 0.0, 42.1,  33.9),
        ("Rob Dillingham",           "MIN", 32,  0.9, 17.5, 0.50,  0.5, 0.2, 0.8, 23.1, 25.0,  3.3, 10.0,  3.3, 0.0, 23.3,   3.7),
        ("Kentavious Caldwell-Pope", "MEM", 48,  0.3,  3.2, 1.00,  0.3, 0.1, 0.2, 36.4, 36.4, 21.4,  0.0, 21.4, 0.0, 50.0,  73.0),
        ("Isaac Okoro",              "CHI", 50,  0.3,  3.9, 0.82,  0.3, 0.1, 0.2, 54.5, 54.5, 11.8, 23.5, 11.8, 0.0, 47.1,  39.8),
        ("RJ Barrett",               "TOR", 35,  0.5,  2.8, 0.82,  0.4, 0.2, 0.4, 42.9, 42.9,  5.9, 11.8,  5.9, 0.0, 41.2,  39.8),
        ("Nolan Traore",             "BKN", 37,  0.5,  4.8, 0.78,  0.4, 0.2, 0.4, 46.2, 46.2, 11.1, 16.7,  5.6, 0.0, 44.4,  32.2),
        ("Herbert Jones",            "NOP", 36,  0.5,  5.1, 0.74,  0.4, 0.2, 0.5, 33.3, 38.9,  0.0,  5.3,  0.0, 0.0, 31.6,  26.5),
        ("T.J. McConnell",           "IND", 40,  0.5,  5.5, 0.67,  0.4, 0.2, 0.4, 40.0, 40.0,  4.8, 23.8,  4.8, 0.0, 33.3,  12.9),
        ("Jonas Valančiūnas",        "DEN", 46,  0.3,  3.1, 1.08,  0.3, 0.1, 0.2, 60.0, 65.0,  0.0, 16.7,  0.0, 0.0, 50.0,  86.1),
        ("Onyeka Okongwu",           "ATL", 53,  0.2,  1.5, 1.08,  0.2, 0.1, 0.2, 50.0, 50.0, 25.0,  8.3, 25.0, 0.0, 58.3,  86.1),
        ("Ronald Holland II",        "DET", 51,  0.3,  3.4, 0.81,  0.3, 0.1, 0.3, 35.7, 35.7, 12.5,  6.3, 12.5, 6.3, 37.5,  37.6),
        ("Nique Clifford",           "SAC", 54,  0.3,  3.6, 0.77,  0.2, 0.1, 0.2, 44.4, 50.0, 11.8, 35.3, 11.8, 0.0, 35.3,  30.7),
        ("Cole Anthony",             "MIL", 32,  0.6,  6.7, 0.68,  0.4, 0.2, 0.6, 33.3, 36.1,  0.0,  5.3,  0.0, 0.0, 31.6,  15.6),
        ("Cam Spencer",              "MEM", 53,  0.4,  3.8, 0.65,  0.2, 0.1, 0.2, 30.8, 34.6, 10.0, 25.0, 10.0, 0.0, 30.0,  12.2),
        ("Pat Spencer",              "GSW", 43,  0.5,  6.9, 0.59,  0.3, 0.1, 0.5, 30.0, 30.0,  4.5,  4.5,  4.5, 0.0, 31.8,   6.5),
        ("Ayo Dosunmu",              "CHI", 43,  0.3,  2.1, 1.00,  0.3, 0.1, 0.2, 55.6, 61.1,  8.3, 25.0,  8.3, 8.3, 41.7,  73.0),
        ("Myles Turner",             "MIL", 51,  0.3,  2.2, 0.92,  0.2, 0.1, 0.2, 40.0, 40.0, 23.1,  7.7, 23.1, 7.7, 46.2,  58.6),
        ("Jamaree Bouyea",           "PHX", 30,  0.5,  7.3, 0.86,  0.4, 0.2, 0.4, 46.2, 46.2,  0.0,  7.1,  0.0, 0.0, 42.9,  47.7),
        ("Jarrett Allen",            "CLE", 47,  0.3,  2.3, 0.86,  0.3, 0.1, 0.2, 50.0, 50.0, 14.3, 28.6, 14.3, 0.0, 42.9,  47.7),
    ]

    stats: List[OffensiveIsolationStats] = []
    for row in raw:
        (player, team, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        stats.append(OffensiveIsolationStats(
            player=player,
            team=team,
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
        ))
    return stats


def rank_players_by_offensive_isolation(
    stats: Optional[List["OffensiveIsolationStats"]] = None,
) -> List["OffensiveIsolationStats"]:
    """
    Return all players sorted from best to worst offensive isolation scorer
    (highest percentile first).

    If *stats* is not provided, the full dataset is used.
    """
    if stats is None:
        stats = build_offensive_isolation_stats()
    return sorted(stats, key=lambda s: s.percentile, reverse=True)


def find_isolation_scorers(
    isolation_stats: Optional[List["OffensiveIsolationStats"]] = None,
    opponent_team: Optional[str] = None,
    isolation_defensive_rankings: Optional[Dict[str, "DefensiveIsolationStats"]] = None,
    min_freq_pct: float = 10.0,
    min_ppp: float = 1.00,
) -> List[Dict]:
    """
    Identify players who are high-volume, efficient isolation scorers.

    When *opponent_team* and *isolation_defensive_rankings* are provided the
    results are further annotated with the opponent's defensive PPP and
    percentile.

    Returns a list of dicts sorted by isolation frequency % (highest first),
    each containing:
      - "player"        : player name
      - "team"          : player's team
      - "freq_pct"      : isolation frequency %
      - "ppp"           : player's isolation PPP
      - "pts"           : isolation points per game
      - "percentile"    : player's offensive isolation percentile
      - "def_ppp"       : opponent's isolation defensive PPP (if opponent supplied)
      - "def_percentile": opponent's isolation defensive percentile (if supplied)
    """
    if isolation_stats is None:
        isolation_stats = build_offensive_isolation_stats()

    def_stats = None
    if opponent_team and isolation_defensive_rankings:
        def_stats = isolation_defensive_rankings.get(opponent_team)

    results = []
    for s in isolation_stats:
        if s.freq_pct < min_freq_pct:
            continue
        if s.ppp < min_ppp:
            continue
        entry: Dict = {
            "player":         s.player,
            "team":           s.team,
            "freq_pct":       s.freq_pct,
            "ppp":            s.ppp,
            "pts":            s.pts,
            "percentile":     s.percentile,
            "def_ppp":        def_stats.ppp if def_stats else None,
            "def_percentile": def_stats.percentile if def_stats else None,
        }
        results.append(entry)

    results.sort(key=lambda r: r["freq_pct"], reverse=True)
    return results


def find_isolation_beneficiaries(
    isolation_stats: Optional[List["OffensiveIsolationStats"]] = None,
    opponent_team: str = "",
    isolation_defensive_rankings: Optional[Dict[str, "DefensiveIsolationStats"]] = None,
    min_freq_pct: float = 10.0,
    min_ppp: float = 1.00,
    max_def_percentile: float = 40.0,
) -> List[Dict]:
    """
    Identify players likely to benefit from a weak opponent isolation defense.

    A player is flagged as a beneficiary when:
    - Their isolation frequency % is at least *min_freq_pct*
    - Their isolation PPP is at least *min_ppp*
    - The opposing team's isolation defensive percentile is at most
      *max_def_percentile* (low percentile = weak isolation defense)

    Returns a list of dicts sorted by isolation frequency % (highest first),
    each containing:
      - "player"          : player name
      - "team"            : player's team
      - "freq_pct"        : player's isolation frequency %
      - "ppp"             : player's isolation PPP
      - "pts"             : player's isolation points per game
      - "percentile"      : player's offensive isolation percentile
      - "def_ppp"         : opponent's isolation defensive PPP allowed
      - "def_percentile"  : opponent's isolation defensive percentile (lower = weaker)
      - "edge"            : player isolation PPP minus opponent's defensive PPP
    """
    if isolation_stats is None:
        isolation_stats = build_offensive_isolation_stats()
    if isolation_defensive_rankings is None:
        isolation_defensive_rankings = build_defensive_isolation_rankings()

    def_stats = isolation_defensive_rankings.get(opponent_team)
    if def_stats is None:
        return []

    if def_stats.percentile > max_def_percentile:
        return []

    results = []
    for s in isolation_stats:
        if s.freq_pct < min_freq_pct:
            continue
        if s.ppp < min_ppp:
            continue
        results.append({
            "player":         s.player,
            "team":           s.team,
            "freq_pct":       s.freq_pct,
            "ppp":            s.ppp,
            "pts":            s.pts,
            "percentile":     s.percentile,
            "def_ppp":        def_stats.ppp,
            "def_percentile": def_stats.percentile,
            "edge":           round(s.ppp - def_stats.ppp, 3),
        })

    results.sort(key=lambda r: r["freq_pct"], reverse=True)
    return results


def match_all_isolation_matchups(
    offensive_stats: Optional[List["OffensiveIsolationStats"]] = None,
    defensive_rankings: Optional[Dict[str, "DefensiveIsolationStats"]] = None,
    top_n: int = 50,
    max_def_percentile: float = 40.0,
    min_off_percentile: float = 0.0,
) -> List[Dict]:
    """
    Cross-reference all offensive isolation players with all defensive teams
    to identify the highest-edge matchups.

    For every (player, opponent) pair where the player's own team differs from
    the opponent and the opponent's isolation defensive percentile is at most
    *max_def_percentile*, compute::

        edge = player PPP − opponent defensive PPP allowed

    The *top_n* pairs with the largest edge are returned, sorted by edge
    descending (ties broken by the player's offensive percentile, also
    descending).

    Parameters
    ----------
    offensive_stats:
        Pre-built offensive stats list; defaults to the full 50-player dataset.
    defensive_rankings:
        Pre-built ``{team: DefensiveIsolationStats}`` mapping; defaults to the
        full 30-team dataset.
    top_n:
        Maximum number of matchup records to return (default 50).
    max_def_percentile:
        Upper bound on the opponent's isolation defensive percentile.
        Pass ``100.0`` to include all teams.
    min_off_percentile:
        Lower bound on the player's offensive isolation percentile (default 0).

    Returns
    -------
    list of dict, each containing:
      - ``"player"``         : player name
      - ``"team"``           : player's team abbreviation
      - ``"off_percentile"`` : player's offensive isolation percentile
      - ``"ppp"``            : player's isolation PPP
      - ``"freq_pct"``       : player's isolation frequency %
      - ``"opponent"``       : opponent team abbreviation
      - ``"def_ppp"``        : opponent's isolation defensive PPP allowed
      - ``"def_percentile"`` : opponent's isolation defensive percentile
      - ``"edge"``           : player PPP − opponent defensive PPP (higher = better)
    """
    if offensive_stats is None:
        offensive_stats = build_offensive_isolation_stats()
    if defensive_rankings is None:
        defensive_rankings = build_defensive_isolation_rankings()

    results: List[Dict] = []
    for player in offensive_stats:
        if player.percentile < min_off_percentile:
            continue
        for def_team, d in defensive_rankings.items():
            if def_team == player.team:
                continue
            if d.percentile > max_def_percentile:
                continue
            results.append({
                "player":         player.player,
                "team":           player.team,
                "off_percentile": player.percentile,
                "ppp":            player.ppp,
                "freq_pct":       player.freq_pct,
                "opponent":       def_team,
                "def_ppp":        d.ppp,
                "def_percentile": d.percentile,
                "edge":           round(player.ppp - d.ppp, 3),
            })

    results.sort(key=lambda r: (r["edge"], r["off_percentile"]), reverse=True)
    return results[:top_n]


def predict_isolation_matchup(
    player_name: str,
    opponent_team: str,
    offensive_stats: Optional[List["OffensiveIsolationStats"]] = None,
    defensive_rankings: Optional[Dict[str, "DefensiveIsolationStats"]] = None,
) -> Optional[Dict]:
    """
    Return a head-to-head isolation matchup prediction for *player_name*
    against *opponent_team*'s isolation defense.

    Unlike :func:`find_isolation_beneficiaries`, this function performs a
    direct lookup with **no frequency or PPP thresholds**.

    Parameters
    ----------
    player_name:
        Exact player name (case-insensitive) as it appears in the offensive
        isolation dataset (e.g. ``"Shai Gilgeous-Alexander"``).
    opponent_team:
        Three-letter team abbreviation for the defending team (e.g. ``"SAS"``).
    offensive_stats:
        Pre-built offensive stats list; defaults to the full dataset.
    defensive_rankings:
        Pre-built ``{team: DefensiveIsolationStats}`` mapping; defaults to
        the full 30-team dataset.

    Returns
    -------
    dict or None
        ``None`` when the player or team cannot be found.  Otherwise a dict
        containing:

        - ``"player"``         : player name
        - ``"team"``           : player's team abbreviation
        - ``"gp"``             : games played
        - ``"freq_pct"``       : player's isolation frequency %
        - ``"ppp"``            : player's isolation PPP
        - ``"pts"``            : player's isolation points per game
        - ``"off_percentile"`` : player's offensive isolation percentile
        - ``"opponent"``       : opponent team abbreviation
        - ``"def_ppp"``        : opponent's isolation PPP allowed
        - ``"def_freq_pct"``   : opponent's isolation frequency allowed %
        - ``"def_percentile"`` : opponent's isolation defensive percentile
        - ``"edge"``           : player PPP − opponent defensive PPP
        - ``"verdict"``        : ``"FAVORABLE"``, ``"NEUTRAL"``, or ``"TOUGH"``
    """
    if offensive_stats is None:
        offensive_stats = build_offensive_isolation_stats()
    if defensive_rankings is None:
        defensive_rankings = build_defensive_isolation_rankings()

    player_stat = next(
        (s for s in offensive_stats if s.player.lower() == player_name.lower()),
        None,
    )
    if player_stat is None:
        return None

    def_stat = defensive_rankings.get(opponent_team.upper())
    if def_stat is None:
        return None

    edge = round(player_stat.ppp - def_stat.ppp, 3)
    if edge >= 0.15:
        verdict = "FAVORABLE"
    elif edge <= -0.15:
        verdict = "TOUGH"
    else:
        verdict = "NEUTRAL"

    return {
        "player":         player_stat.player,
        "team":           player_stat.team,
        "gp":             player_stat.gp,
        "freq_pct":       player_stat.freq_pct,
        "ppp":            player_stat.ppp,
        "pts":            player_stat.pts,
        "off_percentile": player_stat.percentile,
        "opponent":       def_stat.team,
        "def_ppp":        def_stat.ppp,
        "def_freq_pct":   def_stat.freq_pct,
        "def_percentile": def_stat.percentile,
        "edge":           edge,
        "verdict":        verdict,
    }


# ---------------------------------------------------------------------------
# Offensive PnR ball handler analytics
# ---------------------------------------------------------------------------

def build_offensive_pnr_ball_handler_stats() -> List["OffensivePnrBallHandlerStats"]:
    """
    Return offensive pick-and-roll ball handler stats for 150 NBA players
    (NBA Synergy data).

    Columns: PLAYER, TEAM, GP, POSS, FREQ%, PPP, PTS, FGM, FGA, FG%, EFG%,
             FT FREQ%, TOV FREQ%, SF FREQ%, AND ONE FREQ%, SCORE FREQ%, PERCENTILE

    PERCENTILE is the NBA Synergy composite ranking.  Higher values indicate a
    more efficient/frequent PnR ball handler.
    """
    raw = [
        # (player, team, gp, poss, freq%, ppp, pts, fgm, fga,
        #  fg%, efg%, ft_freq%, tov_freq%, sf_freq%, and_one_freq%, score_freq%, percentile)
        ("Luka Dončić",              "LAL", 43, 21.3, 69.1, 0.93, 19.9,  6.3, 16.9, 37.3, 45.5, 13.4, 12.6, 12.1, 3.0, 44.7,  55.9),
        ("Shai Gilgeous-Alexander",  "OKC", 45, 14.1, 54.5, 0.99, 14.0,  4.6, 11.7, 39.5, 46.1, 12.7, 13.9, 11.5, 2.2, 46.8,  68.7),
        ("Jalen Brunson",            "NYK", 51, 15.5, 64.0, 0.89, 13.8,  4.7, 13.5, 35.1, 40.9,  9.9, 16.8,  8.9, 2.2, 40.8,  38.5),
        ("LeBron James",             "LAL", 38, 11.4, 52.1, 0.91, 10.4,  3.6, 10.1, 35.8, 42.3, 10.8, 14.9,  9.2, 1.5, 41.6,  44.5),
        ("Stephen Curry",            "GSW", 36,  9.9, 41.3, 1.01,  9.9,  3.3,  8.8, 37.6, 49.4,  8.1, 14.2,  6.7, 0.8, 43.6,  72.8),
        ("Tyrese Maxey",             "PHI", 54, 13.0, 47.6, 0.90, 11.6,  4.0, 11.3, 35.5, 41.7,  9.8, 14.9,  8.7, 1.8, 41.3,  40.4),
        ("Donovan Mitchell",         "CLE", 52, 13.1, 50.4, 0.90, 11.7,  4.2, 11.8, 35.8, 42.2,  8.8, 16.3,  7.7, 1.6, 39.8,  41.1),
        ("Anthony Edwards",          "MIN", 47, 10.3, 39.0, 0.90,  9.3,  3.3,  9.4, 34.8, 40.7,  8.9, 16.1,  7.5, 2.0, 39.8,  41.1),
        ("James Harden",             "CLE", 41, 10.7, 44.1, 1.01, 10.7,  3.3,  8.8, 37.7, 47.8,  9.1, 13.3,  8.3, 1.5, 44.7,  73.5),
        ("LaMelo Ball",              "CHA", 48, 13.7, 64.8, 0.84, 11.4,  4.0, 12.3, 32.5, 38.2,  9.0, 17.1,  8.1, 2.2, 38.7,  27.2),
        ("Ja Morant",                "MEM", 19, 10.8, 49.3, 0.83,  8.9,  2.9,  9.4, 30.7, 36.8,  8.2, 19.2,  7.2, 1.4, 36.4,  25.5),
        ("Jamal Murray",             "DEN", 53, 10.5, 46.5, 0.94,  9.9,  3.4,  9.2, 37.0, 44.1,  7.6, 13.1,  6.7, 1.3, 42.9,  57.3),
        ("Cade Cunningham",          "DET", 50, 13.9, 54.8, 0.83, 11.4,  4.0, 13.1, 30.7, 36.6, 10.2, 15.7,  9.0, 1.5, 38.0,  26.2),
        ("Trae Young",               "ATL", 10, 16.3, 85.0, 0.85, 13.8,  4.5, 13.5, 33.4, 40.6, 10.1, 14.3,  8.9, 1.5, 39.5,  30.2),
        ("De'Aaron Fox",             "SAS", 45, 10.6, 58.8, 0.84,  8.9,  3.0, 10.3, 29.3, 36.0, 10.4, 17.8,  9.2, 1.7, 37.6,  27.2),
        ("Jaylen Brown",             "BOS", 51,  7.6, 26.4, 0.92,  7.0,  2.5,  7.5, 33.7, 38.2,  9.1, 16.7,  7.8, 1.1, 39.3,  49.9),
        ("Devin Booker",             "PHX", 41, 10.3, 41.6, 0.91,  9.4,  3.2,  9.3, 34.8, 40.5,  9.9, 14.5,  9.0, 1.7, 42.3,  45.9),
        ("Kevin Durant",             "HOU", 54,  7.1, 29.9, 0.99,  7.0,  2.5,  6.4, 38.8, 45.0,  8.0, 11.7,  7.0, 1.5, 44.7,  68.0),
        ("Paolo Banchero",           "ORL", 46, 10.2, 46.9, 0.86,  8.7,  3.0, 10.2, 29.5, 34.6,  9.3, 16.4,  8.0, 1.3, 38.0,  31.9),
        ("Darius Garland",           "CLE", 23,  9.7, 52.0, 0.97,  9.5,  3.3,  9.0, 36.9, 44.2,  9.4, 14.3,  8.4, 1.3, 45.2,  64.5),
        ("Russell Westbrook",        "SAC", 53,  5.8, 33.0, 0.88,  5.1,  1.9,  6.1, 30.8, 36.4,  7.9, 15.9,  6.7, 1.2, 35.0,  34.6),
        ("Pascal Siakam",            "IND", 49,  7.2, 30.2, 0.90,  6.5,  2.4,  7.4, 32.4, 37.1,  7.8, 12.8,  6.3, 0.9, 40.0,  42.3),
        ("Julius Randle",            "MIN", 57,  7.3, 34.8, 0.88,  6.5,  2.4,  7.6, 31.7, 37.1,  7.5, 15.0,  6.9, 1.3, 37.7,  34.2),
        ("DeMar DeRozan",            "SAC", 58,  5.1, 31.4, 0.88,  4.5,  1.6,  5.0, 32.8, 34.0,  8.5, 13.4,  7.4, 1.0, 38.5,  36.4),
        ("Scoot Henderson",          "POR",  9,  9.6, 62.9, 0.85,  8.2,  2.8, 10.1, 27.5, 33.5,  9.6, 19.3,  8.4, 1.5, 37.2,  29.0),
        ("D'Angelo Russell",         "DAL", 25,  6.7, 64.8, 0.92,  6.2,  2.2,  6.9, 31.9, 38.0, 10.5, 14.1,  9.0, 2.0, 41.4,  48.1),
        ("Deni Avdija",              "POR", 45,  5.9, 24.6, 0.93,  5.5,  1.9,  5.9, 32.0, 38.3,  8.0, 14.0,  7.0, 1.2, 40.0,  53.3),
        ("Jalen Williams",           "OKC", 23,  9.9, 55.3, 0.87,  8.6,  3.0, 10.4, 28.8, 33.5,  8.2, 13.9,  6.9, 1.5, 37.5,  33.4),
        ("Giannis Antetokounmpo",    "MIL", 28,  9.3, 39.0, 0.88,  8.2,  3.1,  9.5, 32.7, 35.8, 10.4, 15.1,  9.2, 2.3, 38.6,  34.2),
        ("Kawhi Leonard",            "LAC", 42,  5.2, 21.2, 0.91,  4.8,  1.6,  5.2, 31.6, 36.3,  8.1, 16.5,  7.3, 1.0, 38.4,  43.0),
        ("Brandon Ingram",           "TOR", 55,  7.3, 34.4, 0.84,  6.1,  2.2,  7.7, 28.4, 33.1,  8.3, 15.9,  7.6, 1.5, 37.2,  25.4),
        ("Nikola Jokić",             "DEN", 42,  4.7, 19.2, 0.99,  4.7,  1.7,  4.7, 36.2, 40.2,  8.4, 11.7,  7.1, 1.8, 44.7,  67.3),
        ("Isaiah Collier",           "UTA", 50,  6.1, 51.0, 0.84,  5.2,  1.8,  6.5, 27.4, 33.0,  7.9, 18.4,  6.7, 1.2, 36.3,  25.5),
        ("Alperen Sengun",           "HOU", 49,  5.4, 24.5, 0.89,  4.8,  1.7,  5.6, 30.3, 35.0,  8.3, 15.0,  7.1, 1.3, 40.8,  38.8),
        ("Josh Giddey",              "CHI", 37,  6.9, 34.7, 0.85,  5.8,  1.9,  7.4, 25.6, 30.7,  9.1, 15.4,  8.2, 1.2, 36.5,  29.6),
        ("Austin Reaves",            "LAL", 29,  7.5, 35.4, 0.95,  7.1,  2.4,  7.6, 31.9, 37.0, 10.8, 12.4,  9.2, 2.3, 44.7,  61.2),
        ("Kyle Anderson",            "UTA", 20,  3.4, 45.7, 0.98,  3.4,  1.1,  3.7, 29.8, 35.5, 11.5, 14.6,  9.0, 2.0, 43.4,  65.7),
        ("Immanuel Quickley",        "TOR", 55,  6.7, 40.9, 0.87,  5.8,  2.0,  7.2, 27.5, 33.1, 10.0, 15.1,  8.7, 1.8, 38.2,  31.5),
        ("Malcolm Brogdon",          "POR", 40,  5.8, 38.4, 0.89,  5.2,  1.8,  5.9, 30.3, 36.0,  8.9, 13.4,  7.7, 1.5, 40.5,  38.3),
        ("Dennis Schröder",          "SAC", 39,  4.6, 33.3, 0.93,  4.3,  1.4,  4.7, 30.4, 37.2,  9.3, 16.1,  8.1, 1.4, 41.9,  52.8),
        ("Jordan Poole",             "NOP", 33,  5.8, 39.5, 0.84,  4.8,  1.7,  6.7, 25.7, 31.3,  7.4, 19.0,  5.9, 0.8, 35.9,  24.8),
        ("Bogdan Bogdanović",        "ATL", 52,  4.9, 30.7, 0.96,  4.7,  1.6,  5.2, 30.3, 38.9,  6.7, 13.8,  5.8, 1.2, 42.0,  62.2),
        ("Tyus Jones",               "PHX", 55,  5.7, 44.8, 0.86,  4.9,  1.7,  6.1, 27.9, 33.8,  8.2, 17.9,  7.4, 1.2, 38.3,  30.6),
        ("Mike Conley",              "MIN", 54,  4.3, 33.1, 0.94,  4.1,  1.4,  4.7, 29.8, 37.4,  8.2, 13.8,  7.1, 1.3, 42.5,  57.0),
        ("CJ McCollum",              "ATL", 21,  6.2, 32.9, 0.84,  5.2,  1.8,  6.9, 26.3, 32.3,  7.2, 16.6,  6.0, 0.9, 35.8,  24.5),
        ("Jrue Holiday",             "POR", 31,  6.1, 35.6, 0.83,  5.1,  1.7,  6.9, 24.5, 30.7,  8.4, 16.4,  7.5, 1.2, 36.6,  23.0),
        ("Chris Paul",               "GSW", 40,  3.5, 33.3, 0.97,  3.4,  1.1,  3.6, 31.2, 37.5, 10.2, 13.8,  8.9, 1.7, 44.2,  63.3),
        ("Andrew Nembhard",          "IND", 45,  5.4, 30.7, 0.85,  4.6,  1.6,  6.0, 26.4, 31.9,  8.3, 17.5,  7.2, 1.1, 37.1,  28.2),
        ("Keyonte George",           "UTA", 47,  5.4, 24.2, 0.88,  4.8,  1.7,  5.9, 28.5, 33.4,  8.5, 16.9,  7.5, 1.4, 38.4,  33.8),
        # --- next batch ---
        ("Dillon Brooks",            "PHX", 46,  3.8, 17.9, 0.95,  3.6,  1.3,  4.3, 29.5, 34.8,  9.0, 13.9,  7.8, 1.6, 41.5,  59.4),
        ("Anfernee Simons",          "BOS", 47,  5.7, 43.1, 0.87,  5.0,  1.7,  6.5, 26.7, 33.0,  7.9, 15.0,  7.0, 1.3, 38.1,  31.9),
        ("Coby White",               "CHI", 28,  6.3, 33.5, 0.85,  5.3,  1.8,  7.1, 25.0, 30.5,  8.2, 18.1,  7.0, 1.2, 36.9,  28.4),
        ("Desmond Bane",             "ORL", 53,  4.2, 22.8, 0.95,  4.0,  1.4,  4.7, 29.1, 36.7,  8.6, 14.1,  7.6, 1.5, 41.8,  60.5),
        ("T.J. McConnell",           "IND", 40,  5.3, 56.9, 0.84,  4.5,  1.5,  5.9, 25.8, 31.3,  8.2, 15.7,  6.9, 1.2, 36.8,  25.9),
        ("Ryan Rollins",             "MIL", 53,  3.5, 19.8, 0.92,  3.2,  1.1,  3.8, 29.3, 34.4,  9.3, 15.8,  8.2, 1.5, 40.8,  49.1),
        ("Scottie Barnes",           "TOR", 55,  6.2, 31.4, 0.84,  5.2,  1.8,  7.0, 25.5, 31.2,  8.0, 17.0,  7.1, 1.3, 36.9,  24.0),
        ("Jalen Suggs",              "ORL", 30,  4.5, 31.3, 0.89,  4.0,  1.4,  5.0, 28.0, 34.2,  9.2, 14.3,  8.1, 1.6, 41.7,  40.5),
        ("Tre Mann",                 "CHA", 37,  4.5, 55.4, 0.87,  3.9,  1.3,  5.0, 26.7, 32.7,  7.9, 17.1,  6.8, 1.1, 37.9,  31.5),
        ("Stephon Castle",           "SAS", 46,  5.4, 30.7, 0.83,  4.5,  1.5,  5.9, 25.6, 31.4,  9.0, 17.3,  7.9, 1.3, 36.9,  23.9),
        ("Marcus Smart",             "LAL", 46,  3.4, 33.3, 0.90,  3.1,  1.1,  3.7, 29.0, 35.0,  8.0, 16.4,  6.8, 1.2, 40.5,  42.8),
        ("Kobe Sanders",             "LAC", 45,  3.3, 39.6, 0.91,  3.0,  1.0,  3.4, 29.7, 35.8,  9.5, 14.5,  8.3, 1.7, 42.3,  46.0),
        ("Cooper Flagg",             "DAL", 45,  5.1, 25.1, 0.84,  4.3,  1.5,  5.8, 25.5, 31.1,  8.3, 15.8,  7.2, 1.2, 37.0,  26.0),
        ("Amen Thompson",            "HOU", 54,  4.1, 22.3, 0.86,  3.5,  1.2,  4.5, 27.0, 32.8,  7.8, 16.6,  7.0, 1.1, 37.5,  30.0),
        ("Jimmy Butler III",         "GSW", 35,  4.1, 24.1, 0.88,  3.6,  1.2,  4.2, 28.6, 34.3,  8.9, 13.4,  7.8, 1.7, 39.8,  35.0),
        ("Norman Powell",            "MIA", 45,  3.2, 15.7, 0.97,  3.1,  1.0,  3.4, 30.0, 36.2,  9.6, 13.1,  8.4, 1.8, 43.4,  63.8),
        ("Dennis Schröder",          "CLE", 10,  4.5, 35.6, 0.96,  4.3,  1.4,  4.5, 30.9, 37.4,  9.7, 14.8,  8.5, 1.6, 43.5,  62.2),
        ("Payton Pritchard",         "BOS", 56,  3.6, 22.2, 1.00,  3.6,  1.2,  3.5, 33.7, 40.2,  8.5, 13.8,  7.4, 1.4, 44.7,  70.7),
        ("Davion Mitchell",          "MIA", 46,  3.0, 31.5, 0.90,  2.7,  0.9,  3.3, 28.0, 34.3,  8.6, 16.0,  7.5, 1.2, 39.5,  42.4),
        ("Jaime Jaquez Jr.",         "MIA", 52,  3.3, 20.9, 0.87,  2.9,  1.0,  3.6, 27.7, 33.0,  8.0, 15.3,  7.0, 1.0, 38.0,  31.9),
        ("Derik Queen",              "NOP", 57,  3.0, 22.5, 0.89,  2.7,  0.9,  3.2, 27.5, 32.8,  7.7, 15.5,  6.5, 1.1, 38.1,  36.2),
        ("Andrew Wiggins",           "MIA", 52,  2.7, 17.5, 0.92,  2.5,  0.9,  2.9, 30.3, 36.0,  8.5, 13.9,  7.5, 1.3, 42.1,  48.4),
        ("Jaylen Wells",             "MEM", 54,  2.5, 18.9, 0.91,  2.3,  0.8,  2.7, 29.2, 35.6,  8.0, 14.3,  7.0, 1.2, 40.7,  44.3),
        # --- next batch ---
        ("Jaden McDaniels",          "MIN", 55,  2.2, 14.2, 0.94,  2.1,  0.7,  2.4, 30.0, 36.8,  8.7, 14.5,  7.6, 1.4, 42.9,  56.6),
        ("Franz Wagner",             "ORL", 25,  6.1, 30.5, 0.83,  5.0,  1.7,  6.5, 25.6, 31.0,  8.4, 15.5,  7.3, 1.2, 37.2,  23.5),
        ("Kentavious Caldwell-Pope", "MEM", 48,  2.1, 22.3, 0.92,  2.0,  0.7,  2.3, 30.5, 36.9,  8.0, 13.8,  6.9, 1.3, 40.8,  47.7),
        ("Jalen Green",              "PHX", 12,  4.4, 27.5, 0.84,  3.7,  1.3,  4.9, 26.1, 31.5,  8.8, 16.9,  7.6, 1.3, 37.5,  26.7),
        ("Dru Smith",                "MIA", 55,  2.0, 29.5, 0.96,  1.9,  0.6,  2.2, 29.5, 36.3,  9.1, 14.5,  8.1, 1.5, 42.5,  61.7),
        ("Tobias Harris",            "DET", 40,  2.3, 19.0, 0.89,  2.0,  0.7,  2.4, 30.0, 35.7,  7.7, 15.4,  6.7, 1.1, 39.1,  37.5),
        ("Jordan Clarkson",          "NYK", 49,  2.5, 31.6, 0.87,  2.2,  0.8,  2.7, 28.9, 34.5,  7.5, 16.2,  6.5, 0.9, 38.3,  32.0),
        ("Aaron Wiggins",            "OKC", 44,  2.0, 17.2, 0.95,  1.9,  0.6,  2.1, 30.0, 36.3,  8.6, 13.8,  7.7, 1.4, 42.6,  58.5),
        ("Jalen Pickett",            "DEN", 39,  2.9, 55.9, 0.87,  2.5,  0.9,  3.2, 27.8, 33.5,  8.1, 16.0,  6.9, 1.2, 37.7,  31.5),
        ("Caris LeVert",             "DET", 38,  2.5, 30.4, 0.89,  2.2,  0.8,  2.8, 27.7, 33.5,  7.9, 15.2,  7.0, 1.1, 39.6,  36.5),
        ("P.J. Washington",          "DAL", 39,  2.2, 14.3, 0.92,  2.0,  0.7,  2.3, 29.4, 35.9,  8.8, 14.7,  7.6, 1.3, 42.0,  48.1),
        ("Cam Thomas",               "BKN", 24,  5.0, 29.4, 0.84,  4.2,  1.4,  5.5, 25.4, 30.8,  8.8, 17.6,  7.7, 1.3, 37.7,  26.2),
        ("Josh Hart",                "NYK", 43,  2.8, 26.6, 0.88,  2.4,  0.9,  3.0, 29.0, 35.1,  7.8, 16.2,  6.8, 1.1, 38.7,  33.6),
        ("Zach LaVine",              "SAC", 36,  3.1, 18.6, 0.87,  2.7,  0.9,  3.3, 27.0, 32.5,  7.5, 15.9,  6.6, 0.9, 37.6,  31.1),
        ("Aaron Gordon",             "DEN", 22,  4.8, 30.7, 0.88,  4.2,  1.4,  5.0, 28.6, 33.9,  8.6, 15.1,  7.5, 1.4, 39.6,  34.6),
        ("Bones Hyland",             "MIN", 50,  2.3, 31.9, 0.89,  2.0,  0.7,  2.5, 28.5, 34.1,  8.0, 15.1,  7.0, 1.1, 39.7,  37.2),
        ("Pelle Larsson",            "MIA", 46,  1.9, 19.3, 0.93,  1.8,  0.6,  2.1, 29.9, 36.5,  8.3, 14.3,  7.2, 1.3, 42.1,  51.1),
        ("Jordan Miller",            "LAC", 36,  2.5, 29.3, 0.86,  2.2,  0.7,  2.7, 27.1, 32.9,  8.0, 16.8,  7.0, 1.1, 37.5,  29.6),
        ("Naji Marshall",            "DAL", 54,  1.8, 12.7, 0.97,  1.7,  0.6,  1.9, 31.7, 38.4,  9.4, 13.5,  8.3, 1.6, 43.8,  63.1),
        ("Kyle Kuzma",               "MIL", 52,  1.6, 12.3, 0.93,  1.5,  0.5,  1.8, 29.6, 36.2,  8.6, 15.2,  7.5, 1.3, 42.0,  51.3),
        # --- next batch ---
        ("Shaedon Sharpe",           "POR", 46,  2.4, 10.6, 0.92,  2.2,  0.7,  2.5, 29.5, 35.9,  8.3, 13.7,  7.3, 1.3, 41.8,  49.2),
        ("Nolan Traore",             "BKN", 37,  2.1, 21.2, 0.90,  1.9,  0.6,  2.2, 29.3, 35.6,  8.5, 15.9,  7.3, 1.2, 41.5,  43.8),
        ("Michael Porter Jr.",       "BKN", 45,  2.0,  8.7, 0.93,  1.9,  0.7,  2.0, 33.6, 40.8,  7.8, 12.7,  6.7, 1.3, 42.5,  52.2),
        ("Miles Bridges",            "CHA", 53,  2.1, 12.0, 0.90,  1.9,  0.6,  2.2, 29.6, 35.2,  8.6, 14.5,  7.5, 1.3, 40.5,  43.0),
        ("Nikola Vučević",           "BOS", 45,  1.7,  9.4, 0.95,  1.6,  0.6,  1.8, 32.5, 38.9,  8.0, 13.0,  7.0, 1.2, 42.7,  58.2),
        ("Brice Sensabaugh",         "UTA", 55,  1.8, 13.7, 0.92,  1.6,  0.6,  1.9, 30.5, 36.8,  8.4, 14.1,  7.3, 1.3, 41.5,  48.6),
        ("De'Anthony Melton",        "GSW", 32,  2.3, 16.4, 0.87,  2.0,  0.6,  2.5, 26.7, 32.2,  8.1, 17.3,  7.0, 1.1, 37.1,  31.1),
        ("Bilal Coulibaly",          "WAS", 36,  2.0, 17.6, 0.87,  1.8,  0.6,  2.1, 27.4, 33.5,  8.0, 16.6,  7.1, 1.1, 37.8,  30.9),
        ("Ty Jerome",                "MEM",  8,  4.9, 29.6, 0.98,  4.8,  1.5,  4.5, 33.6, 41.8,  9.3, 14.2,  8.3, 1.6, 43.5,  64.9),
        ("Ousmane Dieng",            "OKC", 25,  2.3, 60.1, 0.88,  2.0,  0.7,  2.5, 27.2, 33.0,  8.3, 15.4,  7.2, 1.2, 38.4,  34.3),
        ("Quentin Grimes",           "PHI", 50,  2.1, 16.9, 0.88,  1.9,  0.6,  2.2, 27.8, 33.4,  8.3, 15.7,  7.2, 1.2, 38.5,  33.5),
        ("Rob Dillingham",           "MIN", 32,  3.2, 62.1, 0.84,  2.7,  0.9,  3.6, 24.7, 30.1,  8.8, 18.2,  7.6, 1.3, 36.9,  24.5),
        ("OG Anunoby",               "NYK", 43,  1.8, 10.9, 0.93,  1.7,  0.6,  1.9, 30.5, 37.1,  8.5, 14.9,  7.5, 1.3, 42.3,  52.4),
        ("Myles Turner",             "MIL", 51,  1.5,  9.7, 0.96,  1.4,  0.5,  1.7, 30.8, 38.3,  8.6, 13.9,  7.6, 1.4, 43.2,  61.0),
        ("Mikal Bridges",            "NYK", 55,  1.4,  9.5, 0.94,  1.3,  0.5,  1.5, 31.0, 38.2,  8.7, 14.4,  7.6, 1.3, 42.9,  56.8),
        ("Kevin Porter Jr.",         "MIL", 33,  2.8, 15.2, 0.84,  2.3,  0.8,  3.1, 25.9, 31.6,  8.2, 17.5,  7.2, 1.2, 37.3,  24.9),
        ("Collin Sexton",            "CHA", 39,  2.2, 17.0, 0.91,  2.0,  0.7,  2.4, 28.6, 34.7,  8.7, 13.6,  7.6, 1.4, 41.5,  45.5),
        ("Lauri Markkanen",          "UTA", 40,  1.6,  6.5, 0.96,  1.5,  0.5,  1.7, 31.0, 38.3,  8.5, 13.4,  7.5, 1.3, 43.0,  61.2),
        ("Derrick White",            "BOS", 55,  1.9, 10.6, 0.90,  1.7,  0.6,  2.0, 29.8, 35.9,  8.2, 14.7,  7.1, 1.2, 40.7,  42.5),
        ("Victor Wembanyama",        "SAS", 43,  3.2, 14.9, 0.83,  2.7,  0.9,  3.3, 26.0, 31.8,  8.4, 17.2,  7.3, 1.2, 37.3,  22.8),
        # --- next batch ---
        ("Jeremiah Fears",           "NOP", 58,  2.1, 13.5, 0.85,  1.8,  0.6,  2.3, 25.9, 31.8,  8.2, 17.8,  7.0, 1.1, 36.9,  27.5),
        ("Jamal Shead",              "TOR", 57,  2.0, 24.3, 0.87,  1.8,  0.6,  2.2, 27.3, 33.1,  8.3, 16.6,  7.2, 1.1, 38.2,  31.7),
        ("Devin Carter",             "SAC", 23,  2.5, 32.5, 0.84,  2.1,  0.7,  2.8, 24.5, 30.5,  8.6, 18.4,  7.4, 1.2, 36.5,  24.2),
        ("VJ Edgecombe",             "PHI", 54,  2.3, 14.7, 0.87,  2.0,  0.7,  2.5, 27.0, 32.8,  8.0, 16.0,  7.0, 1.1, 38.1,  31.3),
        ("Dylan Harper",             "SAS", 44,  2.6, 23.4, 0.84,  2.2,  0.7,  2.9, 24.7, 30.5,  8.9, 17.7,  7.7, 1.2, 37.0,  24.4),
        ("Reed Sheppard",            "HOU", 56,  1.8, 13.5, 0.90,  1.6,  0.5,  1.9, 28.6, 34.9,  8.4, 14.7,  7.4, 1.2, 41.6,  43.2),
        ("Ace Bailey",               "UTA", 51,  2.0, 16.7, 0.86,  1.7,  0.6,  2.2, 26.9, 32.7,  8.1, 16.8,  7.0, 1.1, 37.5,  29.3),
        ("Bub Carrington",           "WAS", 55,  1.9, 15.2, 0.88,  1.7,  0.6,  2.1, 27.8, 33.7,  8.2, 15.7,  7.0, 1.1, 38.7,  33.3),
        ("Jaden Ivey",               "DET", 31,  2.8, 30.7, 0.84,  2.3,  0.8,  3.0, 25.9, 31.5,  9.0, 18.0,  7.8, 1.3, 36.8,  24.2),
        ("Caleb Love",               "POR", 42,  2.0, 15.7, 0.87,  1.7,  0.6,  2.2, 27.6, 33.3,  8.2, 15.6,  7.1, 1.1, 38.4,  31.1),
        ("Tremont Waters",           "PHI", 30,  1.6, 36.6, 0.91,  1.5,  0.5,  1.7, 29.6, 35.9,  8.7, 13.7,  7.6, 1.3, 41.9,  45.1),
        ("Tre Johnson",              "WAS", 44,  2.1, 17.0, 0.85,  1.8,  0.6,  2.3, 25.7, 31.5,  8.6, 17.6,  7.4, 1.2, 36.9,  28.1),
        ("Cason Wallace",            "OKC", 53,  1.7, 19.8, 0.90,  1.5,  0.5,  1.8, 28.8, 34.9,  8.4, 14.9,  7.3, 1.2, 41.3,  43.0),
        ("Daniss Jenkins",           "DET", 46,  1.8, 19.1, 0.88,  1.6,  0.5,  1.9, 27.8, 33.8,  8.0, 15.4,  7.0, 1.1, 39.5,  34.2),
        ("Ajay Mitchell",            "OKC", 38,  1.8, 12.2, 0.90,  1.6,  0.5,  1.9, 27.9, 33.5,  8.5, 15.3,  7.3, 1.2, 41.1,  43.0),
        ("Will Riley",               "WAS", 47,  1.7, 19.3, 0.89,  1.5,  0.5,  1.8, 27.5, 33.1,  8.4, 15.5,  7.2, 1.2, 40.3,  38.5),
        ("Max Christie",             "DAL", 50,  1.6, 14.4, 0.91,  1.5,  0.5,  1.7, 28.8, 34.8,  8.5, 14.8,  7.4, 1.3, 41.6,  45.0),
        ("Saddiq Bey",               "NOP", 51,  1.5, 10.0, 0.90,  1.4,  0.5,  1.6, 28.1, 34.3,  8.3, 15.3,  7.2, 1.2, 40.7,  43.1),
        ("Gradey Dick",              "TOR", 55,  1.5, 12.3, 0.91,  1.3,  0.5,  1.6, 28.7, 35.0,  8.1, 14.6,  7.0, 1.2, 41.2,  44.9),
        ("Ryan Nembhard",            "DAL", 36,  1.7, 19.7, 0.89,  1.5,  0.5,  1.8, 27.9, 33.6,  8.4, 15.6,  7.2, 1.2, 40.4,  38.8),
        ("Jonathan Kuminga",         "GSW", 20,  3.0, 21.9, 0.83,  2.5,  0.8,  3.2, 25.0, 30.5,  8.5, 18.3,  7.3, 1.2, 36.5,  23.5),
    ]

    stats: List[OffensivePnrBallHandlerStats] = []
    for row in raw:
        (player, team, gp, poss, freq_pct, ppp, pts, fgm, fga,
         fg_pct, efg_pct, ft_freq_pct, tov_freq_pct,
         sf_freq_pct, and_one_freq_pct, score_freq_pct, percentile) = row
        stats.append(OffensivePnrBallHandlerStats(
            player=player,
            team=team,
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
        ))
    return stats


def rank_players_by_offensive_pnr_ball_handler(
    stats: Optional[List["OffensivePnrBallHandlerStats"]] = None,
) -> List["OffensivePnrBallHandlerStats"]:
    """
    Return all players sorted from best to worst PnR ball handler
    (highest percentile first).

    If *stats* is not provided, the full dataset is used.
    """
    if stats is None:
        stats = build_offensive_pnr_ball_handler_stats()
    return sorted(stats, key=lambda s: s.percentile, reverse=True)


def find_pnr_ball_handler_scorers(
    pnr_stats: Optional[List["OffensivePnrBallHandlerStats"]] = None,
    opponent_team: Optional[str] = None,
    pnr_defensive_rankings: Optional[Dict[str, "DefensivePnrBallHandlerStats"]] = None,
    min_freq_pct: float = 20.0,
    min_ppp: float = 0.90,
) -> List[Dict]:
    """
    Identify players who are high-volume, efficient PnR ball handlers.

    When *opponent_team* and *pnr_defensive_rankings* are provided the
    results are further annotated with the opponent's defensive PPP and
    percentile.

    Returns a list of dicts sorted by PnR ball handler frequency %
    (highest first), each containing:
      - "player"        : player name
      - "team"          : player's team
      - "freq_pct"      : PnR ball handler frequency %
      - "ppp"           : player's PnR ball handler PPP
      - "pts"           : PnR ball handler points per game
      - "percentile"    : player's offensive PnR ball handler percentile
      - "def_ppp"       : opponent's PnR ball handler defensive PPP (if supplied)
      - "def_percentile": opponent's PnR ball handler defensive percentile (if supplied)
    """
    if pnr_stats is None:
        pnr_stats = build_offensive_pnr_ball_handler_stats()

    def_stats = None
    if opponent_team and pnr_defensive_rankings:
        def_stats = pnr_defensive_rankings.get(opponent_team)

    results = []
    for s in pnr_stats:
        if s.freq_pct < min_freq_pct:
            continue
        if s.ppp < min_ppp:
            continue
        entry: Dict = {
            "player":         s.player,
            "team":           s.team,
            "freq_pct":       s.freq_pct,
            "ppp":            s.ppp,
            "pts":            s.pts,
            "percentile":     s.percentile,
            "def_ppp":        def_stats.ppp if def_stats else None,
            "def_percentile": def_stats.percentile if def_stats else None,
        }
        results.append(entry)

    results.sort(key=lambda r: r["freq_pct"], reverse=True)
    return results


def predict_pnr_ball_handler_matchup(
    player_name: str,
    opponent_team: str,
    offensive_stats: Optional[List["OffensivePnrBallHandlerStats"]] = None,
    defensive_rankings: Optional[Dict[str, "DefensivePnrBallHandlerStats"]] = None,
) -> Optional[Dict]:
    """
    Return a head-to-head PnR ball handler matchup prediction for
    *player_name* against *opponent_team*'s PnR ball handler defense.

    Parameters
    ----------
    player_name:
        Exact player name (case-insensitive) as it appears in the offensive
        PnR ball handler dataset (e.g. ``"Luka Dončić"``).
    opponent_team:
        Three-letter team abbreviation for the defending team (e.g. ``"SAS"``).
    offensive_stats:
        Pre-built offensive stats list; defaults to the full dataset.
    defensive_rankings:
        Pre-built ``{team: DefensivePnrBallHandlerStats}`` mapping; defaults
        to the full 30-team dataset.

    Returns
    -------
    dict or None
        ``None`` when the player or team cannot be found.  Otherwise a dict
        containing:

        - ``"player"``         : player name
        - ``"team"``           : player's team abbreviation
        - ``"gp"``             : games played
        - ``"freq_pct"``       : player's PnR ball handler frequency %
        - ``"ppp"``            : player's PnR ball handler PPP
        - ``"pts"``            : player's PnR ball handler points per game
        - ``"off_percentile"`` : player's offensive PnR ball handler percentile
        - ``"opponent"``       : opponent team abbreviation
        - ``"def_ppp"``        : opponent's PnR ball handler PPP allowed
        - ``"def_freq_pct"``   : opponent's PnR ball handler frequency allowed %
        - ``"def_percentile"`` : opponent's PnR ball handler defensive percentile
        - ``"edge"``           : player PPP − opponent defensive PPP
        - ``"verdict"``        : ``"FAVORABLE"``, ``"NEUTRAL"``, or ``"TOUGH"``
    """
    if offensive_stats is None:
        offensive_stats = build_offensive_pnr_ball_handler_stats()
    if defensive_rankings is None:
        defensive_rankings = build_pnr_ball_handler_defensive_rankings()

    player_stat = next(
        (s for s in offensive_stats if s.player.lower() == player_name.lower()),
        None,
    )
    if player_stat is None:
        return None

    def_stat = defensive_rankings.get(opponent_team.upper())
    if def_stat is None:
        return None

    edge = round(player_stat.ppp - def_stat.ppp, 3)
    if edge >= 0.10:
        verdict = "FAVORABLE"
    elif edge <= -0.10:
        verdict = "TOUGH"
    else:
        verdict = "NEUTRAL"

    return {
        "player":         player_stat.player,
        "team":           player_stat.team,
        "gp":             player_stat.gp,
        "freq_pct":       player_stat.freq_pct,
        "ppp":            player_stat.ppp,
        "pts":            player_stat.pts,
        "off_percentile": player_stat.percentile,
        "opponent":       def_stat.team,
        "def_ppp":        def_stat.ppp,
        "def_freq_pct":   def_stat.freq_pct,
        "def_percentile": def_stat.percentile,
        "edge":           edge,
        "verdict":        verdict,
    }


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


def _print_transition_matchups(
    matchups: List[Dict],
    title: str = "Top Offensive Transition Matchups vs Weak Transition Defenses",
) -> None:
    """Pretty-print the results of :func:`match_all_transition_matchups`."""
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")
    print(
        f"  {'#':>3}  {'Player':<25} {'Tm':<4}  {'Off%':>5}  {'PPP':>5}"
        f"  {'vs':<4}  {'DefPPP':>6}  {'Def%':>5}  {'Edge':>6}"
    )
    print(f"  {'-' * 68}")
    for i, m in enumerate(matchups, 1):
        print(
            f"  {i:>3}. {m['player']:<25} {m['team']:<4}  "
            f"{m['off_percentile']:>5.1f}  {m['ppp']:>5.2f}  "
            f"{m['opponent']:<4}  {m['def_ppp']:>6.2f}  "
            f"{m['def_percentile']:>5.1f}  {m['edge']:>+6.3f}"
        )
    print(f"{'=' * 72}\n")


def _print_transition_matchup_prediction(prediction: Optional[Dict]) -> None:
    """Pretty-print the result of :func:`predict_transition_matchup`."""
    if prediction is None:
        print("\n[predict_transition_matchup] Player or team not found.\n")
        return
    p = prediction
    print(f"\n{'=' * 60}")
    print(f"  Transition Matchup Prediction")
    print(f"{'=' * 60}")
    print(f"  Player  : {p['player']} ({p['team']})  —  {p['gp']} GP")
    print(f"  Opponent: {p['opponent']} transition defense")
    print(f"")
    print(f"  Offensive Transition (player)")
    print(f"    Frequency  : {p['freq_pct']:.1f}%")
    print(f"    PPP        : {p['ppp']:.2f}")
    print(f"    Pts/game   : {p['pts']:.1f}")
    print(f"    Percentile : {p['off_percentile']:.1f}")
    print(f"")
    print(f"  Defensive Transition ({p['opponent']})")
    print(f"    Freq allowed: {p['def_freq_pct']:.1f}%")
    print(f"    PPP allowed : {p['def_ppp']:.2f}")
    print(f"    Percentile  : {p['def_percentile']:.1f}  (higher = stronger defense)")
    print(f"")
    print(f"  Edge (player PPP − def PPP): {p['edge']:+.3f}")
    print(f"  Verdict: {p['verdict']}")
    print(f"{'=' * 60}\n")


def _print_isolation_matchups(
    matchups: List[Dict],
    title: str = "Top Offensive Isolation Matchups vs Weak Isolation Defenses",
) -> None:
    """Pretty-print the results of :func:`match_all_isolation_matchups`."""
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")
    print(
        f"  {'#':>3}  {'Player':<28} {'Tm':<4}  {'Off%':>5}  {'PPP':>5}"
        f"  {'vs':<4}  {'DefPPP':>6}  {'Def%':>5}  {'Edge':>6}"
    )
    print(f"  {'-' * 68}")
    for i, m in enumerate(matchups, 1):
        print(
            f"  {i:>3}. {m['player']:<28} {m['team']:<4}  "
            f"{m['off_percentile']:>5.1f}  {m['ppp']:>5.2f}  "
            f"{m['opponent']:<4}  {m['def_ppp']:>6.2f}  "
            f"{m['def_percentile']:>5.1f}  {m['edge']:>+6.3f}"
        )
    print(f"{'=' * 72}\n")


def _print_isolation_matchup_prediction(prediction: Optional[Dict]) -> None:
    """Pretty-print the result of :func:`predict_isolation_matchup`."""
    if prediction is None:
        print("\n[predict_isolation_matchup] Player or team not found.\n")
        return
    p = prediction
    print(f"\n{'=' * 60}")
    print(f"  Isolation Matchup Prediction")
    print(f"{'=' * 60}")
    print(f"  Player  : {p['player']} ({p['team']})  —  {p['gp']} GP")
    print(f"  Opponent: {p['opponent']} isolation defense")
    print(f"")
    print(f"  Offensive Isolation (player)")
    print(f"    Frequency  : {p['freq_pct']:.1f}%")
    print(f"    PPP        : {p['ppp']:.2f}")
    print(f"    Pts/game   : {p['pts']:.1f}")
    print(f"    Percentile : {p['off_percentile']:.1f}")
    print(f"")
    print(f"  Defensive Isolation ({p['opponent']})")
    print(f"    Freq allowed: {p['def_freq_pct']:.1f}%")
    print(f"    PPP allowed : {p['def_ppp']:.2f}")
    print(f"    Percentile  : {p['def_percentile']:.1f}  (higher = stronger defense)")
    print(f"")
    print(f"  Edge (player PPP − def PPP): {p['edge']:+.3f}")
    print(f"  Verdict: {p['verdict']}")
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

    # Example 4: Josh Hart vs San Antonio (mid-tier defense vs cut & putback)
    hart = next(p for p in players if p.name == "Josh Hart")
    result = analyze_matchup(hart, defense_map["SAS"], players)
    _print_analysis(result)

    # Transition matchups: top offensive players vs weak transition defenses
    matchups = match_all_transition_matchups(top_n=25, max_def_percentile=40.0)
    _print_transition_matchups(matchups)

    # Targeted prediction: Josh Hart (NYK) offensive transition vs SAS defense
    hart_sas = predict_transition_matchup("Josh Hart", "SAS")
    _print_transition_matchup_prediction(hart_sas)

    # Isolation matchups: top offensive iso players vs weak isolation defenses
    iso_matchups = match_all_isolation_matchups(top_n=25, max_def_percentile=40.0)
    _print_isolation_matchups(iso_matchups)

    # Targeted isolation predictions: SGA vs SAS, Harden vs SAS
    sga_sas = predict_isolation_matchup("Shai Gilgeous-Alexander", "SAS")
    _print_isolation_matchup_prediction(sga_sas)

    harden_sas = predict_isolation_matchup("James Harden", "SAS")
    _print_isolation_matchup_prediction(harden_sas)


if __name__ == "__main__":
    main()
