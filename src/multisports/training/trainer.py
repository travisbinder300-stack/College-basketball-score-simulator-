"""Training orchestration for sport models."""

from __future__ import annotations

from typing import List

import pandas as pd

from multisports.config.base import SportConfig
from multisports.models.base import SportModel
from multisports.training.evaluation import evaluate_all
from multisports.utils.time_split import TimeBasedSplitter


class Trainer:
    """Train and validate a collection of models on chronological splits."""

    def __init__(self, config: SportConfig, models: List[SportModel]) -> None:
        """Store configuration and model instances."""
        self.config = config
        self.models = models
        self.trained_models: dict[str, SportModel] = {}
        self.splitter = TimeBasedSplitter()

    def train(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        """Train all models on a time-based split and return validation metrics."""
        if len(df) < self.config.min_train_games:
            raise ValueError(
                f"Need at least {self.config.min_train_games} games to train, received {len(df)}"
            )

        train_df, val_df = self.splitter.split(df, date_col="date", train_ratio=0.8)
        X_train = train_df[self.config.feature_columns].to_numpy(dtype=float)
        y_train = train_df[self.config.prediction_target].to_numpy(dtype=float)
        X_val = val_df[self.config.feature_columns].to_numpy(dtype=float)
        y_val = val_df[self.config.prediction_target].to_numpy(dtype=float)

        results: dict[str, dict[str, float]] = {}
        for model in self.models:
            model.fit(X_train, y_train)
            predictions = model.predict(X_val)
            results[model.name] = evaluate_all(y_val, predictions)
            self.trained_models[model.name] = model
        return results
