"""
Projection engine for NBA player props.

Calculates per-game stat projections using:
  - Season-average baseline
  - Recent form (rolling 5-game average)
  - Home/away split
  - Opponent defensive rating adjustment
"""

import statistics
from typing import Optional

from .player_data import OPPONENT_DEF_RATINGS, get_player

STAT_KEYS = ["pts", "reb", "ast", "stl", "blk"]

# Weight given to recent-form (rolling 5-game avg) vs season average.
# 0.0 = pure season avg, 1.0 = pure recent form.
RECENT_FORM_WEIGHT = 0.40

# Home-court advantage multiplier per stat category (applied to the
# baseline projection when the player is playing at home).
HOME_BOOST = {
    "pts": 1.025,
    "reb": 1.015,
    "ast": 1.020,
    "stl": 1.010,
    "blk": 1.010,
}


class PlayerProjection:
    """Generate stat projections for a single player in a specific matchup.

    Args:
        player_id: Player lookup key, e.g. ``'luka_doncic'``.
        opponent: Three-letter team abbreviation of the upcoming opponent,
            e.g. ``'GSW'``.  Must be a key in ``OPPONENT_DEF_RATINGS``.
        home: ``True`` if the player is playing at home.
        recent_games: Number of recent games to use for rolling average
            (default 5).
    """

    def __init__(
        self,
        player_id: str,
        opponent: str,
        home: bool = True,
        recent_games: int = 5,
    ) -> None:
        self._data = get_player(player_id)
        self.player_id = player_id
        self.name: str = self._data["name"]
        self.team: str = self._data["team"]
        self.opponent = opponent.upper()
        self.home = home
        self.recent_games = recent_games

        if self.opponent not in OPPONENT_DEF_RATINGS:
            raise ValueError(
                f"Unknown opponent '{self.opponent}'. "
                f"Available teams: {sorted(OPPONENT_DEF_RATINGS.keys())}"
            )

        self._projections: Optional[dict] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def project(self) -> dict:
        """Compute and return projected stats for each category.

        Returns:
            Dictionary with stat keys ``pts``, ``reb``, ``ast``,
            ``stl``, ``blk`` mapped to projected float values rounded
            to one decimal place.  Also includes ``pts_reb_ast``
            (points + rebounds + assists combo) and raw computation
            metadata.
        """
        if self._projections is not None:
            return self._projections

        season_avg = self._data["season_avg"]
        game_log = self._data["game_log"]
        recent = game_log[: self.recent_games]

        opp_factor = OPPONENT_DEF_RATINGS[self.opponent]

        result = {}
        for stat in STAT_KEYS:
            # Season average baseline
            season_val = season_avg[stat]

            # Rolling average over the most-recent N games
            rolling_val = statistics.mean(g[stat] for g in recent) if recent else season_val

            # Blend season avg with recent form
            blended = (1 - RECENT_FORM_WEIGHT) * season_val + RECENT_FORM_WEIGHT * rolling_val

            # Apply opponent defensive adjustment
            # Scoring/rebounding/assists scale with opponent rating;
            # steals and blocks are slightly less opponent-dependent
            if stat in ("pts", "reb", "ast"):
                adjusted = blended * opp_factor
            else:
                # For stl/blk use a dampened adjustment (50% effect)
                adjusted = blended * (1 + (opp_factor - 1) * 0.5)

            # Apply home/away boost
            if self.home:
                adjusted *= HOME_BOOST.get(stat, 1.0)

            result[stat] = round(adjusted, 1)

        result["pts_reb_ast"] = round(
            result["pts"] + result["reb"] + result["ast"], 1
        )

        self._projections = result
        return result

    def standard_deviation(self) -> dict:
        """Return standard deviation of each stat across the full game log.

        Useful for estimating variance / upside-downside range.
        """
        game_log = self._data["game_log"]
        result = {}
        for stat in STAT_KEYS:
            values = [g[stat] for g in game_log]
            result[stat] = round(statistics.stdev(values), 1) if len(values) >= 2 else 0.0
        return result

    def summary(self) -> dict:
        """Return a summary dictionary with player info and projections."""
        proj = self.project()
        std = self.standard_deviation()
        return {
            "player": self.name,
            "team": self.team,
            "opponent": self.opponent,
            "home": self.home,
            "projections": proj,
            "std_dev": std,
        }
