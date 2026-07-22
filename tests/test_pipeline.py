"""End-to-end pipeline tests."""

from pathlib import Path
import unittest

from multisports.config.nba import NBA_CONFIG
from multisports.data.ingestion import generate_sample_nba_games
from multisports.pipeline.pipeline import Pipeline


class PipelineTests(unittest.TestCase):
    """Validate the full NBA sample-data pipeline."""

    def test_pipeline_run(self) -> None:
        games = generate_sample_nba_games(n=200, seed=21)
        pipeline = Pipeline(NBA_CONFIG)
        results = pipeline.run(games)

        self.assertIn("metrics", results)
        self.assertIn("mean_baseline", results["metrics"])
        self.assertIn("gradient_boost", results["metrics"])
        for model_name in ("mean_baseline", "gradient_boost"):
            metrics = results["metrics"][model_name]
            self.assertGreaterEqual(metrics["mae"], 0.0)
            self.assertGreaterEqual(metrics["rmse"], 0.0)
            self.assertGreaterEqual(metrics["accuracy_within_10"], 0.0)
            self.assertLessEqual(metrics["accuracy_within_10"], 1.0)
        self.assertTrue(Path(results["artifact_path"]).exists())


if __name__ == "__main__":
    unittest.main()
