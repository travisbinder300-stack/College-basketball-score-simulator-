# Quick Start Guide - Soccer Simulator

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-

# 2. Install dependencies
pip install -r requirements.txt
```

## 30-Second Demo

```bash
# Run the basic simulator with example matches
python soccer_simulator.py
```

## 2-Minute Tutorial

### 1. Simulate a Single Match

```python
from soccer_simulator import Team, SoccerSimulator

# Create two teams with ratings
man_city = Team("Manchester City", offensive_rating=1.45, defensive_rating=0.75)
liverpool = Team("Liverpool", offensive_rating=1.40, defensive_rating=0.80)

# Create simulator and run 10,000 simulations
simulator = SoccerSimulator()
simulator.print_simulation_report(man_city, liverpool, num_simulations=10000)
```

### 2. Get Betting Odds

```python
from soccer_simulator import Team, SoccerSimulator

team_a = Team("Team A", offensive_rating=1.30, defensive_rating=0.90)
team_b = Team("Team B", offensive_rating=1.20, defensive_rating=1.00)

simulator = SoccerSimulator()
odds = simulator.calculate_match_odds(team_a, team_b, num_simulations=10000)

print(f"Home win odds: {odds['decimal_odds']['home_win']}")
print(f"Draw odds: {odds['decimal_odds']['draw']}")
print(f"Away win odds: {odds['decimal_odds']['away_win']}")
```

### 3. Load Teams from Configuration

```python
from soccer_simulator import load_teams_from_file, SoccerSimulator

# Load pre-configured teams
teams = load_teams_from_file('teams_example.json')

# Simulate match between first two teams
simulator = SoccerSimulator()
simulator.print_simulation_report(teams[0], teams[1], num_simulations=10000)
```

## Understanding the Output

### Expected Goals (xG)
The theoretical goals each team should score based on their ratings.

Example: `Manchester City: 2.31` means City is expected to score ~2.3 goals.

### Match Probabilities
Percentage chance of each outcome based on 10,000 simulations.

Example: `Manchester City Win: 49.2%` means City wins in 4,920 of 10,000 simulations.

### Decimal Odds
Fair betting odds (without bookmaker margin).

Example: `2.03` means a $1 bet returns $2.03 if successful (49.2% probability).

### Most Likely Scores
The top 10 scorelines ordered by probability.

Example: `2-1 - 11.23%` means this score occurs in ~11% of simulations.

## Common Use Cases

### Finding Value Bets
```python
# Get fair odds
odds = simulator.calculate_match_odds(home, away, num_simulations=10000)
fair_odds = odds['decimal_odds']['home_win']

# Compare with bookmaker
bookmaker_odds = 2.50

if bookmaker_odds > fair_odds:
    print(f"VALUE BET! Bookmaker odds ({bookmaker_odds}) > Fair odds ({fair_odds})")
```

### Analyzing Different Leagues
```python
# Premier League
pl_sim = SoccerSimulator(league_avg_goals=2.75, home_advantage=0.3)

# Bundesliga (higher scoring)
bl_sim = SoccerSimulator(league_avg_goals=3.10, home_advantage=0.3)

# Serie A (more defensive)
sa_sim = SoccerSimulator(league_avg_goals=2.65, home_advantage=0.25)
```

### Neutral Venue (Cup Finals)
```python
# No home advantage for neutral venues
simulator = SoccerSimulator(home_advantage=0.0)
simulator.print_simulation_report(team_a, team_b, num_simulations=10000)
```

## Advanced Examples

For more examples, run:
```bash
python advanced_examples.py
```

This includes:
- League comparison analysis
- Over/Under goals predictions
- Home advantage impact studies
- Season simulations
- Value betting analysis

## Tips for Accurate Ratings

### Offensive Rating (typical range: 0.8 - 1.5)
- **1.50**: Elite attack (Man City, Bayern Munich)
- **1.30**: Strong attack (Top 6 teams)
- **1.00**: Average attack (Mid-table)
- **0.80**: Weak attack (Relegation teams)

### Defensive Rating (typical range: 0.7 - 1.4)
- **0.75**: Elite defense (very hard to score against)
- **0.90**: Strong defense (Top teams)
- **1.00**: Average defense (Mid-table)
- **1.30**: Weak defense (concedes many goals)

## Need Help?

1. Check the full README.md for detailed documentation
2. Review advanced_examples.py for complex use cases
3. Examine teams_example.json for team rating examples

## What Makes This "Haralabos Voulgaris Style"?

Haralabos Voulgaris is a legendary sports bettor known for:
- Statistical modeling over gut feelings
- Poisson distribution for score predictions
- Team strength ratings
- Monte Carlo simulations (10,000+ iterations)
- Expected goals (xG) analysis
- Value betting through odds comparison

This simulator implements all these principles for soccer analysis.
