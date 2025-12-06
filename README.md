# College Basketball Score Predictor

A Python-based college men's basketball scoring prediction system that uses point spreads and totals to predict game outcomes. This tool implements statistical models similar to KenPom methodology, using efficiency ratings, tempo, and other advanced metrics.

## Features

- **Statistical Prediction Engine**: Uses offensive/defensive efficiency ratings and tempo to predict game scores
- **Point Spread & Total Analysis**: Can predict outcomes from betting lines (spread and total points)
- **Team Statistics**: Support for KenPom-style team efficiency metrics
- **Monte Carlo Simulation**: Run thousands of game simulations for probability distributions with configurable iterations (supports up to 20,000 simulations like professional models)
- **Home Court Advantage**: Configurable home court advantage factor with neutral site and venue-specific adjustments
- **Win Probability**: Calculate win probabilities based on point spreads
- **Recent Form Weighting**: Weight recent games (last 5-10) more heavily than early season performance
- **Injury/Roster Impact**: Adjust efficiency ratings for missing key players
- **Rest Days Factor**: Account for fatigue from back-to-back games or short rest
- **Venue-Specific Adjustments**: Different adjustments for home, away, and neutral site games
- **Strength of Schedule**: Weight performance against tougher opponents
- **Tournament/Motivation Boost**: Optional intensity boost for high-stakes games
- **Free Throw Differential**: Account for teams' fouling rates and free throw percentage
- **Calibratable Variance**: Adjustable score variance parameter for improved accuracy
- **Blowout Detection**: Automatically detects large efficiency gaps and adjusts variance for potential blowouts
- **Advanced Analytics**: Comprehensive statistical modeling for professional-grade predictions

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
- `--neutral`: Flag for neutral site games (reduces home court advantage)
- `--venue-type`: Specify venue type: `home` (default), `neutral`, or `away`
- `--tournament`: Enable tournament/high-stakes intensity boost
- `--simulate`: Run Monte Carlo simulation
- `--num-simulations`: Number of simulations to run (default: 1000, max recommended: 20000)

### Running 20,000 Simulations (Professional-Grade Analysis)

For maximum precision similar to professional sports analytics models:

```bash
python basketball_predictor.py \
  --mode team_stats \
  --home "Gonzaga" \
  --away "Kentucky" \
  --team-data example_teams.json \
  --simulate \
  --num-simulations 20000 \
  --tournament
```

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

### Advanced Team Data Format (with All Features)

For maximum accuracy, you can include all advanced features:

```json
{
  "Duke": {
    "offensive_efficiency": 115.2,
    "defensive_efficiency": 92.8,
    "tempo": 71.5,
    "recent_games_weight": 0.3,
    "recent_offensive_efficiency": 118.5,
    "recent_defensive_efficiency": 90.1,
    "injury_impact": -3.0,
    "rest_days": 1,
    "free_throw_rate": 0.28,
    "free_throw_pct": 0.75,
    "strength_of_schedule": 108.5
  }
}
```

### Metrics Explained

**Core Metrics:**
- **Offensive Efficiency**: Points scored per 100 possessions
- **Defensive Efficiency**: Points allowed per 100 possessions  
- **Tempo**: Average possessions per game

**Advanced Metrics (all optional):**
- **Recent Games Weight**: Weight given to recent games (0-1, where 0.3 means 30% recent, 70% season average)
- **Recent Offensive Efficiency**: Offensive efficiency for last 5-10 games
- **Recent Defensive Efficiency**: Defensive efficiency for last 5-10 games
- **Injury Impact**: Efficiency adjustment for missing players (-10 to 0, where -5 = missing star player)
- **Rest Days**: Days since last game (0 = back-to-back, affects fatigue penalty)
- **Free Throw Rate**: FT attempts per FG attempt (typical: 0.2-0.3)
- **Free Throw Percentage**: Free throw shooting percentage (typical: 0.65-0.75)
- **Strength of Schedule**: Average opponent efficiency (100 = national average, >105 = tough schedule)

These metrics can be obtained from sites like KenPom.com, Barttorvik.com, or similar college basketball analytics sources.

## How It Works

### Statistical Model

The predictor uses comprehensive statistical methodology:

1. **Tempo Calculation**: Estimates game tempo using geometric mean of team tempos
2. **Recent Form Weighting**: Applies configurable weighting to emphasize recent games over season averages
3. **Injury & Roster Adjustments**: Accounts for missing key players with efficiency penalties
4. **Rest & Fatigue Modeling**: Adjusts for back-to-back games and short rest periods
5. **Efficiency Adjustment**: Adjusts team offensive efficiency against opponent's defensive efficiency
6. **Free Throw Differential**: Incorporates fouling rates and FT% into scoring predictions
7. **Strength of Schedule**: Weights performance against tougher opponents higher
8. **Score Prediction**: Calculates expected points using efficiency per 100 possessions
9. **Venue-Specific Adjustments**: Different advantages for home (~3.5 pts), neutral (~1.5 pts), and away (0 pts)
10. **Tournament Intensity**: Optional boost for high-stakes games (March Madness, conference tournaments)
11. **Blowout Detection**: Identifies potential blowouts based on efficiency gaps and increases variance
12. **Win Probability**: Uses logistic regression on point spread
13. **Monte Carlo Simulation**: Runs up to 20,000 simulations with calibratable variance for distribution analysis

### Example Calculation

For Duke (115 OffEff, 92 DefEff, 71 tempo) vs UNC (112 OffEff, 94 DefEff, 73 tempo):

1. Expected tempo = √(71 × 73) ≈ 72 possessions
2. Duke offense vs UNC defense: (115 × 100 / 94) = 122.3 rating
3. Duke expected score: (122.3 × 72 / 100) + 3.5 (HCA) + FT differential ≈ 91.5 points

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
