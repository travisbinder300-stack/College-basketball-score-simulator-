#!/usr/bin/env python3
"""
NBA Player Projection Props — Command-Line Interface

Usage examples
--------------
# Show projections for Luka Doncic vs Golden State Warriors (away game):
    python main.py --player luka_doncic --opponent GSW --away

# Luka vs OKC at home with prop lines:
    python main.py --player luka_doncic --opponent OKC \
        --props pts=28.5 reb=8.5 ast=9.5

# Show all available players:
    python main.py --list-players

# Show projection for every available player vs a common opponent:
    python main.py --all-players --opponent LAL
"""

import argparse
import sys

from nba_projections import get_all_players, PropAnalyzer


def parse_props(raw: list) -> dict:
    """Parse a list of 'stat=value' strings into a dict."""
    result = {}
    for item in raw:
        if "=" not in item:
            print(f"  [warn] Ignoring invalid prop format '{item}' (expected 'stat=value')")
            continue
        stat, _, val = item.partition("=")
        try:
            result[stat.strip()] = float(val.strip())
        except ValueError:
            print(f"  [warn] Ignoring non-numeric value in '{item}'")
    return result


def run_single(args) -> None:
    """Project stats for a single player."""
    prop_lines = parse_props(args.props) if args.props else {}
    home = not args.away

    analyzer = PropAnalyzer(
        player_id=args.player,
        opponent=args.opponent,
        home=home,
        recent_games=args.recent_games,
    )
    print(analyzer.display_report(prop_lines or None))


def run_all(args) -> None:
    """Project stats for all available players against the same opponent."""
    home = not args.away
    for player_id in get_all_players():
        try:
            analyzer = PropAnalyzer(
                player_id=player_id,
                opponent=args.opponent,
                home=home,
                recent_games=args.recent_games,
            )
            print(analyzer.display_report())
            print()
        except Exception as exc:
            print(f"  [error] Could not project {player_id}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NBA Player Projection Props",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--player",
        metavar="PLAYER_ID",
        help="Player ID to project (e.g. luka_doncic).",
    )
    parser.add_argument(
        "--opponent",
        metavar="TEAM",
        help="Three-letter opponent team abbreviation (e.g. GSW).",
    )
    parser.add_argument(
        "--away",
        action="store_true",
        default=False,
        help="Player is playing away (default: home).",
    )
    parser.add_argument(
        "--props",
        nargs="+",
        metavar="STAT=LINE",
        help="Optional sportsbook prop lines, e.g. pts=27.5 reb=8.5 ast=9.5",
    )
    parser.add_argument(
        "--recent-games",
        type=int,
        default=5,
        metavar="N",
        help="Number of recent games for rolling average (default: 5).",
    )
    parser.add_argument(
        "--list-players",
        action="store_true",
        default=False,
        help="List all available player IDs and exit.",
    )
    parser.add_argument(
        "--all-players",
        action="store_true",
        default=False,
        help="Run projections for all players (requires --opponent).",
    )

    args = parser.parse_args()

    if args.list_players:
        print("Available players:")
        for pid in get_all_players():
            print(f"  {pid}")
        sys.exit(0)

    if args.all_players:
        if not args.opponent:
            parser.error("--all-players requires --opponent")
        run_all(args)
        return

    if not args.player:
        parser.error("--player is required (or use --list-players / --all-players)")
    if not args.opponent:
        parser.error("--opponent is required")

    run_single(args)


if __name__ == "__main__":
    main()
