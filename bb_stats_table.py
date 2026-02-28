#!/usr/bin/env python3
"""
College Baseball – Base on Balls (BB) Stats Table
==================================================
Print a ranked table of teams sorted by total base on balls (walks) allowed.

Columns
-------
  Rank  – BB rank (1 = most walks allowed)
  Teams – team name
  G     – games played
  BB    – total base on balls (walks issued)

Usage
-----
  python bb_stats_table.py              # interactive: enter teams manually
  python bb_stats_table.py --sample     # prints built-in sample data
  python bb_stats_table.py data.csv     # loads Rank,Teams,G,BB CSV (header optional)
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class BBRow:
    rank: int
    team: str
    g: int
    bb: int


# ---------------------------------------------------------------------------
# Built-in sample data  (NCAA Division I Baseball, approximate season stats)
# ---------------------------------------------------------------------------

SAMPLE_DATA: List[BBRow] = [
    BBRow(rank=1,  team="Louisiana",            g=56, bb=367),
    BBRow(rank=2,  team="Texas",                g=60, bb=358),
    BBRow(rank=3,  team="Auburn",               g=59, bb=341),
    BBRow(rank=4,  team="Tennessee",            g=63, bb=334),
    BBRow(rank=5,  team="Miami (FL)",           g=57, bb=326),
    BBRow(rank=6,  team="Oregon State",         g=55, bb=318),
    BBRow(rank=7,  team="Virginia",             g=58, bb=309),
    BBRow(rank=8,  team="Vanderbilt",           g=61, bb=301),
    BBRow(rank=9,  team="Arkansas",             g=62, bb=295),
    BBRow(rank=10, team="LSU",                  g=64, bb=289),
    BBRow(rank=11, team="Ole Miss",             g=57, bb=282),
    BBRow(rank=12, team="Florida",              g=59, bb=276),
    BBRow(rank=13, team="Stanford",             g=54, bb=271),
    BBRow(rank=14, team="TCU",                  g=58, bb=265),
    BBRow(rank=15, team="North Carolina",       g=56, bb=259),
    BBRow(rank=16, team="Dallas Baptist",       g=55, bb=253),
    BBRow(rank=17, team="Louisville",           g=57, bb=247),
    BBRow(rank=18, team="Georgia Tech",         g=56, bb=241),
    BBRow(rank=19, team="Southern Miss",        g=58, bb=235),
    BBRow(rank=20, team="Arizona",              g=53, bb=229),
    BBRow(rank=21, team="NC State",             g=55, bb=223),
    BBRow(rank=22, team="South Carolina",       g=57, bb=217),
    BBRow(rank=23, team="Indiana",              g=52, bb=211),
    BBRow(rank=24, team="Coastal Carolina",     g=55, bb=205),
    BBRow(rank=25, team="East Carolina",        g=56, bb=199),
]


# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------

def load_csv(path: str) -> List[BBRow]:
    """
    Load BB stats from a CSV file.
    Accepted column orders (case-insensitive header OR headerless):
      Rank, Teams, G, BB
    Rows are sorted by BB descending and re-ranked automatically.
    """
    rows: List[BBRow] = []
    with open(path, newline="", encoding="utf-8") as fh:
        sample = fh.read(1024)
        fh.seek(0)
        has_header = not sample.strip()[0].isdigit()
        reader = csv.reader(fh)
        if has_header:
            next(reader, None)          # skip header line
        for line in reader:
            if len(line) < 4:
                continue
            try:
                rank = int(line[0].strip())
                team = line[1].strip()
                g    = int(line[2].strip())
                bb   = int(line[3].strip())
                rows.append(BBRow(rank=rank, team=team, g=g, bb=bb))
            except ValueError:
                continue

    # Re-sort by BB descending and re-rank
    rows.sort(key=lambda r: r.bb, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = idx
    return rows


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

HEADERS = ["Rank", "Teams", "G", "BB"]


def format_table(rows: List[BBRow]) -> str:
    """Return a neatly aligned table string for the given BB rows."""
    data = [[str(r.rank), r.team, str(r.g), str(r.bb)] for r in rows]

    # Compute column widths
    widths = [len(h) for h in HEADERS]
    for row in data:
        for c, val in enumerate(row):
            widths[c] = max(widths[c], len(val))

    sep = "-" * (sum(widths) + 3 * (len(widths) - 1))

    def fmt_row(vals: List[str], header: bool = False) -> str:
        out = []
        for c, v in enumerate(vals):
            # Teams column: left-align; all others: right-align
            if c == 1:
                out.append(v.ljust(widths[c]))
            else:
                out.append(v.rjust(widths[c]))
        return "  ".join(out)

    lines = [
        "BASE ON BALLS STATS",
        sep,
        fmt_row(HEADERS, header=True),
        sep,
    ]
    for row in data:
        lines.append(fmt_row(row))
    lines.append(sep)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(rows: List[BBRow]) -> str:
    """Return a plain-text analysis of the BB stats rows."""
    if not rows:
        return "No data to analyze."

    total_teams = len(rows)
    total_bb    = sum(r.bb for r in rows)
    total_g     = sum(r.g  for r in rows)
    avg_bb      = total_bb / total_teams
    avg_g       = total_g  / total_teams

    leader      = rows[0]
    trailer     = rows[-1]
    bb_range    = leader.bb - trailer.bb

    # BB per game rate for every team, then take top-5 and bottom-5
    rates = sorted(rows, key=lambda r: r.bb / r.g, reverse=True)
    top_rate    = rates[:5]
    bottom_rate = rates[-5:]

    # Average BB/G across all teams
    avg_bb_per_g = sum(r.bb / r.g for r in rows) / total_teams

    lines = [
        "ANALYSIS",
        f"  Teams listed          : {total_teams}",
        f"  Total BB (all teams)  : {total_bb}",
        f"  Avg BB per team       : {avg_bb:.1f}",
        f"  Avg games per team    : {avg_g:.1f}",
        f"  Avg BB/G (rate)       : {avg_bb_per_g:.2f}",
        "",
        f"  BB leader  : {leader.team} — {leader.bb} BB in {leader.g} G "
        f"({leader.bb / leader.g:.2f} BB/G)",
        f"  BB trailer : {trailer.team} — {trailer.bb} BB in {trailer.g} G "
        f"({trailer.bb / trailer.g:.2f} BB/G)",
        f"  BB range   : {bb_range} ({leader.team} vs {trailer.team})",
        "",
        "  Top 5 by BB/G rate:",
    ]
    for r in top_rate:
        lines.append(f"    {r.rank:>3}.  {r.team:<22s}  {r.bb / r.g:.2f} BB/G  ({r.bb} BB, {r.g} G)")

    lines += ["", "  Bottom 5 by BB/G rate:"]
    for r in bottom_rate:
        lines.append(f"    {r.rank:>3}.  {r.team:<22s}  {r.bb / r.g:.2f} BB/G  ({r.bb} BB, {r.g} G)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive manual entry
# ---------------------------------------------------------------------------

def prompt_rows() -> List[BBRow]:
    """
    Interactively ask the user to enter BB stats row by row.
    Press Enter with a blank team name (or Ctrl-C) to finish entry.
    Rows are sorted by BB descending and ranked automatically.
    """
    print("Enter BB stats (leave Team blank to finish):")
    rows: List[BBRow] = []
    while True:
        try:
            team = input("  Team name  : ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not team:
            break
        while True:
            try:
                g_str = input("  Games (G)  : ").strip()
                g = int(g_str)
                if g <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a positive integer for G.")
        while True:
            try:
                bb_str = input("  Base on Balls (BB): ").strip()
                bb = int(bb_str)
                if bb < 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a non-negative integer for BB.")
        rows.append(BBRow(rank=0, team=team, g=g, bb=bb))
        print()

    # Sort by BB descending and assign ranks
    rows.sort(key=lambda r: r.bb, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = idx
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    arg: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None

    if arg == "--sample":
        rows: List[BBRow] = SAMPLE_DATA
    elif arg:
        try:
            rows = load_csv(arg)
        except (OSError, ValueError) as exc:
            print(f"Error loading '{arg}': {exc}", file=sys.stderr)
            return 1
    else:
        rows = prompt_rows()
        if not rows:
            print("No data entered. Exiting.")
            return 0

    print(format_table(rows))
    print()
    print(analyze(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
