"""Tests for model implementations."""

from pathlib import Path
import unittest

import numpy as np

from multisports.models.baseline import MeanBaseline
from multisports.models.gradient_boost import GradientBoostModel


class ModelTests(unittest.TestCase):
    """Validate fit, predict, save, and load behavior."""

    def setUp(self) -> None:
        self.X = np.array([[1.0, 0.2], [2.0, 0.1], [3.0, 0.4], [4.0, 0.6], [5.0, 0.8]])
        self.y = np.array([200.0, 205.0, 210.0, 218.0, 225.0])
        self.output_dir = Path("test_artifacts")
        self.output_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        for path in self.output_dir.glob("*.pkl"):
            path.unlink()
        self.output_dir.rmdir()

    def test_mean_baseline_round_trip(self) -> None:
        model = MeanBaseline()
        model.fit(self.X, self.y)
        predictions = model.predict(self.X)
        self.assertEqual(predictions.shape, (len(self.X),))
        self.assertTrue(np.allclose(predictions, np.mean(self.y)))

        path = self.output_dir / "baseline.pkl"
        model.save(str(path))
        loaded = MeanBaseline.load(str(path))
        self.assertTrue(np.allclose(loaded.predict(self.X), predictions))

    def test_gradient_boost_round_trip(self) -> None:
        model = GradientBoostModel()
        model.fit(self.X, self.y)
        predictions = model.predict(self.X)
        self.assertEqual(predictions.shape, (len(self.X),))

        path = self.output_dir / "gbr.pkl"
        model.save(str(path))
        loaded = GradientBoostModel.load(str(path))
        self.assertEqual(loaded.predict(self.X).shape, predictions.shape)


if __name__ == "__main__":
    unittest.main()
