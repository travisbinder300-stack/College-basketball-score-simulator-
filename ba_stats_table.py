#!/usr/bin/env python3
"""
College Baseball – Batting Average (BA) Stats Table
====================================================
Print a ranked table of teams sorted by batting average.

Columns
-------
  Rank  – BA rank (1 = highest batting average)
  Team  – team name
  G     – games played
  AB    – at-bats
  H     – hits
  BA    – batting average (H / AB, displayed as .000)

Usage
-----
  python ba_stats_table.py              # loads ba_data.csv if present, else interactive
  python ba_stats_table.py --sample     # prints built-in sample data
  python ba_stats_table.py data.csv     # loads Rank,Team,G,AB,H,BA CSV (header optional)
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
class BARow:
    rank: str
    team: str
    g: int
    ab: int
    h: int

    @property
    def ba(self) -> float:
        return self.h / self.ab if self.ab > 0 else 0.0

    def ba_str(self) -> str:
        return f"{self.ba:.3f}"


# ---------------------------------------------------------------------------
# Built-in sample data  (NCAA Division I Baseball, approximate season stats)
# ---------------------------------------------------------------------------

SAMPLE_DATA: List[BARow] = [
    BARow(rank="1",  team="Georgia Tech",    g=9,  ab=308, h=103),
    BARow(rank="2",  team="Oklahoma",        g=9,  ab=318, h=104),
    BARow(rank="3",  team="LSU",             g=9,  ab=322, h=103),
    BARow(rank="4",  team="Virginia",        g=8,  ab=275, h=87),
    BARow(rank="5",  team="Texas Tech",      g=8,  ab=285, h=89),
]


# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------

def load_csv(path: str) -> List[BARow]:
    """
    Load BA stats from a CSV file.
    Accepted column order (case-insensitive header OR headerless):
      Rank, Team, G, AB, H, BA
    The BA column is ignored on load (recalculated from H/AB).
    Rows are sorted by BA descending and re-ranked automatically.
    """
    rows: List[BARow] = []
    with open(path, newline="", encoding="utf-8") as fh:
        sample = fh.read(1024)
        fh.seek(0)
        first_char = sample.strip()[0] if sample.strip() else ""
        has_header = not first_char.isdigit() and first_char != "-"
        reader = csv.reader(fh)
        if has_header:
            next(reader, None)          # skip header line
        for line in reader:
            if len(line) < 5:
                continue
            try:
                rank = line[0].strip()
                team = line[1].strip()
                g    = int(line[2].strip())
                ab   = int(line[3].strip())
                h    = int(line[4].strip())
                rows.append(BARow(rank=rank, team=team, g=g, ab=ab, h=h))
            except ValueError:
                continue

    # Re-sort by BA descending and re-rank
    rows.sort(key=lambda r: r.ba, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = str(idx)
    return rows


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

HEADERS = ["Rank", "Team", "G", "AB", "H", "BA"]


def format_table(rows: List[BARow]) -> str:
    """Return a neatly aligned table string for the given BA rows."""
    data = [[r.rank, r.team, str(r.g), str(r.ab), str(r.h), r.ba_str()] for r in rows]

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
        "BATTING AVERAGE STATS",
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

def analyze(rows: List[BARow]) -> str:
    """Return a plain-text analysis of the BA stats rows."""
    if not rows:
        return "No data to analyze."

    total_teams = len(rows)
    total_ab    = sum(r.ab for r in rows)
    total_h     = sum(r.h  for r in rows)
    total_g     = sum(r.g  for r in rows)
    overall_ba  = total_h / total_ab if total_ab > 0 else 0.0
    avg_g       = total_g / total_teams

    leader  = rows[0]
    trailer = rows[-1]

    # Top-5 and bottom-5 by BA
    top5    = rows[:5]
    bot5    = rows[-5:]

    lines = [
        "ANALYSIS",
        f"  Teams listed          : {total_teams}",
        f"  Total AB (all teams)  : {total_ab}",
        f"  Total H  (all teams)  : {total_h}",
        f"  Overall BA            : {overall_ba:.3f}",
        f"  Avg games per team    : {avg_g:.1f}",
        "",
        f"  BA leader  : {leader.team} — {leader.ba_str()} ({leader.h} H / {leader.ab} AB, {leader.g} G)",
        f"  BA trailer : {trailer.team} — {trailer.ba_str()} ({trailer.h} H / {trailer.ab} AB, {trailer.g} G)",
        f"  BA range   : {leader.ba - trailer.ba:.3f} ({leader.team} vs {trailer.team})",
        "",
        "  Top 5 by BA:",
    ]
    for r in top5:
        lines.append(f"    {r.rank:>3}.  {r.team:<22s}  {r.ba_str()}  ({r.h} H / {r.ab} AB, {r.g} G)")

    lines += ["", "  Bottom 5 by BA:"]
    for r in bot5:
        lines.append(f"    {r.rank:>3}.  {r.team:<22s}  {r.ba_str()}  ({r.h} H / {r.ab} AB, {r.g} G)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive manual entry
# ---------------------------------------------------------------------------

def prompt_rows() -> List[BARow]:
    """
    Interactively ask the user to enter BA stats row by row.
    Press Enter with a blank team name (or Ctrl-C) to finish entry.
    BA is computed automatically from H / AB.
    Rows are sorted by BA descending and ranked automatically.
    """
    print("Enter Batting Average stats (leave Team blank to finish):")
    rows: List[BARow] = []
    while True:
        try:
            team = input("  Team name       : ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not team:
            break
        while True:
            try:
                g = int(input("  Games (G)       : ").strip())
                if g <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a positive integer for G.")
        while True:
            try:
                ab = int(input("  At-bats (AB)    : ").strip())
                if ab <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a positive integer for AB.")
        while True:
            try:
                h = int(input("  Hits (H)        : ").strip())
                if h < 0 or h > ab:
                    raise ValueError
                break
            except ValueError:
                print(f"  Please enter a non-negative integer for H (0–{ab}).")
        rows.append(BARow(rank="-", team=team, g=g, ab=ab, h=h))
        print(f"  BA = {rows[-1].ba_str()}")
        print()

    # Sort by BA descending and assign ranks
    rows.sort(key=lambda r: r.ba, reverse=True)
    for idx, row in enumerate(rows, start=1):
        row.rank = str(idx)
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_CSV = "ba_data.csv"


def main() -> int:
    arg: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None

    if arg == "--sample":
        rows: List[BARow] = SAMPLE_DATA
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
        if not rows:
            print("ba_data.csv is empty — no teams entered yet.")
            return 0
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
