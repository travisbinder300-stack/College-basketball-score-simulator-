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
