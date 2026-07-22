"""Abstract model interface."""

from abc import ABC, abstractmethod

import numpy as np


class SportModel(ABC):
    """Abstract model protocol for multi-sport regressors."""

    name: str

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the model to feature matrix X and target y."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict targets for feature matrix X."""
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str) -> None:
        """Serialize the model to disk."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def load(cls, path: str) -> "SportModel":
        """Load a serialized model from disk."""
        raise NotImplementedError
