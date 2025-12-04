# Expected Value (EV) Calculation Guide

## Overview
Expected Value (EV) is a fundamental concept in sports betting that represents the average profit or loss you can expect from a bet over the long term. The NBA analysis system automatically calculates EV for all overvalue opportunities.

## What is Expected Value?

Expected Value tells you whether a bet is profitable in the long run:
- **Positive EV (+EV)**: Expect to make money over time
- **Negative EV (-EV)**: Expect to lose money over time
- **Zero EV**: Break even over time

## EV Formula

```
EV = (Win Probability × Profit) - (Loss Probability × Stake)
```

### Components:
1. **Win Probability**: Derived from our prediction confidence (e.g., 73.9% = 0.739)
2. **Loss Probability**: 1 - Win Probability (e.g., 1 - 0.739 = 0.261)
3. **Profit**: Amount won if bet succeeds (for -110 odds: $100)
4. **Stake**: Amount risked on the bet (for -110 odds: $110, but normalized to $100)

## Standard Betting Odds

### -110 Odds (Most Common)
- Risk: $110
- Win: $100
- This is the standard "juice" or "vig" for spread bets

### How the System Calculates EV

For a $100 standard bet at -110 odds:
1. Profit if you win: $100
2. Loss if you lose: $100
3. Use prediction confidence as win probability

**Example Calculation:**
```
Confidence: 73.9% (0.739 win probability)
EV = (0.739 × $100) - (0.261 × $100)
EV = $73.90 - $26.10
EV = +$47.80 per $100 bet
EV% = +47.8%
```

## Interpreting EV

### Positive EV Examples

**High EV (+47.8%)**
```
Expected Value: +$47.82 per $100 bet (+47.8%)
```
- This is an excellent bet
- For every $100 wagered, expect to profit $47.82 over time
- With 73.9% confidence, this suggests strong value

**Moderate EV (+5.0%)**
```
Expected Value: +$5.00 per $100 bet (+5.0%)
```
- Still a profitable bet
- Smaller edge but still positive value
- Lower confidence or smaller spread difference

**Small EV (+1.2%)**
```
Expected Value: +$1.20 per $100 bet (+1.2%)
```
- Marginally profitable
- Very small edge
- May not be worth betting due to variance

### Negative EV (Avoid)

**Negative EV (-5.0%)**
```
Expected Value: -$5.00 per $100 bet (-5.0%)
```
- Losing bet over time
- The system filters these out - you won't see them in overvalue opportunities

## When EV is Calculated

The system calculates EV **only** when:
1. ✓ Market spread is provided
2. ✓ Overvalue is detected (≥2.5 point difference)
3. ✓ Confidence meets 70%+ threshold

If any condition is not met, EV will be `None`.

## EV and Confidence

Higher confidence generally leads to higher EV:

| Confidence | Break-Even | Typical EV Range |
|-----------|-----------|------------------|
| 70% | 52.4% | +15% to +35% |
| 75% | 52.4% | +25% to +45% |
| 80% | 52.4% | +35% to +55% |
| 85% | 52.4% | +45% to +65% |
| 90% | 52.4% | +60% to +80% |

*Break-even at -110 odds is ~52.4% (110/(110+100))*

## Real-World Example

### Brooklyn Nets @ Golden State Warriors

**Market Line:** Warriors +8.0 (home team)
**Predicted Spread:** Warriors +5.0
**Confidence:** 73.9%

**Analysis:**
- Value Difference: 3.0 points (market overvalues Warriors)
- Recommended Bet: AWAY side (Brooklyn Nets)
- Expected Value: +$47.82 per $100 (+47.8%)

**Interpretation:**
The market has the Warriors as 8-point underdogs, but our model predicts only 5 points. This 3-point discrepancy with 73.9% confidence creates significant value on betting the Nets. Over many similar bets, you'd expect to profit $47.82 for every $100 wagered.

## Using EV in Practice

### Bankroll Management
If you have a $1,000 bankroll:
- Conservative: Bet 1-2% per play ($10-$20)
- Moderate: Bet 2-3% per play ($20-$30)
- Aggressive: Bet 3-5% per play ($30-$50)

### Expected Profit Calculation
```
Expected Profit = (Number of Bets × Bet Size × EV%)

Example with 10 bets at $50 each with +25% EV:
Expected Profit = 10 × $50 × 0.25 = $125
```

### Variance Consideration
- Even with positive EV, short-term results vary
- Higher confidence = lower variance
- Need sufficient bankroll to weather losing streaks
- Positive EV bets are profitable over many trials

## Important Notes

1. **Confidence ≠ Guaranteed Win**: A 73.9% confidence means you'll win ~74% of the time over many bets, but any single bet can lose.

2. **EV is Long-Term**: Don't judge success on a single bet. Positive EV strategies require sustained betting to realize profits.

3. **Market Efficiency**: Our model may not capture all information. Real markets incorporate injury reports, lineup changes, and other factors not in basic stats.

4. **Odds Variation**: The system assumes -110 odds. Actual odds may vary, affecting true EV.

5. **Past Performance**: Predictions are based on historical performance metrics, which may not predict future results.

## Accessing EV in Code

```python
from nba_analysis import NBAAnalyzer, Game, Team

analyzer = NBAAnalyzer(min_confidence=70.0)

# Create game with market spread
game = Game(home_team, away_team, "2025-12-04", market_spread=8.5)

# Analyze game
prediction = analyzer.analyze_game(game)

# Access EV if available
if prediction.expected_value is not None:
    print(f"EV: ${prediction.expected_value:+.2f}")
    print(f"EV%: {prediction.ev_percentage:+.1f}%")
```

## Testing EV Calculations

Run EV-specific tests:
```bash
python3 test_nba_analysis.py TestExpectedValue -v
```

Tests validate:
- EV calculation with overvalue
- No EV without overvalue
- Positive EV with high confidence
- EV percentage matches dollar amount
- No EV without market spread

## Further Reading

- **Kelly Criterion**: Optimal bet sizing strategy based on EV and bankroll
- **Variance**: Understanding short-term fluctuations in results
- **Regression to the Mean**: Why extreme performances tend to normalize
- **Market Efficiency**: How betting markets process information

## Disclaimer

This tool is for educational and analytical purposes. Sports betting involves risk, and past predictions do not guarantee future results. Always bet responsibly and within your means.
