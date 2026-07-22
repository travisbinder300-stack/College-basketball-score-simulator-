"""Prediction helpers for trained sport models."""

from __future__ import annotations

import numpy as np

from multisports.config.base import SportConfig
from multisports.models.base import SportModel


class Predictor:
    """Run single-game inference using a fitted or loaded model."""

    def __init__(self, model: SportModel, config: SportConfig) -> None:
        """Store the model and config used for inference."""
        self.model = model
        self.config = config

    def predict_game(self, features: dict) -> float:
        """Predict a game's total score from a feature dictionary."""
        ordered = np.array([[float(features[column]) for column in self.config.feature_columns]], dtype=float)
        return float(self.model.predict(ordered)[0])
