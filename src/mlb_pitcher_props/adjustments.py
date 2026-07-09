from .models import PitcherInput, WeatherConditions


def weather_outs_multiplier(weather: WeatherConditions) -> float:
    """Simple weather effect for innings/outs stability."""
    multiplier = 1.0
    if weather.precipitation_risk >= 0.5:
        multiplier *= 0.92
    if weather.temperature_f >= 90:
        multiplier *= 0.98
    return max(0.75, min(1.10, multiplier))


def weather_strikeout_multiplier(weather: WeatherConditions) -> float:
    """Simple weather effect for strikeout environment."""
    multiplier = 1.0
    if weather.wind_out_to_center and weather.wind_mph >= 10:
        multiplier *= 0.97
    if weather.temperature_f <= 50:
        multiplier *= 1.02
    return max(0.85, min(1.15, multiplier))


def context_outs_multiplier(pitcher_input: PitcherInput) -> float:
    """Context multiplier from pitch count + opponent tendencies."""
    multiplier = pitcher_input.opponent_contact_multiplier
    if pitcher_input.pitch_count_cap is not None:
        if pitcher_input.pitch_count_cap < 75:
            multiplier *= 0.88
        elif pitcher_input.pitch_count_cap < 90:
            multiplier *= 0.95
    return max(0.70, min(1.20, multiplier))

