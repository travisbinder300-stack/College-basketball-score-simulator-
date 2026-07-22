# Multi-Sports ML Platform

A production-oriented machine learning platform for predicting game totals across major sports leagues. The shared prediction target is **total score** (home + away), which generalizes cleanly across all supported sports.

## Supported Sports

| Sport | Key | League | Status | Sample Generator |
|---|---|---|---|---|
| NBA | `nba` | National Basketball Association | ✅ Active | `generate_sample_nba_games()` |
| NFL | `nfl` | National Football League | ✅ Active | `generate_sample_nfl_games()` |
| MLB | `mlb` | Major League Baseball | ✅ Active | `generate_sample_mlb_games()` |
| NHL | `nhl` | National Hockey League | ✅ Active | `generate_sample_nhl_games()` |
| WNBA | `wnba` | Women's National Basketball Association | ✅ Active | `generate_sample_wnba_games()` |
| NCAAB | `ncaab` | NCAA Division I Men's Basketball | ✅ Active | `generate_sample_ncaab_games()` |
| NCAAF | `ncaaf` | NCAA Division I Men's Football (FBS) | ✅ Active | `generate_sample_ncaaf_games()` |
| College Baseball | `ncaa_baseball` | NCAA Division I Baseball | ✅ Active | `generate_sample_ncaa_baseball_games()` |

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run the end-to-end pipeline for any supported sport using its generated sample data:

```python
# NBA example
from multisports.config.nba import NBA_CONFIG
from multisports.data.ingestion import generate_sample_nba_games
from multisports.pipeline.pipeline import Pipeline

results = Pipeline(NBA_CONFIG).run(generate_sample_nba_games(n=200))
print(results)
```

```python
# NHL example
from multisports.config.nhl import NHL_CONFIG
from multisports.data.ingestion import generate_sample_nhl_games
from multisports.pipeline.pipeline import Pipeline

results = Pipeline(NHL_CONFIG).run(generate_sample_nhl_games(n=200))
print(results)
```

Replace `NHL_CONFIG` / `generate_sample_nhl_games` with any supported sport's equivalents.

## Project Structure

```
src/multisports/
  config/          sport-specific SportConfig instances (nba, nfl, mlb, nhl, wnba, ncaab, ncaaf, ncaa_baseball)
  data/            Game/Team/Player schema, CSV/JSON loaders, sample data generators
  features/        Leak-safe rolling feature generation (shift(1) prevents data leakage)
  models/          MeanBaseline and GradientBoostingRegressor with save/load
  training/        Time-based train/val split, evaluation metrics (MAE, RMSE, accuracy, calibration)
  prediction/      Inference helper (Predictor)
  pipeline/        End-to-end orchestrator: ingest → clean → features → train → evaluate → save
configs/           YAML config files for each sport
tests/             Unit tests for schema, features, models, evaluation, and full pipeline
```

## Key Design Principles

- **No data leakage**: all rolling features use `.shift(1)` — each row only sees past games
- **Time-based validation only**: 80/20 chronological split, never random
- **Explicit feature columns**: `SportConfig.feature_columns` is an ordered list; models never silently use wrong features
- **Sport-isolated logic**: each sport has its own config and can have its own feature generator

## How to Add a New Sport

1. Create `src/multisports/config/<sport>.py` with a `SportConfig` instance
2. Add a YAML equivalent to `configs/<sport>.yaml`
3. Add the config to `src/multisports/config/__init__.py`
4. Add a `generate_sample_<sport>_games()` function to `src/multisports/data/ingestion.py` (or a real data loader)
5. Add tests covering schema, features, models, and pipeline behavior

## Testing

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Live Data Script

Fetch live scoreboard data and save normalized game rows to JSON:

```bash
PYTHONPATH=src python scripts/get_live_data.py --sport ncaab --dates 20260722
```

By default the script writes to `data/live/<sport>_<dates>.json`.

## Predictive Rankings Integration (WNBA 2026)

The WNBA pipeline supports optional **predictive power ratings** sourced from
[TeamRankings](https://www.teamrankings.com/wnba/ranking/predictive-by-other/).
Each team's rating represents their expected point-differential against an
average opponent on a neutral court (positive → stronger, negative → weaker).

### Bundled 2026 rankings

A mid-season 2026 snapshot is committed at
`data/rankings/wnba_2026_predictive.csv` (15 teams including the Toronto Tempo
and Portland Fire expansion franchises).

### Use rankings in the WNBA pipeline

```python
from multisports.config.wnba import WNBA_CONFIG
from multisports.data.ingestion import generate_sample_wnba_games
from multisports.pipeline.pipeline import Pipeline

results = Pipeline(WNBA_CONFIG).run(
    generate_sample_wnba_games(n=200),
    rankings_path="data/rankings/wnba_2026_predictive.csv",
)
```

Teams not found in the CSV (e.g. synthetic team IDs) receive the mean rating
automatically — the pipeline never errors on unknown teams.

### Refresh rankings from TeamRankings

```bash
PYTHONPATH=src python scripts/fetch_rankings.py --sport wnba --season 2026
```

This overwrites `data/rankings/wnba_2026_predictive.csv` with fresh data.
Run it at the start of each week or after a major trade deadline.

| Flag | Description |
|---|---|
| `--sport` | Sport key. One of: `mlb`, `nba`, `ncaab`, `ncaaf`, `nfl`, `nhl`, `wnba` |
| `--season` | Season label used in the default output filename (e.g. `2026`). |
| `--output` | Custom output path. |

### Load rankings directly

```python
from multisports.data.rankings import enrich_with_rankings, load_rankings_csv

ratings = load_rankings_csv("data/rankings/wnba_2026_predictive.csv")
enriched_df = enrich_with_rankings(featured_df, ratings)
```

## Scrape Script

Paste any schedule/results page URL and the script will find game rows in the HTML tables, normalize them to the project `Game` schema, and save as JSON:

```bash
# Paste the URL of whichever schedule page you want
PYTHONPATH=src python scripts/scrape_data.py \
    --url "https://example-site.com/ncaab/2024-schedule" \
    --sport ncaab --season 2024

# Multiple pages at once
PYTHONPATH=src python scripts/scrape_data.py \
    --url "https://example-site.com/page1" "https://example-site.com/page2" \
    --sport nba --season 2024

# Custom output path
PYTHONPATH=src python scripts/scrape_data.py \
    --url "https://example-site.com/mlb-2024" \
    --sport mlb --season 2024 \
    --output data/scraped/mlb_2024.json
```

By default the script writes to `data/scraped/<sport>_<season>.json`.

| Flag | Description |
|---|---|
| `--url` | **Required.** One or more schedule/results page URLs to scrape (paste in whatever page you like). |
| `--sport` | Sport key for schema context and default output filename. One of: `mlb`, `nba`, `ncaa_baseball`, `ncaab`, `ncaaf`, `nfl`, `nhl`, `wnba` |
| `--season` | Season label stored on each game row (e.g. `2024` or `2023-2024`). |
| `--output` | Custom output file path. |
