# College Baseball Score Simulator

> ⚾ **This is a college BASEBALL simulator — not basketball.**
> All data, statistics, and simulations in this repository are for college baseball only.
> Do not add basketball content here.

## Data

`bb_data.csv` contains base-on-balls (BB) statistics for all 250 NCAA teams (complete dataset).

Columns: `rank, team, games, BB`

| Stat | Value |
|------|-------|
| Teams | 250 |
| BB leader | Georgia Tech — 79 BB in 9 G |
| BB trailer | UMBC — 8 BB in 3 G |

## Scripts

- `data_inventory.py` — **prints a complete summary of all datasets and tools in the system** (`python data_inventory.py`)
- `bb_stats_table.py` — prints a ranked BB (Base on Balls) stats table with analysis
- `ba_stats_table.py` — prints a ranked BA (Batting Average) stats table with reliability analysis
- `dp_stats_table.py` — prints a ranked DP (Double Play) stats table with analysis
- `game_simulator.py` — simulates game scores (supports ML odds, run lines, RPI, SOS)
- `rpi_table_printer.py` — prints RPI table from raw text input

## Batting Average Data

`ba_data.csv` contains batting average (BA) statistics for all 300 NCAA Division I teams (complete dataset).

Columns: `Rank, Team, G, AB, H, BA`

| Column | Description |
|--------|-------------|
| Rank | BA rank (1 = highest average) |
| Team | Team name |
| G | Games played |
| AB | At-bats |
| H | Hits |
| BA | Batting average (H / AB) |

| Stat | Value |
|------|-------|
| Teams | 300 |
| BA leader | Georgia Tech — .414 (138 H / 333 AB, 9 G) |
| BA trailer | Coppin St. — .147 (15 H / 102 AB, 4 G) |
| Overall BA | .270 |
| Reliability | `Rel% = AB / (AB + 350) × 100` — higher means more trustworthy BA |

> Run `python data_inventory.py` to see current leader/trailer and full stats.

## Double Play Data

`dp_data.csv` contains double play (DP) statistics. Teams are added manually one at a time.

Columns: `Rank, Team, G, DP`

| Column | Description |
|--------|-------------|
| Rank | DP rank (1 = most double plays turned) |
| Team | Team name |
| G | Games played |
| DP | Total double plays turned |

Add a row:
```
echo "1,Texas A&M,10,18" >> dp_data.csv
python dp_stats_table.py
```

> Run `python dp_stats_table.py --sample` to see a preview with built-in sample data.

