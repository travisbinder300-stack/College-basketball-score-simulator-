"""Base sport configuration models."""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class SportConfig:
    """Configuration describing how a sport should be modeled."""

    sport: str
    league: str
    prediction_target: str
    rolling_window: int
    rest_cap: int
    feature_columns: List[str] = field(default_factory=list)
    min_train_games: int = 50
    model_dir: str = "artifacts"

    def __post_init__(self) -> None:
        """Validate core config fields."""
        if not self.sport:
            raise ValueError("sport must be provided")
        if self.rolling_window <= 0:
            raise ValueError("rolling_window must be positive")
        if self.rest_cap <= 0:
            raise ValueError("rest_cap must be positive")
        if self.min_train_games <= 0:
            raise ValueError("min_train_games must be positive")
        if not self.feature_columns:
            raise ValueError("feature_columns must not be empty")
