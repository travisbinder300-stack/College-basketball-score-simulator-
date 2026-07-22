# Multi-Sports ML Platform

A production-oriented, greenfield machine learning platform for predicting game totals across sports. Version 1 focuses on NBA total-score prediction (home score + away score), which is the shared target designed to generalize to NFL, MLB, and future sports.

## Roadmap

- **NBA (v1):** end-to-end data generation, feature engineering, training, evaluation, and prediction
- **NFL:** config and model-registration stub included for future expansion
- **MLB:** config and model-registration stub included for future expansion

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run the end-to-end NBA pipeline with generated sample data:

```bash
PYTHONPATH=src python - <<'PY'
from multisports.config.nba import NBA_CONFIG
from multisports.data.ingestion import generate_sample_nba_games
from multisports.pipeline.pipeline import Pipeline

games = generate_sample_nba_games(n=200, seed=42)
results = Pipeline(NBA_CONFIG).run(games)
print(results)
PY
```

## Project Structure

- `multisports.config`: sport-specific configuration
- `multisports.data`: schema, ingestion, and cleaning utilities
- `multisports.features`: leak-safe feature generation
- `multisports.models`: baseline and gradient boosting regressors
- `multisports.training`: evaluation metrics and training loop
- `multisports.prediction`: inference helper
- `multisports.pipeline`: orchestration layer

## How to Add a New Sport

1. Create a new `SportConfig` with explicit `feature_columns`.
2. Register a feature generator in `src/multisports/features/registry.py`.
3. Register models in `src/multisports/models/registry.py`.
4. Add ingestion logic or sample-data generation for the new sport.
5. Add tests covering schema, features, models, and pipeline behavior.

## Testing

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
