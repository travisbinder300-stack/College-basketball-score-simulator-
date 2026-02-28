#!/usr/bin/env python3
"""
College Baseball Game Simulator
===================================
Parse a betting-line string and simulate a game outcome.
Optionally accepts RPI rank and SOS rank for each team to refine the simulation.

Supported input formats
-----------------------
Full format (with ML keyword and "at" separator):
  <Team A> ML <ml_odds> <run_line> <rl_odds> [RPI <n> SOS <n>] at
  <Team B> ML <ml_odds> <run_line> <rl_odds> [RPI <n> SOS <n>]

Short format (spread only, no ML keyword):
  <Team A> <run_line> <rl_odds> <Team B> <run_line> <rl_odds>

Examples:
  Illinois State ML -139 -1.5 +108 at Middle Tennessee ML +104 +1.5 -148
  Illinois State ML -139 -1.5 +108 RPI 45 SOS 78 at Middle Tennessee ML +104 +1.5 -148 RPI 67 SOS 120
  UT Arlington +5.5 -136 Arkansas -5.5 +100

Usage:
  python game_simulator.py "UT Arlington +5.5 -136 Arkansas -5.5 +100"
  python game_simulator.py "Illinois State ML -139 -1.5 +108 at Middle Tennessee ML +104 +1.5 -148"
  python game_simulator.py          # interactive prompt
"""

from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Team:
    name: str
    is_home: bool
    ml_odds: int               # American odds, e.g. -139 or +104
    run_line: float            # e.g. -1.5 (favourite) or +1.5 (underdog)
    rl_odds: int               # American odds on the run line
    rpi_rank: Optional[int] = None   # NCAA RPI rank (lower = stronger)
    sos_rank: Optional[int] = None   # Strength-of-Schedule rank (lower = harder schedule)


@dataclass
class Matchup:
    away: Team
    home: Team


# ---------------------------------------------------------------------------
# Odds helpers
# ---------------------------------------------------------------------------

def american_to_implied_prob(odds: int) -> float:
    """Convert American moneyline odds to implied win probability (0-1)."""
    if odds < 0:
        return (-odds) / (-odds + 100)
    else:
        return 100 / (odds + 100)


def remove_vig(prob_a: float, prob_b: float) -> tuple[float, float]:
    """Remove the bookmaker's vig so probabilities sum to 1."""
    total = prob_a + prob_b
    return prob_a / total, prob_b / total


def implied_total_from_run_line(run_line: float, base_total: float = 8.5) -> float:
    """
    Estimate an expected run total based on the run line.
    A larger absolute run line implies a slightly higher-scoring game;
    we nudge the expected total slightly.
    """
    return base_total + abs(run_line) * 0.2


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

# Matches tokens like: -139  +108  -1.5  +1.5  0

def parse_team_fragment(tokens: list[str], is_home: bool) -> Team:
    """
    Parse tokens for one team side.  Expected pattern:
      <name words...> ML <ml_odds> <run_line> <rl_odds> [RPI <n>] [SOS <n>]
    """
    # Find "ML" keyword
    try:
        ml_idx = next(i for i, t in enumerate(tokens) if t.upper() == "ML")
    except StopIteration:
        raise ValueError(f"Could not find 'ML' keyword in: {' '.join(tokens)}")

    name = " ".join(tokens[:ml_idx]).strip()
    if not name:
        raise ValueError(f"Could not determine team name from: {' '.join(tokens)}")

    rest = tokens[ml_idx + 1:]
    if len(rest) < 3:
        raise ValueError(
            f"Expected <ml_odds> <run_line> <rl_odds> after ML, got: {rest}"
        )

    try:
        ml_odds = int(rest[0])
        run_line = float(rest[1])
        rl_odds = int(rest[2])
    except ValueError as exc:
        raise ValueError(f"Could not parse odds from {rest[:3]}: {exc}") from exc

    # Parse optional RPI and SOS tokens
    rpi_rank: Optional[int] = None
    sos_rank: Optional[int] = None
    extra = rest[3:]
    i = 0
    while i < len(extra) - 1:
        key = extra[i].upper()
        if key == "RPI":
            try:
                rpi_rank = int(extra[i + 1])
                i += 2
                continue
            except ValueError:
                pass
        elif key == "SOS":
            try:
                sos_rank = int(extra[i + 1])
                i += 2
                continue
            except ValueError:
                pass
        i += 1

    return Team(
        name=name,
        is_home=is_home,
        ml_odds=ml_odds,
        run_line=run_line,
        rl_odds=rl_odds,
        rpi_rank=rpi_rank,
        sos_rank=sos_rank,
    )


def _is_numeric_token(s: str) -> bool:
    """Return True if s looks like a signed or unsigned number (e.g. +5.5, -136, 1.5)."""
    return bool(re.match(r'^[+-]?\d+(\.\d+)?$', s))


def parse_spread_matchup(line: str) -> Matchup:
    """
    Parse a short spread-only line such as:
      UT Arlington +5.5 -136 Arkansas -5.5 +100

    Format: <Team A> <run_line> <rl_odds> <Team B> <run_line> <rl_odds>
    The first team is treated as away, the second as home.
    The run-line odds are also used as a moneyline proxy for win-probability.
    """
    tokens = line.strip().split()

    # Locate the first pair of consecutive numeric tokens — those are
    # run_line + rl_odds for team A.  Everything before them is the name.
    split_idx = None
    for i in range(1, len(tokens) - 1):
        if _is_numeric_token(tokens[i]) and _is_numeric_token(tokens[i + 1]):
            split_idx = i
            break

    if split_idx is None:
        raise ValueError(
            "Could not detect spread format. "
            "Expected: <Team A> <run_line> <odds> <Team B> <run_line> <odds>"
        )

    away_name = " ".join(tokens[:split_idx])
    if not away_name:
        raise ValueError("Could not determine away team name.")

    try:
        away_run_line = float(tokens[split_idx])
        away_rl_odds = int(tokens[split_idx + 1])
    except ValueError as exc:
        raise ValueError(f"Could not parse away run-line/odds: {exc}") from exc

    rest = tokens[split_idx + 2:]
    if len(rest) < 3:
        raise ValueError(
            "Not enough tokens for home team. "
            "Expected: <Team B name> <run_line> <odds>"
        )

    try:
        home_run_line = float(rest[-2])
        home_rl_odds = int(rest[-1])
    except ValueError as exc:
        raise ValueError(f"Could not parse home run-line/odds: {exc}") from exc

    home_name = " ".join(rest[:-2])
    if not home_name:
        raise ValueError("Could not determine home team name.")

    # Use run-line odds as ML proxy for win-probability estimation
    away = Team(name=away_name, is_home=False, ml_odds=away_rl_odds, run_line=away_run_line, rl_odds=away_rl_odds)
    home = Team(name=home_name, is_home=True, ml_odds=home_rl_odds, run_line=home_run_line, rl_odds=home_rl_odds)
    return Matchup(away=away, home=home)


def parse_matchup(line: str) -> Matchup:
    """
    Parse a full matchup line such as:
      Illinois State ML -139 -1.5 +108 at Middle Tennessee ML +104 +1.5 -148

    If no 'ML' keyword is found, falls back to the short spread-only format:
      UT Arlington +5.5 -136 Arkansas -5.5 +100
    """
    tokens = line.strip().split()

    # If no ML keyword present, use the short spread format
    ml_positions = [i for i, t in enumerate(tokens) if t.upper() == "ML"]
    if len(ml_positions) < 2:
        return parse_spread_matchup(line)

    first_ml = ml_positions[0]
    second_ml = ml_positions[1]

    # Find "at" between the two ML markers
    at_pos = None
    for i in range(first_ml + 1, second_ml):
        if tokens[i].lower() == "at":
            at_pos = i
            break

    if at_pos is None:
        raise ValueError(
            "Could not find 'at' separator between the two team entries.\n"
            "Make sure your line looks like:\n"
            "  <Away> ML <odds> <run_line> <rl_odds> at <Home> ML <odds> <run_line> <rl_odds>"
        )

    away_tokens = tokens[:at_pos]
    home_tokens = tokens[at_pos + 1:]

    away = parse_team_fragment(away_tokens, is_home=False)
    home = parse_team_fragment(home_tokens, is_home=True)
    return Matchup(away=away, home=home)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

HOME_ADVANTAGE_RUNS = 0.3     # typical home-field edge in college baseball (runs)
MARGIN_STD = 3.0              # college baseball run-margin std-dev (~3 runs/game)
MAX_RPI_RANK = 350            # approximate size of the NCAA field
TEAM_NAME_WIDTH = 28          # column width for team names in the report


def _normal_cdf(x: float) -> float:
    """Standard normal CDF: Φ(x) = P(Z ≤ x).

    Derivation: erfc(z) = 2·Φ(−z·√2), so Φ(x) = erfc(−x/√2) / 2.
    Uses math.erfc for numerical accuracy near the tails.
    """
    return 0.5 * math.erfc(-x / math.sqrt(2))


def _rpi_adjustments(
    away: "Team", home: "Team", win_prob_away: float, adjusted_margin_away: float
) -> tuple[float, float, float, float]:
    """
    Blend RPI-based win probability and adjust run margin when RPI ranks are available.

    RPI blending
    ------------
    - Compute a straight RPI-ratio win probability: lower rank = better team.
    - Weight that probability against the ML-derived one using the average
      SOS quality of the two teams (tougher schedule → more trustworthy RPI).
    - The RPI contribution is capped at 40 % of the final probability.

    Margin adjustment
    -----------------
    - A rank difference of 100 translates to ~0.8 run advantage.
    - Positive value favours the away team (their rank is lower/better).

    Returns
    -------
    Tuple of (blended_win_prob_away, adjusted_margin_away, rpi_prob_away, rpi_weight).
    Raises ValueError if either team has an RPI rank of 0.
    """
    if away.rpi_rank == 0 or home.rpi_rank == 0:
        raise ValueError("RPI rank must be a positive integer (1 or greater).")

    rpi_prob_away = home.rpi_rank / (away.rpi_rank + home.rpi_rank)

    # SOS quality: 0 (weakest schedule) → 1 (hardest schedule)
    away_sos_q = (MAX_RPI_RANK - (away.sos_rank or MAX_RPI_RANK // 2)) / MAX_RPI_RANK
    home_sos_q = (MAX_RPI_RANK - (home.sos_rank or MAX_RPI_RANK // 2)) / MAX_RPI_RANK
    avg_sos_quality = (away_sos_q + home_sos_q) / 2

    # RPI weight: 0.15 (easy schedules) → 0.35 (tough schedules), capped at 0.40
    rpi_weight = min(0.40, 0.15 + avg_sos_quality * 0.20)

    blended_away = win_prob_away * (1 - rpi_weight) + rpi_prob_away * rpi_weight

    # Margin nudge: (home_rank − away_rank) × 0.008 run/rank
    rpi_margin_adj = (home.rpi_rank - away.rpi_rank) * 0.008
    adjusted_margin_away += rpi_margin_adj

    return blended_away, adjusted_margin_away, rpi_prob_away, rpi_weight


def calculate_game(matchup: Matchup) -> dict:
    """
    Compute game probabilities and projected scores using pure closed-form math.

    Method
    ------
    - Convert American odds to de-vigged win probabilities.
    - Derive expected run margin from the run line; apply home-field adjustment.
    - Blend in RPI/SOS data when available (unchanged from previous model).
    - Model the run margin as M ~ N(μ, MARGIN_STD²).
    - Win probability  = Φ(μ / σ)                   [P(M > 0)]
    - Cover probability = Φ((μ − threshold) / σ)     [P(M > −run_line)]
    - Over/Under is 50/50 (expected total IS the line by construction).
    - Projected scores are derived directly from μ and the expected total.
    No random sampling is used.
    """
    away = matchup.away
    home = matchup.home

    # --- Win probabilities from moneyline ---
    raw_away = american_to_implied_prob(away.ml_odds)
    raw_home = american_to_implied_prob(home.ml_odds)
    ml_prob_away, ml_prob_home = remove_vig(raw_away, raw_home)

    # --- Expected run margin (away − home) from the run line ---
    # run_line = -1.5 for the favourite means expected margin = +1.5 for away
    expected_margin_away = -away.run_line
    adjusted_margin_away = expected_margin_away - HOME_ADVANTAGE_RUNS

    # --- RPI / SOS adjustments (when both teams have RPI rank data) ---
    rpi_used = away.rpi_rank is not None and home.rpi_rank is not None
    rpi_weight_used: float = 0.0
    rpi_prob_away_used: float = 0.0
    blended_prob_away = ml_prob_away
    blended_prob_home = ml_prob_home
    if rpi_used:
        blended_prob_away, adjusted_margin_away, rpi_prob_away_used, rpi_weight_used = (
            _rpi_adjustments(away, home, ml_prob_away, adjusted_margin_away)
        )
        blended_prob_home = 1.0 - blended_prob_away

    # --- Expected total runs ---
    expected_total = implied_total_from_run_line(away.run_line)

    # --- Pure-math win probability ---
    # M ~ N(adjusted_margin_away, MARGIN_STD²)
    # P(away wins) = P(M > 0) = Φ(μ / σ)
    math_win_prob_away = _normal_cdf(adjusted_margin_away / MARGIN_STD)
    math_win_prob_home = 1.0 - math_win_prob_away

    # --- Pure-math cover probability ---
    # Away covers when M > −away.run_line  (e.g. run_line = -1.5 → threshold = +1.5)
    cover_threshold = -away.run_line
    away_cover_pct = _normal_cdf((adjusted_margin_away - cover_threshold) / MARGIN_STD)
    home_cover_pct = 1.0 - away_cover_pct

    # --- Over / Under ---
    # Our O/U line is defined as the expected total itself, so P(total > line) = Φ(0) = 50%.
    # A separate O/U line input would allow asymmetric probabilities; absent one, 50/50 is exact.
    over_pct = 0.5
    under_pct = 0.5

    # --- Projected scores ---
    proj_away = (expected_total + adjusted_margin_away) / 2
    proj_home = (expected_total - adjusted_margin_away) / 2

    return {
        "away": away,
        "home": home,
        "ml_win_prob_away": ml_prob_away,
        "ml_win_prob_home": ml_prob_home,
        "rpi_used": rpi_used,
        "rpi_prob_away": rpi_prob_away_used,
        "rpi_prob_home": 1.0 - rpi_prob_away_used,
        "rpi_weight": rpi_weight_used,
        "blended_win_prob_away": blended_prob_away,
        "blended_win_prob_home": blended_prob_home,
        "math_win_prob_away": math_win_prob_away,
        "math_win_prob_home": math_win_prob_home,
        "projected_score_away": proj_away,
        "projected_score_home": proj_home,
        "projected_margin_away": adjusted_margin_away,
        "projected_total": expected_total,
        "expected_total": expected_total,
        "away_cover_pct": away_cover_pct,
        "home_cover_pct": home_cover_pct,
        "over_pct": over_pct,
        "under_pct": under_pct,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_report(r: dict) -> str:
    away: Team = r["away"]
    home: Team = r["home"]

    def pct(v: float) -> str:
        return f"{v * 100:.1f}%"

    def score(v: float) -> str:
        return f"{v:.1f}"

    pick_ml = away.name if r["math_win_prob_away"] > 0.50 else home.name
    pick_rl = (
        f"{away.name} {away.run_line:+.1f}"
        if r["away_cover_pct"] > 0.50
        else f"{home.name} {home.run_line:+.1f}"
    )
    pick_ou = "OVER" if r["over_pct"] > 0.50 else "UNDER"

    lines = [
        "=" * 60,
        "  COLLEGE BASEBALL GAME SIMULATION",
        "=" * 60,
        f"  {'Away:':8s} {away.name}",
        f"  {'Home:':8s} {home.name}",
        "-" * 60,
        "  ODDS INPUT",
        f"  {away.name:<{TEAM_NAME_WIDTH}s}  ML {away.ml_odds:+d}  "
        f"RL {away.run_line:+.1f} ({away.rl_odds:+d})",
        f"  {home.name:<{TEAM_NAME_WIDTH}s}  ML {home.ml_odds:+d}  "
        f"RL {home.run_line:+.1f} ({home.rl_odds:+d})",
        "-" * 60,
        "  MONEYLINE IMPLIED WIN PROBABILITY (de-vigged)",
        f"  {away.name:<{TEAM_NAME_WIDTH}s}  {pct(r['ml_win_prob_away'])}",
        f"  {home.name:<{TEAM_NAME_WIDTH}s}  {pct(r['ml_win_prob_home'])}",
    ]

    # --- Optional RPI / SOS section ---
    if r["rpi_used"]:
        rpi_w = r["rpi_weight"]
        lines += [
            "-" * 60,
            "  RPI / SOS DATA",
            f"  {away.name:<{TEAM_NAME_WIDTH}s}  RPI {away.rpi_rank}  SOS {away.sos_rank if away.sos_rank is not None else '--'}",
            f"  {home.name:<{TEAM_NAME_WIDTH}s}  RPI {home.rpi_rank}  SOS {home.sos_rank if home.sos_rank is not None else '--'}",
            f"  RPI-based win probability        "
            f"{away.name} {pct(r['rpi_prob_away'])}  |  "
            f"{home.name} {pct(r['rpi_prob_home'])}",
            f"  SOS-weighted RPI blend           {rpi_w * 100:.0f}% RPI + {(1 - rpi_w) * 100:.0f}% ML",
            f"  Blended win probability          "
            f"{away.name} {pct(r['blended_win_prob_away'])}  |  "
            f"{home.name} {pct(r['blended_win_prob_home'])}",
        ]

    lines += [
        "-" * 60,
        "  MATH ANALYSIS",
        f"  {'Win %':<{TEAM_NAME_WIDTH}s}  {away.name} {pct(r['math_win_prob_away'])}  |  "
        f"{home.name} {pct(r['math_win_prob_home'])}",
        f"  {'Run Line cover %':<{TEAM_NAME_WIDTH}s}  {away.name} {pct(r['away_cover_pct'])}  |  "
        f"{home.name} {pct(r['home_cover_pct'])}",
        f"  {'Over/Under %':<{TEAM_NAME_WIDTH}s}  OVER {pct(r['over_pct'])}  |  UNDER {pct(r['under_pct'])}",
        "-" * 60,
        "  PROJECTED SCORE (runs)",
        f"  {away.name:<{TEAM_NAME_WIDTH}s}  {score(r['projected_score_away'])}",
        f"  {home.name:<{TEAM_NAME_WIDTH}s}  {score(r['projected_score_home'])}",
        f"  {'Projected total runs':<{TEAM_NAME_WIDTH}s}  {score(r['projected_total'])}",
        "-" * 60,
        "  PICKS",
        f"  Moneyline : {pick_ml}",
        f"  Run Line  : {pick_rl}",
        f"  Over/Under: {pick_ou} {score(r['expected_total'])}",
        f"  Score     : {away.name} {round(r['projected_score_away'])} - {home.name} {round(r['projected_score_home'])}",
        "=" * 60,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) > 1:
        line = " ".join(sys.argv[1:])
    else:
        print("Enter matchup line:")
        print("  Full format : Team A ML -139 -1.5 +108 at Team B ML +104 +1.5 -148")
        print("  Short format: Team A +5.5 -136 Team B -5.5 +100")
        line = input().strip()

    if not line:
        print("No input provided.", file=sys.stderr)
        return 1

    try:
        matchup = parse_matchup(line)
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    results = calculate_game(matchup)
    print(format_report(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
