"""End-to-end machine learning pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from multisports.config.base import SportConfig
from multisports.data.cleaning import clean_games, games_to_dataframe
from multisports.data.rankings import enrich_with_rankings, load_rankings_csv
from multisports.data.schema import Game
from multisports.features.registry import get_feature_generator
from multisports.models.registry import get_models_for_sport
from multisports.training.trainer import Trainer


class Pipeline:
    """Coordinate ingestion-ready games through training and model persistence."""

    def __init__(self, config: SportConfig) -> None:
        """Store the sport configuration."""
        self.config = config

    def run(self, games: list[Game], rankings_path: Optional[str] = None) -> dict:
        """Run cleaning, feature engineering, training, evaluation, and persistence.

        Parameters
        ----------
        games:
            List of :class:`~multisports.data.schema.Game` objects to train on.
        rankings_path:
            Optional path to a predictive-rankings CSV (see
            :func:`~multisports.data.rankings.load_rankings_csv`).  When
            supplied, ``home_predictive_rating`` and
            ``away_predictive_rating`` columns are appended to the feature
            DataFrame before training.  Unknown teams receive the mean rating.
        """
        cleaned_games = clean_games(games)
        df = games_to_dataframe(cleaned_games)
        feature_generator = get_feature_generator(self.config)
        featured_df = feature_generator.generate(df)

        if rankings_path is not None:
            ratings = load_rankings_csv(rankings_path)
            featured_df = enrich_with_rankings(featured_df, ratings)

        trainer = Trainer(self.config, get_models_for_sport(self.config.sport))
        results = trainer.train(featured_df)

        best_model_name = min(results, key=lambda name: results[name]["mae"])
        artifact_dir = Path(self.config.model_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_dir / f"{self.config.sport}_{best_model_name}.pkl"
        trainer.trained_models[best_model_name].save(str(artifact_path))

        return {
            "sport": self.config.sport,
            "metrics": results,
            "best_model": best_model_name,
            "artifact_path": str(artifact_path),
        }
