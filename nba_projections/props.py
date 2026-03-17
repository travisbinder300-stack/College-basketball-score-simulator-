"""
Prop line analyzer for NBA player projections.

Compares projected stats against sportsbook prop lines and calculates
historical hit rates from the game log.
"""

from typing import Dict, List, Optional, Tuple

from .projections import PlayerProjection, STAT_KEYS
from .player_data import get_player


class PropResult:
    """Outcome of a single prop-line evaluation.

    Attributes:
        player: Player's full name.
        stat: Stat category (e.g. ``'pts'``).
        line: Prop line to beat (e.g. ``27.5``).
        projection: Model projection for this stat.
        edge: ``projection - line`` (positive = lean Over).
        recommendation: ``'OVER'``, ``'UNDER'``, or ``'PUSH'``.
        confidence: Confidence label (``'High'``, ``'Medium'``, ``'Low'``).
        hit_rate: Historical rate the player has exceeded *line* in the
            provided game log (0.0 – 1.0).
    """

    # Edge thresholds for confidence labels
    _HIGH_EDGE = 3.0
    _MEDIUM_EDGE = 1.5

    def __init__(
        self,
        player: str,
        stat: str,
        line: float,
        projection: float,
        hit_rate: float,
    ) -> None:
        self.player = player
        self.stat = stat
        self.line = line
        self.projection = projection
        self.hit_rate = hit_rate
        self.edge = round(projection - line, 1)
        self.recommendation = self._recommend()
        self.confidence = self._confidence()

    def _recommend(self) -> str:
        if self.edge > 0:
            return "OVER"
        if self.edge < 0:
            return "UNDER"
        return "PUSH"

    def _confidence(self) -> str:
        abs_edge = abs(self.edge)
        if abs_edge >= self._HIGH_EDGE:
            return "High"
        if abs_edge >= self._MEDIUM_EDGE:
            return "Medium"
        return "Low"

    def __repr__(self) -> str:
        return (
            f"PropResult(player={self.player!r}, stat={self.stat!r}, "
            f"line={self.line}, proj={self.projection}, "
            f"edge={self.edge:+.1f}, rec={self.recommendation}, "
            f"conf={self.confidence}, hit_rate={self.hit_rate:.0%})"
        )


class PropAnalyzer:
    """Evaluate one or more prop lines for a player in a matchup.

    Args:
        player_id: Player lookup key (e.g. ``'luka_doncic'``).
        opponent: Three-letter team abbreviation.
        home: ``True`` if the player is at home.
        recent_games: Games used in rolling average (default 5).
    """

    def __init__(
        self,
        player_id: str,
        opponent: str,
        home: bool = True,
        recent_games: int = 5,
    ) -> None:
        self._projection = PlayerProjection(
            player_id, opponent, home=home, recent_games=recent_games
        )
        self._player_data = get_player(player_id)
        self._proj_values = self._projection.project()
        self._std_dev = self._projection.standard_deviation()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_prop(self, stat: str, line: float) -> PropResult:
        """Evaluate a single prop line for the given stat.

        Args:
            stat: Stat category (``'pts'``, ``'reb'``, ``'ast'``,
                ``'stl'``, ``'blk'``, ``'pts_reb_ast'``).
            line: The sportsbook prop line value.

        Returns:
            A :class:`PropResult` with recommendation and confidence.
        """
        valid_stats = STAT_KEYS + ["pts_reb_ast"]
        if stat not in valid_stats:
            raise ValueError(f"Invalid stat '{stat}'. Choose from: {valid_stats}")

        projection = self._proj_values[stat]
        hit_rate = self._historical_hit_rate(stat, line)

        return PropResult(
            player=self._player_data["name"],
            stat=stat,
            line=line,
            projection=projection,
            hit_rate=hit_rate,
        )

    def evaluate_all(self, prop_lines: Dict[str, float]) -> List[PropResult]:
        """Evaluate multiple prop lines at once.

        Args:
            prop_lines: Mapping of stat name to line value,
                e.g. ``{'pts': 27.5, 'reb': 8.5, 'ast': 9.5}``.

        Returns:
            List of :class:`PropResult` objects, one per stat.
        """
        results = []
        for stat, line in prop_lines.items():
            results.append(self.evaluate_prop(stat, line))
        return results

    def display_report(self, prop_lines: Optional[Dict[str, float]] = None) -> str:
        """Generate a human-readable projection report.

        Args:
            prop_lines: Optional sportsbook lines to compare against.
                If ``None``, only projections are displayed without
                over/under recommendations.

        Returns:
            Formatted multi-line string report.
        """
        proj = self._proj_values
        std = self._std_dev
        summary = self._projection.summary()

        lines_out: List[str] = []
        lines_out.append("=" * 60)
        lines_out.append(f"  NBA PLAYER PROJECTION REPORT")
        lines_out.append("=" * 60)
        lines_out.append(f"  Player   : {summary['player']} ({summary['team']})")
        location = "Home" if summary["home"] else "Away"
        lines_out.append(f"  Matchup  : {location} vs {summary['opponent']}")
        lines_out.append("-" * 60)
        lines_out.append(f"  {'STAT':<12} {'PROJ':>6}  {'±STD':>6}")

        if prop_lines:
            lines_out[-1] += f"  {'LINE':>6}  {'EDGE':>6}  {'REC':<6}  {'CONF':<8}  {'HIT%':>5}"

        lines_out.append("-" * 60)

        display_stats = [
            ("pts",         "Points"),
            ("reb",         "Rebounds"),
            ("ast",         "Assists"),
            ("stl",         "Steals"),
            ("blk",         "Blocks"),
            ("pts_reb_ast", "Pts+Reb+Ast"),
        ]

        for stat_key, label in display_stats:
            projection = proj[stat_key]
            sd = std.get(stat_key, 0.0) if stat_key != "pts_reb_ast" else "—"
            sd_str = f"{sd}" if sd != "—" else "  —"

            row = f"  {label:<12} {projection:>6.1f}  {sd_str:>6}"

            if prop_lines and stat_key in prop_lines:
                result = self.evaluate_prop(stat_key, prop_lines[stat_key])
                edge_str = f"{result.edge:+.1f}"
                row += (
                    f"  {result.line:>6.1f}"
                    f"  {edge_str:>6}"
                    f"  {result.recommendation:<6}"
                    f"  {result.confidence:<8}"
                    f"  {result.hit_rate:>4.0%}"
                )

            lines_out.append(row)

        lines_out.append("=" * 60)
        return "\n".join(lines_out)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _historical_hit_rate(self, stat: str, line: float) -> float:
        """Return the fraction of logged games where the player exceeded *line*."""
        game_log = self._player_data["game_log"]

        if stat == "pts_reb_ast":
            values = [g["pts"] + g["reb"] + g["ast"] for g in game_log]
        else:
            values = [g[stat] for g in game_log]

        if not values:
            return 0.0

        hits = sum(1 for v in values if v > line)
        return round(hits / len(values), 4)
