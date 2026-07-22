"""Base feature generation abstractions."""

from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class FeatureGenerator(ABC):
    """Abstract base class for sport-specific feature generation."""

    @abstractmethod
    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add feature columns to df sorted by date and return it."""
        raise NotImplementedError

    @abstractmethod
    def feature_names(self) -> List[str]:
        """Return the list of feature columns produced by the generator."""
        raise NotImplementedError
