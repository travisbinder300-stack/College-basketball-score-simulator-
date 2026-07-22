#!/usr/bin/env python3
"""Scrape game scores from any URL you provide and save as JSON.

Paste the URL of any schedule/results page and the script will scan every
HTML table on that page, pick out rows that look like game results (two
team names + two numeric scores + a date), normalize them into the
project's ``Game`` schema, and write a JSON file.

Usage
-----
    # Paste in whatever schedule page you want
    PYTHONPATH=src python scripts/scrape_data.py \\
        --url "https://example-site.com/ncaab/2024-schedule" \\
        --sport ncaab --season 2024

    # Multiple pages (e.g. one per month)
    PYTHONPATH=src python scripts/scrape_data.py \\
        --url "https://..." "https://..." \\
        --sport nba --season 2024

    # Custom output path
    PYTHONPATH=src python scripts/scrape_data.py \\
        --url "https://..." \\
        --sport mlb --season 2024 \\
        --output data/scraped/mlb_2024.json
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag  # type: ignore[import-untyped]

from multisports.data.schema import Game


_USER_AGENT = (
    "Mozilla/5.0 (compatible; multisports-scraper/1.0; "
    "+https://github.com/travisbinder300-stack)"
)
_REQUEST_DELAY = 2.0  # seconds between requests — be polite

# Supported sports (used only for schema context and output filename)
SPORTS = [
    "mlb",
    "nba",
    "ncaa_baseball",
    "ncaab",
    "ncaaf",
    "nfl",
    "nhl",
    "wnba",
]

# Date formats to try when parsing score-page date strings
_DATE_FORMATS = [
    "%a, %b %d, %Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d-%b-%Y",
]

# Heuristic: column header words that suggest a date column
_DATE_HEADERS = {"date", "game date", "game_date", "day", "when"}
# Heuristic: column header words that suggest score columns
_SCORE_HEADERS = {
    "pts", "points", "score", "r", "runs", "g", "goals",
    "visitor_pts", "home_pts", "away_pts", "away score", "home score",
}
# Heuristic: column header words that suggest team columns
_TEAM_HEADERS = {
    "team", "visitor", "home", "away", "home team", "away team",
    "visitor team", "home_team", "away_team",
}


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:  # nosec B310
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"HTTP error fetching {url!r}: {exc}") from exc


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def _safe_date(raw: str) -> Optional[date]:
    raw = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    # Try stripping a leading day-of-week ("Mon Nov 6, 2023" → "Nov 6, 2023")
    cleaned = re.sub(r"^\w{3,},?\s*", "", raw)
    if cleaned != raw:
        return _safe_date(cleaned)
    return None


def _looks_like_score(text: str) -> bool:
    return bool(re.fullmatch(r"\d{1,3}", text.strip()))


def _header_matches(text: str, keyword_set: set[str]) -> bool:
    return text.strip().lower() in keyword_set


# ---------------------------------------------------------------------------
# Generic table scraper
# ---------------------------------------------------------------------------

def _extract_games_from_table(
    table: Tag,
    sport: str,
    season: str,
    url: str,
    seen_ids: set[str],
    game_counter: list[int],
) -> List[Game]:
    """Try to extract Game objects from a single <table> element."""
    rows = table.find_all("tr")
    if not rows:
        return []

    # Collect header row
    header_row = rows[0]
    headers = [
        th.get_text(strip=True).lower()
        for th in header_row.find_all(["th", "td"])
    ]

    # Identify column indices by heuristic
    date_col: Optional[int] = None
    away_col: Optional[int] = None
    home_col: Optional[int] = None
    away_score_col: Optional[int] = None
    home_score_col: Optional[int] = None

    for idx, h in enumerate(headers):
        if date_col is None and _header_matches(h, _DATE_HEADERS):
            date_col = idx
        if h in {"visitor", "away", "away team", "away_team", "visitor team",
                 "visitor_team_name"}:
            away_col = idx
        if h in {"home", "home team", "home_team", "home_team_name"}:
            home_col = idx
        if h in {"visitor_pts", "away_pts", "away score", "pts"} and away_score_col is None:
            away_score_col = idx
        if h in {"home_pts", "home score"} and home_score_col is None:
            home_score_col = idx

    # If we can't map at least home/away teams, bail early on this table
    if away_col is None and home_col is None:
        return []

    games: List[Game] = []
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        # Skip sub-header rows
        if all(c.name == "th" for c in cells):
            continue

        texts = [c.get_text(strip=True) for c in cells]
        if not any(texts):
            continue

        # --- Date ---
        game_date: Optional[date] = None
        if date_col is not None and date_col < len(texts):
            game_date = _safe_date(texts[date_col])
        if game_date is None:
            # Try every cell in the row for a parseable date
            for t in texts:
                game_date = _safe_date(t)
                if game_date:
                    break
        if game_date is None:
            continue

        # --- Teams ---
        away_team = texts[away_col].strip() if away_col is not None and away_col < len(texts) else ""
        home_team = texts[home_col].strip() if home_col is not None and home_col < len(texts) else ""

        # If either team is blank, try to pull two non-date, non-score text cells
        if not away_team or not home_team:
            candidates = [
                t for t in texts
                if t and not _looks_like_score(t) and _safe_date(t) is None
            ]
            if len(candidates) >= 2:
                away_team = away_team or candidates[0]
                home_team = home_team or candidates[1]

        if not away_team or not home_team:
            continue

        # --- Scores ---
        away_score = 0
        home_score = 0
        if away_score_col is not None and away_score_col < len(texts):
            away_score = _safe_int(texts[away_score_col])
        if home_score_col is not None and home_score_col < len(texts):
            home_score = _safe_int(texts[home_score_col])
        if away_score == 0 and home_score == 0:
            # Fallback: grab first two numeric-looking cells
            numeric = [t for t in texts if _looks_like_score(t)]
            if len(numeric) >= 2:
                away_score = _safe_int(numeric[0])
                home_score = _safe_int(numeric[1])

        # --- Venue ---
        venue_candidates = [
            h for h in headers
            if "venue" in h or "arena" in h or "stadium" in h or "location" in h
        ]
        venue = ""
        if venue_candidates:
            vc_idx = headers.index(venue_candidates[0])
            if vc_idx < len(texts):
                venue = texts[vc_idx]
        venue = venue or "Unknown Venue"

        # --- Game ID ---
        game_counter[0] += 1
        game_id = f"{sport}_{game_date}_{away_team[:4]}_{home_team[:4]}_{game_counter[0]:04d}"
        # Deduplicate
        if game_id in seen_ids:
            continue
        seen_ids.add(game_id)

        try:
            games.append(
                Game(
                    id=game_id,
                    sport=sport,
                    date=game_date,
                    season=season,
                    home_team_id=home_team,
                    away_team_id=away_team,
                    home_score=home_score,
                    away_score=away_score,
                    venue=venue,
                    is_neutral_site=False,
                    home_rest_days=0,
                    away_rest_days=0,
                )
            )
        except (ValueError, TypeError):
            continue

    return games


def scrape_url(url: str, sport: str, season: str) -> List[Game]:
    """Fetch *url*, scan all HTML tables, and return normalized Game objects."""
    print(f"  Fetching {url}")
    html = _fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    all_games: List[Game] = []
    seen_ids: set[str] = set()
    counter = [0]

    for table in soup.find_all("table"):
        games = _extract_games_from_table(
            table=table,
            sport=sport,
            season=season,
            url=url,
            seen_ids=seen_ids,
            game_counter=counter,
        )
        all_games.extend(games)

    return all_games


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scrape game scores from any schedule/results page you provide.\n"
            "Paste one or more URLs with --url."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        nargs="+",
        required=True,
        metavar="URL",
        help="One or more schedule/results page URLs to scrape.",
    )
    parser.add_argument(
        "--sport",
        choices=sorted(SPORTS),
        default="ncaab",
        help="Sport key used for schema context and default output filename.",
    )
    parser.add_argument(
        "--season",
        default=str(datetime.now().year),
        help="Season label (e.g. '2024' or '2023-2024') stored on each game row.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Default: data/scraped/<sport>_<season>.json",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    all_games: List[Game] = []
    seen_ids: set[str] = set()

    for i, url in enumerate(args.url):
        games = scrape_url(url=url, sport=args.sport, season=args.season)
        for g in games:
            if g.id not in seen_ids:
                seen_ids.add(g.id)
                all_games.append(g)
        print(f"  → {len(games)} game(s) found")
        if i < len(args.url) - 1:
            time.sleep(_REQUEST_DELAY)

    output_path = (
        Path(args.output)
        if args.output
        else Path("data") / "scraped" / f"{args.sport}_{args.season}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([asdict(g) for g in all_games], indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\nSaved {len(all_games)} total game(s) to {output_path}")


if __name__ == "__main__":
    main()

