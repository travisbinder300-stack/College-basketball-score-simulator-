from .models import PitcherInput, WeatherConditions

PRECIP_RISK_REDUCTION_THRESHOLD = 0.5
PRECIP_OUTS_MULTIPLIER = 0.92

HIGH_TEMP_THRESHOLD_F = 90
HIGH_TEMP_OUTS_MULTIPLIER = 0.98

LOW_TEMP_THRESHOLD_F = 50
LOW_TEMP_STRIKEOUT_MULTIPLIER = 1.02

HIGH_WIND_THRESHOLD_MPH = 10
WIND_OUT_STRIKEOUT_MULTIPLIER = 0.97

OUTS_MULTIPLIER_MIN = 0.75
OUTS_MULTIPLIER_MAX = 1.10
STRIKEOUT_MULTIPLIER_MIN = 0.85
STRIKEOUT_MULTIPLIER_MAX = 1.15

EARLY_EXIT_PITCH_COUNT_THRESHOLD = 75
REDUCED_LENGTH_PITCH_COUNT_THRESHOLD = 90
EARLY_EXIT_CONTEXT_MULTIPLIER = 0.88
REDUCED_LENGTH_CONTEXT_MULTIPLIER = 0.95
CONTEXT_MULTIPLIER_MIN = 0.70
CONTEXT_MULTIPLIER_MAX = 1.20


def weather_outs_multiplier(weather: WeatherConditions) -> float:
    """Simple weather effect for innings/outs stability."""
    multiplier = 1.0
    if weather.precipitation_risk >= PRECIP_RISK_REDUCTION_THRESHOLD:
        multiplier *= PRECIP_OUTS_MULTIPLIER
    if weather.temperature_f >= HIGH_TEMP_THRESHOLD_F:
        multiplier *= HIGH_TEMP_OUTS_MULTIPLIER
    return max(OUTS_MULTIPLIER_MIN, min(OUTS_MULTIPLIER_MAX, multiplier))


def weather_strikeout_multiplier(weather: WeatherConditions) -> float:
    """Simple weather effect for strikeout environment."""
    multiplier = 1.0
    if weather.wind_out_to_center and weather.wind_mph >= HIGH_WIND_THRESHOLD_MPH:
        multiplier *= WIND_OUT_STRIKEOUT_MULTIPLIER
    if weather.temperature_f <= LOW_TEMP_THRESHOLD_F:
        multiplier *= LOW_TEMP_STRIKEOUT_MULTIPLIER
    return max(STRIKEOUT_MULTIPLIER_MIN, min(STRIKEOUT_MULTIPLIER_MAX, multiplier))


def context_outs_multiplier(pitcher_input: PitcherInput) -> float:
    """Context multiplier from pitch count + opponent tendencies."""
    multiplier = pitcher_input.opponent_contact_multiplier
    if pitcher_input.pitch_count_cap is not None:
        if pitcher_input.pitch_count_cap < EARLY_EXIT_PITCH_COUNT_THRESHOLD:
            multiplier *= EARLY_EXIT_CONTEXT_MULTIPLIER
        elif pitcher_input.pitch_count_cap < REDUCED_LENGTH_PITCH_COUNT_THRESHOLD:
            multiplier *= REDUCED_LENGTH_CONTEXT_MULTIPLIER
    return max(CONTEXT_MULTIPLIER_MIN, min(CONTEXT_MULTIPLIER_MAX, multiplier))
