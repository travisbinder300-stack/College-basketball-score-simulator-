#!/usr/bin/env python3
"""
College Baseball – Double Play (DP) Stats Table
================================================
Print a ranked table of teams sorted by total double plays (DP) turned.

Columns
-------
  Rank  – DP rank (1 = most double plays turned)
  Team  – team name
  G     – games played
  DP    – total double plays turned

Usage
-----
  python dp_stats_table.py              # loads dp_data.csv if present, else interactive
  python dp_stats_table.py --sample     # prints built-in sample data
  python dp_stats_table.py data.csv     # loads Rank,Team,G,DP CSV (header optional)
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
class DPRow:
    rank: str
    team: str
    g: int
    dp: int


# ---------------------------------------------------------------------------
# Built-in sample data  (NCAA Division I Baseball, approximate season stats)
# ---------------------------------------------------------------------------

SAMPLE_DATA: List[DPRow] = [
    DPRow(rank="1",  team="Texas A&M",        g=10, dp=18),
    DPRow(rank="2",  team="LSU",              g=9,  dp=17),
    DPRow(rank="-",  team="Vanderbilt",       g=9,  dp=17),
    DPRow(rank="4",  team="Ole Miss",         g=9,  dp=16),
    DPRow(rank="-",  team="Virginia",         g=8,  dp=16),
    DPRow(rank="6",  team="Georgia Tech",     g=9,  dp=15),
    DPRow(rank="-",  team="Miami (FL)",       g=10, dp=15),
    DPRow(rank="-",  team="TCU",              g=9,  dp=15),
    DPRow(rank="9",  team="Arkansas",         g=9,  dp=14),
    DPRow(rank="-",  team="Florida",          g=9,  dp=14),
    DPRow(rank="-",  team="North Carolina",   g=9,  dp=14),
    DPRow(rank="-",  team="Oklahoma",         g=9,  dp=14),
    DPRow(rank="13", team="Auburn",           g=9,  dp=13),
    DPRow(rank="-",  team="Duke",             g=10, dp=13),
    DPRow(rank="-",  team="Georgia",          g=8,  dp=13),
    DPRow(rank="-",  team="Mississippi St.",  g=9,  dp=13),
    DPRow(rank="-",  team="Notre Dame",       g=9,  dp=13),
    DPRow(rank="-",  team="Texas",            g=8,  dp=13),
    DPRow(rank="19", team="Alabama",          g=9,  dp=12),
    DPRow(rank="-",  team="Arizona",          g=9,  dp=12),
]


# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------

def load_csv(path: str) -> List[DPRow]:
    """
    Load DP stats from a CSV file.
    Accepted column order (case-insensitive header OR headerless):
      Rank, Team, G, DP
    Rows are sorted by DP descending and re-ranked automatically.
    """
    rows: List[DPRow] = []
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
                rank = line[0].strip()
                team = line[1].strip()
                g    = int(line[2].strip())
                dp   = int(line[3].strip())
                rows.append(DPRow(rank=rank, team=team, g=g, dp=dp))
            except ValueError:
                continue

    # Re-sort by DP descending and re-rank
    rows.sort(key=lambda r: r.dp, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = str(idx)
    return rows


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

HEADERS = ["Rank", "Team", "G", "DP"]


def format_table(rows: List[DPRow]) -> str:
    """Return a neatly aligned table string for the given DP rows."""
    data = [[r.rank, r.team, str(r.g), str(r.dp)] for r in rows]

    # Compute column widths
    widths = [len(h) for h in HEADERS]
    for row in data:
        for c, val in enumerate(row):
            widths[c] = max(widths[c], len(val))

    sep = "-" * (sum(widths) + 3 * (len(widths) - 1))

    def fmt_row(vals: List[str]) -> str:
        out = []
        for c, v in enumerate(vals):
            # Team column: left-align; all others: right-align
            if c == 1:
                out.append(v.ljust(widths[c]))
            else:
                out.append(v.rjust(widths[c]))
        return "  ".join(out)

    lines = [
        "DOUBLE PLAY STATS",
        sep,
        fmt_row(HEADERS),
        sep,
    ]
    for row in data:
        lines.append(fmt_row(row))
    lines.append(sep)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(rows: List[DPRow]) -> str:
    """Return a plain-text analysis of the DP stats rows."""
    if not rows:
        return "No data to analyze."

    total_teams = len(rows)
    total_dp    = sum(r.dp for r in rows)
    avg_dp      = total_dp / total_teams
    avg_g       = sum(r.g for r in rows) / total_teams
    avg_dp_per_g = sum(r.dp / r.g for r in rows if r.g > 0) / total_teams

    leader  = rows[0]
    trailer = rows[-1]
    dp_range = leader.dp - trailer.dp

    # DP per game rate for every team, then take top-5 and bottom-5
    rates       = sorted(rows, key=lambda r: r.dp / r.g if r.g > 0 else 0, reverse=True)
    top_rate    = rates[:5]
    bottom_rate = rates[-5:]

    lines = [
        "ANALYSIS",
        f"  Teams listed          : {total_teams}",
        f"  Total DP (all teams)  : {total_dp}",
        f"  Avg DP per team       : {avg_dp:.1f}",
        f"  Avg games per team    : {avg_g:.1f}",
        f"  Avg DP/G (rate)       : {avg_dp_per_g:.2f}",
        "",
        f"  DP leader  : {leader.team} — {leader.dp} DP in {leader.g} G "
        f"({leader.dp / leader.g:.2f} DP/G)" if leader.g > 0 else
        f"  DP leader  : {leader.team} — {leader.dp} DP",
        f"  DP trailer : {trailer.team} — {trailer.dp} DP in {trailer.g} G "
        f"({trailer.dp / trailer.g:.2f} DP/G)" if trailer.g > 0 else
        f"  DP trailer : {trailer.team} — {trailer.dp} DP",
        f"  DP range   : {dp_range} ({leader.team} vs {trailer.team})",
        "",
        "  Top 5 by DP/G rate:",
    ]
    for r in top_rate:
        dp_g = r.dp / r.g if r.g > 0 else 0.0
        lines.append(f"    {r.rank:>3}.  {r.team:<22s}  {dp_g:.2f} DP/G  ({r.dp} DP, {r.g} G)")

    lines += ["", "  Bottom 5 by DP/G rate:"]
    for r in bottom_rate:
        dp_g = r.dp / r.g if r.g > 0 else 0.0
        lines.append(f"    {r.rank:>3}.  {r.team:<22s}  {dp_g:.2f} DP/G  ({r.dp} DP, {r.g} G)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive manual entry
# ---------------------------------------------------------------------------

def prompt_rows() -> List[DPRow]:
    """
    Interactively ask the user to enter DP stats row by row.
    Press Enter with a blank team name (or Ctrl-C) to finish entry.
    Rows are sorted by DP descending and ranked automatically.
    """
    print("Enter DP stats (leave Team blank to finish):")
    rows: List[DPRow] = []
    while True:
        try:
            team = input("  Team name    : ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not team:
            break
        while True:
            try:
                g_str = input("  Games (G)    : ").strip()
                g = int(g_str)
                if g <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a positive integer for G.")
        while True:
            try:
                dp_str = input("  Double Plays (DP): ").strip()
                dp = int(dp_str)
                if dp < 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a non-negative integer for DP.")
        rows.append(DPRow(rank="-", team=team, g=g, dp=dp))
        print()

    # Sort by DP descending and assign ranks
    rows.sort(key=lambda r: r.dp, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = str(idx)
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_CSV = "dp_data.csv"


def main() -> int:
    arg: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None

    if arg == "--sample":
        rows: List[DPRow] = SAMPLE_DATA
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

    if not rows:
        print(f"'{DEFAULT_CSV}' is empty — no entries yet.")
        print("Add rows manually to dp_data.csv (Rank,Team,G,DP) and re-run.")
        return 0

    print(format_table(rows))
    print()
    print(analyze(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
