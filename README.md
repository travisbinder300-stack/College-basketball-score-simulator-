# College-basketball-score-simulator-
Basketball-simulator 

## NBA Spread and Total Analysis

This repository now includes a comprehensive NBA spread and total analysis system that provides predictions with **70% or higher confidence** and identifies **overvalue betting opportunities**.

### Features

- **Spread Analysis**: Predicts point spreads for NBA games with confidence metrics
- **Total Points Analysis**: Predicts total points (over/under) for NBA games with confidence metrics
- **High Confidence Filtering**: Only displays predictions that meet the 70%+ confidence threshold
- **Overvalue Detection**: Identifies games where betting lines differ significantly from predicted spreads (2.5+ points)
- **Betting Recommendations**: Shows which side (home/away) offers value when overvalue is detected
- **Advanced Metrics**: Uses offensive rating, defensive rating, pace, win percentage, and recent form

### How It Works

The analysis system considers multiple factors:

1. **Offensive Rating**: Points scored per 100 possessions
2. **Defensive Rating**: Points allowed per 100 possessions
3. **Pace**: Possessions per game (affects total scoring)
4. **Win Percentage**: Season-long performance indicator
5. **Recent Form**: Last 10 games performance metric
6. **Home Court Advantage**: Built-in 3.5 point advantage for home teams
7. **Market Spread Comparison**: Compares predictions to betting lines for value opportunities

#### Confidence Calculation

**Spread Confidence**:
- Base confidence: 65%
- Increases with larger rating differentials
- Increases with larger win percentage gaps
- Increases with significant form differences
- Capped at 95% maximum

**Total Confidence**:
- Base confidence: 65%
#### Overvalue Detection

**How Overvalue Works**:
- Compares the predicted spread to the market/betting line spread
- Identifies opportunities where the difference is ≥ 2.5 points (default threshold)
- Recommends which side (home or away) to bet based on the value
- Only shows overvalue opportunities that also meet the 70%+ confidence threshold

**Value Calculation**:
- If predicted spread > market spread: Home team is undervalued by the market
- If predicted spread < market spread: Away team is undervalued by the market

### Usage

#### Running the Analysis

```bash
python3 nba_analysis.py
```

This will analyze sample NBA games and display:
1. All predictions with 70%+ confidence for both spread and total
2. Overvalue spread opportunities with recommended bets

#### Example Output

```
================================================================================
NBA SPREAD AND TOTAL ANALYSIS WITH OVERVALUE DETECTION
Minimum Confidence: 70%
================================================================================

Analyzed 6 games
Found 3 predictions meeting 70%+ confidence threshold

HIGH CONFIDENCE PREDICTIONS (70%+ confidence):
================================================================================

Prediction #1:

Game: Brooklyn Nets @ Golden State Warriors (2025-12-04)
Spread: Golden State Warriors +5.0 (Confidence: 73.9%)
Total: 233.8 points (Confidence: 94.2%)
*** OVERVALUE OPPORTUNITY ***
Market Spread: Golden State Warriors +8.0
Value Difference: 3.0 points
Recommended Bet: AWAY side (Brooklyn Nets)

...

================================================================================
OVERVALUE SPREAD OPPORTUNITIES
================================================================================
Found 1 overvalue opportunities (≥2.5 point difference)

RECOMMENDED BETS (High confidence + significant value):
================================================================================

Overvalue Bet #1:
[Details of the best betting opportunities]
```

### Customization

You can modify the minimum confidence threshold by changing the `NBAAnalyzer` initialization:

```python
# For 80% minimum confidence
analyzer = NBAAnalyzer(min_confidence=80.0)

# For 75% minimum confidence
analyzer = NBAAnalyzer(min_confidence=75.0)
```

You can also customize the overvalue detection threshold:

```python
# Find overvalue opportunities with 3.0+ point difference
overvalue_predictions = analyzer.find_overvalue_spreads(games, min_value_threshold=3.0)

# Find overvalue opportunities with 2.0+ point difference (more opportunities)
overvalue_predictions = analyzer.find_overvalue_spreads(games, min_value_threshold=2.0)
```

### Adding Your Own Teams and Games

Modify the `create_sample_teams()` and `create_sample_games()` functions in `nba_analysis.py` to add your own teams with real statistics:

```python
teams = {
    "YourTeam": Team(
        name="Your Team Name",
        offensive_rating=115.0,  # Your team's offensive rating
        defensive_rating=110.0,  # Your team's defensive rating
        pace=100.0,              # Your team's pace
        win_percentage=0.600,    # Your team's win percentage (0-1)
        recent_form=0.70         # Recent form (0-1, where 1.0 = 10-0)
    )
}
```

Create games with market spreads to enable overvalue detection:

```python
games = [
    Game(
        home_team=teams["YourTeam"], 
        away_team=teams["OpponentTeam"],
        date="2025-12-04",
        market_spread=5.5  # Current betting line (positive = home favored)
    )
]
```

**Note**: If `market_spread` is not provided (None), overvalue detection will be skipped for that game.

### Requirements

- Python 3.7 or higher (for dataclasses support)
- No external dependencies required (uses Python standard library only)

### License

See LICENSE file for details. 
