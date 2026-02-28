#!/usr/bin/env python3
"""
Paste your RPI dump into STDIN (or a file) and print:
1) a spaced, aligned table in the same "table example" style
2) optional analysis

Usage:
  python rpi_table_printer.py < raw.txt
  python rpi_table_printer.py raw.txt
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple


RE_INT = re.compile(r"^\d+$")
RE_RECORD = re.compile(r"^\d+-\d+(?:-\d+)?$")  # allows ties: 8-1-1
RE_DELTA = re.compile(r"^[+-]?\d+$")


@dataclass
class Row:
    rpi: int
    team: str
    record: str
    sos: int
    nc_rec: str
    nc_rpi: int
    nc_sos: int
    h: str
    r: str
    n: str
    q1: str
    q2: str
    q3: str
    q4: str
    extra: str
    delta: str


HEADERS = [
    "RPI",
    "Team",
    "Record",
    "SOS",
    "NC Rec",
    "NC RPI",
    "NC SOS",
    "H",
    "R",
    "N",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "Extra",
    "RPI Delta",
]


def is_int(s: str) -> bool:
    return bool(RE_INT.match(s))


def is_record(s: str) -> bool:
    return bool(RE_RECORD.match(s))


def is_delta(s: str) -> bool:
    return bool(RE_DELTA.match(s))


def read_text(path: Optional[str]) -> str:
    if path:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    return sys.stdin.read()


def tokenize(text: str) -> List[str]:
    # Keep only meaningful tokens (numbers/records/words). We'll reconstruct team names.
    # This intentionally drops the conference lines like "ACC (0-0)".
    raw = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip known boilerplate header fragments
        if line.startswith("RPI") and "Team" in line and "Record" in line:
            continue
        if line.lower().startswith("freestar"):
            continue
        if line.startswith("Corrections") or line.startswith("Copyright"):
            continue
        raw.append(line)

    # Split on whitespace and tabs, but keep whole records like 8-1-1
    tokens: List[str] = []
    for line in raw:
        parts = re.split(r"\s+", line)
        tokens.extend([p for p in parts if p])
    return tokens


def parse_rows(tokens: List[str]) -> List[Row]:
    rows: List[Row] = []
    i = 0

    def next_token() -> str:
        nonlocal i
        t = tokens[i]
        i += 1
        return t

    while i < len(tokens):
        # Find next RPI number
        if not is_int(tokens[i]):
            i += 1
            continue

        rpi = int(next_token())

        # Team name: consume until we hit a record token (e.g. 6-2 or 8-1-1)
        team_parts = []
        while i < len(tokens) and not is_record(tokens[i]):
            # If we hit a lone integer that looks like SOS prematurely, keep as team part? usually not.
            team_parts.append(next_token())
        if i >= len(tokens):
            break

        team = " ".join(team_parts).strip()

        record = next_token()
        if i + 4 >= len(tokens):
            break

        sos = int(next_token())
        nc_rec = next_token()
        nc_rpi = int(next_token())
        nc_sos = int(next_token())

        # H R N Q1 Q2 Q3 Q4 Extra Delta
        h = next_token()
        r = next_token()
        n = next_token()
        q1 = next_token()
        q2 = next_token()
        q3 = next_token()
        q4 = next_token()

        # Extra is a record-like token; if missing, keep blank
        extra = ""
        if i < len(tokens) and is_record(tokens[i]):
            extra = next_token()

        # Delta is +/-int; if missing, keep blank
        delta = ""
        if i < len(tokens) and is_delta(tokens[i]):
            delta = next_token()

        rows.append(
            Row(
                rpi=rpi,
                team=team,
                record=record,
                sos=sos,
                nc_rec=nc_rec,
                nc_rpi=nc_rpi,
                nc_sos=nc_sos,
                h=h,
                r=r,
                n=n,
                q1=q1,
                q2=q2,
                q3=q3,
                q4=q4,
                extra=extra,
                delta=delta,
            )
        )

    return rows


def format_table(rows: List[Row]) -> str:
    data = []
    for row in rows:
        data.append(
            [
                str(row.rpi),
                row.team,
                row.record,
                str(row.sos),
                row.nc_rec,
                str(row.nc_rpi),
                str(row.nc_sos),
                row.h,
                row.r,
                row.n,
                row.q1,
                row.q2,
                row.q3,
                row.q4,
                row.extra,
                row.delta,
            ]
        )

    # compute widths
    widths = [len(h) for h in HEADERS]
    for row in data:
        for c, val in enumerate(row):
            widths[c] = max(widths[c], len(val))

    # build lines
    def fmt_row(vals: List[str]) -> str:
        out = []
        for c, v in enumerate(vals):
            # left-align team, right-align numeric-ish columns
            if c == 1:
                out.append(v.ljust(widths[c]))
            else:
                out.append(v.rjust(widths[c]))
        return "  ".join(out)

    lines = [fmt_row(HEADERS)]
    for row in data:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def basic_analysis(rows: List[Row]) -> str:
    # Simple: count, best/worst delta, unbeaten, etc.
    deltas: List[Tuple[int, str, int]] = []
    unbeaten: List[Row] = []
    for r in rows:
        if r.delta and RE_DELTA.match(r.delta):
            deltas.append((r.rpi, r.team, int(r.delta)))
        # unbeaten check: "W-L" or "W-L-T" with L==0
        parts = r.record.split("-")
        if len(parts) >= 2 and parts[1] == "0":
            unbeaten.append(r)

    lines = []
    lines.append(f"Teams parsed: {len(rows)}")
    if deltas:
        up = sorted(deltas, key=lambda x: x[2], reverse=True)[:5]
        down = sorted(deltas, key=lambda x: x[2])[:5]
        lines.append("")
        lines.append("Top risers (Delta):")
        for rpi, team, d in up:
            lines.append(f"- {rpi} {team}: {d:+d}")
        lines.append("")
        lines.append("Top fallers (Delta):")
        for rpi, team, d in down:
            lines.append(f"- {rpi} {team}: {d:+d}")

    if unbeaten:
        lines.append("")
        lines.append("Unbeaten (Record with 0 losses):")
        for r in unbeaten:
            lines.append(f"- {r.rpi} {r.team} {r.record}")

    return "\n".join(lines)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else None
    text = read_text(path)
    tokens = tokenize(text)
    rows = parse_rows(tokens)

    print(format_table(rows))

    # If you want analysis always, leave this on. If not, comment it out.
    print("\nAnalysis")
    print(basic_analysis(rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
