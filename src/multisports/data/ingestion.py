"""Data ingestion and synthetic sample generation utilities."""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from .schema import Game


def _generate_games(
    sport: str,
    n: int,
    seed: int,
    num_teams: int,
    start_date: date,
    season: str,
    games_per_day: int,
    total_mean: float,
    total_std: float,
    total_min: float,
    total_max: float,
    home_edge: float,
    margin_std: float,
    min_team_score: int,
    rest_days_lo: int,
    rest_days_hi: int,
    rest_cap: int,
    arena_prefix: str,
    neutral_site_prob: float = 0.02,
) -> List[Game]:
    """Generic synthetic game generator shared across all sports."""
    if n <= 0:
        return []

    rng = np.random.default_rng(seed)
    teams = [f"{sport.upper()}_{idx:02d}" for idx in range(num_teams)]
    team_attack = {t: rng.normal(total_mean / 2, total_std / 2) for t in teams}
    team_defense = {t: rng.normal(total_mean / 2, total_std / 2) for t in teams}
    last_played: Dict[str, date] = {}
    games: List[Game] = []

    for idx in range(n):
        game_date = start_date + timedelta(days=idx // games_per_day)
        home_team, away_team = rng.choice(teams, size=2, replace=False).tolist()
        home_rest = (
            int(np.clip((game_date - last_played[home_team]).days, 1, rest_cap))
            if home_team in last_played
            else int(rng.integers(rest_days_lo, rest_days_hi))
        )
        away_rest = (
            int(np.clip((game_date - last_played[away_team]).days, 1, rest_cap))
            if away_team in last_played
            else int(rng.integers(rest_days_lo, rest_days_hi))
        )
        neutral_site = bool(rng.random() < neutral_site_prob)

        expected_total = (
            team_attack[home_team]
            + team_attack[away_team]
            - team_defense[home_team] * 0.3
            - team_defense[away_team] * 0.3
            + (home_edge if not neutral_site else 0.0)
        )
        total = int(np.clip(rng.normal(expected_total, total_std), total_min, total_max))
        edge = home_edge if not neutral_site else 0.0
        margin = int(round(rng.normal(edge, margin_std)))
        home_score = max(min_team_score, int(round(total / 2 + margin / 2)))
        away_score = max(min_team_score, total - home_score)
        total = home_score + away_score

        games.append(
            Game(
                id=f"{sport}_{idx:04d}",
                sport=sport,
                date=game_date,
                season=season,
                home_team_id=home_team,
                away_team_id=away_team,
                home_score=home_score,
                away_score=away_score,
                venue=f"{arena_prefix} {home_team}",
                is_neutral_site=neutral_site,
                home_rest_days=home_rest,
                away_rest_days=away_rest,
            )
        )
        last_played[home_team] = game_date
        last_played[away_team] = game_date

    return games

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
    return _generate_games(
        sport="nba",
        n=n,
        seed=seed,
        num_teams=10,
        start_date=date(2023, 10, 20),
        season="2023-2024",
        games_per_day=3,
        total_mean=222.0,
        total_std=12.0,
        total_min=170.0,
        total_max=275.0,
        home_edge=2.5,
        margin_std=10.0,
        min_team_score=80,
        rest_days_lo=1,
        rest_days_hi=4,
        rest_cap=14,
        arena_prefix="Arena",
    )


def generate_sample_nfl_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic NFL games suitable for pipeline testing and demos."""
    return _generate_games(
        sport="nfl",
        n=n,
        seed=seed,
        num_teams=16,
        start_date=date(2023, 9, 7),
        season="2023",
        games_per_day=14,
        total_mean=45.0,
        total_std=10.0,
        total_min=14.0,
        total_max=90.0,
        home_edge=2.5,
        margin_std=10.0,
        min_team_score=3,
        rest_days_lo=6,
        rest_days_hi=14,
        rest_cap=21,
        arena_prefix="Stadium",
        neutral_site_prob=0.01,
    )


def generate_sample_mlb_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic MLB games suitable for pipeline testing and demos."""
    return _generate_games(
        sport="mlb",
        n=n,
        seed=seed,
        num_teams=15,
        start_date=date(2023, 4, 1),
        season="2023",
        games_per_day=7,
        total_mean=8.8,
        total_std=2.5,
        total_min=1.0,
        total_max=25.0,
        home_edge=0.3,
        margin_std=3.0,
        min_team_score=0,
        rest_days_lo=1,
        rest_days_hi=3,
        rest_cap=10,
        arena_prefix="Ballpark",
    )


def generate_sample_nhl_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic NHL games suitable for pipeline testing and demos."""
    return _generate_games(
        sport="nhl",
        n=n,
        seed=seed,
        num_teams=16,
        start_date=date(2023, 10, 10),
        season="2023-2024",
        games_per_day=5,
        total_mean=5.8,
        total_std=1.6,
        total_min=1.0,
        total_max=14.0,
        home_edge=0.2,
        margin_std=2.0,
        min_team_score=0,
        rest_days_lo=1,
        rest_days_hi=4,
        rest_cap=7,
        arena_prefix="Rink",
    )


def generate_sample_wnba_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic WNBA games suitable for pipeline testing and demos."""
    return _generate_games(
        sport="wnba",
        n=n,
        seed=seed,
        num_teams=12,
        start_date=date(2024, 5, 14),
        season="2024",
        games_per_day=3,
        total_mean=158.0,
        total_std=10.0,
        total_min=120.0,
        total_max=200.0,
        home_edge=2.0,
        margin_std=9.0,
        min_team_score=55,
        rest_days_lo=1,
        rest_days_hi=4,
        rest_cap=7,
        arena_prefix="Arena",
    )


def generate_sample_ncaab_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic NCAA Men's Basketball games for pipeline testing and demos."""
    return _generate_games(
        sport="ncaab",
        n=n,
        seed=seed,
        num_teams=20,
        start_date=date(2023, 11, 6),
        season="2023-2024",
        games_per_day=10,
        total_mean=145.0,
        total_std=12.0,
        total_min=105.0,
        total_max=200.0,
        home_edge=3.5,
        margin_std=11.0,
        min_team_score=45,
        rest_days_lo=2,
        rest_days_hi=7,
        rest_cap=10,
        arena_prefix="Fieldhouse",
        neutral_site_prob=0.05,
    )


def generate_sample_ncaaf_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic NCAA Men's Football (FBS) games for pipeline testing and demos."""
    return _generate_games(
        sport="ncaaf",
        n=n,
        seed=seed,
        num_teams=20,
        start_date=date(2023, 9, 2),
        season="2023",
        games_per_day=25,
        total_mean=55.0,
        total_std=13.0,
        total_min=10.0,
        total_max=110.0,
        home_edge=3.0,
        margin_std=14.0,
        min_team_score=0,
        rest_days_lo=6,
        rest_days_hi=14,
        rest_cap=21,
        arena_prefix="Stadium",
        neutral_site_prob=0.06,
    )


def generate_sample_ncaa_baseball_games(n: int = 200, seed: int = 42) -> List[Game]:
    """Generate synthetic NCAA Baseball games for pipeline testing and demos."""
    return _generate_games(
        sport="ncaa_baseball",
        n=n,
        seed=seed,
        num_teams=20,
        start_date=date(2024, 2, 16),
        season="2024",
        games_per_day=10,
        total_mean=12.5,
        total_std=3.5,
        total_min=1.0,
        total_max=35.0,
        home_edge=0.5,
        margin_std=4.0,
        min_team_score=0,
        rest_days_lo=1,
        rest_days_hi=4,
        rest_cap=5,
        arena_prefix="Ballpark",
        neutral_site_prob=0.08,
    )

