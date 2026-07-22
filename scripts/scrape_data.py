#!/usr/bin/env python3
"""Scrape historical game scores from Sports-Reference sites and save as JSON.

Supported sports and sources
-----------------------------
  nba        https://www.basketball-reference.com
  wnba       https://www.basketball-reference.com
  ncaab      https://www.sports-reference.com/cbb
  nfl        https://www.pro-football-reference.com
  mlb        https://www.baseball-reference.com
  nhl        https://www.hockey-reference.com

Data is scraped from publicly available monthly schedule/results pages and
normalized into the project's ``Game`` schema, then written to JSON.

Usage
-----
    PYTHONPATH=src python scripts/scrape_data.py --sport ncaab --season 2024
    PYTHONPATH=src python scripts/scrape_data.py --sport nba --season 2024 --months 10 11
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup  # type: ignore[import-untyped]

from multisports.data.schema import Game


_USER_AGENT = (
    "Mozilla/5.0 (compatible; multisports-scraper/1.0; +https://github.com/travisbinder300-stack)"
)
_REQUEST_DELAY = 3.0  # seconds between requests — be polite to the server


# ---------------------------------------------------------------------------
# Site metadata
# ---------------------------------------------------------------------------

_SITE_INFO: Dict[str, Dict[str, Any]] = {
    "nba": {
        "base": "https://www.basketball-reference.com",
        "path": "/leagues/NBA_{season}_games-{month}.html",
        "months": [10, 11, 12, 1, 2, 3, 4, 5, 6],
        "season_offset": 0,  # season year == year of the *end* of the season
    },
    "wnba": {
        "base": "https://www.basketball-reference.com",
        "path": "/wnba/years/{season}_games.html",
        "months": [],  # single-page, no monthly split
        "season_offset": 0,
    },
    "ncaab": {
        "base": "https://www.sports-reference.com",
        "path": "/cbb/seasons/men/{season}-schedule.html",
        "months": [],  # single-page
        "season_offset": 0,
    },
    "nfl": {
        "base": "https://www.pro-football-reference.com",
        "path": "/years/{season}/games.htm",
        "months": [],
        "season_offset": 0,
    },
    "mlb": {
        "base": "https://www.baseball-reference.com",
        "path": "/leagues/majors/{season}-schedule.shtml",
        "months": [],
        "season_offset": 0,
    },
    "nhl": {
        "base": "https://www.hockey-reference.com",
        "path": "/leagues/NHL_{season}_games.html",
        "months": [],
        "season_offset": 0,
    },
}

_MONTH_NAMES = {
    1: "january",
    2: "february",
    3: "march",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "august",
    9: "september",
    10: "october",
    11: "november",
    12: "december",
}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:  # nosec B310
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"HTTP error fetching {url!r}: {exc}") from exc


def _parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


# ---------------------------------------------------------------------------
# Table parsers
# ---------------------------------------------------------------------------

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def _safe_date(raw: str) -> Optional[date]:
    for fmt in ("%a, %b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%b %d, %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_bref_game_table(
    soup: BeautifulSoup,
    sport: str,
    season: str,
    table_id: str = "schedule",
) -> List[Game]:
    """Parse a Basketball/Hockey/Pro-Football-Reference schedule table."""
    table = soup.find("table", id=table_id)
    if table is None:
        return []

    games: List[Game] = []
    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        # Skip header rows (cells are all <th> with scope="col")
        if all(c.name == "th" for c in cells):
            continue
        row_data = {c.get("data-stat", ""): c.get_text(strip=True) for c in cells}

        date_str = row_data.get("date_game") or row_data.get("game_date", "")
        if not date_str or date_str.lower() in {"date", "playoffs"}:
            continue
        game_date = _safe_date(date_str)
        if game_date is None:
            continue

        visitor = row_data.get("visitor_team_name") or row_data.get("away_team", "")
        home = row_data.get("home_team_name") or row_data.get("home_team", "")
        visitor_pts = _safe_int(row_data.get("visitor_pts") or row_data.get("away_pts", 0))
        home_pts = _safe_int(row_data.get("home_pts", 0) or row_data.get("pts", 0))

        if not visitor or not home:
            continue

        venue = row_data.get("game_location", "") or row_data.get("arena", "")
        neutral = "@" not in str(row_data.get("game_location", "")) and bool(venue)

        row_cells = row.find_all(["td", "th"])
        game_id_cell = row.find("td", {"data-stat": "date_game"})
        game_link = game_id_cell.find("a") if game_id_cell else None
        game_id = game_link["href"].split("/")[-1].replace(".html", "") if game_link and game_link.get("href") else f"{sport}_{game_date}_{visitor[:3]}_{home[:3]}"

        games.append(
            Game(
                id=game_id,
                sport=sport,
                date=game_date,
                season=season,
                home_team_id=home,
                away_team_id=visitor,
                home_score=home_pts,
                away_score=visitor_pts,
                venue=venue or "Unknown Venue",
                is_neutral_site=neutral,
                home_rest_days=0,
                away_rest_days=0,
            )
        )
    return games


def _parse_baseball_ref_schedule(
    soup: BeautifulSoup,
    sport: str,
    season: str,
) -> List[Game]:
    """Parse a Baseball-Reference schedule page."""
    games: List[Game] = []
    for row in soup.find_all("p", class_="game"):
        # BBRef uses <p class="game"> with embedded team/score text
        text = row.get_text(" ", strip=True)
        # Fall back to generic table parser if structure differs
        _ = text  # currently using table fallback below

    # Try the standard schedule table as fallback
    return _parse_bref_game_table(soup, sport, season, table_id="schedule")


def _parse_cbb_schedule(
    soup: BeautifulSoup,
    sport: str,
    season: str,
) -> List[Game]:
    """Parse Sports-Reference CBB schedule (single-page)."""
    return _parse_bref_game_table(soup, sport, season, table_id="schedule")


# ---------------------------------------------------------------------------
# High-level scraper per sport
# ---------------------------------------------------------------------------

def _urls_for_sport(sport: str, season: int, months: Optional[List[int]]) -> List[str]:
    info = _SITE_INFO[sport]
    base = info["base"]
    path_tpl = info["path"]
    default_months = info["months"]
    selected_months = months if months else default_months

    if selected_months:
        return [
            base + path_tpl.format(season=season, month=_MONTH_NAMES[m])
            for m in selected_months
        ]
    # Single-page sports
    return [base + path_tpl.format(season=season)]


def scrape_sport(
    sport: str,
    season: int,
    months: Optional[List[int]] = None,
) -> List[Game]:
    """Scrape historical game data for *sport* and *season*."""
    urls = _urls_for_sport(sport, season, months)
    season_str = str(season)
    all_games: List[Game] = []
    seen_ids: set[str] = set()

    for url in urls:
        print(f"  Fetching {url}")
        try:
            html = _fetch_html(url)
        except RuntimeError as exc:
            print(f"  WARNING: {exc} — skipping")
            time.sleep(_REQUEST_DELAY)
            continue

        soup = _parse_html(html)

        if sport == "mlb":
            games = _parse_baseball_ref_schedule(soup, sport, season_str)
        elif sport == "ncaab":
            games = _parse_cbb_schedule(soup, sport, season_str)
        else:
            games = _parse_bref_game_table(soup, sport, season_str)

        for game in games:
            if game.id not in seen_ids:
                seen_ids.add(game.id)
                all_games.append(game)

        time.sleep(_REQUEST_DELAY)

    return all_games


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape historical game scores from Sports-Reference sites."
    )
    parser.add_argument("--sport", choices=sorted(_SITE_INFO.keys()), default="ncaab")
    parser.add_argument(
        "--season",
        type=int,
        default=datetime.now().year,
        help="Season year (e.g. 2024 means the 2023-24 season for NBA/NCAAB).",
    )
    parser.add_argument(
        "--months",
        type=int,
        nargs="+",
        default=None,
        metavar="M",
        help="Restrict to specific months (1-12). Only relevant for NBA.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Default: data/scraped/<sport>_<season>.json",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    print(f"Scraping {args.sport.upper()} season {args.season} ...")
    games = scrape_sport(sport=args.sport, season=args.season, months=args.months)

    output_path = (
        Path(args.output)
        if args.output
        else Path("data") / "scraped" / f"{args.sport}_{args.season}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([asdict(g) for g in games], indent=2, default=str),
        encoding="utf-8",
    )
    print(f"Saved {len(games)} games to {output_path}")


if __name__ == "__main__":
    main()
