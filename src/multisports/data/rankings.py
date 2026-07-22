"""Rankings data loader and game-dataframe enrichment utilities.

Predictive ranking CSVs (e.g. from TeamRankings) map each team to a numeric
power rating that represents expected point-differential against an average
opponent on a neutral court.  Positive ratings → stronger teams, negative →
weaker teams.

The enricher merges these static ratings into a game DataFrame as two new
feature columns so the ML pipeline can use pre-season / current team strength
as an additional signal alongside the rolling historical features.

CSV format (required columns)
------------------------------
    rank,team,abbreviation,rating,...
    1,Minnesota Lynx,MIN,8.5,...
    2,Las Vegas Aces,LVA,7.8,...

The ``abbreviation`` field is matched (case-insensitively) against the
``home_team_id`` / ``away_team_id`` columns in the game DataFrame.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Optional

import pandas as pd


def load_rankings_csv(path: str) -> Dict[str, float]:
    """Load a predictive-rankings CSV and return an abbreviation → rating map.

    Parameters
    ----------
    path:
        Filesystem path to the rankings CSV.  Must contain at least
        ``abbreviation`` and ``rating`` columns.

    Returns
    -------
    dict
        Upper-cased abbreviation keys mapped to float power ratings.
    """
    ratings: Dict[str, float] = {}
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = row.get("abbreviation", "").strip().upper()
            raw = row.get("rating", "").strip()
            if key and raw:
                try:
                    ratings[key] = float(raw)
                except ValueError:
                    ratings[key] = 0.0
    return ratings


def enrich_with_rankings(
    df: pd.DataFrame,
    ratings: Dict[str, float],
    default_rating: Optional[float] = None,
    home_col: str = "home_team_id",
    away_col: str = "away_team_id",
) -> pd.DataFrame:
    """Add ``home_predictive_rating`` and ``away_predictive_rating`` columns.

    Teams whose ``team_id`` is not found in *ratings* receive *default_rating*
    (defaults to the mean of all known ratings, or 0.0 when *ratings* is
    empty).

    Parameters
    ----------
    df:
        Game DataFrame produced by the feature-generation step.
    ratings:
        Abbreviation → rating mapping from :func:`load_rankings_csv`.
    default_rating:
        Rating to use for unknown teams.  Falls back to the mean of all values
        in *ratings* when ``None``.
    home_col:
        Column in *df* containing the home team identifier.
    away_col:
        Column in *df* containing the away team identifier.

    Returns
    -------
    pd.DataFrame
        Copy of *df* with two additional float columns appended.
    """
    if default_rating is None:
        default_rating = float(sum(ratings.values()) / len(ratings)) if ratings else 0.0

    upper_ratings = {k.upper(): v for k, v in ratings.items()}
    enriched = df.copy()
    enriched["home_predictive_rating"] = (
        enriched[home_col].str.upper().map(upper_ratings).fillna(default_rating)
    )
    enriched["away_predictive_rating"] = (
        enriched[away_col].str.upper().map(upper_ratings).fillna(default_rating)
    )
    return enriched
