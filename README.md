# College-baseball-score-simulator-
Baseball-simulator

## Data

`bb_data.csv` contains base-on-balls (BB) statistics for all 250 NCAA teams (complete dataset).

Columns: `rank, team, games, BB`

| Stat | Value |
|------|-------|
| Teams | 250 |
| BB leader | Georgia Tech — 79 BB in 9 G |
| BB trailer | UMBC — 8 BB in 3 G |

## Scripts

- `bb_stats_table.py` — prints a ranked BB (Base on Balls) stats table with analysis
- `ba_stats_table.py` — prints a ranked BA (Batting Average) stats table with analysis
- `game_simulator.py` — simulates game scores
- `rpi_table_printer.py` — prints RPI table

## Batting Average Data

`ba_data.csv` contains batting average (BA) statistics. Teams are added manually one at a time.

Columns: `Rank, Team, G, AB, H, BA`

| Column | Description |
|--------|-------------|
| Rank | BA rank (1 = highest average) |
| Team | Team name |
| G | Games played |
| AB | At-bats |
| H | Hits |
| BA | Batting average (H / AB) |

