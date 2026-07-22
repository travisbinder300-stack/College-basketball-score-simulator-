#!/usr/bin/env python3
"""Fetch predictive power rankings from TeamRankings and save as CSV.

The script scrapes the ``/ranking/predictive-by-other/`` table for any
supported sport on TeamRankings.com and writes a clean CSV that can be fed
directly into the pipeline via ``Pipeline.run(rankings_path=...)``.

Usage
-----
    # Fetch current 2026 WNBA rankings
    PYTHONPATH=src python scripts/fetch_rankings.py --sport wnba --season 2026

    # Custom output path
    PYTHONPATH=src python scripts/fetch_rankings.py \\
        --sport wnba --season 2026 \\
        --output data/rankings/wnba_2026_predictive.csv

The script writes to ``data/rankings/<sport>_<season>_predictive.csv`` by
default.

Output columns
--------------
    rank, team, abbreviation, rating, win_pct, home_win_pct, away_win_pct

The current home-court rankings are also printed after the predictive
rankings are saved, along with away-court rankings.
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup  # type: ignore[import-untyped]


_USER_AGENT = (
    "Mozilla/5.0 (compatible; multisports-ranker/1.0; "
    "+https://github.com/travisbinder300-stack)"
)
_REQUEST_DELAY = 2.0

# TeamRankings sport slugs for the predictive-by-other rankings page
_SPORT_SLUGS: Dict[str, str] = {
    "nba": "nba",
    "wnba": "wnba",
    "ncaab": "ncaa-basketball",
    "nfl": "nfl",
    "ncaaf": "ncaa-football",
    "mlb": "mlb",
    "nhl": "nhl",
}


def _fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:  # nosec B310
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"HTTP error fetching {url!r}: {exc}") from exc


def _safe_float(text: str, default: float = 0.0) -> float:
    try:
        return float(text.strip().replace("%", "").replace("+", ""))
    except (ValueError, TypeError):
        return default


def _pct_to_float(text: str) -> float:
    """Convert '68.0%' → 0.680, or a bare decimal '0.680' to itself."""
    cleaned = text.strip().replace("%", "")
    try:
        val = float(cleaned)
        return val / 100.0 if val > 1.5 else val
    except (ValueError, TypeError):
        return 0.0


def _team_abbreviation(name: str) -> str:
    """Derive a short 3-letter abbreviation from a team name."""
    words = [w for w in re.split(r"[\s\-]+", name) if w]
    if len(words) == 1:
        return words[0][:3].upper()
    # Use the last word (usually the nickname) up to 3 chars
    return words[-1][:3].upper()


def fetch_rankings(sport: str) -> List[Dict[str, Any]]:
    """Fetch the predictive rankings table for *sport* from TeamRankings.

    Returns a list of dicts with keys:
        rank, team, abbreviation, rating, win_pct, home_win_pct, away_win_pct
    """
    slug = _SPORT_SLUGS.get(sport)
    if not slug:
        raise ValueError(
            f"Unsupported sport {sport!r}. Supported: {sorted(_SPORT_SLUGS)}"
        )
    url = f"https://www.teamrankings.com/{slug}/ranking/predictive-by-other/"
    print(f"  Fetching {url}")
    html = _fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    rows: List[Dict[str, Any]] = []
    for table in soup.find_all("table"):
        headers = [
            th.get_text(strip=True).lower()
            for th in table.find_all("tr")[0].find_all(["th", "td"])
        ]
        # Look for a table that has a "rating" or "power rating" column
        if not any("rating" in h or "power" in h for h in headers):
            continue

        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if not cells or all(not c for c in cells):
                continue
            if len(cells) < 3:
                continue

            # Column heuristics: rank (idx 0), team (idx 1), rating (first numeric)
            rank_text = cells[0]
            team_name = cells[1] if len(cells) > 1 else ""
            # Find the rating: first cell that looks like a signed float
            rating: float = 0.0
            win_pct: float = 0.0
            home_win_pct: float = 0.0
            away_win_pct: float = 0.0

            for idx, h in enumerate(headers):
                if idx >= len(cells):
                    break
                if "rating" in h or "power" in h:
                    rating = _safe_float(cells[idx])
                elif h in {"win%", "win pct", "pct", "win_pct"}:
                    win_pct = _pct_to_float(cells[idx])
                elif "home" in h and ("win" in h or "pct" in h):
                    home_win_pct = _pct_to_float(cells[idx])
                elif "away" in h and ("win" in h or "pct" in h):
                    away_win_pct = _pct_to_float(cells[idx])

            if not team_name:
                continue

            try:
                rank = int(rank_text)
            except ValueError:
                continue

            rows.append(
                {
                    "rank": rank,
                    "team": team_name,
                    "abbreviation": _team_abbreviation(team_name),
                    "rating": rating,
                    "win_pct": win_pct,
                    "home_win_pct": home_win_pct,
                    "away_win_pct": away_win_pct,
                }
            )

    if not rows:
        raise RuntimeError(
            f"No ranking rows found on {url}. "
            "The page layout may have changed — inspect the HTML and update the parser."
        )
    return rows


def _fetch_location_rankings(sport: str, location: str) -> List[Dict[str, str]]:
    """Fetch and return a home- or away-by-other table for *sport*.

    Location rankings are informational output only, so their source columns
    are preserved rather than coerced into the predictive-ratings schema.
    """
    slug = _SPORT_SLUGS.get(sport)
    if not slug:
        raise ValueError(
            f"Unsupported sport {sport!r}. Supported: {sorted(_SPORT_SLUGS)}"
        )
    url = f"https://www.teamrankings.com/{slug}/ranking/{location}-by-other/"
    print(f"  Fetching {url}")
    soup = BeautifulSoup(_fetch_html(url), "html.parser")

    for table in soup.find_all("table"):
        table_rows = table.find_all("tr")
        if not table_rows:
            continue
        headers = [
            cell.get_text(" ", strip=True)
            for cell in table_rows[0].find_all(["th", "td"])
        ]
        normalized_headers = [header.lower() for header in headers]
        if not any(location in header for header in normalized_headers):
            continue
        if not any("team" in header for header in normalized_headers):
            continue

        rows: List[Dict[str, str]] = []
        for tr in table_rows[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
            if len(cells) != len(headers) or not any(cells):
                continue
            rows.append(dict(zip(headers, cells)))
        if rows:
            return rows

    raise RuntimeError(
        f"No {location} ranking rows found on {url}. "
        "The page layout may have changed — inspect the HTML and update the parser."
    )


def fetch_home_rankings(sport: str) -> List[Dict[str, str]]:
    """Fetch and return the home-by-other table for *sport*."""
    return _fetch_location_rankings(sport, "home")


def fetch_away_rankings(sport: str) -> List[Dict[str, str]]:
    """Fetch and return the away-by-other table for *sport*."""
    return _fetch_location_rankings(sport, "away")


def print_home_rankings(rows: List[Dict[str, str]]) -> None:
    """Print home ranking rows in the source table's column order."""
    _print_location_rankings(rows, "Home")


def print_away_rankings(rows: List[Dict[str, str]]) -> None:
    """Print away ranking rows in the source table's column order."""
    _print_location_rankings(rows, "Away")


def _print_location_rankings(rows: List[Dict[str, str]], location: str) -> None:
    """Print location ranking rows in the source table's column order."""
    if not rows:
        return
    ranked_rows = [
        row
        for _, row in sorted(
            enumerate(rows), key=lambda item: _ranking_number(item[1], item[0])
        )
    ]
    headers = list(rows[0])
    print(f"\n{location}-by-other rankings:")
    print(" | ".join(headers))
    print("-+-".join("-" * len(header) for header in headers))
    for row in rows:
        print(" | ".join(row.get(header, "") for header in headers))
    print(f"Best team: {_team_name(ranked_rows[0])}")
    print(f"Worst team: {_team_name(ranked_rows[-1])}")


def _ranking_number(row: Dict[str, str], fallback: int) -> int:
    """Return a row's numeric rank, or its source position when unavailable."""
    try:
        return int(row.get("Rank", "").strip())
    except (AttributeError, ValueError):
        return fallback


def _team_name(row: Dict[str, str]) -> str:
    """Return a row's team name using the source table's Team column."""
    return row.get("Team", row.get("team", "")).strip()


def save_rankings_csv(rows: List[Dict[str, Any]], output_path: Path) -> None:
    """Write ranking rows to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["rank", "team", "abbreviation", "rating", "win_pct", "home_win_pct", "away_win_pct"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {len(rows)} team(s) to {output_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch predictive power rankings from TeamRankings and save as CSV.\n"
            "Output: data/rankings/<sport>_<season>_predictive.csv"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--sport",
        choices=sorted(_SPORT_SLUGS),
        default="wnba",
        help="Sport to fetch rankings for.",
    )
    parser.add_argument(
        "--season",
        default=str(datetime.now().year),
        help="Season label used only in the default output filename (e.g. '2026').",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path. Default: data/rankings/<sport>_<season>_predictive.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    rows = fetch_rankings(sport=args.sport)
    home_rows = fetch_home_rankings(sport=args.sport)
    away_rows = fetch_away_rankings(sport=args.sport)

    output_path = (
        Path(args.output)
        if args.output
        else Path("data") / "rankings" / f"{args.sport}_{args.season}_predictive.csv"
    )
    save_rankings_csv(rows, output_path)
    print_home_rankings(home_rows)
    print_away_rankings(away_rows)
    sport_upper = args.sport.upper()
    print(f"\nFetched {len(rows)} team(s) for {sport_upper} {args.season}.")
    print(
        f"\nTo use in the pipeline:\n"
        f"    Pipeline({sport_upper}_CONFIG).run(games, rankings_path='{output_path}')"
    )


if __name__ == "__main__":
    main()
