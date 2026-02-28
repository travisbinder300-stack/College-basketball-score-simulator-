#!/usr/bin/env python3
"""
College Baseball – Double Plays Per Game (PG) Stats Table
==========================================================
Print a ranked table of teams sorted by double plays per game (PG = DP ÷ G).

Columns
-------
  Rank  – PG rank (1 = highest PG rate); tied teams share a rank and show '-'
  Team  – team name
  G     – games played
  DP    – total double plays turned
  PG    – double plays per game (DP ÷ G); values below 1.00 omit the leading zero

Usage
-----
  python dpg_stats_table.py              # loads dpg_data.csv if present, else interactive
  python dpg_stats_table.py --sample     # prints built-in sample data
  python dpg_stats_table.py data.csv     # loads Rank,Team,G,DP CSV (header optional)
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
class DPGRow:
    rank: str
    team: str
    g: int
    dp: int

    def pg_rate(self) -> float:
        """DP/G ratio rounded to 2 decimal places; 0.0 when G is zero."""
        return round(self.dp / self.g, 2) if self.g > 0 else 0.0

    def pg_str(self) -> str:
        """Return PG formatted to 2 decimal places.
        Values below 1.00 are displayed without a leading zero (e.g. '.89').
        """
        if self.g <= 0:
            return "-"
        val = self.dp / self.g
        formatted = f"{val:.2f}"
        if formatted.startswith("0."):
            return formatted[1:]   # drop leading zero: "0.89" → ".89"
        return formatted


# ---------------------------------------------------------------------------
# Built-in sample data  (NCAA Division I Baseball, approximate season stats)
# ---------------------------------------------------------------------------

SAMPLE_DATA: List[DPGRow] = [
    DPGRow(rank="-", team="Texas A&M",       g=10, dp=18),
    DPGRow(rank="-", team="LSU",             g=9,  dp=17),
    DPGRow(rank="-", team="Vanderbilt",      g=9,  dp=17),
    DPGRow(rank="-", team="Ole Miss",        g=9,  dp=16),
    DPGRow(rank="-", team="Virginia",        g=8,  dp=16),
    DPGRow(rank="-", team="Georgia Tech",    g=9,  dp=15),
    DPGRow(rank="-", team="Miami (FL)",      g=10, dp=15),
    DPGRow(rank="-", team="TCU",             g=9,  dp=15),
    DPGRow(rank="-", team="Arkansas",        g=9,  dp=14),
    DPGRow(rank="-", team="Florida",         g=9,  dp=14),
    DPGRow(rank="-", team="North Carolina",  g=9,  dp=14),
    DPGRow(rank="-", team="Oklahoma",        g=9,  dp=14),
    DPGRow(rank="-", team="Auburn",          g=9,  dp=13),
    DPGRow(rank="-", team="Duke",            g=10, dp=13),
    DPGRow(rank="-", team="Georgia",         g=8,  dp=13),
    DPGRow(rank="-", team="Mississippi St.", g=9,  dp=13),
    DPGRow(rank="-", team="Notre Dame",      g=9,  dp=13),
    DPGRow(rank="-", team="Texas",           g=8,  dp=13),
    DPGRow(rank="-", team="Alabama",         g=9,  dp=12),
    DPGRow(rank="-", team="Arizona",         g=9,  dp=12),
]


# ---------------------------------------------------------------------------
# Sorting and ranking helper
# ---------------------------------------------------------------------------

def _sort_and_rank(rows: List[DPGRow]) -> None:
    """Sort rows by PG descending (then team name ascending for ties) and
    assign competition-style ranks: the first team in a tied group gets the
    sequential position number; tied partners get '-'.
    """
    rows.sort(
        key=lambda r: (-r.pg_rate() if r.g > 0 else float("inf"), r.team)
    )
    if not rows:
        return
    prev_pg = rows[0].pg_rate()
    rows[0].rank = "1"
    for i in range(1, len(rows)):
        pg = rows[i].pg_rate()
        if pg == prev_pg:
            rows[i].rank = "-"
        else:
            rows[i].rank = str(i + 1)
            prev_pg = pg


# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------

def load_csv(path: str) -> List[DPGRow]:
    """
    Load DP/G stats from a CSV file.
    Accepted column order (case-insensitive header OR headerless):
      Rank, Team, G, DP
    PG is computed from DP ÷ G.
    Rows are sorted by PG descending and re-ranked automatically.
    """
    rows: List[DPGRow] = []
    with open(path, newline="", encoding="utf-8") as fh:
        sample = fh.read(1024)
        fh.seek(0)
        has_header = bool(sample.strip()) and not sample.strip()[0].isdigit()
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
                rows.append(DPGRow(rank=rank, team=team, g=g, dp=dp))
            except ValueError:
                continue

    _sort_and_rank(rows)
    return rows


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

HEADERS = ["Rank", "Team", "G", "DP", "PG"]


def format_table(rows: List[DPGRow]) -> str:
    """Return a neatly aligned table string for the given DPG rows."""
    data = [[r.rank, r.team, str(r.g), str(r.dp), r.pg_str()] for r in rows]

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
        "DOUBLE PLAYS PER GAME STATS",
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

def analyze(rows: List[DPGRow]) -> str:
    """Return a plain-text analysis of the DPG stats rows."""
    if not rows:
        return "No data to analyze."

    total_teams  = len(rows)
    total_dp     = sum(r.dp for r in rows)
    avg_dp       = total_dp / total_teams
    avg_g        = sum(r.g for r in rows) / total_teams
    teams_with_g = sum(1 for r in rows if r.g > 0)
    avg_pg       = (
        sum(r.dp / r.g for r in rows if r.g > 0) / teams_with_g
        if teams_with_g else 0.0
    )

    leader  = rows[0]
    trailer = rows[-1]

    top5    = rows[:5]
    bot5    = rows[-5:]

    lines = [
        "ANALYSIS",
        f"  Teams listed          : {total_teams}",
        f"  Total DP (all teams)  : {total_dp}",
        f"  Avg DP per team       : {avg_dp:.1f}",
        f"  Avg games per team    : {avg_g:.1f}",
        f"  Avg PG (rate)         : {avg_pg:.2f}",
        "",
        f"  PG leader  : {leader.team} — {leader.pg_str()} PG  ({leader.dp} DP, {leader.g} G)",
        f"  PG trailer : {trailer.team} — {trailer.pg_str()} PG  ({trailer.dp} DP, {trailer.g} G)",
        "",
        "  Top 5 by PG:",
    ]
    for r in top5:
        lines.append(
            f"    {r.rank:>3}.  {r.team:<22s}  {r.pg_str():>4} PG  ({r.dp} DP, {r.g} G)"
        )

    lines += ["", "  Bottom 5 by PG:"]
    for r in bot5:
        lines.append(
            f"    {r.rank:>3}.  {r.team:<22s}  {r.pg_str():>4} PG  ({r.dp} DP, {r.g} G)"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive manual entry
# ---------------------------------------------------------------------------

def prompt_rows() -> List[DPGRow]:
    """
    Interactively ask the user to enter DP/G stats row by row.
    Press Enter with a blank team name (or Ctrl-C) to finish entry.
    Rows are sorted by PG descending and ranked automatically.
    """
    print("Enter DP per game stats (leave Team blank to finish):")
    rows: List[DPGRow] = []
    while True:
        try:
            team = input("  Team name         : ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not team:
            break
        while True:
            try:
                g = int(input("  Games (G)         : ").strip())
                if g <= 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a positive integer for G.")
        while True:
            try:
                dp = int(input("  Double Plays (DP) : ").strip())
                if dp < 0:
                    raise ValueError
                break
            except ValueError:
                print("  Please enter a non-negative integer for DP.")
        rows.append(DPGRow(rank="-", team=team, g=g, dp=dp))
        print(f"  PG = {rows[-1].pg_str()}")
        print()

    _sort_and_rank(rows)
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DEFAULT_CSV = "dpg_data.csv"


def main() -> int:
    arg: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None

    if arg == "--sample":
        rows: List[DPGRow] = list(SAMPLE_DATA)
        _sort_and_rank(rows)
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
        print(f"'{DEFAULT_CSV}' is empty — add rows to dpg_data.csv (Rank,Team,G,DP) and re-run.")
        return 0

    print(format_table(rows))
    print()
    print(analyze(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
