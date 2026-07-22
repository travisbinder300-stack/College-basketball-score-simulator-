"""Feature generator registry."""

from multisports.config.base import SportConfig

from .base import FeatureGenerator
from .team_features import TeamFeatureGenerator


def get_feature_generator(config: SportConfig) -> FeatureGenerator:
    """Return the feature generator for a sport config."""
    return TeamFeatureGenerator(config)
