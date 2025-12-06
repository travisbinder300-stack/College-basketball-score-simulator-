# Soccer 10,000 Game Simulator - Haralabos Voulgaris Style

A sophisticated soccer match simulator inspired by the analytical approach of renowned sports bettor Haralabos Voulgaris. This simulator uses advanced statistical modeling to predict match outcomes through Monte Carlo simulations.

## Features

### Core Capabilities
- **10,000+ Game Monte Carlo Simulations**: Run thousands of simulations to determine probable outcomes
- **Poisson Distribution Modeling**: Statistically sound goal distribution based on team strengths
- **Expected Goals (xG)**: Calculate expected goals for each team based on offensive and defensive ratings
- **Team Rating System**: Offensive and defensive strength ratings for accurate modeling
- **Home Advantage Factor**: Accounts for home field advantage in calculations
- **Probability Analysis**: Win/Draw/Loss probabilities with betting odds
- **Score Line Predictions**: Most likely final scores with occurrence probabilities

### Haralabos Voulgaris Style Analytics
This simulator implements key principles from Voulgaris's analytical methodology:
- Data-driven predictions using statistical models
- Poisson distribution for goal/score modeling
- Team strength ratings (offensive & defensive capabilities)
- Monte Carlo simulations for outcome probabilities
- Expected goals (xG) metrics
- Fair odds calculation (no bookmaker margin)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the simulator with example matches:
```bash
python soccer_simulator.py
```

### Custom Match Simulation

```python
from soccer_simulator import Team, SoccerSimulator

# Create teams with ratings
home_team = Team("Manchester City", offensive_rating=1.45, defensive_rating=0.75)
away_team = Team("Liverpool", offensive_rating=1.40, defensive_rating=0.80)

# Create simulator
simulator = SoccerSimulator(league_avg_goals=2.75, home_advantage=0.3)

# Run 10,000 simulations
simulator.print_simulation_report(home_team, away_team, num_simulations=10000)
```

### Load Teams from Configuration

```python
from soccer_simulator import load_teams_from_file, SoccerSimulator

# Load teams from JSON file
teams = load_teams_from_file('teams_example.json')

# Select teams and simulate
simulator = SoccerSimulator()
simulator.print_simulation_report(teams[0], teams[1], num_simulations=10000)
```

## Understanding Team Ratings

### Offensive Rating
- **1.50+**: Elite attacking team (e.g., prime Barcelona, Manchester City)
- **1.30-1.50**: Very strong attack (top teams)
- **1.00-1.30**: Average to above-average attack
- **0.80-1.00**: Below average attack
- **<0.80**: Weak attacking team

### Defensive Rating
- **<0.75**: Elite defense (very hard to score against)
- **0.75-0.90**: Very strong defense
- **0.90-1.10**: Average defense
- **1.10-1.30**: Weak defense
- **1.30+**: Very weak defense (concedes many goals)

### League Average Goals
- **Premier League**: ~2.75 goals per game
- **La Liga**: ~2.65 goals per game
- **Bundesliga**: ~3.10 goals per game
- **Serie A**: ~2.70 goals per game
- **Ligue 1**: ~2.75 goals per game

### Home Advantage Factor
- **0.3**: Standard home advantage (~30% boost)
- **0.2**: Lower home advantage
- **0.4**: Strong home advantage

## Output Explanation

The simulator provides comprehensive match analysis:

### Expected Goals (xG)
Theoretical goals each team should score based on their ratings and match conditions.

### Match Outcome Probabilities
Percentage chance of home win, draw, or away win based on 10,000 simulations.

### Decimal Odds
Fair odds (without bookmaker margin) for each outcome. Lower odds = higher probability.

### Simulated Averages
Actual average goals scored in the simulations (may differ slightly from xG due to randomness).

### Top Score Lines
Most likely final scores with their probability of occurrence.

## Example Output

```
================================================================================
SOCCER MATCH SIMULATOR - Haralabos Voulgaris Style
================================================================================

Match: Manchester City (Home) vs Liverpool (Away)
Simulations: 10,000

Team Ratings:
  Manchester City: Offensive=1.45, Defensive=0.75
  Liverpool: Offensive=1.40, Defensive=0.80

--------------------------------------------------------------------------------
EXPECTED GOALS (xG)
--------------------------------------------------------------------------------
  Manchester City: 2.31
  Liverpool: 1.68

--------------------------------------------------------------------------------
MATCH OUTCOME PROBABILITIES
--------------------------------------------------------------------------------
  Manchester City Win: 49.2%
  Draw:                25.8%
  Liverpool Win:       25.0%

--------------------------------------------------------------------------------
DECIMAL ODDS (Fair Odds - No Margin)
--------------------------------------------------------------------------------
  Manchester City Win: 2.03
  Draw:                3.88
  Liverpool Win:       4.00

--------------------------------------------------------------------------------
TOP 10 MOST LIKELY SCORELINES
--------------------------------------------------------------------------------
   1. 2-1   -  11.23% (1,123 occurrences)
   2. 1-1   -   9.87% (987 occurrences)
   3. 2-0   -   8.45% (845 occurrences)
   4. 1-0   -   7.92% (792 occurrences)
   5. 3-1   -   7.34% (734 occurrences)
   ...
```

## Technical Details

### Statistical Methodology

1. **Expected Goals Calculation**:
   ```
   xG = (League_Avg_Goals / 2) × Attack_Rating × Defense_Rating × Home_Factor
   ```

2. **Poisson Distribution**: 
   Goals are sampled from a Poisson distribution with λ (lambda) equal to the expected goals.

3. **Monte Carlo Simulation**:
   Each match is simulated 10,000 times to generate statistically significant probabilities.

4. **Probability Calculation**:
   Outcome probabilities are calculated as the frequency of each result across all simulations.

## Customization

### Create Custom Teams

Edit `teams_example.json` or create your own team configuration:

```json
{
  "teams": [
    {
      "name": "Your Team",
      "offensive_rating": 1.25,
      "defensive_rating": 0.95
    }
  ]
}
```

### Adjust Simulation Parameters

```python
# Create simulator with custom parameters
simulator = SoccerSimulator(
    league_avg_goals=3.0,  # Higher scoring league
    home_advantage=0.4      # Stronger home advantage
)
```

## Use Cases

- **Sports Betting Analysis**: Calculate fair odds and value bets
- **Match Predictions**: Predict likely outcomes and scores
- **Team Performance Analysis**: Compare team strengths
- **League Simulations**: Simulate entire seasons or tournaments
- **Statistical Education**: Learn about Poisson distribution and Monte Carlo methods

## Dependencies

- Python 3.7+
- NumPy: Numerical computing
- SciPy: Statistical functions (Poisson distribution)
- Pandas: Data manipulation (future features)

## Contributing

Contributions are welcome! Areas for enhancement:
- Player-level statistics
- In-game state modeling (red cards, injuries)
- Historical data integration
- Tournament bracket simulations
- Machine learning for rating calibration

## License

This project is licensed under the terms included in the LICENSE file.

## Credits

Inspired by the analytical methodology of Haralabos Voulgaris and modern sports analytics principles.

## Disclaimer

This simulator is for educational and analytical purposes. Past performance and statistical models do not guarantee future results. Use responsibly for betting decisions.
