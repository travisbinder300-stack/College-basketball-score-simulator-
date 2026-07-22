#!/usr/bin/env python3
"""Fetch live scoreboard data and save normalized game rows as JSON."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from multisports.data.schema import Game


SPORT_ENDPOINTS: Dict[str, str] = {
    "nba": "basketball/nba",
    "wnba": "basketball/wnba",
    "ncaab": "basketball/mens-college-basketball",
    "nfl": "football/nfl",
    "ncaaf": "football/college-football",
    "mlb": "baseball/mlb",
    "ncaa_baseball": "baseball/college-baseball",
    "nhl": "hockey/nhl",
}


def _build_url(sport: str, dates: str) -> str:
    endpoint = SPORT_ENDPOINTS[sport]
    return f"https://site.api.espn.com/apis/site/v2/sports/{endpoint}/scoreboard?dates={dates}"


def _read_json(url: str) -> Dict[str, Any]:
    try:
        with urlopen(url, timeout=20) as response:  # nosec B310
            payload = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Failed to fetch live data: {exc}") from exc
    return json.loads(payload)


def _extract_competitors(event: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    competitors = event.get("competitions", [{}])[0].get("competitors", [])
    by_side: Dict[str, Dict[str, Any]] = {}
    for competitor in competitors:
        side = competitor.get("homeAway")
        if side in {"home", "away"}:
            by_side[side] = competitor
    return by_side


def _to_game(event: Dict[str, Any], sport: str) -> Game | None:
    competitors = _extract_competitors(event)
    home = competitors.get("home")
    away = competitors.get("away")
    if not home or not away:
        return None

    competition = event.get("competitions", [{}])[0]
    venue = competition.get("venue", {}).get("fullName") or "Unknown Venue"
    event_date = datetime.fromisoformat(event["date"].replace("Z", "+00:00")).date()
    season_year = event.get("season", {}).get("year", event_date.year)
    season_type = event.get("season", {}).get("type", 2)
    season = str(season_year) if season_type != 3 else f"{season_year}-{season_year + 1}"

    return Game(
        id=str(event["id"]),
        sport=sport,
        date=event_date,
        season=season,
        home_team_id=str(home.get("team", {}).get("id") or home.get("team", {}).get("abbreviation") or "UNKNOWN_HOME"),
        away_team_id=str(away.get("team", {}).get("id") or away.get("team", {}).get("abbreviation") or "UNKNOWN_AWAY"),
        home_score=int(float(home.get("score", 0))),
        away_score=int(float(away.get("score", 0))),
        venue=venue,
        is_neutral_site=bool(competition.get("neutralSite", False)),
        home_rest_days=0,
        away_rest_days=0,
    )


def fetch_live_games(sport: str, dates: str) -> List[Game]:
    """Fetch and normalize live games from ESPN public scoreboard endpoints."""
    payload = _read_json(_build_url(sport=sport, dates=dates))
    games: List[Game] = []
    for event in payload.get("events", []):
        game = _to_game(event=event, sport=sport)
        if game is not None:
            games.append(game)
    return games


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch live sports data and save as JSON.")
    parser.add_argument("--sport", choices=sorted(SPORT_ENDPOINTS.keys()), default="ncaab")
    parser.add_argument(
        "--dates",
        default=datetime.now(UTC).strftime("%Y%m%d"),
        help="Scoreboard date in YYYYMMDD format (default: today UTC).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path. Default: data/live/<sport>_<dates>.json",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    games = fetch_live_games(sport=args.sport, dates=args.dates)
    output_path = (
        Path(args.output)
        if args.output
        else Path("data") / "live" / f"{args.sport}_{args.dates}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps([asdict(game) for game in games], indent=2, default=str), encoding="utf-8")
    print(f"Saved {len(games)} games to {output_path}")


if __name__ == "__main__":
    main()
