#!/usr/bin/env python3
"""
College Baseball – Data Inventory
==================================
Print a complete summary of every dataset currently in the system.

Shows, for each CSV dataset:
  • File name and path
  • Columns present
  • Number of records (teams)
  • Key summary statistics (leader, trailer, averages, totals)

Also lists every tool/script available and what it does.

Usage
-----
  python data_inventory.py
"""

from __future__ import annotations

import csv
import os
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_DIR = os.path.dirname(os.path.abspath(__file__))


def _file_path(name: str) -> str:
    return os.path.join(REPO_DIR, name)


def _sep(width: int = 60) -> str:
    return "-" * width


def _heading(title: str, width: int = 60) -> str:
    return f"{'=' * width}\n  {title}\n{'=' * width}"


# ---------------------------------------------------------------------------
# BA dataset summary  (ba_data.csv)
# ---------------------------------------------------------------------------

def _ba_summary(path: str) -> List[str]:
    """Return lines describing the batting average dataset."""
    rows: List[Tuple[str, int, int, int, float]] = []   # team, g, ab, h, ba
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)   # skip header
        for line in reader:
            if len(line) < 5:
                continue
            try:
                team = line[1].strip()
                g    = int(line[2].strip())
                ab   = int(line[3].strip())
                h    = int(line[4].strip())
                ba   = h / ab if ab > 0 else 0.0
                rows.append((team, g, ab, h, ba))
            except ValueError:
                continue

    if not rows:
        return ["  (no records found)"]

    total_teams = len(rows)
    total_ab    = sum(r[2] for r in rows)
    total_h     = sum(r[3] for r in rows)
    overall_ba  = total_h / total_ab if total_ab > 0 else 0.0
    avg_g       = sum(r[1] for r in rows) / total_teams

    by_ba = sorted(rows, key=lambda r: r[4], reverse=True)
    leader  = by_ba[0]
    trailer = by_ba[-1]

    by_ab = sorted(rows, key=lambda r: r[2], reverse=True)
    most_ab  = by_ab[0]
    least_ab = by_ab[-1]

    lines = [
        f"  File            : ba_data.csv",
        f"  Columns         : Rank, Team, G (games), AB (at-bats), H (hits), BA (batting avg), Rel% (reliability)",
        f"  Records         : {total_teams} teams",
        f"  Total at-bats   : {total_ab:,}",
        f"  Total hits      : {total_h:,}",
        f"  Overall BA      : {overall_ba:.3f}",
        f"  Avg games/team  : {avg_g:.1f}",
        _sep(),
        f"  BA leader       : {leader[0]}  —  .{round(leader[4]*1000):03d}  ({leader[3]} H / {leader[2]} AB, {leader[1]} G)",
        f"  BA trailer      : {trailer[0]}  —  .{round(trailer[4]*1000):03d}  ({trailer[3]} H / {trailer[2]} AB, {trailer[1]} G)",
        _sep(),
        f"  Largest sample  : {most_ab[0]}  —  {most_ab[2]} AB  (Rel% = {most_ab[2]/(most_ab[2]+350)*100:.1f}%)",
        f"  Smallest sample : {least_ab[0]}  —  {least_ab[2]} AB  (Rel% = {least_ab[2]/(least_ab[2]+350)*100:.1f}%)",
        f"  Reliability note: Rel% = AB / (AB + 350) × 100.  Teams above 50% have a majority-sample BA.",
    ]
    return lines


# ---------------------------------------------------------------------------
# BB dataset summary  (bb_data.csv)
# ---------------------------------------------------------------------------

def _bb_summary(path: str) -> List[str]:
    """Return lines describing the base-on-balls dataset."""
    rows: List[Tuple[str, int, int]] = []   # team, g, bb
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)   # skip header
        for line in reader:
            if len(line) < 4:
                continue
            try:
                team = line[1].strip()
                g    = int(line[2].strip())
                bb   = int(line[3].strip())
                rows.append((team, g, bb))
            except ValueError:
                continue

    if not rows:
        return ["  (no records found)"]

    total_teams = len(rows)
    total_bb    = sum(r[2] for r in rows)
    avg_bb      = total_bb / total_teams
    avg_g       = sum(r[1] for r in rows) / total_teams
    avg_bb_per_g = sum(r[2] / r[1] for r in rows if r[1] > 0) / total_teams

    by_bb = sorted(rows, key=lambda r: r[2], reverse=True)
    leader  = by_bb[0]
    trailer = by_bb[-1]

    lines = [
        f"  File            : bb_data.csv",
        f"  Columns         : Rank, Team, G (games), BB (base on balls / walks)",
        f"  Records         : {total_teams} teams",
        f"  Total BB        : {total_bb:,}",
        f"  Avg BB/team     : {avg_bb:.1f}",
        f"  Avg games/team  : {avg_g:.1f}",
        f"  Avg BB/G (rate) : {avg_bb_per_g:.2f}",
        _sep(),
        f"  BB leader       : {leader[0]}  —  {leader[2]} BB in {leader[1]} G  ({leader[2]/leader[1]:.2f} BB/G)",
        f"  BB trailer      : {trailer[0]}  —  {trailer[2]} BB in {trailer[1]} G  ({trailer[2]/trailer[1]:.2f} BB/G)",
    ]
    return lines


# ---------------------------------------------------------------------------
# DP dataset summary  (dp_data.csv)
# ---------------------------------------------------------------------------

def _dp_summary(path: str) -> List[str]:
    """Return lines describing the double play dataset."""
    rows: List[Tuple[str, int, int]] = []   # team, g, dp
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)   # skip header
        for line in reader:
            if len(line) < 4:
                continue
            try:
                team = line[1].strip()
                g    = int(line[2].strip())
                dp   = int(line[3].strip())
                rows.append((team, g, dp))
            except ValueError:
                continue

    if not rows:
        return [
            f"  File            : dp_data.csv",
            f"  Columns         : Rank, Team, G (games), DP (double plays)",
            f"  Records         : 0 teams  (file is empty — add rows manually)",
        ]

    total_teams = len(rows)
    total_dp    = sum(r[2] for r in rows)
    avg_dp      = total_dp / total_teams
    avg_g       = sum(r[1] for r in rows) / total_teams
    teams_with_g = sum(1 for r in rows if r[1] > 0)
    avg_dp_per_g = sum(r[2] / r[1] for r in rows if r[1] > 0) / teams_with_g if teams_with_g else 0.0

    by_dp = sorted(rows, key=lambda r: r[2], reverse=True)
    leader  = by_dp[0]
    trailer = by_dp[-1]

    lines = [
        f"  File            : dp_data.csv",
        f"  Columns         : Rank, Team, G (games), DP (double plays)",
        f"  Records         : {total_teams} teams",
        f"  Total DP        : {total_dp:,}",
        f"  Avg DP/team     : {avg_dp:.1f}",
        f"  Avg games/team  : {avg_g:.1f}",
        f"  Avg DP/G (rate) : {avg_dp_per_g:.2f}",
        _sep(),
        f"  DP leader       : {leader[0]}  —  {leader[2]} DP in {leader[1]} G  "
        f"({leader[2]/leader[1]:.2f} DP/G)" if leader[1] > 0 else
        f"  DP leader       : {leader[0]}  —  {leader[2]} DP",
        f"  DP trailer      : {trailer[0]}  —  {trailer[2]} DP in {trailer[1]} G  "
        f"({trailer[2]/trailer[1]:.2f} DP/G)" if trailer[1] > 0 else
        f"  DP trailer      : {trailer[0]}  —  {trailer[2]} DP",
    ]
    return lines


# ---------------------------------------------------------------------------
# Tools inventory
# ---------------------------------------------------------------------------

TOOLS = [
    (
        "ba_stats_table.py",
        "Batting Average (BA) stats table",
        "Loads ba_data.csv; prints ranked BA table with Rel% column and "
        "reliability analysis (which team's BA can be trusted most).",
        "python ba_stats_table.py",
    ),
    (
        "bb_stats_table.py",
        "Base on Balls (BB) stats table",
        "Loads bb_data.csv; prints ranked BB table with BB/G rate analysis.",
        "python bb_stats_table.py",
    ),
    (
        "game_simulator.py",
        "Game score simulator",
        "Parses a betting-line string and simulates game outcomes using "
        "Monte Carlo (10,000 runs) + closed-form math.  Supports ML odds, "
        "run lines, RPI rank, and SOS rank.",
        'python game_simulator.py "Team A ML -139 -1.5 +108 at Team B ML +104 +1.5 -148"',
    ),
    (
        "rpi_table_printer.py",
        "RPI table printer",
        "Reads raw RPI text (from stdin or a file), parses it, and prints "
        "an aligned table with delta/riser/faller analysis.",
        "python rpi_table_printer.py < raw_rpi.txt",
    ),
    (
        "dp_stats_table.py",
        "Double Play (DP) stats table",
        "Loads dp_data.csv; prints ranked DP table with DP/G rate analysis. "
        "Add rows to dp_data.csv manually (Rank,Team,G,DP) then run this script.",
        "python dp_stats_table.py",
    ),
    (
        "data_inventory.py",
        "Data inventory (this script)",
        "Prints a complete summary of all datasets and tools in the system.",
        "python data_inventory.py",
    ),
]


def _tools_section() -> List[str]:
    lines: List[str] = []
    for filename, title, desc, usage in TOOLS:
        present = "✓" if os.path.isfile(_file_path(filename)) else "✗"
        lines += [
            f"  [{present}] {filename}",
            f"       {title}",
            f"       {desc}",
            f"       Usage : {usage}",
            "",
        ]
    return lines


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print(_heading("COLLEGE BASEBALL — SYSTEM DATA INVENTORY"))
    print()

    # --- Datasets ---
    print("  DATASETS")
    print(_sep())
    print()

    datasets = [
        ("ba_data.csv",  "Batting Average",   _ba_summary),
        ("bb_data.csv",  "Base on Balls",      _bb_summary),
        ("dp_data.csv",  "Double Plays",       _dp_summary),
    ]

    found_any = False
    for filename, label, summary_fn in datasets:
        path = _file_path(filename)
        if os.path.isfile(path):
            found_any = True
            print(f"  ── {label.upper()} ──")
            for line in summary_fn(path):
                print(line)
            print()
        else:
            print(f"  ── {label.upper()} ──")
            print(f"  File '{filename}' not found in {REPO_DIR}")
            print()

    if not found_any:
        print("  No dataset CSV files found.")
        print()

    # --- Tools ---
    print(_sep())
    print("  AVAILABLE TOOLS & SCRIPTS")
    print(_sep())
    print()
    for line in _tools_section():
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
