# NHL Spread and Total Analytics System

A Python-based analytics system that provides NHL game predictions with 70% confidence intervals using real NHL data from the official NHL API.

## Features

- **Real-Time NHL Data**: Fetches current standings, team statistics, and schedules from the official NHL API
- **Spread Predictions**: Calculates expected point spreads with 70% confidence intervals
- **Total Predictions**: Predicts over/under totals with 70% confidence intervals
- **Statistical Modeling**: Uses team strength ratings, goals per game, and defensive metrics
- **Confidence Intervals**: Provides statistical confidence ranges for all predictions

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the analytics system with example matchups:

```bash
python nhl_analytics.py
```

### Python API

```python
from nhl_analytics import NHLAnalytics

# Initialize the analytics system
analytics = NHLAnalytics()

# Get spread prediction
spread = analytics.predict_spread("TOR", "MTL")  # Toronto vs Montreal
print(f"Predicted Spread: {spread['predicted_spread']}")
print(f"70% Confidence: [{spread['confidence_interval']['lower']}, {spread['confidence_interval']['upper']}]")

# Get total prediction
total = analytics.predict_total("TOR", "MTL")
print(f"Predicted Total: {total['predicted_total']}")
print(f"70% Confidence: [{total['confidence_interval']['lower']}, {total['confidence_interval']['upper']}]")

# Get complete analysis
analysis = analytics.get_full_analysis("TOR", "MTL")
print(analysis)
```

## NHL Team Abbreviations

Common NHL team abbreviations:
- **ANA**: Anaheim Ducks
- **BOS**: Boston Bruins
- **BUF**: Buffalo Sabres
- **CAR**: Carolina Hurricanes
- **CBJ**: Columbus Blue Jackets
- **CGY**: Calgary Flames
- **CHI**: Chicago Blackhawks
- **COL**: Colorado Avalanche
- **DAL**: Dallas Stars
- **DET**: Detroit Red Wings
- **EDM**: Edmonton Oilers
- **FLA**: Florida Panthers
- **LAK**: Los Angeles Kings
- **MIN**: Minnesota Wild
- **MTL**: Montreal Canadiens
- **NJD**: New Jersey Devils
- **NSH**: Nashville Predators
- **NYI**: New York Islanders
- **NYR**: New York Rangers
- **OTT**: Ottawa Senators
- **PHI**: Philadelphia Flyers
- **PIT**: Pittsburgh Penguins
- **SEA**: Seattle Kraken
- **SJS**: San Jose Sharks
- **STL**: St. Louis Blues
- **TBL**: Tampa Bay Lightning
- **TOR**: Toronto Maple Leafs
- **VAN**: Vancouver Canucks
- **VGK**: Vegas Golden Knights
- **WPG**: Winnipeg Jets
- **WSH**: Washington Capitals

## How It Works

### Spread Predictions

The system calculates the expected goal differential between teams using:

1. **Team Strength Rating** (0-100 scale):
   - Win percentage (60% weight)
   - Goal differential per game (40% weight)

2. **Home Ice Advantage**: ~3 points added to home team

3. **Confidence Interval**: 70% confidence using normal distribution with standard deviation of 1.5 goals

### Total Predictions

The system predicts the combined score using:

1. **Offensive Metrics**: Goals per game for each team
2. **Defensive Metrics**: Goals allowed per game for each team
3. **Expected Goals**: Average of offensive capability vs defensive vulnerability
4. **Confidence Interval**: 70% confidence using normal distribution with standard deviation of 1.8 goals

## Data Sources

- **NHL API**: Official NHL statistics API (api-web.nhle.com)
- **Real-Time Data**: Current season standings, team stats, and schedules
- **Historical Data**: Team performance metrics from completed games

## Statistical Methodology

The system uses statistical modeling to ensure 70% confidence:

- **Z-Score Calculation**: Uses scipy.stats to calculate appropriate z-scores for 70% confidence (~1.04)
- **Confidence Intervals**: Provides ranges where actual results should fall 70% of the time
- **Standard Deviations**: Based on historical NHL game variance
  - Spreads: σ = 1.5 goals
  - Totals: σ = 1.8 goals

## Example Output

```
============================================================
NHL Spread and Total Analytics System
70% Confidence Level Predictions
============================================================

============================================================
Analyzing: MTL @ TOR
============================================================

📊 SPREAD PREDICTION:
   Predicted Spread: 2.15
   TOR favored by 2.1 goals
   70% Confidence Interval: [0.59, 3.71]
   TOR Strength: 61.5
   MTL Strength: 52.0

🎯 TOTAL PREDICTION:
   Predicted Total: 6.2
   Average-scoring game expected
   70% Confidence Interval: [4.33, 8.07]
   Expected TOR Goals: 3.5
   Expected MTL Goals: 2.7
```

## Limitations

- Predictions are based on current season statistics
- Does not account for injuries, lineup changes, or recent form
- Confidence intervals represent statistical ranges, not certainties
- Requires internet connection to fetch real-time NHL data

## Testing

Run the test suite:
```bash
python test_nhl_analytics.py
```

## License

See LICENSE file for details.

## Contributing

This project provides NHL analytics with statistical confidence. Contributions to improve prediction accuracy are welcome.
