# College Football Score Prediction System

A Python-based college football game prediction system that uses **FEI (Fremeau Efficiency Index)** methodology to predict game outcomes, point spreads, and totals. Now includes **Monte Carlo simulation** (10,000 runs) in the style of Haralabos Voulgaris.

## Overview

This prediction system analyzes college football matchups using efficiency metrics to predict:
- **Game Winner** and margin of victory
- **Point Spread** for betting purposes
- **Total Points (Over/Under)** for betting purposes
- **Confidence Level** of predictions
- **Win Probabilities** via Monte Carlo simulation
- **Spread Coverage** probabilities
- **Over/Under** hit rates

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
- ✅ **Monte Carlo simulations (10,000 runs - Haralabos Voulgaris style)**
- ✅ **Win probability distributions**
- ✅ **Spread coverage analysis**
- ✅ **Over/Under hit rate predictions**
- ✅ **Score distribution charts**
- ✅ Interactive CLI mode for custom matchups
- ✅ Sample data from 2022 college football season

## Installation

No external dependencies required! Just Python 3.6+

```bash
# Make the script executable (optional, Linux/macOS only)
chmod +x football_predictor.py
```

## Usage

### Run Example Predictions

```bash
python3 football_predictor.py
```

This will display:
1. Example predictions for notable matchups
2. **Monte Carlo simulations (10,000 runs)** for key games
3. Interactive mode where you can input your own matchups

### Interactive Mode

When prompted:
1. Enter the home team (or first team)
2. Enter the away team (or second team)
3. Specify if it's a neutral site game (y/n)
4. **Choose to run simulation (y/n)** - Run 10,000 Monte Carlo simulations

### Monte Carlo Simulations (Haralabos Voulgaris Style)

The system can run 10,000 Monte Carlo simulations for any matchup, adding variance to the base prediction to generate:
- **Win probabilities** for each team
- **Spread coverage percentages**
- **Over/Under hit rates**
- **Score distribution charts**

This approach, popularized by sports betting analyst Haralabos Voulgaris, provides probabilistic analysis rather than single-point predictions.

### Example Output - Standard Prediction

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

### Example Output - Monte Carlo Simulation

```
======================================================================
MONTE CARLO SIMULATION RESULTS (Haralabos Voulgaris Style)
======================================================================

Matchup: Michigan vs Ohio State
Simulations Run: 10,000

                          WIN PROBABILITIES                           
----------------------------------------------------------------------
  Michigan: 24.22%
  Ohio State: 75.78%

                       AVERAGE SIMULATED SCORES                       
----------------------------------------------------------------------
  Michigan: 38.0
  Ohio State: 45.0
  Average Margin: 9.8 points
  Average Total: 83.0 points

                           SPREAD ANALYSIS                            
----------------------------------------------------------------------
  Predicted Spread: 7.0
  Michigan covers: 50.1%
  Ohio State covers: 49.9%

                         OVER/UNDER ANALYSIS                          
----------------------------------------------------------------------
  Predicted Total: 83.0
  Over hits: 50.1%
  Under hits: 49.9%

           SCORE DISTRIBUTION (Top 5 ranges for each team)            
----------------------------------------------------------------------

  Michigan:
    35-41 points: 37.3%
    28-34 points: 26.2%
    42-48 points: 22.7%
    21-27 points: 6.8%
    49-55 points: 5.6%

  Ohio State:
    42-48 points: 38.2%
    35-41 points: 25.6%
    49-55 points: 22.5%
    28-34 points: 7.1%
    56-62 points: 5.4%
======================================================================
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

### Base Prediction Algorithm

1. **Efficiency Matching**: Compares offensive efficiency of one team against defensive efficiency of opponent
2. **Scoring Calculation**: Adjusts historical scoring averages based on efficiency matchup
3. **Home Field Advantage**: Adds ~3 points for home team (unless neutral site)
4. **Spread Calculation**: Difference between predicted scores
5. **Total Calculation**: Sum of both predicted scores
6. **Confidence**: Based on the difference in overall FEI ratings

### Monte Carlo Simulation (10,000 runs)

1. **Base Prediction**: Generates base predicted score for each team
2. **Variance Application**: Adds random variance (±7 points standard deviation) to each simulation
3. **10,000 Iterations**: Runs 10,000 independent game simulations
4. **Statistical Analysis**: Aggregates results to determine:
   - Win probability for each team
   - Average scores across all simulations
   - Spread coverage percentages
   - Over/Under hit rates
   - Score distribution patterns

This approach mirrors the methodology used by professional sports analysts like Haralabos Voulgaris.

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
