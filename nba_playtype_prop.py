"""
NBA Playtype Player Prop Estimator
===================================
Estimates player prop lines (points, assists, rebounds) based on:
  - The offensive player's play-type distribution and per-play efficiency
  - The defensive matchup's play-type defensive ratings
  - Similarity to other players of the same position and play-type profile

Play types follow the Synergy/NBA Second Spectrum taxonomy:
  ISOLATION, PICK_AND_ROLL_BALL_HANDLER, PICK_AND_ROLL_ROLL_MAN,
  POST_UP, SPOT_UP, HAND_OFF, CUT, OFF_SCREEN, PUTBACK, TRANSITION
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Position(str, Enum):
    POINT_GUARD = "PG"
    SHOOTING_GUARD = "SG"
    SMALL_FORWARD = "SF"
    POWER_FORWARD = "PF"
    CENTER = "C"


class PlayType(str, Enum):
    ISOLATION = "isolation"
    PICK_AND_ROLL_BALL_HANDLER = "pick_and_roll_ball_handler"
    PICK_AND_ROLL_ROLL_MAN = "pick_and_roll_roll_man"
    POST_UP = "post_up"
    SPOT_UP = "spot_up"
    HAND_OFF = "hand_off"
    CUT = "cut"
    OFF_SCREEN = "off_screen"
    PUTBACK = "putback"
    TRANSITION = "transition"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class PlayTypeStats:
    """Per-play-type offensive statistics for a single player."""
    play_type: PlayType
    frequency: float          # fraction of total possessions for this play type (0-1)
    points_per_play: float    # average points scored on this play type
    assist_chance: float      # probability of an assist being generated (0-1)
    rebound_chance: float     # probability of an offensive rebound being generated (0-1)

    def __post_init__(self) -> None:
        if not 0.0 <= self.frequency <= 1.0:
            raise ValueError(f"frequency must be in [0, 1], got {self.frequency}")
        if not 0.0 <= self.assist_chance <= 1.0:
            raise ValueError(f"assist_chance must be in [0, 1], got {self.assist_chance}")
        if not 0.0 <= self.rebound_chance <= 1.0:
            raise ValueError(f"rebound_chance must be in [0, 1], got {self.rebound_chance}")


@dataclass
class DefensiveMatchupProfile:
    """
    How a specific defender (or a team's defensive scheme) rates against
    each play type.  Values represent the *opponent points-per-play allowed*
    relative to league average (1.0 = league average).
    Values > 1.0 mean the defender allows more than average (bad defense),
    values < 1.0 mean better-than-average defense.
    """
    defender_name: str
    defender_position: Position
    play_type_ratings: Dict[PlayType, float] = field(default_factory=dict)

    def rating_for(self, play_type: PlayType) -> float:
        """Return the defensive rating multiplier for a given play type.
        Defaults to 1.0 (league average) if no data available.
        """
        return self.play_type_ratings.get(play_type, 1.0)


@dataclass
class PlayerProfile:
    """Offensive player profile used to generate prop estimates."""
    name: str
    position: Position
    team: str
    possessions_per_game: float          # total offensive possessions per game
    play_type_stats: List[PlayTypeStats] = field(default_factory=list)

    def __post_init__(self) -> None:
        total_freq = sum(s.frequency for s in self.play_type_stats)
        if self.play_type_stats and not (0.999 <= total_freq <= 1.001):
            raise ValueError(
                f"play_type_stats frequencies must sum to 1.0, got {total_freq:.4f}"
            )


# ---------------------------------------------------------------------------
# Similarity engine
# ---------------------------------------------------------------------------

def _euclidean_distance(a: Dict[PlayType, float], b: Dict[PlayType, float]) -> float:
    """Compute Euclidean distance between two play-type frequency vectors."""
    play_types = list(PlayType)
    dist_sq = sum((a.get(pt, 0.0) - b.get(pt, 0.0)) ** 2 for pt in play_types)
    return dist_sq ** 0.5


def find_similar_players(
    target: PlayerProfile,
    player_pool: List[PlayerProfile],
    top_n: int = 5,
    same_position_only: bool = True,
) -> List[PlayerProfile]:
    """
    Return the *top_n* most similar players to *target* from *player_pool*,
    ranked by Euclidean distance in play-type frequency space.

    Parameters
    ----------
    target:
        The offensive player whose prop we are estimating.
    player_pool:
        A list of players to compare against.
    top_n:
        Number of similar players to return.
    same_position_only:
        If True (default) only consider players who share the same position
        as *target*.
    """
    target_freq: Dict[PlayType, float] = {
        s.play_type: s.frequency for s in target.play_type_stats
    }

    candidates = [
        p for p in player_pool
        if p.name != target.name
        and (not same_position_only or p.position == target.position)
    ]

    ranked = sorted(
        candidates,
        key=lambda p: _euclidean_distance(
            target_freq,
            {s.play_type: s.frequency for s in p.play_type_stats},
        ),
    )
    return ranked[:top_n]


# ---------------------------------------------------------------------------
# Prop estimation
# ---------------------------------------------------------------------------

@dataclass
class PropEstimate:
    """Estimated stat lines for a player against a specific matchup."""
    player_name: str
    defender_name: str
    projected_points: float
    projected_assists: float
    projected_rebounds: float
    play_type_breakdown: Dict[str, float] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [
            f"=== Prop Estimate: {self.player_name} vs {self.defender_name} ===",
            f"  Projected Points  : {self.projected_points:.1f}",
            f"  Projected Assists : {self.projected_assists:.1f}",
            f"  Projected Rebounds: {self.projected_rebounds:.1f}",
            "  Play-Type Point Breakdown:",
        ]
        for pt, pts in sorted(self.play_type_breakdown.items(), key=lambda x: -x[1]):
            lines.append(f"    {pt:<35} {pts:.2f} pts")
        return "\n".join(lines)


def estimate_props(
    player: PlayerProfile,
    matchup: DefensiveMatchupProfile,
    league_avg_points_per_play: float = 1.0,
) -> PropEstimate:
    """
    Estimate a player's stat line given their play-type profile and the
    defender's play-type defensive ratings.

    The model multiplies the player's expected points on each play type by the
    defender's relative rating for that play type, then sums across all play
    types weighted by frequency and possessions per game.

    Parameters
    ----------
    player:
        Offensive player profile.
    matchup:
        Defensive matchup profile for the primary defender.
    league_avg_points_per_play:
        Baseline reference value (default 1.0 PPP).

    Returns
    -------
    PropEstimate with projected points, assists, and rebounds.
    """
    projected_points = 0.0
    projected_assists = 0.0
    projected_rebounds = 0.0
    breakdown: Dict[str, float] = {}

    for stat in player.play_type_stats:
        possessions_on_this_type = player.possessions_per_game * stat.frequency
        def_multiplier = matchup.rating_for(stat.play_type)

        # Adjust expected scoring by the defender's relative difficulty
        adjusted_ppp = stat.points_per_play * def_multiplier / league_avg_points_per_play

        pts = possessions_on_this_type * adjusted_ppp
        ast = possessions_on_this_type * stat.assist_chance
        reb = possessions_on_this_type * stat.rebound_chance

        projected_points += pts
        projected_assists += ast
        projected_rebounds += reb
        breakdown[stat.play_type.value] = round(pts, 3)

    return PropEstimate(
        player_name=player.name,
        defender_name=matchup.defender_name,
        projected_points=round(projected_points, 1),
        projected_assists=round(projected_assists, 1),
        projected_rebounds=round(projected_rebounds, 1),
        play_type_breakdown=breakdown,
    )


def estimate_props_with_similarity(
    player: PlayerProfile,
    matchup: DefensiveMatchupProfile,
    player_pool: List[PlayerProfile],
    top_n: int = 5,
    similarity_weight: float = 0.25,
    league_avg_points_per_play: float = 1.0,
) -> PropEstimate:
    """
    Blend the player's own prop estimate with an average from the most similar
    players (by play-type profile and position) to reduce noise.

    Parameters
    ----------
    player:
        Offensive player profile.
    matchup:
        Defensive matchup profile.
    player_pool:
        Reference pool of players for similarity lookup.
    top_n:
        Number of similar players to include in the blend.
    similarity_weight:
        Weight given to similar-player average (0 = ignore, 1 = use only peers).
    league_avg_points_per_play:
        Baseline reference value.

    Returns
    -------
    PropEstimate blended from the player's own projection and peer averages.
    """
    own_estimate = estimate_props(player, matchup, league_avg_points_per_play)

    similar_players = find_similar_players(player, player_pool, top_n=top_n)
    if not similar_players:
        return own_estimate

    peer_estimates = [
        estimate_props(p, matchup, league_avg_points_per_play)
        for p in similar_players
    ]
    avg_peer_pts = sum(e.projected_points for e in peer_estimates) / len(peer_estimates)
    avg_peer_ast = sum(e.projected_assists for e in peer_estimates) / len(peer_estimates)
    avg_peer_reb = sum(e.projected_rebounds for e in peer_estimates) / len(peer_estimates)

    w_own = 1.0 - similarity_weight
    blended_pts = round(w_own * own_estimate.projected_points + similarity_weight * avg_peer_pts, 1)
    blended_ast = round(w_own * own_estimate.projected_assists + similarity_weight * avg_peer_ast, 1)
    blended_reb = round(w_own * own_estimate.projected_rebounds + similarity_weight * avg_peer_reb, 1)

    return PropEstimate(
        player_name=player.name,
        defender_name=matchup.defender_name,
        projected_points=blended_pts,
        projected_assists=blended_ast,
        projected_rebounds=blended_reb,
        play_type_breakdown=own_estimate.play_type_breakdown,
    )


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

def _demo() -> None:
    """Simple demonstration of the prop estimator."""

    # -- Offensive player ------------------------------------------------
    player = PlayerProfile(
        name="Demo Guard",
        position=Position.POINT_GUARD,
        team="Team A",
        possessions_per_game=18.0,
        play_type_stats=[
            PlayTypeStats(PlayType.PICK_AND_ROLL_BALL_HANDLER, 0.35, 1.05, 0.35, 0.05),
            PlayTypeStats(PlayType.ISOLATION,                   0.20, 0.95, 0.10, 0.08),
            PlayTypeStats(PlayType.TRANSITION,                  0.15, 1.20, 0.20, 0.06),
            PlayTypeStats(PlayType.SPOT_UP,                     0.15, 1.10, 0.05, 0.10),
            PlayTypeStats(PlayType.HAND_OFF,                    0.08, 0.90, 0.25, 0.04),
            PlayTypeStats(PlayType.CUT,                         0.07, 1.30, 0.02, 0.12),
        ],
    )

    # -- Defensive matchup -----------------------------------------------
    matchup = DefensiveMatchupProfile(
        defender_name="Lockdown Defender",
        defender_position=Position.POINT_GUARD,
        play_type_ratings={
            PlayType.PICK_AND_ROLL_BALL_HANDLER: 0.88,  # very good PnR defense
            PlayType.ISOLATION:                  0.92,  # good iso defense
            PlayType.TRANSITION:                 1.05,  # slightly below avg in transition
            PlayType.SPOT_UP:                    0.95,
            PlayType.HAND_OFF:                   1.00,
            PlayType.CUT:                        1.02,
        },
    )

    estimate = estimate_props(player, matchup)
    print(estimate)


if __name__ == "__main__":
    _demo()
