"""Cleaning and transformation helpers for game data."""

from __future__ import annotations

from dataclasses import asdict
from typing import List

import pandas as pd
from sklearn.preprocessing import StandardScaler

from .schema import Game


def clean_games(games: List[Game]) -> List[Game]:
    """Drop games with missing scores and remove duplicates by id."""
    cleaned: List[Game] = []
    seen_ids: set[str] = set()
    for game in games:
        if game.id in seen_ids:
            continue
        if game.home_score is None or game.away_score is None:
            continue
        cleaned.append(game)
        seen_ids.add(game.id)
    return cleaned


def games_to_dataframe(games: List[Game]) -> pd.DataFrame:
    """Convert Game objects into a pandas DataFrame."""
    rows = []
    for game in games:
        row = asdict(game)
        row["total_score"] = game.total_score
        rows.append(row)
    return pd.DataFrame(rows)


def normalize_features(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """Return a copy of df with selected feature columns standardized."""
    scaled_df = df.copy()
    if not feature_cols:
        return scaled_df
    scaler = StandardScaler()
    scaled_df[feature_cols] = scaler.fit_transform(scaled_df[feature_cols])
    return scaled_df
