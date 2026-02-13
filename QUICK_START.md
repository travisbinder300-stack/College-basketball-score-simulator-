# Billy Walters Framework - Quick Start Guide

## ⚠️ IMPORTANT: Use Current 2025-26 Season Data

**All data used in this system should be from the CURRENT 2025-26 season.** Do not use outdated data from previous seasons. Update team statistics, ATS records, and all metrics regularly throughout the season.

**⚠️ ATS RECORDS**: When using ATS tracking tools, ensure all data is from 2025-26 season. The system displays warnings when importing data to verify season currency.

## What is This?

A complete college basketball prediction system based on Billy Walters' legendary sports betting methodology from his book "Gambler: Secrets from a Life at Risk".

**NEW:** Now includes complete 356-team database with all offensive and defensive statistics!

**LATEST:** Manhattan vs Niagara game prediction - Full MAAC matchup analysis!

## Files Overview

### Game Predictions
- **`manhattan_vs_niagara_prediction.py`** - Complete Manhattan vs Niagara analysis (NEW!)

### Core System
- **`billy_walters_predictor.py`** - Main prediction engine with power ratings, game factors, and bankroll management
- **`advanced_analysis.py`** - Monte Carlo simulations, advanced metrics, and line movement analysis
- **`game_slate_analyzer.py`** - Analyze multiple games to find best betting opportunities
- **`customization_guide.py`** - Examples of extending and customizing the system

### Complete Team System
- **`complete_team_system.py`** - Track all 356 Division I teams with complete stats
- **`teams_data_template.csv`** - CSV template for loading team data
- **`COMPLETE_SYSTEM_GUIDE.md`** - Full documentation for 356-team system
- **`team_rankings.csv`** - Generated rankings export
- **`team_database.json`** - Complete database export

### ATS Tracking
- **`ats_tracker.py`** - Manual ATS record tracking system
- **`teamrankings_importer.py`** - Import ATS data from TeamRankings.com
- **`sample_teamrankings_data.csv`** - Sample ATS data template
- **`ats_demo.py`** - Complete demonstration of ATS tracking
- **`best_ats_performers.py`** - Identify which teams cover spread most
- **`major_vs_nonmajor_analysis.py`** - Why major teams cover more
- **`ATS_GUIDE.md`** - Comprehensive ATS tracking guide

### Configuration
- **`requirements.txt`** - Python dependencies (numpy, pandas, scipy)
- **`.gitignore`** - Files to exclude from git
- **`README.md`** - Complete documentation

## Quick Start (4 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Example Prediction
```bash
python billy_walters_predictor.py
```

### 3. Analyze a Game Slate
```bash
python game_slate_analyzer.py
```

### 4. Track All 356 Teams (NEW!)
```bash
# Complete team system with SOS and rankings
python complete_team_system.py

# Track ATS records
python ats_demo.py

# Find best ATS performers (which teams cover spread most)
python best_ats_performers.py

# Analyze why major teams cover more than mid-majors
python major_vs_nonmajor_analysis.py
```

## Core Concepts

### Power Ratings
Numeric values representing team strength, calculated from:
- Offensive/defensive efficiency (points per 100 possessions)
- Strength of schedule
- Recent form (last 5 games)
- Injury impact

### Game Factors
Situational adjustments including:
- Home court advantage (+3.5 points typical)
- Travel fatigue
- Rivalry/revenge game motivation
- Conference game importance

### Edge Calculation
Comparing your model's prediction vs market line:
- 1 point difference ≈ 2.5% win probability edge
- Minimum 3% edge required to bet (Walters principle)

### Bankroll Management
Conservative approach:
- Risk only 1-3% per bet
- Scale bet size by edge and confidence
- Never chase losses
- Total daily action < 10% of bankroll

### ATS (Against The Spread) - NEW!
Track how teams perform vs betting spreads:
- **Win ATS**: Team covers the spread
- **Loss ATS**: Team fails to cover
- **Above 55% ATS**: Strong performer (profitable)
- Track by home/away and favorite/underdog
- Import from TeamRankings.com for historical data

**See [ATS_GUIDE.md](ATS_GUIDE.md) for complete ATS documentation.**

### Complete Team System (NEW!)
Track all 356 Division I teams with:
- **All Offensive Stats**: Points, FG%, 3P%, FT%, assists, rebounds, turnovers, steals, blocks
- **All Defensive Stats**: Opponent scoring, defense, rebounding, forcing turnovers
- **Advanced Metrics**: Efficiency, Four Factors, tempo, SOS
- **Rankings**: National and conference rankings
- **Pace-Adjusted Predictions**: Score predictions with tempo factors

**See [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md) for full documentation.**

## Billy Walters' 7 Key Principles

1. **Only bet with clear mathematical edge (>3%)**
2. **Strict bankroll management - never risk more than 1-3% per bet**
3. **Build detailed power ratings from comprehensive data**
4. **Account for all game factors: travel, rest, motivation, injuries**
5. **Line shop across multiple sportsbooks for best value**
6. **Don't chase losses - be disciplined and patient**
7. **Exploit market inefficiencies, don't follow public trends**

## Example Output

```
GAME PREDICTION
----------------------------------------------------------------------
Matchup: Duke vs UNC (at Duke)
Predicted Spread: Duke -9.6
Market Line: Duke -5.5

RECOMMENDATION
----------------------------------------------------------------------
Should Bet: True
Bet Side: Duke -5.5
Bet Size: $100.00
Edge: 10.2%

Reasoning: Edge of 10.2% detected. Model disagrees with market by 4.1 points.
```

## Next Steps

### For Learning
- Read through `billy_walters_predictor.py` to understand the core logic
- Run `advanced_analysis.py` to see Monte Carlo simulations
- Study `customization_guide.py` for extension examples

### For Production Use
1. Integrate real data sources (KenPom, The Odds API, etc.)
2. Back-test on historical data to validate model
3. Track all bets and analyze performance
4. Refine parameters based on results
5. Start with small stakes while building confidence

### For Customization
- Extend `PowerRatings` class for custom factors
- Modify `GameFactors` for specific situations (tournaments, etc.)
- Adjust `BankrollManagement` for your risk tolerance
- Add new metrics to `AdvancedMetrics`

## Important Warnings

⚠️ **This is for educational purposes only**
- Sports betting involves significant risk
- Only bet what you can afford to lose
- Gambling may not be legal in your jurisdiction
- Past performance doesn't guarantee future results
- This is not financial or betting advice

✓ **If you do bet:**
- Only use licensed, regulated sportsbooks
- Follow all local laws and regulations
- Keep detailed records for taxes
- Set strict loss limits
- Take breaks if it becomes stressful

## Additional Resources

### Learn More About Billy Walters
- Book: "Gambler: Secrets from a Life at Risk" by Billy Walters
- Focus on the "Master Class" chapters for betting strategy
- Study his Computer Group methodology

### Data Sources
- **KenPom.com** - Premier college basketball analytics
- **BartTorvik.com** - Advanced metrics and predictions
- **The Odds API** - Market lines from multiple sportsbooks
- **ESPN/CBS Sports** - Injury reports and news

### Further Reading
- "The Signal and the Noise" by Nate Silver
- "Thinking in Bets" by Annie Duke
- "Sharp Sports Betting" by Stanford Wong

## Support

This system implements the framework described in Billy Walters' book. For questions about the methodology, refer to the book's "Master Class" chapters.

For technical issues or enhancements, see the customization guide or extend the classes as needed.

## License

See LICENSE file for details.

---

**Remember:** Billy Walters' success came from discipline, patience, and mathematical rigor - not luck. Follow the principles, track your results, and make data-driven decisions.
