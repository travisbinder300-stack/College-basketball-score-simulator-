# College Basketball Score Simulator

A comprehensive and accurate college basketball game simulator that uses realistic statistics and game mechanics to simulate basketball games with high fidelity.

## Features

- **Realistic Game Simulation**: Simulates college basketball games with accurate scoring, possessions, and game flow
- **Enhanced Realism** (NEW): 
  - **Game-to-game variance**: Teams don't perform at exact averages every game - simulates hot/cold shooting nights
  - **Home court advantage**: Home teams get ~3-4 point boost through improved shooting
  - **Momentum and scoring runs**: Teams on scoring runs shoot better; cold teams struggle more
  - **Pace of play**: Adjustable game tempo affects total possessions and scoring
- **Detailed Statistics**: Tracks field goals, 3-pointers, free throws, rebounds, assists, steals, blocks, turnovers, and fouls
- **Customizable Teams**: Configure teams with custom statistics (shooting percentages, turnover rates, etc.)
- **Multiple Simulation Modes**: 
  - Quick simulation with preset teams
  - Custom simulation with user-defined teams
  - Multiple simulations for aggregate statistics
- **Spread Analysis**: Find teams that can cover point spreads with high confidence
  - Run 1000+ simulations to analyze spread coverage
  - Identify high-confidence betting opportunities (70%+ success rate)
  - Calculate optimal spreads for even matchups
  - **Find overvalued spreads** where underdog is getting too many points (value bets)
  - **Find undervalued spreads** where favorite is giving too many points (trap bets)
- **Overtime Support**: Automatically simulates overtime periods when games are tied
- **Play-by-Play**: Optional detailed play-by-play commentary for each possession
- **Box Score**: Comprehensive box score with detailed team statistics

## Installation

No external dependencies required! This simulator uses only Python 3.6+ standard library.

```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

## Usage

### Basic Simulation

Run a basic simulation with preset teams:

```bash
python3 basketball_simulator.py
```

### Interactive Mode

For more control and customization options:

```bash
python3 interactive_simulator.py
```

The interactive mode offers three options:
1. **Quick Simulation**: Run a single game with preset teams
2. **Custom Simulation**: Define your own teams with custom statistics
3. **Multiple Simulations**: Run multiple games and see aggregate results

### Spread Analysis (Find Teams That Cover Spreads)

Find teams that can cover point spreads with high accuracy:

```bash
python3 spread_finder.py
```

This tool runs 1000+ simulations and identifies:
- Which team can cover specific spreads with 70%+ confidence
- The optimal spread for a 50/50 matchup
- High-confidence betting opportunities
- **Overvalued spreads** where the underdog is getting too many points (value bets)
- **Undervalued spreads** where the favorite is giving too many points (trap bets to avoid)

**Find Today's Best Picks:**

```bash
python3 find_picks.py
```

This tool analyzes multiple games and provides betting recommendations:
- Simulates each matchup to determine optimal spreads
- Identifies HIGH confidence picks (70%+ coverage)
- Shows value assessment (extra points given/needed)
- Filters out trap bets and close calls
- Provides clear betting summary with best picks

**See a Complete Example:**

```bash
python3 good_example.py
```

This comprehensive example demonstrates:
- Duke vs UNC rivalry game analysis with 1000 simulations
- Testing multiple betting scenarios (3, 5, 7, 10, 12 point spreads)
- Identifying value bets and trap bets
- Detailed recommendations with coverage percentages
- Quick comparison of 3 different matchup types

**Example: Finding a team that covers the spread**

```bash
python3 spread_analyzer.py
```

This runs automated analysis on preset matchups and shows:
- Team win percentages
- Average scores and point differentials
- Spread coverage rates at different lines
- Confidence levels for each spread
- **Overvalued spreads report** - identifies when underdogs are getting extra points
- **Undervalued spreads report** - identifies when favorites can't cover (traps to avoid)

**Programmatic Usage:**

```python
from spread_analyzer import SpreadAnalyzer

# Define teams
team1 = {'name': 'Duke', 'fg_percentage': 0.48, 'three_pt_percentage': 0.38}
team2 = {'name': 'UNC', 'fg_percentage': 0.45, 'three_pt_percentage': 0.35}

# Run analysis
analyzer = SpreadAnalyzer(team1, team2, num_simulations=1000)
analyzer.run_simulations()

# Check if team can cover a 5-point spread
analysis = analyzer.analyze_spread(5.0)
print(f"Coverage rate: {analysis['cover_rate']:.1f}%")
print(f"Best bet: {analysis['best_bet']}")
print(f"Confidence: {analysis['confidence']}")

# Find overvalued spreads (underdog getting too many points - VALUE BETS)
overvalued = analyzer.find_overvalued_spreads()
for bet in overvalued:
    print(f"{bet['underdog']} +{abs(bet['spread']):.1f}: {bet['underdog_covers_pct']:.1f}% coverage")
    print(f"Extra points: {bet['extra_points']:.1f} (Value: {bet['value_rating']})")

# Find undervalued spreads (favorite giving too many points - TRAP BETS)
undervalued = analyzer.find_undervalued_spreads()
for bet in undervalued:
    print(f"AVOID: {bet['favorite']} -{abs(bet['spread']):.1f} (only covers {bet['favorite_covers_pct']:.1f}%)")
    print(f"Risk: {bet['risk_rating']} - {bet['advice']}")
```

## Team Statistics

Teams can be customized with the following statistics:

### Core Stats
- **Field Goal Percentage** (0.20-0.70): Overall shooting accuracy
- **Three-Point Percentage** (0.15-0.50): 3-point shooting accuracy
- **Free Throw Percentage** (0.50-0.95): Free throw accuracy
- **Turnover Rate** (0.05-0.30): Probability of turning the ball over
- **Offensive Rebound Rate** (0.15-0.45): Probability of getting offensive rebounds
- **Defensive Rebound Rate** (0.55-0.85): Probability of getting defensive rebounds
- **Three-Point Attempt Rate** (0.20-0.60): Percentage of shots that are 3-pointers
- **Steal Rate** (0.03-0.15): Probability of stealing the ball on defense
- **Block Rate** (0.02-0.12): Probability of blocking a shot

### Advanced Stats (NEW)
- **Home Court** (True/False): Whether the team is playing at home (adds ~3-4 point advantage)
- **Pace Factor** (0.85-1.15): Game tempo - 1.0 is average, higher = faster pace/more possessions
- **Variance Enabled** (True/False): Whether game-to-game performance variance is enabled (default: True)

### Example with Home Court Advantage:
```python
# Home team with advantage
home_team = {
    'name': 'Tennessee',
    'fg_percentage': 0.50,
    'three_pt_percentage': 0.38,
    'home_court': True,  # Home court advantage enabled
    'pace_factor': 1.0
}

# Away team
away_team = {
    'name': 'Rutgers',
    'fg_percentage': 0.44,
    'three_pt_percentage': 0.33,
    'home_court': False,
    'pace_factor': 0.95  # Slower-paced team
}
```

## Game Mechanics

The simulator accurately models:

- **Possessions**: Each team gets approximately 70 possessions per game (35 per half), adjusted by pace factor
- **Shot Selection**: Teams choose between 2-point and 3-point attempts based on their strategy
- **Turnovers**: Random turnovers based on team's turnover rate (affected by momentum)
- **Fouls**: Realistic foul calling with appropriate free throw situations
- **Rebounds**: Offensive and defensive rebounding with second-chance opportunities
- **Defensive Plays**: Steals and blocks affect game outcomes
- **Overtime**: 5-possession overtime periods when games are tied

### Enhanced Realism Features

- **Game-to-Game Variance**: Each simulation randomly adjusts team shooting (+/- 5%) to simulate hot/cold nights
- **Home Court Advantage**: Home teams shoot ~1.5% better on FG and 3PT, slight FT boost
- **Momentum System**: Teams on scoring runs get shooting bonuses; cold teams get penalties
- **Pace of Play**: Adjustable tempo affects total possessions (faster pace = more scoring variance)

These features create more realistic score distributions where:
- Favorites don't always cover large spreads
- Underdogs sometimes win outright
- Games can have unexpected blowouts (like real basketball)

## Example Output

```
============================================================
                 COLLEGE BASKETBALL SIMULATION              
          Blue Devils           vs           Wildcats       
============================================================

Possession 1: Blue Devils has the ball
  Blue Devils scores 2 points on a 2-pointer! Score: Blue Devils 2 - Wildcats 0

...

============================================================
                         FINAL SCORE                        
============================================================
Blue Devils: 78
Wildcats: 72

Winner: Blue Devils
============================================================

                         BOX SCORE                          
============================================================

Blue Devils:
  Points: 78
  Field Goals: 22/48 (45.8%)
  3-Pointers: 8/22 (36.4%)
  Free Throws: 18/24 (75.0%)
  Rebounds: 35
  Assists: 16
  Steals: 6
  Blocks: 3
  Turnovers: 10
  Fouls: 18
```

## Accuracy

This simulator achieves high accuracy by:

1. Using realistic statistical ranges based on actual college basketball data
2. Modeling actual game flow with alternating possessions
3. Simulating realistic possession counts (~70 per game)
4. Including all major basketball events (shots, turnovers, rebounds, fouls)
5. Proper overtime handling
6. Realistic correlation between team stats and game outcomes

The default statistics are based on NCAA Division I averages, ensuring realistic final scores typically in the 60-90 point range.

## License

This project is licensed under the terms included in the LICENSE file.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the simulator.
