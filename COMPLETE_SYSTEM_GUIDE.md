# Complete 356-Team System Guide

## Overview

This system tracks all 356 Division I college basketball teams with:
- **Strength of Schedule (SOS)** calculations
- **Team rankings** based on Billy Walters power ratings
- **Pace-adjusted predictions** using tempo and possession length
- **Enhanced Billy Walters formulas** with Four Factors and advanced metrics

## Files

1. **`complete_team_system.py`** - Complete team database and ranking system
2. **`teams_data_template.csv`** - CSV template for loading team data
3. **`team_rankings.csv`** - Exported rankings (generated)
4. **`team_database.json`** - Full database export (generated)

## Key Features

### 1. Team Data Structure

Each team includes:
- **Basic Info**: Name, conference
- **Efficiency**: Offensive/defensive efficiency (per 100 possessions)
- **Pace**: Tempo (possessions/game), possession length
- **Record**: Overall and conference wins/losses
- **Four Factors**: eFG%, TO%, ORB%, FT Rate
- **Advanced**: SOS, power rating, ranking
- **Recent Form**: Last 10 games results

### 2. Billy Walters Enhanced Power Rating

The system calculates power ratings using:

```
Power Rating = Base Rating + SOS Adjustment + Recent Form + 
               Injury Penalty + Pace Factor + Four Factors Bonus
```

**Components:**
- **Base Rating**: Net efficiency / 10
- **SOS Adjustment**: Average opponent rating × 0.20
- **Recent Form**: (Win% - 0.5) × 2.0
- **Injury Penalty**: -1.5 per key injury
- **Pace Factor**: Tempo adjustment for efficiency
- **Four Factors**: Dean Oliver's offensive factors

### 3. Strength of Schedule (SOS)

Calculated as the average power rating of all opponents played.

**Formula:**
```
SOS = Average(Opponent Power Ratings)
```

This creates a feedback loop:
1. Calculate initial power ratings from efficiency
2. Calculate SOS from opponents' ratings
3. Recalculate power ratings including SOS
4. Generate final rankings

### 4. Pace-Adjusted Score Predictions

Predictions account for both teams' pace:

```python
Expected Pace = (Home Tempo + Away Tempo) / 2

Home Score = (Home Off Eff × 0.6 + Adjusted Def × 0.4) × 
             (Expected Pace / 100) + Home Advantage

Away Score = (Away Off Eff × 0.6 + Adjusted Def × 0.4) × 
             (Expected Pace / 100)
```

## Usage

### Loading Teams from CSV

```python
from complete_team_system import CompleteDivisionIDatabase

db = CompleteDivisionIDatabase()
db.load_from_csv('teams_data_template.csv')
```

### Adding Teams Manually

```python
from complete_team_system import TeamData

team = TeamData(
    team_name="Duke",
    conference="ACC",
    offensive_efficiency=118.5,
    defensive_efficiency=95.2,
    tempo=72.0,
    wins=22,
    losses=6,
    recent_games=['W','W','L','W','W'],
    effective_fg_pct=0.520,
    turnover_pct=0.165,
    offensive_rebound_pct=0.320,
    free_throw_rate=0.340
)

db.add_team(team)
```

### Calculating Rankings

```python
# Calculate all metrics
db.update_all_power_ratings()  # Calculates SOS and power ratings
db.generate_rankings()         # Creates rankings

# Display top 25
db.display_rankings(top_n=25)

# Get conference rankings
acc_teams = db.get_conference_rankings("ACC")
```

### Making Predictions

```python
# Predict score with pace
home_score, away_score, pace = db.predict_score_with_pace(
    "Duke", "UNC", neutral_site=False
)
print(f"Duke {home_score}, UNC {away_score}")
print(f"Expected pace: {pace} possessions")

# Predict spread
spread, favorite = db.predict_spread("Duke", "UNC")
print(f"{favorite} -{spread}")
```

### Viewing Team Details

```python
# Full team profile
db.display_team_profile("Duke")

# Get specific team
team = db.teams["Duke"]
print(f"Power Rating: {team.power_rating}")
print(f"Ranking: #{team.ranking}")
print(f"SOS: {team.strength_of_schedule}")
```

### Exporting Data

```python
# Export to CSV
db.export_to_csv('team_rankings.csv')

# Export to JSON (complete database)
db.export_to_json('team_database.json')
```

## CSV Template Format

Your CSV should have these columns:

```csv
Team,Conference,OffEff,DefEff,Tempo,Wins,Losses,eFG,TOPct,ORBPct,FTRate
```

**Column Descriptions:**
- **Team**: Team name
- **Conference**: Conference abbreviation
- **OffEff**: Offensive efficiency (points per 100 possessions)
- **DefEff**: Defensive efficiency (points allowed per 100 possessions)
- **Tempo**: Average possessions per game
- **Wins**: Season wins
- **Losses**: Season losses
- **eFG**: Effective field goal percentage (0.0-1.0)
- **TOPct**: Turnover percentage (0.0-1.0)
- **ORBPct**: Offensive rebound percentage (0.0-1.0)
- **FTRate**: Free throw rate (0.0-1.0)

## Data Sources

To populate all 356 teams, use data from:

1. **KenPom.com** - Best source for efficiency and tempo data
   - Adjusted offensive/defensive efficiency
   - Adjusted tempo
   - Four Factors

2. **BartTorvik.com** - Alternative efficiency metrics
   - Similar to KenPom
   - Free access to some data

3. **TeamRankings.com** - Record and schedule data
   - Win-loss records
   - Schedule information for SOS

4. **Sports-Reference.com (CBB)** - Historical and current stats
   - Team records
   - Basic statistics

## Example: Complete Workflow

```python
from complete_team_system import CompleteDivisionIDatabase

# 1. Create database
db = CompleteDivisionIDatabase()

# 2. Load teams from CSV (all 356 teams)
db.load_from_csv('all_356_teams.csv')

# 3. Add opponent data for SOS calculations
# (You would need to track who played whom)
for team_name in db.teams:
    team = db.teams[team_name]
    # team.opponents_played = [list of opponent names]

# 4. Calculate everything
db.update_all_power_ratings()
rankings = db.generate_rankings()

# 5. Display results
db.display_rankings(top_n=25)

# 6. Make predictions
home, away, pace = db.predict_score_with_pace("Duke", "UNC")
print(f"Prediction: Duke {home}, UNC {away} ({pace} pace)")

# 7. Export results
db.export_to_csv('complete_rankings.csv')
db.export_to_json('complete_database.json')
```

## Advanced Features

### Conference Analysis

```python
# Get all conferences
conferences = set(team.conference for team in db.teams.values())

# Rank conferences by average power rating
conf_ratings = {}
for conf in conferences:
    teams = [t for t in db.teams.values() if t.conference == conf]
    avg_rating = sum(t.power_rating for t in teams) / len(teams)
    conf_ratings[conf] = avg_rating

# Sort and display
for conf, rating in sorted(conf_ratings.items(), 
                          key=lambda x: x[1], 
                          reverse=True):
    print(f"{conf}: {rating:.2f}")
```

### Head-to-Head Analysis

```python
def compare_teams(db, team1, team2):
    t1 = db.teams[team1]
    t2 = db.teams[team2]
    
    print(f"{team1} vs {team2}")
    print(f"Power Rating: {t1.power_rating:.2f} vs {t2.power_rating:.2f}")
    print(f"Ranking: #{t1.ranking} vs #{t2.ranking}")
    print(f"Tempo: {t1.tempo:.1f} vs {t2.tempo:.1f}")
    
    # Predict both ways
    home1, away1, _ = db.predict_score_with_pace(team1, team2)
    home2, away2, _ = db.predict_score_with_pace(team2, team1)
    
    print(f"At {team1}: {team1} {home1}, {team2} {away1}")
    print(f"At {team2}: {team2} {home2}, {team1} {away2}")

compare_teams(db, "Duke", "Kansas")
```

### Tournament Seeding

```python
# Get top 68 for tournament field
top_68 = db.get_top_teams(n=68)

# Create seed lines (1-16)
seeds = {}
for i in range(1, 17):
    seed_teams = top_68[(i-1)*4:i*4]
    seeds[i] = [team[1] for team in seed_teams]
    
# Display
for seed, teams in seeds.items():
    print(f"Seed {seed}: {', '.join(teams)}")
```

## Billy Walters Principles Applied

1. **Comprehensive Data**: Uses efficiency, tempo, and advanced metrics
2. **SOS Integration**: Accounts for opponent quality
3. **Recent Form**: Emphasizes current team state
4. **Pace Adjustment**: Recognizes different playing styles
5. **Mathematical Foundation**: All calculations are data-driven
6. **Ranking System**: Provides context for all teams

## Performance Metrics

The power rating correlates with:
- **Win Percentage**: Strong positive correlation
- **Tournament Success**: Higher ratings = deeper runs
- **Spread Coverage**: Better ratings = better ATS performance
- **Conference Strength**: Clusters by conference quality

## Limitations and Notes

1. **Data Quality**: Ratings are only as good as input data
2. **Sample Size**: Early season ratings less reliable
3. **Injuries**: Manual tracking required for injury impact
4. **Opponent Data**: SOS requires complete schedule data
5. **Home Court**: Default 3.5 points may vary by venue

## Extending the System

### Add Play-by-Play Data

```python
# Extend TeamData with play-by-play metrics
team.points_per_possession = 1.08
team.points_allowed_per_possession = 0.95
team.true_shooting_pct = 0.575
```

### Add Betting Lines

```python
# Track market lines vs predictions
team.ats_record = {'wins': 18, 'losses': 12, 'pushes': 1}
team.average_line_diff = 2.3  # How much market differs from rating
```

### Add Player Data

```python
# Track key players
team.roster = [
    {'name': 'Player 1', 'ppg': 18.5, 'efficiency': 125.0},
    {'name': 'Player 2', 'ppg': 14.2, 'efficiency': 118.0}
]
```

## Integration with Other Systems

### With ATS Tracker

```python
from ats_tracker import ATSTracker
from complete_team_system import CompleteDivisionIDatabase

# Load both systems
db = CompleteDivisionIDatabase()
tracker = ATSTracker()

# Make prediction
spread, favorite = db.predict_spread("Duke", "UNC")

# Track actual result
tracker.add_game("2024-02-15", "Duke", "UNC", 85, 78, -spread)
```

### With Billy Walters Predictor

```python
from billy_walters_predictor import PredictionEngine, PowerRatings
from complete_team_system import CompleteDivisionIDatabase

# Use complete database for predictions
db = CompleteDivisionIDatabase()
db.load_from_csv('all_teams.csv')
db.update_all_power_ratings()

# Convert to Billy Walters format
pr = PowerRatings()
for team_name, team in db.teams.items():
    pr.ratings[team_name] = team.power_rating

# Make predictions with full framework
engine = PredictionEngine(pr)
```

## Running the Demo

```bash
# Run complete demonstration
python complete_team_system.py
```

This will:
1. Load sample teams
2. Calculate SOS and power ratings
3. Generate rankings
4. Display top 25 teams
5. Show conference rankings
6. Display detailed team profiles
7. Make predictions with pace
8. Export to CSV and JSON

## Support for All 356 Teams

To track all 356 Division I teams:

1. **Create comprehensive CSV** with all teams
2. **Collect efficiency data** from KenPom or BartTorvik
3. **Track schedules** to populate opponents_played
4. **Update regularly** throughout season
5. **Recalculate rankings** after each game day

The system is designed to scale from sample teams to the complete Division I field.

## Tips

- **Update after each game day** for current rankings
- **Weight recent games more** for tournament predictions
- **Check SOS** before making predictions on mid-majors
- **Compare pace** when predicting high/low-scoring teams
- **Use conference rankings** for in-conference games
- **Export regularly** to track changes over time

For questions or enhancements, see the main Billy Walters framework documentation.
