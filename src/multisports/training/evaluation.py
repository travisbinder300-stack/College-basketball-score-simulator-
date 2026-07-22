"""Evaluation metrics for regression predictions."""

from __future__ import annotations

import numpy as np


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return mean absolute error."""
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return root mean squared error."""
    errors = np.asarray(y_true) - np.asarray(y_pred)
    return float(np.sqrt(np.mean(np.square(errors))))


def accuracy_within_n(y_true: np.ndarray, y_pred: np.ndarray, n: float = 10.0) -> float:
    """Return the share of predictions within n points of truth."""
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred)) <= n))


def calibration_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return the signed average error to measure prediction bias."""
    return float(np.mean(np.asarray(y_pred) - np.asarray(y_true)))


def evaluate_all(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute the standard metric suite for total prediction."""
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "accuracy_within_10": accuracy_within_n(y_true, y_pred, n=10.0),
        "calibration_error": calibration_error(y_true, y_pred),
    }
