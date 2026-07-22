"""Model registry."""

from multisports.models.base import SportModel

from .baseline import MeanBaseline
from .gradient_boost import GradientBoostModel


def get_models_for_sport(sport: str) -> list[SportModel]:
    """Return the default model set for a sport."""
    _ = sport
    return [MeanBaseline(), GradientBoostModel()]
