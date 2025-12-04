# Overvalue Spread Detection - Feature Guide

## Overview
The overvalue spread detection feature identifies betting opportunities where the market/betting line differs significantly from our predicted spread, creating potential value for bettors.

## How It Works

### 1. Market Comparison
The system compares:
- **Predicted Spread**: Our calculated spread based on team statistics
- **Market Spread**: The current betting line/spread offered by bookmakers

### 2. Value Calculation
```
spread_value = predicted_spread - market_spread
```

**Positive Value**: Home team is undervalued by the market
- Example: Predicted +5.0, Market +8.0 → Value = -3.0 (Away team undervalued)

**Negative Value**: Away team is undervalued by the market
- Example: Predicted +8.0, Market +5.0 → Value = +3.0 (Home team undervalued)

### 3. Threshold Detection
Default threshold: **2.5 points**
- If `|spread_value| >= 2.5`: Overvalue opportunity detected
- Customizable via `min_value_threshold` parameter

### 4. Betting Recommendation
The system identifies which side has value:
- **Home side value**: Bet on the home team
- **Away side value**: Bet on the away team

## Usage Examples

### Basic Usage
```python
from nba_analysis import NBAAnalyzer, Game, Team

# Create analyzer
analyzer = NBAAnalyzer(min_confidence=70.0)

# Create game with market spread
game = Game(
    home_team=lakers,
    away_team=celtics,
    date="2025-12-04",
    market_spread=5.5  # Current betting line
)

# Analyze and get prediction with overvalue detection
prediction = analyzer.analyze_game(game)

if prediction.is_overvalue:
    print(f"Overvalue found! Bet {prediction.value_side} side")
    print(f"Value difference: {abs(prediction.spread_value):.1f} points")
```

### Find All Overvalue Opportunities
```python
# Find all overvalue opportunities across multiple games
overvalue_predictions = analyzer.find_overvalue_spreads(games)

for pred in overvalue_predictions:
    print(f"Game: {pred.game.away_team.name} @ {pred.game.home_team.name}")
    print(f"Recommended bet: {pred.value_side.upper()} side")
    print(f"Value: {abs(pred.spread_value):.1f} points\n")
```

### Custom Value Threshold
```python
# More conservative (larger edge required)
overvalue_3pt = analyzer.find_overvalue_spreads(games, min_value_threshold=3.0)

# More aggressive (smaller edge acceptable)
overvalue_2pt = analyzer.find_overvalue_spreads(games, min_value_threshold=2.0)
```

## Example Output

```
*** OVERVALUE OPPORTUNITY ***
Market Spread: Golden State Warriors +8.0
Value Difference: 3.0 points
Recommended Bet: AWAY side (Brooklyn Nets)
```

**Interpretation**: 
- Market has Warriors as 8-point underdogs
- Our prediction has Warriors as 5-point underdogs
- The 3-point difference suggests the market is overvaluing the Warriors
- Therefore, bet on the Brooklyn Nets (away team) as they're undervalued

## Key Features

1. **Automatic Detection**: Overvalue is automatically detected when analyzing games with market spreads
2. **High Confidence Filter**: Only overvalue opportunities that meet 70%+ confidence are shown
3. **Clear Recommendations**: System explicitly states which side to bet
4. **Customizable Thresholds**: Adjust value threshold based on your risk tolerance
5. **Comprehensive Testing**: 8 unit tests specifically for overvalue detection

## Configuration Options

### Confidence Threshold
```python
# Require higher confidence for recommendations
analyzer = NBAAnalyzer(min_confidence=80.0)
```

### Value Threshold
```python
# Require larger edge for overvalue
overvalue_predictions = analyzer.find_overvalue_spreads(
    games, 
    min_value_threshold=3.5  # 3.5+ points required
)
```

## Important Notes

1. **Market Spread Required**: If `market_spread=None`, overvalue detection is skipped
2. **Both Filters Applied**: Predictions must meet BOTH confidence (70%+) AND value (2.5+) thresholds
3. **Point Spread Convention**: Positive spread = home team favored, Negative = away team favored
4. **Value Side**: The recommended betting side is always the undervalued team

## Real-World Application

To use with real data:
1. Get team statistics from NBA.com or basketball-reference.com
2. Get current betting lines from sportsbooks
3. Input market spreads as `market_spread` parameter
4. System will identify value opportunities automatically

## Testing

Run tests for overvalue detection:
```bash
python3 test_nba_analysis.py TestOvervalueDetection -v
```

Tests cover:
- Detection with/without market spreads
- Significant vs. insignificant differences
- Home vs. away side value identification
- Custom threshold functionality
- Filtering for overvalue opportunities
