# College Basketball & Football Score Simulator

A comprehensive and accurate college sports game simulator that uses realistic statistics and game mechanics to simulate basketball and football games with high fidelity.

## 🏀 Basketball Features

- **Realistic Game Simulation**: Simulates college basketball games with accurate scoring, possessions, and game flow
- **Enhanced Realism with Calibrated Parameters** (UPDATED): 
  - **Game-to-game variance**: Teams perform 5-8% better or worse than averages (calibrated from real game data)
  - **Home court advantage**: Home teams get ~4 point boost through improved shooting (2% FG/3PT boost)
  - **Momentum and scoring runs**: Enhanced momentum system creates dramatic runs and slumps (up to 3% FG boost)
  - **Pace of play**: Adjustable game tempo affects total possessions and scoring
  - **Calibrated for real-world accuracy**: Parameters tuned based on actual college basketball game outcomes
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

## 🏈 Football Features (NEW!)

- **Realistic Game Simulation**: Simulates college football games with accurate drive mechanics, play calling, and scoring
- **Enhanced Realism**:
  - **Game-to-game variance**: Teams perform better or worse than averages to simulate hot/cold days
  - **Home field advantage**: Home teams get pass completion and rushing bonuses
  - **Momentum system**: Teams on scoring streaks get performance boosts
  - **Pace of play**: Adjustable tempo affects total plays and possessions
- **Detailed Play Types**:
  - Pass plays with completions, incompletions, interceptions, and sacks
  - Rush plays with varying yard gains and fumbles
  - Field goals with distance-adjusted success rates
  - Punts with realistic distance and returns
- **Complete Statistics**: Pass/rush yards, touchdowns, field goals, turnovers, first downs, third-down conversions, time of possession
- **Spread & Total Analysis**: Same powerful spread analysis as basketball
  - Analyze point spreads with 1000+ simulations
  - Over/under total analysis
  - Find value picks and avoid trap bets
- **Overtime Support**: College football overtime rules with alternating possessions from the 25-yard line

## Installation

No external dependencies required! This simulator uses only Python 3.6+ standard library.

```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

## Usage

### 🏀 Basketball Simulation

Run a basic basketball simulation with preset teams:

```bash
python3 basketball_simulator.py
```

### 🏈 Football Simulation

Run a basic football simulation with preset teams:

```bash
cd college_football
python3 football_simulator.py
```

**Football Spread Analysis:**

```bash
cd college_football
python3 football_spread_analyzer.py  # Full spread analysis
python3 football_find_picks.py       # Quick picks finder
python3 football_example.py          # Comprehensive examples
```

**Football Programmatic Usage:**

```python
# Option 1: Run from the college_football directory
from football_simulator import FootballTeam, FootballSimulator
from football_spread_analyzer import FootballSpreadAnalyzer

# Option 2: Import as a package from the root directory
from college_football import FootballTeam, FootballSimulator, FootballSpreadAnalyzer

# Define teams
team1_config = {
    'name': 'Alabama',
    'pass_completion_pct': 0.65,
    'yards_per_completion': 13.5,
    'rush_yards_per_carry': 5.2,
    'turnover_rate': 0.02,
    'red_zone_td_pct': 0.70,
    'field_goal_pct': 0.82,
    'home_field': True
}

team2_config = {
    'name': 'Auburn',
    'pass_completion_pct': 0.58,
    'yards_per_completion': 11.5,
    'rush_yards_per_carry': 4.5,
    'turnover_rate': 0.03,
    'red_zone_td_pct': 0.58,
    'field_goal_pct': 0.75
}

# Run spread analysis
analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=1000)
analyzer.run_simulations()

# Check spread coverage
analysis = analyzer.analyze_spread(14.0)  # Alabama -14
print(f"Alabama -14 covers: {analysis['team1_cover_pct']:.1f}%")
print(f"Auburn +14 covers: {analysis['team2_cover_pct']:.1f}%")

# Check over/under
total_analysis = analyzer.analyze_total(52.5)
print(f"Over 52.5: {total_analysis['over_pct']:.1f}%")
print(f"Under 52.5: {total_analysis['under_pct']:.1f}%")
```

### Basketball Interactive Mode

For more control and customization options:

```bash
python3 interactive_simulator.py
```

The interactive mode offers three options:
1. **Quick Simulation**: Run a single game with preset teams
2. **Custom Simulation**: Define your own teams with custom statistics
3. **Multiple Simulations**: Run multiple games and see aggregate results

### Basketball Spread Analysis (Find Teams That Cover Spreads)

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

### 🏀 Basketball Team Stats

Teams can be customized with the following statistics:

#### Core Stats
- **Field Goal Percentage** (0.20-0.70): Overall shooting accuracy
- **Three-Point Percentage** (0.15-0.50): 3-point shooting accuracy
- **Free Throw Percentage** (0.50-0.95): Free throw accuracy
- **Turnover Rate** (0.05-0.30): Probability of turning the ball over
- **Offensive Rebound Rate** (0.15-0.45): Probability of getting offensive rebounds
- **Defensive Rebound Rate** (0.55-0.85): Probability of getting defensive rebounds
- **Three-Point Attempt Rate** (0.20-0.60): Percentage of shots that are 3-pointers
- **Steal Rate** (0.03-0.15): Probability of stealing the ball on defense
- **Block Rate** (0.02-0.12): Probability of blocking a shot

#### Advanced Stats
- **Home Court** (True/False): Whether the team is playing at home (adds ~3-4 point advantage)
- **Pace Factor** (0.85-1.15): Game tempo - 1.0 is average, higher = faster pace/more possessions
- **Variance Enabled** (True/False): Whether game-to-game performance variance is enabled (default: True)

### 🏈 Football Team Stats

Football teams can be customized with:

#### Offensive Stats
- **Pass Completion Pct** (0.50-0.75): Pass completion percentage
- **Yards Per Completion** (8.0-16.0): Average yards per completed pass
- **Rush Yards Per Carry** (3.0-6.0): Average rushing yards per attempt
- **Turnover Rate** (0.01-0.05): Probability of turnover per play
- **Red Zone TD Pct** (0.45-0.80): Touchdown percentage in the red zone
- **Field Goal Pct** (0.60-0.90): Field goal success rate
- **Pass Play Rate** (0.40-0.70): Percentage of plays that are passes

#### Defensive Stats
- **Sack Rate** (0.03-0.10): Probability of sacking the QB
- **Interception Rate** (0.01-0.04): Interception rate on pass plays

#### Advanced Stats
- **Home Field** (True/False): Home field advantage (pass/rush boosts)
- **Pace Factor** (0.85-1.15): Game tempo affecting total plays

### Example with Home Field Advantage:
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
