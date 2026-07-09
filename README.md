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

- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src/mlb_pitcher_props/models.py` - data models
- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src/mlb_pitcher_props/baseline.py` - baseline projection logic
- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src/mlb_pitcher_props/adjustments.py` - weather/context adjustments
- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src/mlb_pitcher_props/odds.py` - market odds + edge math
- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src/mlb_pitcher_props/evaluation.py` - backtesting/calibration scaffold
- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src/mlb_pitcher_props/cli.py` - command line entrypoint
- `/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/tests` - core unit tests

## Run the CLI

```bash
PYTHONPATH=/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src \
python -m mlb_pitcher_props.cli \
  --input /home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/examples/sample_input.json
```

## Run tests

```bash
cd /home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-
PYTHONPATH=/home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/src \
python -m unittest discover -s /home/runner/work/College-basketball-score-simulator-/College-basketball-score-simulator-/tests -v
```
