# College Basketball Score Predictor

A Python-based college men's basketball scoring prediction system that uses point spreads and totals to predict game outcomes. This tool implements statistical models similar to KenPom methodology, using efficiency ratings, tempo, and other advanced metrics.

## Features

- **Statistical Prediction Engine**: Uses offensive/defensive efficiency ratings and tempo to predict game scores
- **Point Spread & Total Analysis**: Can predict outcomes from betting lines (spread and total points)
- **Team Statistics**: Support for KenPom-style team efficiency metrics
- **Monte Carlo Simulation**: Run thousands of game simulations for probability distributions
- **Home Court Advantage**: Configurable home court advantage factor
- **Win Probability**: Calculate win probabilities based on point spreads

## Installation

1. Clone this repository:
```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Using Team Statistics

Predict a game using team efficiency ratings (similar to KenPom data):

```bash
python basketball_predictor.py \
  --mode team_stats \
  --home "Duke" \
  --away "North Carolina" \
  --team-data example_teams.json
```

### Method 2: Using Point Spread and Total

Predict scores from betting lines:

```bash
python basketball_predictor.py \
  --mode spread_total \
  --home "Duke" \
  --away "North Carolina" \
  --spread 5.5 \
  --total 148.5
```

### Options

- `--mode`: Choose prediction mode (`team_stats` or `spread_total`)
- `--home`: Name of the home team
- `--away`: Name of the away team
- `--team-data`: JSON file containing team statistics (required for `team_stats` mode)
- `--spread`: Point spread, positive means home team favored (required for `spread_total` mode)
- `--total`: Expected total points (required for `spread_total` mode)
- `--neutral`: Flag for neutral site games (removes home court advantage)
- `--simulate`: Run Monte Carlo simulation with 1000 iterations

### Example Output

```
Game Prediction:
North Carolina @ Duke
Predicted Score: North Carolina 72.3 - Duke 77.8
Point Spread: Duke -5.5
Total: 150.1
Home Win Probability: 65.4%
```

## Team Data Format

Team statistics should be provided in JSON format with KenPom-style metrics:

```json
{
  "Duke": {
    "offensive_efficiency": 115.2,
    "defensive_efficiency": 92.8,
    "tempo": 71.5,
    "coaching_style": "offensive"
  }
}
```

### Metrics Explained

- **Offensive Efficiency**: Points scored per 100 possessions
- **Defensive Efficiency**: Points allowed per 100 possessions  
- **Tempo**: Average possessions per game
- **Coaching Style** (optional): Playing philosophy that affects game dynamics
  - `fast-paced`: Emphasizes transition offense, increases tempo (+5%) and offense (+2%)
  - `slow-tempo`: Emphasizes half-court offense, decreases tempo (-5%) and improves defense (+2%)
  - `defensive`: Focus on limiting opponent scoring, improves defense (+5%), reduces offense (-3%)
  - `offensive`: Focus on scoring, improves offense (+5%), reduces defense (-3%)
  - `balanced`: No adjustments (default if not specified)

These metrics can be obtained from sites like KenPom.com or similar college basketball analytics sources.

## How It Works

### Statistical Model

The predictor uses the following methodology:

1. **Tempo Calculation**: Estimates game tempo using geometric mean of team tempos
2. **Coaching Style Adjustments**: Applies tempo and efficiency modifiers based on coaching philosophies
3. **Efficiency Adjustment**: Adjusts team offensive efficiency against opponent's defensive efficiency
4. **Score Prediction**: Calculates expected points using efficiency per 100 possessions
5. **Home Court Advantage**: Adds ~3.5 points for home teams (configurable)
6. **Win Probability**: Uses logistic regression on point spread

### Example Calculation

For Duke (115 OffEff, 92 DefEff, 71 tempo, offensive style) vs UNC (112 OffEff, 94 DefEff, 73 tempo, fast-paced style):

1. Expected tempo = √(71 × 73) ≈ 72 possessions
2. Apply coaching style adjustments (offensive + fast-paced = 4% tempo increase)
3. Duke offense vs UNC defense with style modifiers
4. Duke expected score: adjusted rating × adjusted possessions / 100 + 3.5 (HCA)

## Monte Carlo Simulation

Add the `--simulate` flag to run 1000 game simulations:

```bash
python basketball_predictor.py \
  --mode spread_total \
  --home "Kansas" \
  --away "Kentucky" \
  --spread 3.0 \
  --total 145.0 \
  --simulate
```

This provides:
- Win percentage distributions
- Score ranges (90% confidence intervals)
- Average simulated scores

## Running Tests

Run the test suite:

```bash
python -m unittest test_basketball_predictor.py
```

Or run with verbose output:

```bash
python -m unittest test_basketball_predictor.py -v
```

## Python API

You can also use the predictor programmatically:

```python
from basketball_predictor import BasketballPredictor, TeamStats

# Create predictor
predictor = BasketballPredictor(home_court_advantage=3.5)

# Define teams with coaching styles
duke = TeamStats(name="Duke", offensive_efficiency=115.2, 
                 defensive_efficiency=92.8, tempo=71.5, 
                 coaching_style="offensive")
unc = TeamStats(name="UNC", offensive_efficiency=112.4,
                defensive_efficiency=94.2, tempo=73.8,
                coaching_style="fast-paced")

# Predict game
prediction = predictor.predict_game(duke, unc)
print(prediction)

# Or use spread/total
prediction = predictor.predict_from_spread_and_total(
    "Duke", "UNC", point_spread=5.5, total_points=148.5
)

# Run simulation
results = predictor.simulate_game(prediction, num_simulations=1000)
print(f"Home win probability: {results['home_win_pct']:.1%}")
```

## Data Sources

For real team data, you can use:
- **KenPom.com**: Premium college basketball analytics (requires subscription)
- **BartTorvik.com**: Free college basketball statistics
- **Sports-Reference.com**: Historical team statistics
- **NCAA Stats**: Official NCAA team statistics

## Limitations

- Predictions are based on season-long averages and may not reflect recent form
- Does not account for injuries, lineup changes, or other situational factors
- Efficiency ratings are more reliable with larger sample sizes
- Home court advantage varies by venue (default is 3.5 points)

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Prediction methodology inspired by Ken Pomeroy's efficiency-based basketball analytics system.
