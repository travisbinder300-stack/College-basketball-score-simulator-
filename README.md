# College Basketball Score Predictor

A Python-based college men's basketball scoring prediction system that uses point spreads and totals to predict game outcomes. This tool implements statistical models similar to KenPom methodology, using efficiency ratings, tempo, and other advanced metrics.

## Features

- **Statistical Prediction Engine**: Uses offensive/defensive efficiency ratings and tempo to predict game scores
- **Point Spread & Total Analysis**: Can predict outcomes from betting lines (spread and total points)
- **Team Statistics**: Support for KenPom-style team efficiency metrics
- **Monte Carlo Simulation**: Run thousands of game simulations for probability distributions with configurable iterations (supports 10,000+ simulations like professional models)
- **Home Court Advantage**: Configurable home court advantage factor
- **Win Probability**: Calculate win probabilities based on point spreads
- **Recent Form Weighting**: Weight recent games (last 5-10) more heavily than early season performance
- **Calibratable Variance**: Adjustable score variance parameter for improved accuracy
- **Blowout Detection**: Automatically detects large efficiency gaps and adjusts variance for potential blowouts
- **Advanced Analytics**: Supports recency-weighted efficiency metrics for more accurate predictions

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
- `--simulate`: Run Monte Carlo simulation
- `--num-simulations`: Number of simulations to run (default: 1000, supports 10,000+ for professional-grade analysis)

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
    "tempo": 71.5
  }
}
```

### Advanced Team Data Format (with Recent Form)

For more accurate predictions, you can include recent form data:

```json
{
  "Duke": {
    "offensive_efficiency": 115.2,
    "defensive_efficiency": 92.8,
    "tempo": 71.5,
    "recent_games_weight": 0.3,
    "recent_offensive_efficiency": 118.5,
    "recent_defensive_efficiency": 90.1
  }
}
```

### Metrics Explained

- **Offensive Efficiency**: Points scored per 100 possessions
- **Defensive Efficiency**: Points allowed per 100 possessions  
- **Tempo**: Average possessions per game
- **Recent Games Weight** (optional): Weight given to recent games (0-1, where 0.3 means 30% recent, 70% season average)
- **Recent Offensive Efficiency** (optional): Offensive efficiency for last 5-10 games
- **Recent Defensive Efficiency** (optional): Defensive efficiency for last 5-10 games

These metrics can be obtained from sites like KenPom.com or similar college basketball analytics sources.

## How It Works

### Statistical Model

The predictor uses the following methodology:

1. **Tempo Calculation**: Estimates game tempo using geometric mean of team tempos
2. **Recent Form Weighting**: Applies configurable weighting to emphasize recent games over season averages
3. **Efficiency Adjustment**: Adjusts team offensive efficiency against opponent's defensive efficiency
4. **Score Prediction**: Calculates expected points using efficiency per 100 possessions
5. **Home Court Advantage**: Adds ~3.5 points for home teams (configurable)
6. **Blowout Detection**: Identifies potential blowouts based on efficiency gaps and increases variance
7. **Win Probability**: Uses logistic regression on point spread
8. **Calibratable Variance**: Adjustable standard deviation parameter for score simulations

### Example Calculation

For Duke (115 OffEff, 92 DefEff, 71 tempo) vs UNC (112 OffEff, 94 DefEff, 73 tempo):

1. Expected tempo = √(71 × 73) ≈ 72 possessions
2. Duke offense vs UNC defense: (115 × 100 / 94) = 122.3 rating
3. Duke expected score: (122.3 × 72 / 100) + 3.5 (HCA) ≈ 91.5 points

## Monte Carlo Simulation

Add the `--simulate` flag to run game simulations. By default, it runs 1,000 simulations, but you can specify any number using `--num-simulations`:

```bash
# Run with default 1,000 simulations
python basketball_predictor.py \
  --mode spread_total \
  --home "Kansas" \
  --away "Kentucky" \
  --spread 3.0 \
  --total 145.0 \
  --simulate

# Run with 10,000 simulations (like Haralabos Voulgaris's model)
python basketball_predictor.py \
  --mode team_stats \
  --home "Duke" \
  --away "Kansas" \
  --team-data example_teams.json \
  --simulate \
  --num-simulations 10000
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

# Create predictor with custom parameters
predictor = BasketballPredictor(
    home_court_advantage=3.5,  # Default home court advantage
    score_std_dev=10.5          # Calibrated score variance
)

# Define teams with season averages only
duke = TeamStats(
    name="Duke", 
    offensive_efficiency=115.2, 
    defensive_efficiency=92.8, 
    tempo=71.5
)

# Define teams with recent form weighting
unc = TeamStats(
    name="UNC", 
    offensive_efficiency=112.4,
    defensive_efficiency=94.2, 
    tempo=73.8,
    recent_games_weight=0.3,  # 30% weight to recent games
    recent_offensive_efficiency=115.0,  # Recent form is better
    recent_defensive_efficiency=92.0
)

# Predict game
prediction = predictor.predict_game(duke, unc)
print(prediction)

# Or use spread/total
prediction = predictor.predict_from_spread_and_total(
    "Duke", "UNC", point_spread=5.5, total_points=148.5
)

# Run simulation with blowout detection
results = predictor.simulate_game(
    prediction, 
    num_simulations=10000,
    home_team_stats=duke,  # Pass stats for blowout detection
    away_team_stats=unc
)
print(f"Home win probability: {results['home_win_pct']:.1%}")
print(f"Variance used: {results['score_std_used']:.1f}")
```

## Data Sources

For real team data, you can use:
- **KenPom.com**: Premium college basketball analytics (requires subscription)
- **BartTorvik.com**: Free college basketball statistics
- **Sports-Reference.com**: Historical team statistics
- **NCAA Stats**: Official NCAA team statistics

## Limitations and Improvements

### Current Limitations
- Predictions are based on season-long averages (mitigated with recent form weighting)
- Does not account for injuries or lineup changes
- Efficiency ratings are more reliable with larger sample sizes
- Home court advantage varies by venue (default is 3.5 points)

### Accuracy Improvements (NEW)
The model now includes several enhancements for better predictions:

1. **Recent Form Weighting**: Weight recent games (last 5-10) more heavily to capture team momentum and current performance
2. **Calibratable Variance**: Adjust the `score_std_dev` parameter based on historical prediction errors
3. **Blowout Detection**: Automatically increases variance when large efficiency gaps suggest potential blowouts
4. **Flexible Data Updates**: Support for optional recent efficiency metrics in team data

### Recommended Usage for Best Accuracy
1. Update team efficiency data regularly (weekly or after significant games)
2. Use recent form weighting (0.2-0.4) for teams with strong recent performance trends
3. Calibrate variance based on historical prediction accuracy
4. Include injury adjustments by manually adjusting efficiency ratings
5. Consider situational factors (rest days, travel) when interpreting predictions

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Prediction methodology inspired by Ken Pomeroy's efficiency-based basketball analytics system.
