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
  python bb_stats_table.py              # loads bb_data.csv if present, else interactive
  python bb_stats_table.py --sample     # prints built-in sample data
  python bb_stats_table.py data.csv     # loads Rank,Teams,G,BB CSV (header optional)
"""

from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class BBRow:
    rank: str
    team: str
    g: int
    bb: int


# ---------------------------------------------------------------------------
# Built-in sample data  (NCAA Division I Baseball, approximate season stats)
# ---------------------------------------------------------------------------

SAMPLE_DATA: List[BBRow] = [
    BBRow(rank="1",  team="Georgia Tech",      g=9,  bb=79),
    BBRow(rank="2",  team="Oklahoma",          g=9,  bb=78),
    BBRow(rank="3",  team="SFA",               g=10, bb=73),
    BBRow(rank="4",  team="Miami (FL)",        g=10, bb=71),
    BBRow(rank="-",  team="Miami (OH)",        g=8,  bb=71),
    BBRow(rank="6",  team="New Mexico",        g=8,  bb=70),
    BBRow(rank="7",  team="UIW",               g=9,  bb=68),
    BBRow(rank="8",  team="Virginia",          g=8,  bb=67),
    BBRow(rank="9",  team="Pittsburgh",        g=7,  bb=66),
    BBRow(rank="10", team="Texas Tech",        g=8,  bb=65),
    BBRow(rank="11", team="LSU",               g=9,  bb=64),
    BBRow(rank="-",  team="Mercer",            g=9,  bb=64),
    BBRow(rank="-",  team="Ole Miss",          g=9,  bb=64),
    BBRow(rank="14", team="Wake Forest",       g=8,  bb=62),
    BBRow(rank="15", team="Longwood",          g=8,  bb=60),
    BBRow(rank="-",  team="Vanderbilt",        g=9,  bb=60),
    BBRow(rank="-",  team="Virginia Tech",     g=8,  bb=60),
    BBRow(rank="18", team="Missouri",          g=9,  bb=59),
    BBRow(rank="19", team="VMI",               g=8,  bb=58),
    BBRow(rank="20", team="Alabama",           g=9,  bb=57),
    BBRow(rank="-",  team="FIU",               g=10, bb=57),
    BBRow(rank="-",  team="Wofford",           g=8,  bb=57),
    BBRow(rank="23", team="Duke",              g=10, bb=56),
    BBRow(rank="-",  team="Georgia St.",       g=9,  bb=56),
    BBRow(rank="-",  team="Grambling",         g=8,  bb=56),
    BBRow(rank="-",  team="Texas A&M",         g=8,  bb=56),
    BBRow(rank="27", team="High Point",        g=9,  bb=55),
    BBRow(rank="-",  team="Mississippi St.",   g=9,  bb=55),
    BBRow(rank="-",  team="UNLV",              g=9,  bb=55),
    BBRow(rank="30", team="Baylor",            g=8,  bb=54),
    BBRow(rank="-",  team="Charleston So.",    g=8,  bb=54),
    BBRow(rank="32", team="ETSU",              g=8,  bb=53),
    BBRow(rank="-",  team="Georgia",           g=8,  bb=53),
    BBRow(rank="-",  team="Long Beach St.",    g=8,  bb=53),
    BBRow(rank="35", team="Kansas",            g=8,  bb=52),
    BBRow(rank="-",  team="New Orleans",       g=9,  bb=52),
    BBRow(rank="37", team="Jackson St.",       g=9,  bb=51),
    BBRow(rank="-",  team="La Salle",          g=7,  bb=51),
    BBRow(rank="-",  team="USC Upstate",       g=10, bb=51),
    BBRow(rank="-",  team="Western Ky.",       g=9,  bb=51),
    BBRow(rank="41", team="Austin Peay",       g=8,  bb=50),
    BBRow(rank="-",  team="Georgetown",        g=8,  bb=50),
    BBRow(rank="-",  team="Jacksonville",      g=9,  bb=50),
    BBRow(rank="-",  team="Kansas St.",        g=9,  bb=50),
    BBRow(rank="-",  team="Texas",             g=8,  bb=50),
    BBRow(rank="-",  team="Tulane",            g=9,  bb=50),
    BBRow(rank="-",  team="UNCW",              g=9,  bb=50),
    BBRow(rank="-",  team="UTSA",              g=8,  bb=50),
    BBRow(rank="49", team="Charlotte",         g=8,  bb=49),
    BBRow(rank="-",  team="Cincinnati",        g=9,  bb=49),
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
                rank = line[0].strip()          # keep as string; supports "-" ties
                team = line[1].strip()
                g    = int(line[2].strip())
                bb   = int(line[3].strip())
                rows.append(BBRow(rank=rank, team=team, g=g, bb=bb))
            except ValueError:
                continue

    # Re-sort by BB descending and re-rank
    rows.sort(key=lambda r: r.bb, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = str(idx)
    return rows


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

HEADERS = ["Rank", "Teams", "G", "BB"]


def format_table(rows: List[BBRow]) -> str:
    """Return a neatly aligned table string for the given BB rows."""
    data = [[r.rank, r.team, str(r.g), str(r.bb)] for r in rows]

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
        rows.append(BBRow(rank="-", team=team, g=g, bb=bb))
        print()

    # Sort by BB descending and assign ranks
    rows.sort(key=lambda r: r.bb, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = str(idx)
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_CSV = "bb_data.csv"


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
    elif os.path.isfile(DEFAULT_CSV):
        try:
            rows = load_csv(DEFAULT_CSV)
        except (OSError, ValueError) as exc:
            print(f"Error loading '{DEFAULT_CSV}': {exc}", file=sys.stderr)
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
