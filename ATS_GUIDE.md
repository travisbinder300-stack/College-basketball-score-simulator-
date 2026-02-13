# ATS Record Tracking Guide - 2025-26 Season

⚠️ **CRITICAL: Use ONLY 2025-26 Season Data**

This guide is for tracking the **current 2025-26 season** only.
- **DO NOT** use data from previous seasons (2024-25, 2023-24, etc.)
- **DO NOT** mix data from multiple seasons
- **VERIFY** all game dates are from August 2025 through April 2026
- **UPDATE** data regularly throughout the current season

---

## Overview

This system provides comprehensive ATS (Against The Spread) record tracking for college basketball, with special support for importing data from **TeamRankings.com**.

## What is ATS?

**ATS (Against The Spread)** measures how teams perform relative to betting point spreads:
- **Win ATS**: Team covers the spread (beats the spread by winning or losing by less than predicted)
- **Loss ATS**: Team fails to cover (favorite wins by less than spread, underdog loses by more)
- **Push**: Game lands exactly on the spread (rare)

## Files

1. **`ats_tracker.py`** - Core ATS tracking system for manually adding game results
2. **`teamrankings_importer.py`** - Import pre-existing ATS records from TeamRankings.com
3. **`sample_teamrankings_data.csv`** - Sample data template (2025-26 season)

## Method 1: Manual Game Entry (ats_tracker.py)

Use this when you want to track games as they happen during the 2025-26 season.

### Basic Usage

```python
from ats_tracker import ATSTracker

# Initialize tracker
tracker = ATSTracker()

# Add a game result (use current season dates!)
tracker.add_game(
    date="2026-02-15",  # Current 2025-26 season date
    home_team="Duke",
    away_team="UNC",
    home_score=85,
    away_score=78,
    spread=-7.5  # Duke favored by 7.5
)

# View team stats
tracker.display_team_stats("Duke")

# View leaderboard
tracker.display_leaderboard(min_games=5, top_n=10)
```

### Understanding Spread Convention

- **Negative spread** = Home team favored
  - Example: `spread=-7.5` means home team favored by 7.5 points
  - Home team must win by 8+ to cover
  
- **Positive spread** = Away team favored
  - Example: `spread=3.5` means away team favored by 3.5 points
  - Away team must win by 4+ to cover

### Adding Multiple Games

```python
games = [
    ("2026-01-15", "Duke", "UNC", 85, 78, -7.5),
    ("2026-01-18", "Duke", "Virginia", 72, 68, -8.0),
    ("2026-01-22", "Kentucky", "Duke", 88, 84, -3.5),
]

for game_data in games:
    tracker.add_game(*game_data)
```

### Available Reports

```python
# Individual team stats
tracker.display_team_stats("Duke")

# Leaderboard
tracker.display_leaderboard(min_games=5, top_n=25)

# Head-to-head
h2h = tracker.get_head_to_head("Duke", "UNC")
print(f"Duke: {h2h['team1_wins']}-{h2h['team1_losses']}-{h2h['team1_pushes']}")

# Export all records
records = tracker.export_records()
```

## Method 2: Import from TeamRankings.com

Use this to import comprehensive ATS data from TeamRankings.com.

### From CSV File

```python
from teamrankings_importer import TeamRankingsImporter

# Initialize importer
importer = TeamRankingsImporter()

# Import from CSV
importer.import_from_csv('sample_teamrankings_data.csv')

# Display stats
importer.display_leaderboard(min_games=10, top_n=25)
importer.display_team_stats("Duke")
```

### Manual Entry

```python
importer = TeamRankingsImporter()

# Add team ATS record
importer.add_team_ats_record(
    team="Duke",
    wins=18,
    losses=12,
    pushes=1,
    home_record="10-5-0",
    away_record="8-7-1",
    favorite_record="12-8-1",
    underdog_record="6-4-0",
    conference="ACC"
)

importer.display_team_stats("Duke")
```

### Compare Teams

```python
importer.compare_teams("Duke", "UNC")
importer.compare_teams("Houston", "Purdue")
```

## How to Get Data from TeamRankings.com (2025-26 Season)

⚠️ **IMPORTANT**: When collecting data, ensure you're viewing the **current 2025-26 season** page, NOT previous seasons!

### Step 1: Visit TeamRankings.com

Go to: https://www.teamrankings.com/ncb/trends/ats_trends/

**⚠️ VERIFY**: The page shows "2025-26 Season" data at the top!

### Step 2: View ATS Statistics

TeamRankings.com provides (for current season):
- Overall ATS records (2025-26 season)
- Home/Away splits
- As favorite/underdog splits
- Conference standings
- Historical trends

**⚠️ DO NOT** use data from:
- "Previous Season" dropdown
- "Historical" or "Last Season" tabs
- Archived pages from 2024-25 or earlier

### Step 3: Manual Entry

Copy the data into Python (verify it's from 2025-26 season):

```python
importer = TeamRankingsImporter()

# Add each team's data (2025-26 season only!)
importer.add_team_ats_record(
    team="Duke",
    wins=18,
    losses=12,
    pushes=1,
    home_record="10-5-0",
    away_record="8-7-1",
    favorite_record="12-8-1",
    underdog_record="6-4-0",
    conference="ACC"
)
# Repeat for other teams...
```

### Step 4: Or Create CSV

Create a CSV file with this format (include season header):

```csv
# 2025-26 Season ATS Data from TeamRankings.com
Team,ATS_Wins,ATS_Losses,ATS_Pushes,Home_Record,Away_Record,Favorite_Record,Underdog_Record,Conference
Duke,18,12,1,10-5-0,8-7-1,12-8-1,6-4-0,ACC
UNC,16,14,0,9-6-0,7-8-0,10-9-0,6-5-0,ACC
```

Then import:

```python
importer.import_from_csv('your_data.csv')
```

**⚠️ Before importing**: Double-check the CSV header confirms "2025-26 Season"!

## Integration with Billy Walters Framework

Combine ATS records with the prediction system:

```python
from billy_walters_predictor import PowerRatings, PredictionEngine
from teamrankings_importer import TeamRankingsImporter

# Load ATS data
importer = TeamRankingsImporter()
importer.import_from_csv('sample_teamrankings_data.csv')

# Get team's ATS performance
duke_ats = importer.get_team_data("Duke")

# Use in predictions
if duke_ats.ats_win_pct > 0.55:
    print(f"Duke has strong ATS record ({duke_ats.ats_win_pct:.1%})")
    print("Consider this when evaluating betting value")
```

## Practical Examples

### Example 1: Track Current Season

```python
tracker = ATSTracker()

# Add games as season progresses
tracker.add_game("2026-11-15", "Duke", "Michigan State", 75, 72, -3.5)
tracker.add_game("2026-11-18", "Duke", "Arizona", 78, 73, -2.0)
# ... continue throughout season

# Weekly analysis
tracker.display_team_stats("Duke")
tracker.display_leaderboard(min_games=5)
```

### Example 2: Historical Analysis

```python
# Import full season data from TeamRankings
importer = TeamRankingsImporter()
importer.import_from_csv('2023_24_season_ats.csv')

# Analyze best ATS performers
importer.display_leaderboard(min_games=20, top_n=25)

# Find value opportunities
houston = importer.get_team_data("Houston")
if houston.ats_win_pct > 0.65:
    print(f"Houston covers at {houston.ats_win_pct:.1%} - look for value")
```

### Example 3: Situational Analysis

```python
importer = TeamRankingsImporter()
# Load data...

# Check home vs away performance
duke = importer.get_team_data("Duke")
home_wins, home_losses, home_pushes = importer.parse_record_string(duke.home_ats_record)
away_wins, away_losses, away_pushes = importer.parse_record_string(duke.away_ats_record)

home_pct = home_wins / (home_wins + home_losses)
away_pct = away_wins / (away_wins + away_losses)

print(f"Duke Home ATS: {home_pct:.1%}")
print(f"Duke Away ATS: {away_pct:.1%}")
print(f"Difference: {abs(home_pct - away_pct):.1%}")
```

## Key Statistics to Track

### Win Percentage
- **Above 55%**: Strong ATS performer (profitable)
- **52-55%**: Good ATS performer
- **48-52%**: Average
- **Below 48%**: Poor ATS performer

### Home vs Away
- Look for teams with large home/away splits
- Some teams perform much better ATS at home

### Favorite vs Underdog
- Some teams consistently cover as favorites
- Others perform better as underdogs

### Conference Performance
- Track which conferences have best ATS records
- Public tends to overvalue certain conferences

## Tips for Using ATS Data

1. **Minimum Sample Size**: Need at least 10-15 games for meaningful trends
2. **Recent Form**: Weight recent games more heavily
3. **Situational Context**: Consider injuries, schedule, motivation
4. **Line Shopping**: Compare your ATS expectations to market spreads
5. **Regression to Mean**: Extreme records tend to regress over time

## Output Examples

### Team Statistics
```
======================================================================
ATS STATISTICS FOR DUKE (from TeamRankings.com)
======================================================================

Overall: 18-12-1 ATS
  Win %: 60.0%

Home: 10-5-0 ATS
  Win %: 66.7%

Away: 8-7-1 ATS
  Win %: 53.3%

As Favorite: 12-8-1 ATS
  Win %: 60.0%

As Underdog: 6-4-0 ATS
  Win %: 60.0%
```

### Leaderboard
```
================================================================================
ATS LEADERBOARD (from TeamRankings.com) - Minimum 10 games
================================================================================
Rank  Team                          Record            Win %     Conference      
--------------------------------------------------------------------------------
1     Houston                       21-8-1            72.4%     Big 12          
2     Purdue                        20-9-1            69.0%     Big Ten         
3     Gonzaga                       20-10-0           66.7%     WCC             
```

## Resources

- **TeamRankings.com**: https://www.teamrankings.com/ncb/trends/ats_trends/
- **Billy Walters Framework**: See `billy_walters_predictor.py`
- **Sample Data**: See `sample_teamrankings_data.csv`

## Combining with Predictions

```python
from billy_walters_predictor import PredictionEngine, PowerRatings, TeamStats
from teamrankings_importer import TeamRankingsImporter

# Load ATS data
ats_importer = TeamRankingsImporter()
ats_importer.import_from_csv('sample_teamrankings_data.csv')

# Make prediction
pr = PowerRatings()
# ... set up power ratings ...

engine = PredictionEngine(pr)
predicted_spread, favorite = engine.predict_spread(
    home_team="Duke",
    away_team="UNC",
    is_rivalry=True
)

# Check ATS history
duke_ats = ats_importer.get_team_data("Duke")
unc_ats = ats_importer.get_team_data("UNC")

print(f"Predicted: {favorite} -{predicted_spread}")
print(f"Duke ATS record: {duke_ats.ats_win_pct:.1%}")
print(f"UNC ATS record: {unc_ats.ats_win_pct:.1%}")
```

## Notes

- ATS records are updated throughout the season
- TeamRankings.com provides real-time updates
- Use this data as one factor in your analysis
- Combine with power ratings and situational factors
- Remember: past ATS performance doesn't guarantee future results
