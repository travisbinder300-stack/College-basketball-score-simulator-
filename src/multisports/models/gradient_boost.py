"""Gradient boosting regression model."""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

from .base import SportModel


class GradientBoostModel(SportModel):
    """Wrap sklearn's GradientBoostingRegressor."""

    name = "gradient_boost"

    def __init__(self) -> None:
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the gradient boosting regressor."""
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict with the fitted gradient boosting regressor."""
        return np.asarray(self.model.predict(X), dtype=float)

    def save(self, path: str) -> None:
        """Serialize the wrapped sklearn model."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("wb") as handle:
            pickle.dump(self.model, handle)

    @classmethod
    def load(cls, path: str) -> "GradientBoostModel":
        """Load a serialized gradient boosting model."""
        with Path(path).open("rb") as handle:
            sklearn_model = pickle.load(handle)
        instance = cls()
        instance.model = sklearn_model
        return instance
