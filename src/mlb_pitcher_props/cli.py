import argparse
import json
from pathlib import Path

from .baseline import probability_over_line, project_pitcher_props
from .models import PitcherInput, WeatherConditions
from .odds import compute_market_edge


def _read_payload(input_path: Path) -> dict:
    with input_path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def run_model(input_path: Path) -> dict:
    payload = _read_payload(input_path)
    pitcher = PitcherInput(**payload["pitcher"])
    weather_payload = payload.get("weather")
    weather = WeatherConditions(**weather_payload) if weather_payload else None
    projection = project_pitcher_props(pitcher, weather=weather)

    market = payload.get("market", {})
    prop_type = market.get("prop_type", "strikeouts")
    line = float(market.get("line", 5.5))
    std_dev = float(market.get("std_dev", 1.5))
    selected_odds = float(market.get("odds_over", -110))
    odds_format = market.get("odds_format", "american")

    if prop_type == "outs":
        mean = projection.projected_outs
    else:
        mean = projection.projected_strikeouts

    probability_over = probability_over_line(mean, line, std_dev)
    edge = compute_market_edge(probability_over, selected_odds, odds_format=odds_format)

    return {
        "pitcher_name": projection.pitcher_name,
        "prop_type": prop_type,
        "line": line,
        "projection": {
            "projected_outs": round(projection.projected_outs, 3),
            "projected_strikeouts": round(projection.projected_strikeouts, 3),
            "weather_outs_multiplier": round(projection.weather_outs_multiplier, 4),
            "weather_strikeout_multiplier": round(projection.weather_strikeout_multiplier, 4),
        },
        "market": {
            "model_probability_over": round(edge.model_probability, 4),
            "implied_probability_over": round(edge.implied_probability, 4),
            "edge_over": round(edge.edge, 4),
            "expected_value_per_unit": round(edge.expected_value_per_unit, 4),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MLB pitcher props model scaffold CLI")
    parser.add_argument("--input", type=Path, required=True, help="Path to JSON input payload")
    args = parser.parse_args()

    output = run_model(args.input)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

