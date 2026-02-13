# College Basketball Prediction System - Billy Walters Framework

A comprehensive college basketball prediction system implementing the methodologies from Billy Walters' book **"Gambler: Secrets from a Life at Risk"**.

## Overview

This system replicates the legendary sports bettor Billy Walters' approach to college basketball predictions, incorporating:

- **Power Ratings**: Numeric values representing team strength
- **Advanced Handicapping**: Multi-factor analysis including efficiency metrics, schedule strength, and recent form
- **Game Factors**: Travel fatigue, home court advantage, motivation, and situational elements
- **Bankroll Management**: Conservative 1-3% risk per bet following Walters' principles
- **Edge Calculation**: Identifying value by comparing model predictions to market lines
- **ATS Record Tracking**: Track Against The Spread performance using TeamRankings.com data
- **Complete Team System**: Track all 356 Division I teams with comprehensive statistics

## New: Complete 356-Team Database System

Track all Division I college basketball teams with:

- **All Offensive Stats**: Points, FG%, 3P%, FT%, assists, rebounds, turnovers, steals, blocks
- **All Defensive Stats**: Opponent scoring, field goal defense, rebounding, forcing turnovers
- **Advanced Metrics**: Efficiency ratings, Four Factors, tempo, pace adjustments
- **SOS Calculations**: Strength of Schedule from opponent power ratings
- **Team Rankings**: National and conference rankings using Billy Walters formulas
- **Pace-Adjusted Predictions**: Score predictions accounting for team tempo

**Quick Start:**
```bash
python complete_team_system.py
```

**See [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md) for full documentation.**

## ATS (Against The Spread) Tracking

Track how teams perform against betting spreads with data from **TeamRankings.com**:

- Manual game-by-game ATS tracking
- Import comprehensive ATS records from TeamRankings.com
- Home/Away and Favorite/Underdog splits
- Head-to-head ATS analysis
- Leaderboards and team statistics

**Quick Start:**
```bash
# Track ATS records manually
python ats_tracker.py

# Import from TeamRankings.com data
python teamrankings_importer.py
```

**See [ATS_GUIDE.md](ATS_GUIDE.md) for complete documentation.**

### Identify Best ATS Performers

Find which teams cover the spread most frequently:

```bash
python best_ats_performers.py
```

**Top Spread-Covering Team:** Houston (72.4% ATS, 21-8-1 record)

Analysis includes:
- Overall ATS rankings
- Home vs Away performance
- As Favorite vs Underdog splits
- Conference leaders
- Detailed team breakdowns

## Billy Walters' Framework

Billy Walters is considered one of the most successful sports bettors in history. His framework, as detailed in his book, focuses on:

1. **Data-Driven Power Ratings** - Building proprietary team strength metrics
2. **Comprehensive Game Analysis** - Accounting for every factor that affects outcomes
3. **Disciplined Money Management** - Never risking more than 1-3% per bet
4. **Market Inefficiency Exploitation** - Betting only when model shows clear edge over market
5. **Avoiding Public Bias** - Making decisions based on data, not trends or emotions

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run the example prediction:

```bash
python billy_walters_predictor.py
```

This will demonstrate a Duke vs UNC prediction with full analysis.

## Usage

### 1. Set Up Power Ratings

```python
from billy_walters_predictor import PowerRatings, TeamStats

# Initialize power ratings system
pr = PowerRatings()

# Define team statistics
duke_stats = TeamStats(
    name="Duke",
    offensive_efficiency=115.5,  # Points per 100 possessions
    defensive_efficiency=95.2,   # Points allowed per 100 possessions
    tempo=70.5,                  # Possessions per game
    recent_form=['W', 'W', 'L', 'W', 'W'],  # Last 5 games
    strength_of_schedule=2.5,    # Avg opponent power rating
    injuries=[]                   # Key player injuries
)

# Calculate and store power rating
pr.update_rating("Duke", duke_stats)
```

### 2. Make Predictions

```python
from billy_walters_predictor import PredictionEngine

# Create prediction engine
engine = PredictionEngine(pr)

# Predict point spread
spread, favorite = engine.predict_spread(
    home_team="Duke",
    away_team="UNC",
    is_neutral_site=False,
    miles_traveled=20,
    days_rest_home=3,
    days_rest_away=2,
    is_rivalry=True,
    is_conference_game=True,
    revenge_game=False
)

print(f"Prediction: {favorite} -{spread}")

# Predict total points
total = engine.predict_total("Duke", "UNC", duke_stats, unc_stats)
print(f"Predicted Total: {total}")
```

### 3. Get Betting Recommendations

```python
from billy_walters_predictor import BankrollManagement

# Initialize bankroll
bankroll = BankrollManagement(total_bankroll=10000)

# Get betting recommendation
recommendation = engine.get_betting_recommendation(
    predicted_spread=7.5,
    predicted_favorite="Duke",
    market_spread=5.5,
    market_favorite="Duke",
    bankroll_manager=bankroll,
    confidence=0.75
)

if recommendation['should_bet']:
    print(f"Bet: {recommendation['bet_side']}")
    print(f"Bet Size: ${recommendation['bet_size']}")
    print(f"Edge: {recommendation['edge']:.1%}")
```

## Core Components

### PowerRatings
Calculates team strength using:
- Offensive and defensive efficiency
- Strength of schedule adjustments
- Recent form trends
- Injury impact assessment

### GameFactors
Analyzes situational elements:
- Home court advantage (3.5 points typical)
- Travel fatigue calculations
- Motivation factors (rivalry, revenge, desperation)
- Conference game adjustments

### PredictionEngine
Combines power ratings and game factors to:
- Predict point spreads
- Calculate over/under totals
- Identify betting edges vs market lines

### BankrollManagement
Implements Walters' conservative approach:
- 1-3% maximum risk per bet
- Kelly Criterion-based sizing
- Only bet with minimum 3% edge

## Key Principles

Following Billy Walters' methodology:

1. **Only Bet With Edge**: Never bet without clear mathematical advantage (>3%)
2. **Bankroll Discipline**: Risk only 1-3% per bet to survive variance
3. **Comprehensive Analysis**: Account for all factors affecting game outcomes
4. **Exploit Inefficiencies**: Find games where your model disagrees with market
5. **Ignore Public Trends**: Make data-driven decisions, not emotional ones
6. **Line Shopping**: Compare multiple sportsbooks for best value (not implemented in code)
7. **Patient Approach**: Don't force bets - wait for optimal opportunities

## Example Output

```
======================================================================
BILLY WALTERS COLLEGE BASKETBALL PREDICTION SYSTEM
Based on 'Gambler: Secrets from a Life at Risk'
======================================================================

POWER RATINGS
----------------------------------------------------------------------
Duke: +22.1
UNC:  +16.2

GAME PREDICTION
----------------------------------------------------------------------
Matchup: Duke vs UNC (at Duke)
Predicted Spread: Duke -9.4

Predicted Total: 143.5

BETTING ANALYSIS
----------------------------------------------------------------------
Market Line: Duke -5.5
Our Line:    Duke -9.4

RECOMMENDATION
----------------------------------------------------------------------
Should Bet: True
Bet Side: Duke -5.5
Bet Size: $225.00
Edge: 9.8%

Reasoning: Edge of 9.8% detected. Model disagrees with market by 3.9 points. 
Recommended bet: $225.00 (2.3% of bankroll)
```

## Data Sources

For real-world implementation, you'll need to collect:

- Team efficiency stats (KenPom, BartTorvik, or similar)
- Schedule and results data
- Player injury reports
- Travel distances and rest days
- Market lines from sportsbooks

## Limitations

This is an educational implementation of Billy Walters' framework. For actual betting:

- Use real-time data feeds
- Implement line shopping across multiple sportsbooks
- Account for line movements and steam
- Use more sophisticated models (machine learning, Monte Carlo simulations)
- Consider using "beards" or proxies if betting significant amounts
- Follow all local gambling laws and regulations

## References

- **Book**: "Gambler: Secrets from a Life at Risk" by Billy Walters
- **Approach**: Computer Group methodology and power ratings system
- **Philosophy**: Mathematical edge, disciplined bankroll management, market inefficiency exploitation

## License

See LICENSE file for details.

## Disclaimer

This system is for educational purposes only. Sports betting involves risk. Never bet more than you can afford to lose. Gambling may not be legal in your jurisdiction. This is not financial or betting advice. 
