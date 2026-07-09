from dataclasses import dataclass
from typing import Optional


@dataclass
class PitcherInput:
    pitcher_name: str
    expected_outs_baseline: float
    strikeouts_per_out: float
    opponent_contact_multiplier: float = 1.0
    pitch_count_cap: Optional[int] = None


@dataclass
class WeatherConditions:
    temperature_f: float = 72.0
    wind_mph: float = 0.0
    wind_out_to_center: bool = False
    precipitation_risk: float = 0.0


@dataclass
class MarketLine:
    prop_type: str
    line: float
    odds_over: float
    odds_under: float
    odds_format: str = "american"


@dataclass
class ProjectionResult:
    pitcher_name: str
    projected_outs: float
    projected_strikeouts: float
    weather_outs_multiplier: float
    weather_strikeout_multiplier: float

