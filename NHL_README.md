# NHL Spread and Total Analytics System

A Python-based analytics system that provides NHL game predictions with 70% confidence intervals using real NHL data from the official NHL API.

## Features

- **Real-Time NHL Data**: Fetches current standings, team statistics, and schedules from the official NHL API
- **Spread Predictions**: Calculates expected point spreads with 70% confidence intervals
- **Total Predictions**: Predicts over/under totals with 70% confidence intervals
- **Underdog Identification**: Clearly identifies underdogs in every matchup
- **Value Analysis**: Compare predictions vs market spreads to find overvalued opportunities
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

# Get spread prediction (with underdog identification)
spread = analytics.predict_spread("TOR", "MTL")  # Toronto vs Montreal
print(f"Predicted Spread: {spread['predicted_spread']}")
print(f"Interpretation: {spread['interpretation']}")  # Shows favorite and underdog
print(f"70% Confidence: [{spread['confidence_interval']['lower']}, {spread['confidence_interval']['upper']}]")

# Get total prediction
total = analytics.predict_total("TOR", "MTL")
print(f"Predicted Total: {total['predicted_total']}")
print(f"70% Confidence: [{total['confidence_interval']['lower']}, {total['confidence_interval']['upper']}]")

# Find value opportunities (compare vs market spread)
value = analytics.find_spread_value("TOR", "MTL", market_spread=1.5)
print(f"Underdog: {value['underdog']} (getting +{value['underdog_points']})")
print(f"Value Assessment: {value['value_assessment']}")
print(f"Recommendation: {value['recommended_bet']}")

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

4. **Underdog Identification**: Automatically identifies which team is the underdog in each matchup

### Total Predictions

The system predicts the combined score using:

1. **Offensive Metrics**: Goals per game for each team
2. **Defensive Metrics**: Goals allowed per game for each team
3. **Expected Goals**: Average of offensive capability vs defensive vulnerability
4. **Confidence Interval**: 70% confidence using normal distribution with standard deviation of 1.8 goals

### Value Analysis & Overvalued Spreads

The `find_spread_value()` method compares predicted spreads against market betting lines to identify value opportunities:

1. **Spread Difference**: Calculates how much the prediction differs from the market
2. **Value Threshold**: Differences > 0.5 goals indicate potential value
3. **Underdog Opportunities**: Identifies when underdogs are getting too many or too few points
4. **Betting Recommendations**: Suggests which side offers value based on the analysis

**Example:**
- Market: TOR -1.5 (MTL is underdog getting +1.5)
- Predicted: TOR -3.0
- Analysis: TOR appears undervalued (market spread too low)
- Recommendation: Value on TOR to cover

This helps bettors identify:
- Overvalued favorites (market spread too high)
- Undervalued favorites (market spread too low)
- Underdog opportunities (when underdogs are getting generous points)
- Teams being mispriced by the market

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

## Current Data & Limitations

**Data Source:**
- Connects to official NHL API (api-web.nhle.com) for real-time data
- Falls back to default statistical values when API unavailable
- Uses current season standings, team stats, and performance metrics

**Limitations:**
- Predictions based on season-to-date statistics (updated when API accessible)
- Does not account for injuries, lineup changes, or recent momentum
- Does not include special teams, goaltending matchups, or situational factors
- Confidence intervals represent statistical ranges, not certainties
- Requires internet connection for live data; uses fallback averages offline
- Accuracy improves significantly with access to real-time NHL data

## Testing

Run the test suite:
```bash
python test_nhl_analytics.py
```

## License

See LICENSE file for details.

## Contributing

This project provides NHL analytics with statistical confidence. Contributions to improve prediction accuracy are welcome.
