# College-basketball-score-simulator-
Basketball-simulator 

## NBA Spread and Total Analysis

This repository now includes a comprehensive NBA spread and total analysis system that provides predictions with **70% or higher confidence**.

### Features

- **Spread Analysis**: Predicts point spreads for NBA games with confidence metrics
- **Total Points Analysis**: Predicts total points (over/under) for NBA games with confidence metrics
- **High Confidence Filtering**: Only displays predictions that meet the 70%+ confidence threshold
- **Advanced Metrics**: Uses offensive rating, defensive rating, pace, win percentage, and recent form

### How It Works

The analysis system considers multiple factors:

1. **Offensive Rating**: Points scored per 100 possessions
2. **Defensive Rating**: Points allowed per 100 possessions
3. **Pace**: Possessions per game (affects total scoring)
4. **Win Percentage**: Season-long performance indicator
5. **Recent Form**: Last 10 games performance metric
6. **Home Court Advantage**: Built-in 3.5 point advantage for home teams

#### Confidence Calculation

**Spread Confidence**:
- Base confidence: 65%
- Increases with larger rating differentials
- Increases with larger win percentage gaps
- Increases with significant form differences
- Capped at 95% maximum

**Total Confidence**:
- Base confidence: 65%
- Increases with similar pace between teams
- Increases with consistent offensive/defensive ratings
- Higher for teams with ratings near league average
- Capped at 95% maximum

### Usage

#### Running the Analysis

```bash
python3 nba_analysis.py
```

This will analyze sample NBA games and display only those predictions with 70%+ confidence for both spread and total.

#### Example Output

```
================================================================================
NBA SPREAD AND TOTAL ANALYSIS
Minimum Confidence: 70%
================================================================================

Analyzed 6 games
Found 3 predictions meeting 70%+ confidence threshold

HIGH CONFIDENCE PREDICTIONS (70%+ confidence):
================================================================================

Prediction #1:

Game: Boston Celtics @ Los Angeles Lakers (2025-12-04)
Spread: Los Angeles Lakers +2.5 (Confidence: 75.3%)
Total: 225.8 points (Confidence: 72.1%)

...
```

### Customization

You can modify the minimum confidence threshold by changing the `NBAAnalyzer` initialization:

```python
# For 80% minimum confidence
analyzer = NBAAnalyzer(min_confidence=80.0)

# For 75% minimum confidence
analyzer = NBAAnalyzer(min_confidence=75.0)
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

### Requirements

- Python 3.7 or higher (for dataclasses support)
- No external dependencies required (uses Python standard library only)

### License

See LICENSE file for details. 
