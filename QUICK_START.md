# Billy Walters Framework - Quick Start Guide

## What is This?

A complete college basketball prediction system based on Billy Walters' legendary sports betting methodology from his book "Gambler: Secrets from a Life at Risk".

## Files Overview

### Core System
- **`billy_walters_predictor.py`** - Main prediction engine with power ratings, game factors, and bankroll management
- **`advanced_analysis.py`** - Monte Carlo simulations, advanced metrics, and line movement analysis
- **`game_slate_analyzer.py`** - Analyze multiple games to find best betting opportunities
- **`customization_guide.py`** - Examples of extending and customizing the system

### Configuration
- **`requirements.txt`** - Python dependencies (numpy, pandas, scipy)
- **`.gitignore`** - Files to exclude from git
- **`README.md`** - Complete documentation

## Quick Start (3 Steps)

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
