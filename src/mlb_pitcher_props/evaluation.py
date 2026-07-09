import math
from dataclasses import dataclass


@dataclass
class BacktestRecord:
    predicted_probability_over: float
    actual_over: int  # 1 if over hit else 0


@dataclass
class CalibrationReport:
    sample_size: int
    brier_score: float
    log_loss: float
    mean_prediction: float
    observed_rate: float
    calibration_gap: float


def evaluate_calibration(records: list[BacktestRecord], epsilon: float = 1e-12) -> CalibrationReport:
    if not records:
        raise ValueError("records cannot be empty")

    probs = [record.predicted_probability_over for record in records]
    outcomes = [record.actual_over for record in records]

    for value in probs:
        if not 0.0 <= value <= 1.0:
            raise ValueError("predicted probabilities must be between 0 and 1")
    for outcome in outcomes:
        if outcome not in (0, 1):
            raise ValueError("actual_over must be 0 or 1")

    n = len(records)
    brier = sum((p - y) ** 2 for p, y in zip(probs, outcomes)) / n
    log_loss = -sum(
        (y * math.log(max(epsilon, min(1.0 - epsilon, p))))
        + ((1 - y) * math.log(max(epsilon, min(1.0 - epsilon, 1.0 - p))))
        for p, y in zip(probs, outcomes)
    ) / n
    mean_prediction = sum(probs) / n
    observed_rate = sum(outcomes) / n

    return CalibrationReport(
        sample_size=n,
        brier_score=brier,
        log_loss=log_loss,
        mean_prediction=mean_prediction,
        observed_rate=observed_rate,
        calibration_gap=mean_prediction - observed_rate,
    )

