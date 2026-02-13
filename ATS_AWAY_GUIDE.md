# ATS Away Team Performance Analysis Guide

## Overview

This guide explains how to analyze team performance Against The Spread (ATS) specifically for **away games** (road games). Understanding how teams perform on the road vs at home is crucial for betting success.

⚠️ **CRITICAL**: Use ONLY current 2025-26 season data!

## Why Track Away Team ATS?

### Key Concepts:

1. **Road Performance is Harder**
   - Teams face hostile environments
   - Travel fatigue factor
   - Less comfortable surroundings
   - Referee bias toward home team

2. **Market Inefficiency**
   - Public often overvalues popular road teams
   - Betting lines don't always account for road struggles
   - Value in fading home-dependent teams

3. **Situational Advantage**
   - Identify "road warriors" who excel away
   - Find home-dependent teams to fade
   - Better understand team character

## Data Source

### TeamRankings.com - Away Team ATS

**URL**: https://www.teamrankings.com/ncb/trends/ats_trends/?sc=is_away

**What It Shows**:
- ATS records specifically for away games
- Cover percentage on the road
- Margin of victory away
- ATS +/- (how much teams beat or miss spread)

### How to Collect Data:

1. Go to: https://www.teamrankings.com/ncb/trends/ats_trends/
2. Look for filter/situation dropdown
3. Select "As Away Team" or similar option
4. Ensure you're viewing **2025-26 season** data
5. Export or manually collect the data

## Key Metrics

### Cover Percentage (Away)
- **85%+**: Elite road warriors
- **70-84%**: Strong away performers
- **50-69%**: Average to above average
- **35-49%**: Below average away
- **<35%**: Home-dependent teams

### ATS +/- (Away)
- **Positive**: Consistently beating the spread on road
- **Near Zero**: Meeting expectations
- **Negative**: Failing to cover on road

## Using the Analysis Tool

### Load and Analyze

```python
from ats_away_analysis import ATSAwayAnalyzer

# Create analyzer
analyzer = ATSAwayAnalyzer()

# Load data
analyzer.load_from_csv('ats_away_team_2025_26.csv')

# Display comprehensive report
analyzer.display_comprehensive_report(top_n=10)
```

### Get Specific Insights

```python
# Best road teams (75%+ cover rate)
road_warriors = analyzer.get_road_warriors(min_cover_pct=75.0)

# Worst road teams (<35% cover rate)
strugglers = analyzer.get_home_dependent_teams(max_cover_pct=35.0)

# Analyze specific team
analyzer.display_team_analysis("Portland St")
```

### Run Complete Analysis

```bash
python ats_away_analysis.py
```

## 2025-26 Season Findings

### Top Road Warriors (85%+ Away ATS):
1. **Portland St**: 11-1-0 (91.7%) - Elite road warrior
2. **Georgia Tech**: 6-1-0 (85.7%) - Excellent away
3. **Clemson**: 6-1-0 (85.7%) - Strong on road
4. **San Diego St**: 6-1-0 (85.7%) - Road tested
5. **Utah**: 6-1-0 (85.7%) - Away excellence
6. **Texas A&M**: 6-1-0 (85.7%) - Solid road team
7. **Nebraska**: 6-1-0 (85.7%) - Tough away
8. **Florida**: 6-1-0 (85.7%) - Road warriors

### Home-Dependent Teams (<35% Away ATS):
1. **McNeese**: 1-8-1 (11.1%) - Worst road team
2. **Manhattan**: 2-9-1 (18.2%) - Struggles away

## Betting Strategies

### ✓ BACK ON THE ROAD:

1. **Road Warriors (75%+ away ATS)**
   - Proven performance in hostile environments
   - Portland St, Georgia Tech, Clemson
   - Value when public fades them on road

2. **Positive ATS +/- Away**
   - Consistently beating spreads on road
   - Look for +5.0 or higher ATS +/-
   - Shows they exceed expectations

3. **Battle-Tested Teams**
   - Teams from tough conferences
   - Experience winning on the road
   - Mental toughness advantage

### ⚠️ FADE ON THE ROAD:

1. **Home-Dependent Teams (<35% away ATS)**
   - McNeese, Manhattan
   - Rely too much on home court
   - Vulnerable in away spots

2. **Negative ATS +/- Away**
   - Failing to cover on road
   - Look for -5.0 or worse
   - Public may overvalue them

3. **Popular Teams with Poor Road Records**
   - Brand names that don't travel well
   - Public bets them regardless
   - Line inflation creates value fading

### 💡 ADVANCED STRATEGIES:

1. **Road Warrior as Underdog**
   - Elite road team getting points
   - Double advantage
   - High value opportunity

2. **Home-Dependent Team as Road Favorite**
   - Overvalued due to name/ranking
   - Poor away ATS history
   - Fade opportunity

3. **Conference Road Games**
   - Familiar opponents
   - Less travel fatigue
   - Check conference-only road ATS

## Integration with Other Systems

### With Billy Walters Framework:

```python
from ats_away_analysis import ATSAwayAnalyzer
from billy_walters_predictor import BillyWaltersPredictor

# Check if away team is a road warrior
away_analyzer = ATSAwayAnalyzer()
away_analyzer.load_from_csv('ats_away_team_2025_26.csv')

away_team = "Portland St"
away_record = away_analyzer.get_team_analysis(away_team)

if away_record and away_record.cover_pct > 75.0:
    # Road warrior - add confidence to away team
    print(f"{away_team} is a road warrior ({away_record.cover_pct:.1f}% away ATS)")
    # Adjust prediction accordingly
```

### With Manhattan vs Niagara Prediction:

```python
# Manhattan at Niagara
# Manhattan: 2-9-1 away (18.2%) - Poor road team
# Niagara: 6-8-0 away (42.9%) - Below average away

# Since Manhattan is road team:
manhattan_away = analyzer.get_team_analysis("Manhattan")
if manhattan_away.cover_pct < 35.0:
    print("⚠️ Manhattan is home-dependent - struggles on road")
    print("Additional reason to back Niagara at home")
```

## CSV File Format

```csv
# 2025-26 Season - Away Team ATS Performance
# Source: https://www.teamrankings.com/ncb/trends/ats_trends/?sc=is_away
Team,ATS_Record,Wins,Losses,Pushes,Cover_Pct,MOV,ATS_Plus_Minus
Portland St,11-1-0,11,1,0,91.7,0.5,2.9
Georgia Tech,6-1-0,6,1,0,85.7,-7.3,7.4
Manhattan,2-9-1,2,9,1,18.2,-17.3,-7.3
```

## Common Mistakes to Avoid

❌ **DON'T:**
- Use previous season's away ATS data
- Ignore small sample sizes (need 5+ games)
- Blindly back all road warriors
- Forget to check opponent's home ATS record
- Mix home and away ATS data

✅ **DO:**
- Use current 2025-26 season data only
- Require minimum games for statistical significance
- Consider matchup context (opponent quality)
- Cross-reference with home team's home ATS
- Update data regularly throughout season

## Update Schedule

- **Daily**: After each game day
- **Weekly**: Review and update season trends
- **Monthly**: Analyze pattern changes

## Real-World Example

### Portland St (Road Warrior)

**Away ATS**: 11-1-0 (91.7%)
- ATS +/-: +2.9 points
- MOV: +0.5 points
- 🏆 Elite road warrior

**Betting Application**:
- Back Portland St on the road
- Especially valuable as underdog
- Proven ability to win/cover away
- Mental toughness in hostile environments

### Manhattan (Home-Dependent)

**Away ATS**: 2-9-1 (18.2%)
- ATS +/-: -7.3 points
- MOV: -17.3 points
- ❌ Poor road team

**Betting Application**:
- Fade Manhattan on the road
- Especially when favored away
- Lacks road toughness
- Better opportunities exist

## Conclusion

Away team ATS analysis is crucial for identifying:
- Road warriors who excel in hostile environments
- Home-dependent teams that struggle away
- Market inefficiencies in road game betting
- Situational edges based on location

Always use current 2025-26 season data and combine with other analysis tools for best results.

**Remember**: Road success is harder to achieve, which makes road warriors more valuable for betting purposes.
