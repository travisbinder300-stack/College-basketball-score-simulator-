"""Data ingestion and synthetic sample generation utilities."""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .schema import Game


def _parse_game_row(row: Dict[str, Any], sport: str) -> Game:
    """Parse a CSV or JSON record into a Game instance."""
    raw_date = row["date"]
    parsed_date = raw_date if isinstance(raw_date, date) else datetime.fromisoformat(str(raw_date)).date()
    return Game(
        id=str(row["id"]),
        sport=sport,
        date=parsed_date,
        season=str(row["season"]),
        home_team_id=str(row["home_team_id"]),
        away_team_id=str(row["away_team_id"]),
        home_score=int(row["home_score"]),
        away_score=int(row["away_score"]),
        venue=str(row["venue"]),
        is_neutral_site=bool(row["is_neutral_site"]),
        home_rest_days=int(row["home_rest_days"]),
        away_rest_days=int(row["away_rest_days"]),
    )


def load_games_from_csv(path: str, sport: str) -> List[Game]:
    """Load games from a CSV file whose columns match Game fields."""
    games: List[Game] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = dict(row)
            normalized["is_neutral_site"] = str(row["is_neutral_site"]).strip().lower() in {"1", "true", "yes"}
            games.append(_parse_game_row(normalized, sport=sport))
    return games


def load_games_from_json(path: str, sport: str) -> List[Game]:
    """Load games from a JSON array whose objects match Game fields."""
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [_parse_game_row(row, sport=sport) for row in payload]


def generate_sample_nba_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic NBA games suitable for pipeline testing and demos."""
    if n <= 0:
        return []

    rng = np.random.default_rng(seed)
    teams = [f"NBA_{index:02d}" for index in range(10)]
    team_attack = {team: rng.normal(111, 6) for team in teams}
    team_defense = {team: rng.normal(109, 5) for team in teams}
    team_pace = {team: rng.normal(100, 3) for team in teams}
    last_played: Dict[str, date] = {}
    start_date = date(2023, 10, 20)
    season = "2023-2024"
    games: List[Game] = []

    for idx in range(n):
        game_date = start_date + timedelta(days=idx // 3)
        home_team, away_team = rng.choice(teams, size=2, replace=False).tolist()
        home_rest = int(np.clip((game_date - last_played[home_team]).days, 1, 7)) if home_team in last_played else int(rng.integers(1, 4))
        away_rest = int(np.clip((game_date - last_played[away_team]).days, 1, 7)) if away_team in last_played else int(rng.integers(1, 4))
        neutral_site = bool(rng.random() < 0.03)

        pace_factor = (team_pace[home_team] + team_pace[away_team]) / 2
        offensive_context = (team_attack[home_team] + team_attack[away_team])
        defensive_context = (team_defense[home_team] + team_defense[away_team]) / 2
        rest_adjustment = 0.8 * (home_rest + away_rest - 4)
        home_edge = 2.5 if not neutral_site else 0.0
        expected_total = offensive_context + 0.35 * (pace_factor - 100) - 0.15 * (defensive_context - 109) + rest_adjustment + home_edge
        total_score = int(np.clip(rng.normal(expected_total, 12), 170, 275))
        score_margin = int(np.round(rng.normal(home_edge, 10)))
        home_score = max(80, int(round(total_score / 2 + score_margin / 2)))
        away_score = max(75, total_score - home_score)
        total_score = home_score + away_score

        game = Game(
            id=f"nba_{idx:04d}",
            sport="nba",
            date=game_date,
            season=season,
            home_team_id=home_team,
            away_team_id=away_team,
            home_score=home_score,
            away_score=away_score,
            venue=f"Arena {home_team}",
            is_neutral_site=neutral_site,
            home_rest_days=home_rest,
            away_rest_days=away_rest,
        )
        games.append(game)
        last_played[home_team] = game_date
        last_played[away_team] = game_date
    return games
