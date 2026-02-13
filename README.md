# College Basketball Score Simulator - NBA Prop Betting Module

Basketball simulator with comprehensive NBA prop betting features based on PropMadness.com interfuture data structure.

## Overview

This repository contains a complete NBA prop betting system that includes:
- Data models for NBA players, games, and prop bets
- Prop betting analyzer with value bet detection
- Monte Carlo simulation engine for prop outcomes
- **Shot chart analysis and defensive matchup tracking** ⭐ NEW
- **Player vs defense ranking with similar player matching** ⭐ NEW
- **Defender hit rate tracking and zone-specific analysis** ⭐ NEW
- Interfuture data format based on PropMadness.com structure
- JSON data loader for easy integration

## Features

### 1. NBA Prop Data Model (`nba_prop_data.py`)
- **Player** - NBA player information (name, team, position)
- **Game** - Game details (teams, schedule, venue)
- **PropLine** - Betting lines with odds (American, Decimal)
- **PlayerProp** - Complete prop bet with context data
- **PropBetSlip** - Bet slip for single bets and parlays

Supported prop types:
- Points
- Rebounds
- Assists
- Three-Pointers Made
- Steals & Blocks
- Turnovers
- Combined Stats (PRA - Points + Rebounds + Assists)
- Double-Double & Triple-Double

### 2. Prop Analyzer & Simulator (`nba_prop_simulator.py`)
- **PropAnalyzer** - Analyze props for value and edge
  - Calculate hit probabilities using weighted averages
  - Find value bets with positive expected value
  - Consider injury status and context
- **PropSimulator** - Monte Carlo simulation
  - Simulate individual prop outcomes (10,000+ runs)
  - Simulate parlay outcomes with ROI calculations
  - Statistical analysis of expected values

### 3. Interfuture Data Format (`interfuture_nba_props.json`)
JSON structure based on PropMadness.com format:
- Metadata (source, season, timestamps)
- Games with scheduling information
- Players with team and position data
- Props with complete betting lines and odds
- Player statistics (season avg, last 5 games, vs opponent)
- Context data (injury status, minutes projection, usage rate)
- Bookmaker information

### 4. Data Loader (`nba_prop_loader.py`)
- Load interfuture JSON data into Python objects
- Filter props by game, player, or prop type
- Parse timestamps and odds formats
- Validate data integrity

### 5. Shot Chart & Defensive Matchup Analysis (`shot_chart_defense.py`) ⭐ NEW
- **Shot Chart Data** - Zone-based shooting statistics (paint, mid-range, 3-point zones)
- **Player Profiles** - Play style classification (volume scorer, 3-point specialist, etc.)
- **Defender Stats** - Individual defender metrics and hit rates allowed by zone
- **Team Defense Rankings** - Defensive ratings, scheme types, zone-specific rankings
- **Defensive Matchup Analyzer** - Analyze player vs defense matchups
  - Calculate favorable/unfavorable shooting zones
  - Project hit rates based on defensive matchup
  - Find similar players based on play style and shot distribution
  - Historical performance of similar players vs specific defenses

### 6. Enhanced Prop Integration (`prop_matchup_integration.py`) ⭐ NEW
- **Enhanced Prop Analyzer** - Combines prop analysis with defensive matchups
  - Adjust projections based on shot chart and defensive data
  - Calculate hit probabilities with matchup context
  - Generate confidence levels for recommendations
- **Matchup Reports** - Comprehensive defensive matchup reports
  - Player vs defense analysis
  - Zone-by-zone projections
  - Similar player comparisons
  - Defender-specific adjustments

## Installation

```bash
# Clone the repository
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-

# No external dependencies required - uses Python standard library only
```

## Usage

### Running the Data Model
```bash
python nba_prop_data.py
```
Output: Displays sample NBA props with detailed information.

### Running the Analyzer & Simulator
```bash
python nba_prop_simulator.py
```
Output: 
- Prop analysis with edge calculations
- Value bet recommendations
- Monte Carlo simulation results
- Parlay simulation with expected value

### Loading Data from JSON
```bash
python nba_prop_loader.py
```
Output: 
- Loads all data from interfuture_nba_props.json
- Displays players, games, and props
- Shows filtered examples

### Running Shot Chart & Defensive Analysis ⭐ NEW
```bash
python shot_chart_defense.py
```
Output:
- Shot chart statistics by zone
- Player vs defense matchup analysis
- Favorable/unfavorable shooting zones
- Similar player matching
- Defender hit rate tracking

### Running Enhanced Prop Analysis ⭐ NEW
```bash
python prop_matchup_integration.py
```
Output:
- Enhanced prop analysis with defensive matchups
- Matchup-adjusted projections
- Similar player performance comparisons
- Comprehensive matchup reports

### Using as a Module
```python
from nba_prop_data import generate_sample_props
from nba_prop_simulator import PropAnalyzer, PropSimulator

# Generate or load props
props = generate_sample_props()

# Analyze props
analyzer = PropAnalyzer()
for prop in props:
    analysis = analyzer.analyze_prop(prop)
    print(analysis)

# Find value bets
value_bets = analyzer.find_value_bets(props, min_edge=0.05)
for prop, edge, side in value_bets:
    print(f"{prop} - {side} - Edge: {edge:+.2%}")

# Run simulations
simulator = PropSimulator(analyzer)
sim_result = simulator.simulate_prop_outcome(props[0], num_simulations=10000)
print(sim_result)
```

### Using Shot Chart & Defensive Matchup Analysis ⭐ NEW
```python
from shot_chart_defense import (
    PlayerProfile, DefensiveMatchupAnalyzer,
    generate_sample_shot_charts, generate_sample_team_defenses
)

# Load shot chart and defense data
shot_charts = generate_sample_shot_charts()
team_defenses = generate_sample_team_defenses()

# Create player profile
lebron_profile = PlayerProfile(
    player_id="2544",
    player_name="LeBron James",
    team="Los Angeles Lakers",
    position="SF",
    primary_play_style=PlayStyle.VOLUME_SCORER,
    shot_chart=shot_charts[0],
    usage_rate=0.312,
    true_shooting_pct=0.605,
    effective_fg_pct=0.564,
    preferred_zones=[ShotZone.PAINT, ShotZone.THREE_POINT_TOP],
    avoids_zones=[ShotZone.MID_RANGE]
)

# Analyze matchup vs Warriors defense
analyzer = DefensiveMatchupAnalyzer()
matchup = analyzer.analyze_matchup(
    lebron_profile,
    team_defenses[2],  # Warriors
    None  # No specific defender
)

# Get matchup summary
summary = matchup.get_matchup_summary()
print(f"Matchup Rating: {summary['matchup_rating']}")
print(f"Expected FG Boost: {summary['expected_fg_boost']}")
print(f"Favorable Zones: {summary['favorable_zones']}")

# Find similar players
similar_players = analyzer.find_similar_players(
    lebron_profile,
    all_player_profiles,
    min_similarity=0.6
)
for player, similarity in similar_players:
    print(f"{player.player_name}: {similarity:.1%} similar")
```

### Using Enhanced Prop Analysis with Matchups ⭐ NEW
```python
from prop_matchup_integration import EnhancedPropAnalyzer

# Initialize enhanced analyzer
matchup_analyzer = DefensiveMatchupAnalyzer()
enhanced_analyzer = EnhancedPropAnalyzer(matchup_analyzer)

# Analyze prop with defensive matchup
analysis = enhanced_analyzer.analyze_prop_with_matchup(
    prop=lebron_points_prop,
    player_profile=lebron_profile,
    team_defense=warriors_defense,
    primary_defender=None
)

print(f"Base Projection: {analysis['base_projection']}")
print(f"Adjusted Projection: {analysis['adjusted_projection']}")
print(f"Matchup Rating: {analysis['matchup_rating']}")
print(f"Hit Probability: {analysis['hit_probability']:.1%}")
print(f"Edge: {analysis['edge']:+.2%}")
print(f"Recommendation: {analysis['recommendation']}")
print(f"Confidence: {analysis['confidence']}")

# Compare with similar players
comparison = enhanced_analyzer.compare_with_similar_players(
    lebron_profile,
    all_player_profiles,
    warriors_defense
)
print(f"Similar Players Found: {comparison['num_similar_players']}")
print(f"Historical FG%: {comparison['historical_avg_fg_pct']:.1%}")
```

## Data Structure

### Interfuture JSON Format
```json
{
  "metadata": {
    "source": "PropMadness.com",
    "data_type": "interfuture_nba_props",
    "season": "2023-24"
  },
  "props": [
    {
      "prop_id": "PROP_001",
      "player_id": "2544",
      "game_id": "NBA_2024_LAL_GSW_001",
      "prop_type": "points",
      "line": {
        "value": 25.5,
        "over_odds": -110,
        "under_odds": -110,
        "bookmaker": "DraftKings"
      },
      "player_stats": {
        "season_avg": 27.3,
        "last_5_avg": 29.8,
        "vs_opponent_avg": 28.5
      },
      "context": {
        "injury_status": "healthy",
        "minutes_projection": 35.0
      }
    }
  ]
}
```

## Examples

### Example 1: Analyze a Single Prop
```python
from nba_prop_data import generate_sample_props
from nba_prop_simulator import PropAnalyzer

props = generate_sample_props()
analyzer = PropAnalyzer()

# Analyze LeBron's points prop
lebron_prop = props[0]
analysis = analyzer.analyze_prop(lebron_prop)

print(f"Prop: {analysis['prop']}")
print(f"Estimated Over Probability: {analysis['estimated_over_probability']}")
print(f"Edge: {analysis['edge_over']}")
print(f"Recommendation: {analysis['recommendation']}")
```

### Example 2: Simulate a Parlay
```python
from nba_prop_data import generate_sample_props, PropBetSlip
from nba_prop_simulator import PropAnalyzer, PropSimulator

props = generate_sample_props()
analyzer = PropAnalyzer()
simulator = PropSimulator(analyzer)

# Create a 3-leg parlay
parlay = PropBetSlip(
    slip_id="PARLAY_001",
    props=props[:3],
    stake=50.0,
    bet_type="parlay"
)

# Simulate the parlay
result = simulator.simulate_parlay(parlay, num_simulations=10000)
print(f"Hit Rate: {result['hit_rate']}")
print(f"Expected Value: {result['expected_value']}")
print(f"ROI: {result['roi']}")
```

### Example 3: Load Data from JSON
```python
from nba_prop_loader import PropDataLoader

loader = PropDataLoader('interfuture_nba_props.json')
players, games, props = loader.load_all()

# Filter props by game
game_props = loader.filter_props_by_game("NBA_2024_LAL_GSW_001")
for prop in game_props:
    print(prop)
```

## How It Works

### Prop Analysis Algorithm
1. **Weighted Average Calculation**: Combines season average (40%), last 5 games (40%), and vs opponent average (20%)
2. **Injury Adjustment**: Applies multipliers based on injury status
3. **Probability Estimation**: Uses normal distribution to estimate hit probability
4. **Edge Calculation**: Compares estimated probability to market implied probability
5. **Value Detection**: Identifies props with 5%+ positive edge

### Monte Carlo Simulation
1. **Normal Distribution**: Models player performance using Gaussian distribution
2. **Multiple Runs**: Executes 10,000+ simulations per prop
3. **Hit Rate**: Calculates percentage of simulations where prop hits
4. **Expected Value**: Computes EV = (hit_rate × payout) - stake
5. **Parlay Simulation**: Requires all legs to hit for parlay success

### Shot Chart & Defensive Matchup Analysis ⭐ NEW
1. **Zone Classification**: Divides court into 6 zones (paint, mid-range, 3-point corners/wings/top, free throw line)
2. **Shot Distribution**: Tracks attempts, makes, and efficiency by zone
3. **Play Style Matching**: Classifies players into 8 play styles (volume scorer, 3-point specialist, slasher, etc.)
4. **Defensive Scheme Analysis**: Tracks team defensive types (switch-heavy, drop coverage, aggressive trap, etc.)
5. **Matchup Calculation**: 
   - Compare player's strong zones vs defense's weak zones
   - Adjust FG% projections based on defensive ranking
   - Factor in specific defender matchups
   - Weight by shot frequency for overall impact
6. **Similar Player Algorithm**:
   - 40% weight on play style match
   - 40% weight on shot distribution similarity
   - 20% weight on efficiency similarity
   - Returns top matches with similarity score
7. **Defender Hit Rate**: Tracks FG% allowed by defenders in each zone
8. **Historical Performance**: Aggregates similar players' performance vs specific defenses

## Key Features Summary

### Original Features
✅ **Prop Betting Models** - Complete data structures for props, lines, and bets  
✅ **Value Bet Detection** - Finds props with 5%+ positive edge  
✅ **Monte Carlo Simulation** - 10,000+ run simulations for accurate probabilities  
✅ **Parlay Analysis** - EV and ROI calculations for multi-leg parlays  
✅ **Multiple Prop Types** - Points, rebounds, assists, 3-pointers, combined stats  
✅ **Odds Conversion** - American, Decimal, Fractional formats  

### New Features ⭐
✅ **Shot Chart Analysis** - Zone-based shooting statistics and tendencies  
✅ **Player vs Defense Ranking** - Matchup ratings and projections  
✅ **Similar Player Matching** - Find comparable players by play style  
✅ **Defender Hit Rate Tracking** - Zone-specific defense metrics  
✅ **Matchup-Adjusted Props** - Enhanced projections with defensive context  
✅ **Comprehensive Reports** - Detailed matchup breakdowns with recommendations  

## Technical Details

- **Language**: Python 3.7+
- **Dependencies**: None (uses only standard library)
- **Data Format**: JSON (interfuture format)
- **Odds Formats**: American, Decimal, Fractional
- **Simulation Method**: Monte Carlo with normal distribution

## PropMadness.com Integration

This module is designed to work with PropMadness.com's interfuture data format, which includes:
- Real-time odds from multiple sportsbooks
- Advanced player statistics and trends
- Injury reports and lineup information
- Pace factors and usage rates
- Matchup-specific data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is a simulator for educational and research purposes. Always gamble responsibly and within your means. 
