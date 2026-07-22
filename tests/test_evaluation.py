"""Tests for evaluation metrics."""

import unittest

import numpy as np

from multisports.training.evaluation import accuracy_within_n, calibration_error, evaluate_all, mae, rmse


class EvaluationTests(unittest.TestCase):
    """Validate metric calculations."""

    def test_metric_values(self) -> None:
        y_true = np.array([100.0, 110.0, 120.0])
        y_pred = np.array([102.0, 108.0, 123.0])

        self.assertAlmostEqual(mae(y_true, y_pred), 7.0 / 3.0)
        self.assertAlmostEqual(rmse(y_true, y_pred), (17.0 / 3.0) ** 0.5)
        self.assertAlmostEqual(accuracy_within_n(y_true, y_pred, 2.0), 2.0 / 3.0)
        self.assertAlmostEqual(calibration_error(y_true, y_pred), 1.0)

        results = evaluate_all(y_true, y_pred)
        self.assertSetEqual(
            set(results.keys()),
            {"mae", "rmse", "accuracy_within_10", "calibration_error"},
        )


if __name__ == "__main__":
    unittest.main()
