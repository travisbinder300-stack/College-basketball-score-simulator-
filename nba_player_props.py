"""
nba_player_props.py
-------------------
NBA Player Prop Projection Engine.

Calculates projected stat lines and suggested prop values for each player
based on season averages, recent form, and home/away context.

Supported prop categories
--------------------------
  - Points
  - Rebounds
  - Assists
  - Steals
  - Blocks
  - 3-Pointers Made
  - Points + Rebounds + Assists (PRA)
  - Steals + Blocks (S+B)
  - Turnovers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Player:
    """Represents an NBA player and their season statistics."""

    name: str
    team: str
    position: str

    games_played: int
    minutes_per_game: float
    points_per_game: float
    rebounds_per_game: float
    assists_per_game: float
    steals_per_game: float
    blocks_per_game: float
    three_pointers_per_game: float
    field_goal_pct: float
    three_point_pct: float
    free_throw_pct: float
    turnovers_per_game: float = 0.0

    # Optional context for refined projections
    home_points_per_game: Optional[float] = None
    away_points_per_game: Optional[float] = None
    last_5_points: List[float] = field(default_factory=list)
    last_5_rebounds: List[float] = field(default_factory=list)
    last_5_assists: List[float] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create a Player from a dictionary (as stored in players.py)."""
        return cls(
            name=data["name"],
            team=data["team"],
            position=data["position"],
            games_played=data["games_played"],
            minutes_per_game=data["minutes_per_game"],
            points_per_game=data["points_per_game"],
            rebounds_per_game=data["rebounds_per_game"],
            assists_per_game=data["assists_per_game"],
            steals_per_game=data["steals_per_game"],
            blocks_per_game=data["blocks_per_game"],
            three_pointers_per_game=data["three_pointers_per_game"],
            field_goal_pct=data["field_goal_pct"],
            three_point_pct=data["three_point_pct"],
            free_throw_pct=data["free_throw_pct"],
            turnovers_per_game=data.get("turnovers_per_game", 0.0),
            home_points_per_game=data.get("home_points_per_game"),
            away_points_per_game=data.get("away_points_per_game"),
            last_5_points=data.get("last_5_points", []),
            last_5_rebounds=data.get("last_5_rebounds", []),
            last_5_assists=data.get("last_5_assists", []),
        )


# ---------------------------------------------------------------------------
# Projection engine
# ---------------------------------------------------------------------------

class PropProjection:
    """
    Calculates prop projections for a single player.

    The projection blends:
      - Season average (baseline weight)
      - Recent form — last-5-game average (recency weight, if data available)
      - Home/away split adjustment (if data available)
    """

    # Blending weights
    SEASON_WEIGHT = 0.70
    RECENT_WEIGHT = 0.30

    def __init__(self, player: Player, is_home: bool = True):
        self.player = player
        self.is_home = is_home
        self._projections: Dict[str, float] = {}
        self._calculate()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _recent_avg(values: List[float]) -> Optional[float]:
        """Return the mean of a list, or None if the list is empty."""
        if not values:
            return None
        return sum(values) / len(values)

    def _blend(self, season_avg: float, recent_avg: Optional[float]) -> float:
        """Blend season average with recent form."""
        if recent_avg is None:
            return season_avg
        return round(
            self.SEASON_WEIGHT * season_avg + self.RECENT_WEIGHT * recent_avg, 2
        )

    def _home_away_points(self) -> float:
        """Return the points average appropriate for home/away context."""
        p = self.player
        if self.is_home and p.home_points_per_game is not None:
            return p.home_points_per_game
        if not self.is_home and p.away_points_per_game is not None:
            return p.away_points_per_game
        return p.points_per_game

    # ------------------------------------------------------------------
    # Projection calculations
    # ------------------------------------------------------------------

    def _calculate(self) -> None:
        p = self.player

        # Points — use home/away split as the season baseline when available
        pts_base = self._home_away_points()
        pts_recent = self._recent_avg(p.last_5_points)
        self._projections["points"] = self._blend(pts_base, pts_recent)

        # Rebounds
        reb_recent = self._recent_avg(p.last_5_rebounds)
        self._projections["rebounds"] = self._blend(p.rebounds_per_game, reb_recent)

        # Assists
        ast_recent = self._recent_avg(p.last_5_assists)
        self._projections["assists"] = self._blend(p.assists_per_game, ast_recent)

        # Steals, blocks, 3PM, turnovers — season average only (no L5 data collected)
        self._projections["steals"] = round(p.steals_per_game, 2)
        self._projections["blocks"] = round(p.blocks_per_game, 2)
        self._projections["three_pointers"] = round(p.three_pointers_per_game, 2)
        self._projections["turnovers"] = round(p.turnovers_per_game, 2)

        # Combo props
        self._projections["pra"] = round(
            self._projections["points"]
            + self._projections["rebounds"]
            + self._projections["assists"],
            2,
        )
        self._projections["steals_blocks"] = round(
            self._projections["steals"] + self._projections["blocks"], 2
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get(self, prop: str) -> Optional[float]:
        """Return the projected value for a given prop category."""
        return self._projections.get(prop)

    def all_projections(self) -> Dict[str, float]:
        """Return all projected values as a dictionary."""
        return dict(self._projections)

    def summary(self) -> str:
        """Return a formatted summary string for display."""
        p = self.player
        proj = self._projections
        location = "Home" if self.is_home else "Away"
        lines = [
            f"{'=' * 56}",
            f"  {p.name}  |  {p.team}  |  {p.position}",
            f"  Games: {p.games_played}   Location: {location}",
            f"{'=' * 56}",
            f"  {'Prop':<26}  {'Projection':>10}",
            f"  {'-' * 38}",
            f"  {'Points':<26}  {proj['points']:>10.1f}",
            f"  {'Rebounds':<26}  {proj['rebounds']:>10.1f}",
            f"  {'Assists':<26}  {proj['assists']:>10.1f}",
            f"  {'Steals':<26}  {proj['steals']:>10.1f}",
            f"  {'Blocks':<26}  {proj['blocks']:>10.1f}",
            f"  {'3-Pointers Made':<26}  {proj['three_pointers']:>10.1f}",
            f"  {'Turnovers':<26}  {proj['turnovers']:>10.1f}",
            f"  {'-' * 38}",
            f"  {'Pts + Reb + Ast (PRA)':<26}  {proj['pra']:>10.1f}",
            f"  {'Steals + Blocks':<26}  {proj['steals_blocks']:>10.1f}",
            f"{'=' * 56}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def project_all(players_data: list, is_home: bool = True) -> List[PropProjection]:
    """
    Build PropProjection objects for every player in players_data.

    Parameters
    ----------
    players_data : list
        List of player dictionaries (from players.py PLAYERS list).
    is_home : bool
        Whether the players are playing at home (default True).

    Returns
    -------
    List[PropProjection]
    """
    projections = []
    for data in players_data:
        player = Player.from_dict(data)
        projections.append(PropProjection(player, is_home=is_home))
    return projections


def print_all(projections: List[PropProjection]) -> None:
    """Print the prop projection summary for every player."""
    if not projections:
        print("No players found. Add players to players.py and run again.")
        return
    for proj in projections:
        print(proj.summary())
        print()
