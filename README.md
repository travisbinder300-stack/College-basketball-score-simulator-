# MLB Pitcher Props Model (Scaffold)

This repository has been re-scoped to an MLB pitcher player-prop project.

## Initial scope

- Prop types: **strikeouts** and **recorded outs**
- Inputs:
  - Pitcher baseline rates (strikeouts per out, outs baseline)
  - Opponent/context multipliers
  - Optional weather data
  - Market odds/line
- Outputs:
  - Adjusted projection for strikeouts and outs
  - Over/under probabilities vs market line
  - Implied probability and model edge

## Project layout

- `src/mlb_pitcher_props/models.py` - data models
- `src/mlb_pitcher_props/baseline.py` - baseline projection logic
- `src/mlb_pitcher_props/adjustments.py` - weather/context adjustments
- `src/mlb_pitcher_props/odds.py` - market odds + edge math
- `src/mlb_pitcher_props/evaluation.py` - backtesting/calibration scaffold
- `src/mlb_pitcher_props/cli.py` - command line entrypoint
- `tests` - core unit tests

## Run the CLI

```bash
PYTHONPATH=src \
python -m mlb_pitcher_props.cli \
  --input examples/sample_input.json
```

## Run tests

```bash
cd /home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-
PYTHONPATH=src \
python -m unittest discover -s tests -v
```
