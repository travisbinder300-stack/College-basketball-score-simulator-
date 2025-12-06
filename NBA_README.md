# NBA 10,000 Game Simulator

An advanced NBA game simulator using **Haralabos Voulgaris-style analytics** with **Kelly Criterion betting strategy**.

## Features

### Haralabos Voulgaris-Style Analytics

This simulator implements advanced basketball analytics inspired by Haralabos Voulgaris, one of the most successful NBA bettors and analytics experts:

1. **Four Factors Analysis**
   - Effective Field Goal Percentage (eFG%)
   - Turnover Percentage (TOV%)
   - Offensive Rebound Percentage (ORB%)
   - Free Throw Rate (FT Rate)

2. **Pace-Adjusted Efficiency**
   - Offensive Rating (points per 100 possessions)
   - Defensive Rating (points allowed per 100 possessions)
   - Net Rating calculation
   - Pace adjustment for game simulation

3. **Advanced Statistical Modeling**
   - Home court advantage (~3.5 points)
   - Pythagorean win expectation
   - Variance modeling based on team characteristics
   - Log5 method for win probability

### Kelly Criterion Betting Strategy

The simulator includes a sophisticated betting strategy implementation:

- **Kelly Formula**: Calculates optimal bet size to maximize long-term growth
- **Fractional Kelly**: Uses quarter-Kelly (25%) for reduced variance
- **Expected Value Calculation**: Identifies positive EV betting opportunities
- **Edge Detection**: Compares model probabilities vs market odds
- **Bankroll Management**: Caps bets at 20% maximum

## Installation

### Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

### Setup

```bash
# Clone the repository
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-

# Make the simulator executable
chmod +x nba_simulator.py

# Run the simulator
python3 nba_simulator.py
```

## Usage

### Basic Usage

Run the full 10,000 game simulation:

```bash
python3 nba_simulator.py
```

### Python API

Use the simulator in your own code:

```python
from nba_simulator import NBASimulator, TeamStats, KellyBetting

# Create teams
elite_team = TeamStats(
    name="Championship Contender",
    offensive_rating=118.5,
    defensive_rating=110.2,
    pace=99.5,
    efg_pct=0.565,
    tov_pct=12.5,
    orb_pct=26.5,
    ft_rate=0.245
)

average_team = TeamStats(
    name="Average Team",
    offensive_rating=112.5,
    defensive_rating=112.5,
    pace=97.5,
    efg_pct=0.535,
    tov_pct=14.2,
    orb_pct=23.0,
    ft_rate=0.225
)

# Initialize simulator
simulator = NBASimulator(home_court_advantage=3.5)

# Run 10,000 simulations
results = simulator.simulate_multiple_games(elite_team, average_team, 10000)

print(f"Home Win %: {results['home_win_pct']:.1%}")
print(f"Average Score: {results['avg_home_score']:.1f} - {results['avg_away_score']:.1f}")

# Kelly betting analysis
market_odds = 1.67  # Decimal odds
kelly_size = KellyBetting.calculate_kelly_fraction(
    results['home_win_pct'], 
    market_odds, 
    kelly_fraction=0.25
)

if kelly_size > 0:
    print(f"Bet {kelly_size:.2%} of bankroll")
```

## Understanding the Output

### Simulation Results

- **Home Win Percentage**: Probability of home team winning based on 10,000 simulations
- **Average Scores**: Expected final score for each team
- **Average Margin**: Expected point differential
- **Margin Std Deviation**: Variability in outcomes

### Kelly Betting Analysis

- **Market Odds**: Current betting market odds (decimal format)
- **Model Probability**: Simulator's calculated win probability
- **Quarter-Kelly Bet Size**: Recommended bet as % of bankroll
- **Expected Value**: Expected profit per $100 wagered
- **Edge**: Difference between model and market probability

## Advanced Features

### Custom Team Analysis

Create your own teams with real NBA statistics:

```python
your_team = TeamStats(
    name="Your Team",
    offensive_rating=115.0,  # Points per 100 possessions
    defensive_rating=112.0,  # Points allowed per 100 possessions
    pace=98.0,               # Possessions per game
    efg_pct=0.540,          # Effective FG% (accounts for 3-pointers)
    tov_pct=13.5,           # Turnover % of possessions
    orb_pct=24.0,           # Offensive rebound %
    ft_rate=0.230           # Free throw rate (FTA/FGA)
)
```

### Betting Strategy Customization

Adjust Kelly fraction for different risk tolerance:

```python
# Conservative (Quarter-Kelly)
kelly = KellyBetting.calculate_kelly_fraction(prob, odds, 0.25)

# Moderate (Half-Kelly)
kelly = KellyBetting.calculate_kelly_fraction(prob, odds, 0.50)

# Aggressive (Full-Kelly) - NOT RECOMMENDED
kelly = KellyBetting.calculate_kelly_fraction(prob, odds, 1.00)
```

## Methodology

### Game Simulation Algorithm

1. Calculate game pace using geometric mean of both teams
2. Adjust ratings for home court advantage
3. Calculate expected points using offensive/defensive matchup
4. Add variance based on four factors and pace
5. Generate final score using normal distribution

### Win Probability Model

Uses Pythagorean expectation with NBA-specific exponent (11.5):

```
Win% = (Net Rating)^11.5 / ((Net Rating)^11.5 + (Opp Net Rating)^11.5)
```

### Kelly Criterion Formula

```
f = (bp - q) / b

where:
- f = fraction of bankroll to bet
- b = odds - 1
- p = probability of winning
- q = 1 - p
```

## Why Haralabos Voulgaris Style?

Haralabos Voulgaris is renowned for:

1. **Emphasis on Efficiency**: Focus on per-possession metrics rather than raw totals
2. **Four Factors**: Using Dean Oliver's four factors as core evaluation metrics
3. **Pace Adjustment**: Understanding how tempo affects scoring and outcomes
4. **Value-Based Betting**: Seeking edges in market inefficiencies
5. **Quantitative Approach**: Data-driven decision making over narratives

This simulator implements these principles in its core design.

## Example Output

```
================================================================================
NBA 10,000 GAME SIMULATOR
Haralabos Voulgaris-Style Analytics with Kelly Betting Strategy
================================================================================

SAMPLE TEAMS:
--------------------------------------------------------------------------------
Elite Contender          | ORtg: 118.5 | DRtg: 110.2 | Net:  +8.3 | Pace: 99.5
Good Playoff Team        | ORtg: 115.2 | DRtg: 112.8 | Net:  +2.4 | Pace: 98.2

================================================================================
SIMULATING: Elite Contender (HOME) vs Good Playoff Team (AWAY)
================================================================================

Running 10,000 game simulations...

SIMULATION RESULTS:
--------------------------------------------------------------------------------
Home Win Percentage:     73.2%
Average Home Score:      117.3
Average Away Score:      111.8
Average Margin:          +5.5
Median Margin:           +6.0
Margin Std Deviation:    12.4

================================================================================
KELLY BETTING STRATEGY ANALYSIS
================================================================================

Market Odds (Home Team): 1.67 (Implied Prob: 59.9%)
Model Probability:       73.2%

✓ BETTING EDGE DETECTED!
  Quarter-Kelly Bet Size:  8.32% of bankroll
  Expected Value (per $100): $8.45
  Edge:                    13.3%
```

## Tips for Success

1. **Use Fractional Kelly**: Quarter-Kelly (25%) reduces variance while maintaining growth
2. **Look for Market Inefficiencies**: Best edges often come from less popular games
3. **Track Your Results**: Monitor actual vs expected outcomes
4. **Update Team Stats**: Use current season statistics for accuracy
5. **Consider Context**: Injuries, rest, and other factors not captured in base stats

## Contributing

Contributions are welcome! Areas for enhancement:

- Player-level simulation
- Injury impact modeling
- Back-to-back game adjustments
- Playoff vs regular season modes
- Historical data integration
- Advanced visualization

## License

See LICENSE file for details.

## Acknowledgments

- Haralabos Voulgaris for pioneering advanced NBA analytics
- Dean Oliver for the Four Factors framework
- J.L. Kelly Jr. for the Kelly Criterion
- Basketball analytics community

## Disclaimer

This simulator is for educational and entertainment purposes only. Sports betting involves risk. Always gamble responsibly and within your means.
