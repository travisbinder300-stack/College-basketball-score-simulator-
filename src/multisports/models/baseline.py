"""Baseline mean model."""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

from .base import SportModel


class MeanBaseline(SportModel):
    """Predict the mean of the training target for every game."""

    name = "mean_baseline"

    def __init__(self) -> None:
        self.mean_: float | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Store the mean target value."""
        self.mean_ = float(np.mean(y))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return the stored mean for each row in X."""
        if self.mean_ is None:
            raise ValueError("Model must be fit before predicting")
        return np.full(shape=(len(X),), fill_value=self.mean_, dtype=float)

    def save(self, path: str) -> None:
        """Serialize the model with pickle."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("wb") as handle:
            pickle.dump({"mean_": self.mean_}, handle)

    @classmethod
    def load(cls, path: str) -> "MeanBaseline":
        """Load a serialized baseline model."""
        with Path(path).open("rb") as handle:
            payload = pickle.load(handle)
        model = cls()
        model.mean_ = payload["mean_"]
        return model
