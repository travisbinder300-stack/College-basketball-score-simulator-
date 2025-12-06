# College Basketball Game Simulator - Haralabos Voulgaris Style

A sophisticated Monte Carlo basketball game simulator using advanced analytics inspired by Haralabos Voulgaris's data-driven approach to basketball prediction.

## Features

- **10,000 Monte Carlo Simulations** - Comprehensive statistical modeling
- **Possession-Level Simulation** - Models every possession individually
- **Advanced Efficiency Metrics** - Uses offensive/defensive efficiency (points per 100 possessions)
- **Pace Adjustment** - Accounts for team tempo and style of play
- **Shot Distribution Modeling** - Realistic 2PT/3PT/FT distributions
- **Defensive Adjustments** - Opponent strength affects offensive performance
- **Game-to-Game Variance** - Captures hot/cold shooting nights
- **Comprehensive Statistics** - Win probability, score distributions, percentiles

## Haralabos Voulgaris Style Analytics

This simulator incorporates principles from Haralabos Voulgaris's analytical approach:

1. **Efficiency Over Volume** - Focus on points per possession, not raw totals
2. **Pace Matters** - Faster/slower games fundamentally change outcomes
3. **Opponent Adjustments** - Defense impacts offensive efficiency
4. **Probabilistic Modeling** - Monte Carlo simulation captures uncertainty
5. **Variance Recognition** - Teams don't perform identically every game
6. **Shot Quality** - Different shot types have different values and probabilities

## Installation

```bash
# Clone the repository
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

Run the simulator with example teams:

```bash
python basketball_simulator.py
```

This will simulate 10,000 games between Duke (offensive powerhouse) and Virginia (defensive powerhouse).

## Usage

### Basic Usage

```python
from basketball_simulator import GameSimulator, TeamStats

# Define your teams
team1 = TeamStats(
    name="Duke Blue Devils",
    offensive_efficiency=118.5,  # Points per 100 possessions
    defensive_efficiency=98.2,
    pace=72.5,                   # Possessions per 40 minutes
    three_point_rate=0.42,       # 42% of shots are 3-pointers
    three_point_percentage=0.38,
    two_point_percentage=0.56,
    free_throw_rate=0.38,
    free_throw_percentage=0.75,
    turnover_rate=0.16,
    offensive_rebound_rate=0.32,
    performance_variance=0.06
)

team2 = TeamStats(
    name="Kansas Jayhawks",
    offensive_efficiency=115.0,
    defensive_efficiency=95.5,
    pace=70.0,
    three_point_rate=0.38,
    three_point_percentage=0.37,
    two_point_percentage=0.54,
    free_throw_rate=0.35,
    free_throw_percentage=0.73,
    turnover_rate=0.15,
    offensive_rebound_rate=0.30,
    performance_variance=0.05
)

# Run simulation
simulator = GameSimulator(team1, team2)
results = simulator.run_simulation(num_simulations=10000)

# Access results
print(f"Team 1 Win Probability: {results['team1_win_pct']:.1f}%")
print(f"Expected Score: {results['team1_avg_score']:.1f} - {results['team2_avg_score']:.1f}")
```

## Team Statistics Explained

### Efficiency Metrics
- **Offensive Efficiency**: Points scored per 100 possessions (league avg ~105)
- **Defensive Efficiency**: Points allowed per 100 possessions (lower is better)

### Pace
- **Pace**: Number of possessions per 40 minutes
  - Fast: 72+ possessions
  - Average: 67-72 possessions
  - Slow: <67 possessions

### Shooting Metrics
- **Three Point Rate**: Proportion of field goal attempts that are 3-pointers (0.0-1.0)
- **Three Point Percentage**: 3PT shooting accuracy (NCAA avg ~0.35)
- **Two Point Percentage**: 2PT shooting accuracy (NCAA avg ~0.50)
- **Free Throw Rate**: Free throw attempts per field goal attempt
- **Free Throw Percentage**: FT shooting accuracy

### Possession Factors
- **Turnover Rate**: Turnovers per 100 possessions (0.0-1.0, typical 0.15-0.20)
- **Offensive Rebound Rate**: % of missed shots rebounded (0.0-1.0, typical 0.25-0.35)
- **Performance Variance**: Standard deviation for game-to-game variance (typical 0.04-0.08)

## Output

The simulator provides comprehensive output:

```
======================================================================
COLLEGE BASKETBALL GAME SIMULATOR - HARALABOS VOULGARIS STYLE
======================================================================

Matchup: Duke Blue Devils vs Virginia Cavaliers
Simulations: 10,000

Team Statistics:

Duke Blue Devils:
  Offensive Efficiency: 118.5 pts/100 poss
  Defensive Efficiency: 98.2 pts/100 poss
  Pace: 72.5 poss/40 min

Virginia Cavaliers:
  Offensive Efficiency: 110.2 pts/100 poss
  Defensive Efficiency: 91.5 pts/100 poss
  Pace: 63.8 poss/40 min

======================================================================
RUNNING SIMULATIONS...
======================================================================

Completed 2,000 / 10,000 simulations...
Completed 4,000 / 10,000 simulations...
Completed 6,000 / 10,000 simulations...
Completed 8,000 / 10,000 simulations...
Completed 10,000 / 10,000 simulations...

======================================================================
SIMULATION RESULTS
======================================================================

Win Probability:
  Duke Blue Devils: 68.5%  (6,850 wins)
  Virginia Cavaliers: 31.5%  (3,150 wins)

Projected Scores:
  Duke Blue Devils: 73.2 ± 8.5 (median: 73)
  Virginia Cavaliers: 67.8 ± 7.2 (median: 68)

Expected Margin of Victory: 5.4 points (Duke Blue Devils)

Score Ranges (10th-90th percentile):
  Duke Blue Devils: 62 - 84
  Virginia Cavaliers: 58 - 77

======================================================================
```

## How It Works

1. **Pace Calculation**: Combines both teams' pace preferences to determine total possessions
2. **Possession Simulation**: Each possession is simulated individually:
   - Check for turnover
   - Determine shot type (2PT vs 3PT)
   - Apply defensive adjustments
   - Calculate make/miss based on shooting percentages and variance
   - Check for offensive rebounds (which create new possessions)
   - Handle free throws and and-one situations
3. **Monte Carlo Method**: Runs thousands of simulations to build probability distributions
4. **Statistical Analysis**: Aggregates results to show win probabilities and score distributions

## Advanced Features

### Defensive Adjustments
The simulator adjusts offensive performance based on defensive strength:
```python
def adjust_for_defense(base_rate, defensive_factor):
    league_avg = 105.0
    defensive_adjustment = defensive_factor / league_avg
    return base_rate * (2.0 - defensive_adjustment)
```

### Game Variance
Captures "hot" and "cold" shooting nights:
```python
variance_multiplier = 1.0 + np.random.normal(0, game_variance)
adjusted_shooting_pct = base_pct * variance_multiplier
```

### Offensive Rebounds
Creates additional possessions, affecting total scoring:
```python
if random.random() < offensive_rebound_rate:
    return simulate_possession()  # New possession
```

## Customization

You can create custom teams with any statistics:

```python
my_team = TeamStats(
    name="My Custom Team",
    offensive_efficiency=112.0,
    defensive_efficiency=100.0,
    pace=70.0,
    three_point_rate=0.40,
    three_point_percentage=0.36,
    two_point_percentage=0.53,
    free_throw_rate=0.35,
    free_throw_percentage=0.74,
    turnover_rate=0.17,
    offensive_rebound_rate=0.30,
    performance_variance=0.05
)
```

## Where to Get Real Statistics

To use real team data, you can pull statistics from:
- KenPom.com (requires subscription) - Best for efficiency metrics
- Sports-Reference.com/CBB - Free comprehensive stats
- BartTorvik.com - Free advanced metrics
- NCAA.com - Official statistics

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Credits

Inspired by the analytical approach of Haralabos Voulgaris, NBA executive and sports betting analyst known for his data-driven methodology.
