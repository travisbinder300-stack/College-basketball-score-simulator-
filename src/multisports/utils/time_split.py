"""Chronological dataframe splitting helpers."""

from __future__ import annotations

from typing import Tuple

import pandas as pd


class TimeBasedSplitter:
    """Split dataframes chronologically to avoid future leakage."""

    def split(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
        train_ratio: float = 0.8,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Sort by date and split at the requested train ratio."""
        if df.empty:
            return df.copy(), df.copy()
        if not 0 < train_ratio < 1:
            raise ValueError("train_ratio must be between 0 and 1")
        ordered = df.sort_values(date_col).reset_index(drop=True)
        split_index = max(1, min(len(ordered) - 1, int(len(ordered) * train_ratio)))
        return ordered.iloc[:split_index].copy(), ordered.iloc[split_index:].copy()
