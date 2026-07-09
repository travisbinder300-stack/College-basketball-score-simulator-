import unittest

from mlb_pitcher_props.evaluation import BacktestRecord, evaluate_calibration


class TestEvaluation(unittest.TestCase):
    def test_calibration_report(self) -> None:
        records = [
            BacktestRecord(predicted_probability_over=0.55, actual_over=1),
            BacktestRecord(predicted_probability_over=0.48, actual_over=0),
            BacktestRecord(predicted_probability_over=0.61, actual_over=1),
        ]
        report = evaluate_calibration(records)
        self.assertEqual(report.sample_size, 3)
        self.assertGreaterEqual(report.brier_score, 0.0)

    def test_empty_records_raises(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_calibration([])


if __name__ == "__main__":
    unittest.main()

