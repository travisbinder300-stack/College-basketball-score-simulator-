from dataclasses import dataclass


@dataclass
class MarketEdge:
    model_probability: float
    implied_probability: float
    edge: float
    expected_value_per_unit: float


def implied_probability_from_odds(odds: float, odds_format: str = "american") -> float:
    if odds_format not in {"american", "decimal"}:
        raise ValueError("odds_format must be american or decimal")
    if odds_format == "american":
        if odds == 0:
            raise ValueError("american odds cannot be 0")
        if odds > 0:
            return 100.0 / (odds + 100.0)
        return abs(odds) / (abs(odds) + 100.0)
    if odds <= 1.0:
        raise ValueError("decimal odds must be > 1.0")
    return 1.0 / odds


def decimal_from_odds(odds: float, odds_format: str = "american") -> float:
    if odds_format == "decimal":
        if odds <= 1.0:
            raise ValueError("decimal odds must be > 1.0")
        return odds
    if odds_format != "american":
        raise ValueError("odds_format must be american or decimal")
    if odds == 0:
        raise ValueError("american odds cannot be 0")
    return (1.0 + (odds / 100.0)) if odds > 0 else (1.0 + (100.0 / abs(odds)))


def expected_value_per_unit(model_probability: float, odds: float, odds_format: str = "american") -> float:
    if not 0 <= model_probability <= 1:
        raise ValueError("model_probability must be between 0 and 1")
    decimal_odds = decimal_from_odds(odds, odds_format)
    win_profit = decimal_odds - 1.0
    lose_probability = 1.0 - model_probability
    return (model_probability * win_profit) - lose_probability


def compute_market_edge(model_probability: float, odds: float, odds_format: str = "american") -> MarketEdge:
    implied = implied_probability_from_odds(odds, odds_format)
    ev = expected_value_per_unit(model_probability, odds, odds_format)
    return MarketEdge(
        model_probability=model_probability,
        implied_probability=implied,
        edge=model_probability - implied,
        expected_value_per_unit=ev,
    )

