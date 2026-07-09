import math

from .adjustments import context_outs_multiplier, weather_outs_multiplier, weather_strikeout_multiplier
from .models import PitcherInput, ProjectionResult, WeatherConditions


def _normal_approx_probability_over(line: float, mean: float, std_dev: float) -> float:
    if std_dev <= 0:
        return 1.0 if mean > line else 0.0
    z_score = (line - mean) / std_dev
    cdf = 0.5 * (1.0 + math.erf(z_score / math.sqrt(2.0)))
    return max(0.0, min(1.0, 1.0 - cdf))


def project_pitcher_props(
    pitcher_input: PitcherInput,
    weather: WeatherConditions | None = None,
) -> ProjectionResult:
    if pitcher_input.expected_outs_baseline <= 0:
        raise ValueError("expected_outs_baseline must be > 0")
    if pitcher_input.strikeouts_per_out < 0:
        raise ValueError("strikeouts_per_out must be >= 0")

    weather = weather or WeatherConditions()
    outs_mult = weather_outs_multiplier(weather) * context_outs_multiplier(pitcher_input)
    k_mult = weather_strikeout_multiplier(weather)

    projected_outs = pitcher_input.expected_outs_baseline * outs_mult
    projected_strikeouts = projected_outs * pitcher_input.strikeouts_per_out * k_mult

    return ProjectionResult(
        pitcher_name=pitcher_input.pitcher_name,
        projected_outs=max(0.0, projected_outs),
        projected_strikeouts=max(0.0, projected_strikeouts),
        weather_outs_multiplier=outs_mult,
        weather_strikeout_multiplier=k_mult,
    )


def probability_over_line(
    projection_mean: float,
    market_line: float,
    std_dev: float,
) -> float:
    if std_dev < 0:
        raise ValueError("std_dev must be >= 0")
    return _normal_approx_probability_over(market_line, projection_mean, std_dev)

