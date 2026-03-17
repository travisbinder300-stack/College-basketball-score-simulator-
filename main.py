"""
main.py
-------
Entry point for the NBA Player Prop Projection tool.

Usage
-----
Run all projections (home game):
    python main.py

Run all projections (away game):
    python main.py --away

Project a specific player by name:
    python main.py --player "Player Name"

Show help:
    python main.py --help
"""

import argparse
import sys

from players import PLAYERS
from nba_player_props import project_all, print_all, PropProjection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NBA Player Prop Projection Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--away",
        action="store_true",
        default=False,
        help="Use away-game context instead of home (default: home).",
    )
    parser.add_argument(
        "--player",
        metavar="NAME",
        default=None,
        help="Project a single player by name (case-insensitive partial match).",
    )
    parser.add_argument(
        "--prop",
        metavar="CATEGORY",
        default=None,
        help=(
            "Filter output to a single prop category. "
            "Options: points, rebounds, assists, steals, blocks, "
            "three_pointers, turnovers, pra, steals_blocks."
        ),
    )
    return parser.parse_args()


def filter_players(name_query: str) -> list:
    """Return player dictionaries whose names contain the query string."""
    query = name_query.lower()
    return [p for p in PLAYERS if query in p["name"].lower()]


def print_single_prop(projections: list, prop: str) -> None:
    """Print only one prop category for each player."""
    valid_props = {
        "points", "rebounds", "assists", "steals", "blocks",
        "three_pointers", "turnovers", "pra", "steals_blocks",
    }
    if prop not in valid_props:
        print(f"Unknown prop '{prop}'. Valid options: {', '.join(sorted(valid_props))}")
        sys.exit(1)

    label_map = {
        "points": "Points",
        "rebounds": "Rebounds",
        "assists": "Assists",
        "steals": "Steals",
        "blocks": "Blocks",
        "three_pointers": "3-Pointers Made",
        "turnovers": "Turnovers",
        "pra": "Pts + Reb + Ast (PRA)",
        "steals_blocks": "Steals + Blocks",
    }

    print(f"\n  {'Player':<30}  {'Team':<24}  {label_map[prop]:>10}")
    print(f"  {'-' * 68}")
    for proj in projections:
        p = proj.player
        value = proj.get(prop)
        print(f"  {p.name:<30}  {p.team:<24}  {value:>10.1f}")
    print()


def main() -> None:
    args = parse_args()
    is_home = not args.away

    # Select player subset
    if args.player:
        data = filter_players(args.player)
        if not data:
            print(f"No player found matching '{args.player}'.")
            sys.exit(1)
    else:
        data = PLAYERS

    projections: list[PropProjection] = project_all(data, is_home=is_home)

    if not projections:
        print("No players to project. Add players to players.py and run again.")
        return

    if args.prop:
        print_single_prop(projections, args.prop)
    else:
        print_all(projections)


if __name__ == "__main__":
    main()
