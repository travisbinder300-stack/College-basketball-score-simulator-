# ATS Performance vs Ranked Opponents Guide

## Overview

This guide explains how to track and analyze team performance **Against The Spread (ATS) when playing against ranked opponents** in college basketball.

⚠️ **IMPORTANT: Use ONLY 2025-26 season data. Do not mix with previous seasons!**

## Why Track ATS vs Ranked Opponents?

Understanding how teams perform ATS against ranked opponents reveals:

1. **Teams that rise to competition** - Perform better vs top teams
2. **Teams that struggle vs elite opponents** - Underperform vs ranked teams
3. **Situational betting edges** - Value opportunities in specific matchups
4. **Motivation and quality factors** - How teams respond to challenges

## Data Source

**TeamRankings.com - ATS vs Ranked Trends:**
```
https://www.teamrankings.com/ncb/trends/ats_trends/?sc=vs_ranked
```

This page shows each team's ATS record specifically in games against ranked opponents.

## How to Collect Data

### Step 1: Visit TeamRankings.com

1. Go to: https://www.teamrankings.com/ncb/trends/ats_trends/?sc=vs_ranked
2. **Verify the season shows "2025-26"** at the top of the page
3. This page displays ATS records vs ranked opponents

### Step 2: Collect Team Data

For each team you want to analyze, collect:

**From Main ATS Page** (https://www.teamrankings.com/ncb/trends/ats_trends/):
- Overall ATS record (W-L-P)
- Conference

**From vs Ranked Page** (https://www.teamrankings.com/ncb/trends/ats_trends/?sc=vs_ranked):
- ATS record vs ranked opponents (W-L-P)

### Step 3: Create CSV File

Format your data as:
```csv
Team,Conference,Overall_W,Overall_L,Overall_P,VsRanked_W,VsRanked_L,VsRanked_P
Duke,ACC,18,12,0,9,3,0
Houston,Big 12,21,8,1,7,3,0
```

**Column Descriptions:**
- `Team` - Team name
- `Conference` - Team's conference
- `Overall_W` - Total ATS wins (all games)
- `Overall_L` - Total ATS losses (all games)
- `Overall_P` - Total ATS pushes (all games)
- `VsRanked_W` - ATS wins vs ranked opponents
- `VsRanked_L` - ATS losses vs ranked opponents  
- `VsRanked_P` - ATS pushes vs ranked opponents

## Using the Analysis Tool

### Basic Usage

```python
from ats_vs_ranked_analysis import ATSvsRankedAnalyzer

# Create analyzer
analyzer = ATSvsRankedAnalyzer()

# Load data from CSV
analyzer.load_from_csv('sample_ats_vs_ranked_data.csv')

# Display comprehensive report
analyzer.display_comprehensive_report()
```

### Get Specific Insights

```python
# Best performers vs ranked opponents
best_vs_ranked = analyzer.get_best_vs_ranked(min_games=5)

# Teams that rise to competition
risers = analyzer.get_teams_that_rise_vs_ranked(min_gap=10.0)

# Teams that struggle vs ranked
strugglers = analyzer.get_teams_that_struggle_vs_ranked(min_gap=-10.0)

# Analyze specific team
analyzer.display_team_analysis("Duke")
```

## Understanding the Metrics

### Performance Gap

**Performance Gap = ATS% vs Ranked - ATS% vs Unranked**

- **+15% or higher**: Team significantly better vs ranked opponents (RISES to competition)
- **-15% or lower**: Team significantly worse vs ranked opponents (STRUGGLES vs elite teams)
- **-10% to +10%**: Consistent performer regardless of opponent quality

### Example Interpretations

**Duke: +25.0% gap (75% vs ranked, 50% vs unranked)**
- Rises to competition
- Bet Duke when they face ranked opponents
- They perform much better against top competition

**Marquette: -25.8% gap (33% vs ranked, 59% vs unranked)**
- Struggles vs ranked teams
- Fade Marquette when they face ranked opponents
- They perform much worse against elite competition

## Betting Strategies

### When to Back a Team

✅ **Back these teams when they face ranked opponents:**

1. **Strong vs Ranked Record (70%+ ATS)**
   - Proven performers vs top competition
   - Consistent covers against ranked teams

2. **Rise to Competition (+15% gap)**
   - Teams that elevate their game
   - Especially valuable as underdogs

3. **Underdog with Strong vs Ranked**
   - Best value opportunity
   - Public often fades underdogs, but these teams prove they can compete

### When to Fade a Team

⚠️ **Avoid or fade these teams when they face ranked opponents:**

1. **Weak vs Ranked Record (<40% ATS)**
   - Struggle to cover vs top teams
   - Pattern of underperformance

2. **Big Negative Gap (-15% or worse)**
   - Significantly worse vs ranked opponents
   - Shrink from competition

3. **Favorite with Poor vs Ranked Record**
   - Public bets the name, but they don't perform
   - Often inflated lines

### Best Betting Situations

**🎯 HIGHEST VALUE:**
- Underdog with strong vs ranked record (+70%) facing a ranked opponent
- Team with +15% gap facing ranked opponent (they rise to competition)

**⚠️ BIGGEST TRAPS:**
- Favorite with poor vs ranked record (<40%) facing ranked opponent  
- Team with -15% gap facing ranked opponent (they struggle vs elite teams)

## Real-World Examples

### Example 1: Duke (Rises to Competition)

**Overall ATS:** 18-12 (60.0%)
**vs Ranked:** 9-3 (75.0%)  
**vs Unranked:** 9-9 (50.0%)
**Gap:** +25.0%

**Analysis:**
- Duke significantly better vs ranked opponents
- They rise to elite competition
- **Betting Action:** Back Duke when they face ranked teams, especially as underdog

### Example 2: Marquette (Struggles vs Ranked)

**Overall ATS:** 13-9 (59.1%)
**vs Ranked:** 2-4 (33.3%)
**vs Unranked:** 11-5 (68.8%)
**Gap:** -35.5%

**Analysis:**
- Marquette much worse vs ranked opponents
- They struggle against elite competition
- **Betting Action:** Fade Marquette when they face ranked teams, especially as favorite

## Integration with Other Systems

### With Billy Walters Framework

```python
from ats_vs_ranked_analysis import ATSvsRankedAnalyzer
from billy_walters_predictor import BillyWaltersPredictor

# Load ATS data
ats_analyzer = ATSvsRankedAnalyzer()
ats_analyzer.load_from_csv('ats_vs_ranked_data.csv')

# Get team vs ranked performance
team_vs_ranked = ats_analyzer.get_team_analysis("Duke")

# Factor into prediction
if opponent_is_ranked and team_vs_ranked:
    if team_vs_ranked.ranked_performance_gap > 15:
        print("⬆️ Team rises vs ranked - positive factor")
    elif team_vs_ranked.ranked_performance_gap < -15:
        print("⬇️ Team struggles vs ranked - negative factor")
```

### With Complete Team System

```python
from complete_team_system import CompleteDivisionIDatabase
from ats_vs_ranked_analysis import ATSvsRankedAnalyzer

# Load both systems
db = CompleteDivisionIDatabase()
ats_analyzer = ATSvsRankedAnalyzer()

# Make prediction considering vs ranked performance
home_team_ranked = db.teams["Duke"].ranking <= 25
away_team_ranked = db.teams["UNC"].ranking <= 25

if away_team_ranked:
    # Home team faces ranked opponent
    home_vs_ranked = ats_analyzer.get_team_analysis(home_team)
    # Adjust prediction based on vs ranked performance
```

## Common Mistakes to Avoid

❌ **Don't:**
1. Use small sample sizes (need at least 5 games vs ranked)
2. Mix data from multiple seasons
3. Ignore the context (home/away, injury situations)
4. Assume past performance guarantees future results
5. Bet every ranked matchup - be selective

✅ **Do:**
1. Verify minimum games vs ranked (5+)
2. Use current 2025-26 season data only
3. Consider other factors (home court, injuries, motivation)
4. Look for significant performance gaps (+/- 15%)
5. Focus on highest value situations

## Data Update Schedule

**Update Frequency:**
- After each game day involving ranked opponents
- Check TeamRankings.com daily during season
- Rankings change weekly, affecting which games count

**Season Coverage:**
- Full 2025-26 season (November 2025 - March 2026)
- Conference tournaments
- NCAA Tournament (all opponents ranked for many teams)

## Advanced Analysis

### Conference Trends

Some conferences see more ranked matchups:
- **Big Ten, Big 12, SEC** - Multiple ranked teams, many vs ranked games
- **Big East, ACC** - Several ranked teams
- **Mid-majors** - Fewer ranked matchups, smaller sample sizes

### Time of Season

**Early Season (Nov-Dec):**
- Rankings less established
- Fewer data points
- Be cautious with early trends

**Conference Play (Jan-Feb):**
- Rankings more settled
- More vs ranked games for top conferences
- Best data for analysis

**Late Season/Tournaments (March):**
- Most reliable data
- Pressure situations
- Tournament performance vs ranked teams

## Summary

**Key Takeaways:**

1. **Track ATS performance vs ranked opponents separately**
2. **Look for +15% gaps (rise to competition) or -15% gaps (struggle vs ranked)**
3. **Best value: Underdogs with strong vs ranked records**
4. **Biggest traps: Favorites with poor vs ranked records**
5. **Always use current 2025-26 season data only**

**Data Source:**
https://www.teamrankings.com/ncb/trends/ats_trends/?sc=vs_ranked

**Remember:** This is one factor in a comprehensive analysis. Combine with power ratings, efficiency metrics, home court advantage, and other situational factors for best results.
