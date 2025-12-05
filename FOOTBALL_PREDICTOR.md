# College Football Score Prediction System

A Python-based college football game prediction system that uses **FEI (Fremeau Efficiency Index)** methodology to predict game outcomes, point spreads, and totals.

## Overview

This prediction system analyzes college football matchups using efficiency metrics to predict:
- **Game Winner** and margin of victory
- **Point Spread** for betting purposes
- **Total Points (Over/Under)** for betting purposes
- **Confidence Level** of predictions

## FEI Methodology

The system uses FEI (Fremeau Efficiency Index) metrics similar to those found at bcftoys.com:

- **FEI**: Overall team efficiency rating
- **OFEI**: Offensive efficiency rating
- **DFEI**: Defensive efficiency rating

These metrics are combined with historical scoring averages to predict game outcomes.

## Features

- ✅ Predicts game outcomes based on team efficiency metrics
- ✅ Calculates point spreads and totals for betting analysis
- ✅ Accounts for home field advantage (~3 points)
- ✅ Supports neutral site games
- ✅ Provides confidence ratings for predictions
- ✅ Interactive CLI mode for custom matchups
- ✅ Sample data from 2022 college football season

## Installation

No external dependencies required! Just Python 3.6+

```bash
# Make the script executable (optional)
chmod +x football_predictor.py
```

## Usage

### Run Example Predictions

```bash
python3 football_predictor.py
```

This will display:
1. Example predictions for notable matchups
2. Interactive mode where you can input your own matchups

### Interactive Mode

When prompted:
1. Enter the home team (or first team)
2. Enter the away team (or second team)
3. Specify if it's a neutral site game (y/n)

### Example Output

```
============================================================
COLLEGE FOOTBALL GAME PREDICTION
============================================================

Matchup: Georgia vs Ohio State
Location: Neutral Site

Predicted Winner: Georgia
Margin of Victory: 2.5 points

Predicted Scores:
  Georgia: 34.5
  Ohio State: 32.0

Betting Lines:
  Spread: -2.5 (negative means Georgia favored)
  Total (Over/Under): 66.5

Confidence: 51.5%

Team Efficiency Metrics (FEI):
  Georgia:
    Overall FEI: 0.825
    Offensive FEI: 0.780
    Defensive FEI: 0.870
  Ohio State:
    Overall FEI: 0.810
    Offensive FEI: 0.850
    Defensive FEI: 0.770
============================================================
```

## Available Teams

The system currently includes data for these top 2022 college football teams:
- Alabama
- Clemson
- Georgia
- Kansas State
- Michigan
- Ohio State
- Penn State
- TCU
- Tennessee
- USC

## How It Works

1. **Efficiency Matching**: Compares offensive efficiency of one team against defensive efficiency of opponent
2. **Scoring Calculation**: Adjusts historical scoring averages based on efficiency matchup
3. **Home Field Advantage**: Adds ~3 points for home team (unless neutral site)
4. **Spread Calculation**: Difference between predicted scores
5. **Total Calculation**: Sum of both predicted scores
6. **Confidence**: Based on the difference in overall FEI ratings

## Customization

To add more teams, edit the `team_data` dictionary in the `FootballPredictor` class with:
- `fei`: Overall efficiency (0-1 scale, higher is better)
- `ofei`: Offensive efficiency (0-1 scale)
- `dfei`: Defensive efficiency (0-1 scale)
- `avg_points`: Average points scored per game
- `avg_allowed`: Average points allowed per game

## Data Source

This system is inspired by the FEI methodology from bcftoys.com. The sample data represents approximate 2022 season metrics for demonstration purposes.

## License

See LICENSE file in the repository.
