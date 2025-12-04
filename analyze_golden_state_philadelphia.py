#!/usr/bin/env python3
"""
Analyze specific NBA game: Golden State Warriors vs Philadelphia 76ers
Market Line: Philadelphia -4.0 (home), Total: 123.5
"""

from nba_analysis import Team, Game, NBAAnalyzer
from datetime import datetime


def main():
    """Analyze Golden State vs Philadelphia game with provided market data"""
    
    print("=" * 80)
    print("SPECIFIC GAME ANALYSIS: GOLDEN STATE WARRIORS VS PHILADELPHIA 76ERS")
    print("Market Data: Philadelphia -4.0 (home), Total: 123.5")
    print("=" * 80)
    print()
    
    # Create teams with realistic 2024-25 season statistics
    # Golden State Warriors - Strong team with elite offense
    warriors = Team(
        name="Golden State Warriors",
        offensive_rating=116.8,  # Strong offense
        defensive_rating=112.3,  # Average defense
        pace=103.5,
        win_percentage=0.580,    # Good team
        recent_form=0.60         # Moderate recent performance
    )
    
    # Philadelphia 76ers - Strong team with good all-around play
    sixers = Team(
        name="Philadelphia 76ers",
        offensive_rating=117.5,  # Strong offense
        defensive_rating=110.8,  # Good defense
        pace=100.8,
        win_percentage=0.650,    # Very good team
        recent_form=0.75         # Strong recent performance
    )
    
    # Create game with market spread (-4.0 means Philadelphia favored by 4.0)
    # Convention: positive spread = home favored, so Philadelphia at home = +4.0
    today = datetime.now().strftime("%Y-%m-%d")
    game = Game(
        home_team=sixers,
        away_team=warriors,
        date=today,
        market_spread=4.0  # Philadelphia favored by 4.0
    )
    
    # Create analyzer with 70% minimum confidence
    analyzer = NBAAnalyzer(min_confidence=70.0)
    
    # Analyze the game
    prediction = analyzer.analyze_game(game)
    
    # Display analysis
    print("PREDICTION ANALYSIS:")
    print("=" * 80)
    print(prediction)
    
    # Check if this game meets confidence threshold
    meets_threshold = (prediction.spread_confidence >= 70.0 and 
                      prediction.total_confidence >= 70.0)
    
    print("\nCONFIDENCE ASSESSMENT:")
    print("=" * 80)
    if meets_threshold:
        print("✓ This game MEETS the 70% confidence threshold")
        print(f"  - Spread Confidence: {prediction.spread_confidence:.1f}%")
        print(f"  - Total Confidence: {prediction.total_confidence:.1f}%")
    else:
        print("✗ This game DOES NOT meet the 70% confidence threshold")
        print(f"  - Spread Confidence: {prediction.spread_confidence:.1f}%")
        print(f"  - Total Confidence: {prediction.total_confidence:.1f}%")
    
    # Detailed comparison with market
    print("\nMARKET COMPARISON:")
    print("=" * 80)
    print(f"Market Spread:     Philadelphia -{game.market_spread}")
    print(f"Predicted Spread:  Philadelphia -{prediction.spread:.1f}")
    print(f"Spread Difference: {abs(prediction.spread - game.market_spread):.1f} points")
    print()
    print(f"Market Total:      {123.5:.1f} points")
    print(f"Predicted Total:   {prediction.total:.1f} points")
    print(f"Total Difference:  {abs(prediction.total - 123.5):.1f} points")
    
    # Note about unusual total
    print()
    print("⚠️  NOTE: Market total of 123.5 is extremely unusual for NBA")
    print("   Typical NBA totals range from 200-240 points")
    print("   This may be a data entry error or special circumstances game")
    
    # Overvalue analysis
    if prediction.is_overvalue:
        print("\n🔥 OVERVALUE OPPORTUNITY DETECTED!")
        print("=" * 80)
        print(f"Value Difference: {abs(prediction.spread_value):.1f} points")
        print(f"Recommended Bet: {prediction.value_side.upper()} side")
        if prediction.value_side == "home":
            print(f"  → Bet on Philadelphia 76ers (market undervalues them)")
        else:
            print(f"  → Bet on Golden State Warriors (market overvalues Philadelphia)")
        
        # Display EV if available
        if prediction.expected_value is not None:
            print(f"\nExpected Value (EV):")
            print(f"  Dollar EV: ${prediction.expected_value:+.2f} per $100 bet")
            print(f"  EV Percentage: {prediction.ev_percentage:+.1f}%")
            print(f"  Interpretation: Expected profit of ${abs(prediction.expected_value):.2f} per $100 wagered")
    else:
        print("\n⚠️  NO SIGNIFICANT OVERVALUE DETECTED")
        print("=" * 80)
        if prediction.spread_value is not None:
            print(f"Spread difference ({abs(prediction.spread_value):.1f} pts) is below 2.5 point threshold")
            if abs(prediction.spread_value) > 0:
                if prediction.spread_value > 0:
                    print(f"Slight value on Philadelphia 76ers (+{prediction.spread_value:.1f} pts)")
                else:
                    print(f"Slight value on Golden State Warriors ({prediction.spread_value:.1f} pts)")
    
    # Total points analysis
    print("\nTOTAL POINTS ANALYSIS:")
    print("=" * 80)
    total_diff = prediction.total - 123.5
    if abs(total_diff) >= 3.0:
        if total_diff > 0:
            print(f"📈 OVER {123.5} is STRONGLY recommended ({prediction.total:.1f} predicted)")
            print(f"   Difference: +{total_diff:.1f} points above market")
            print(f"   This represents a MASSIVE discrepancy - market total appears incorrect")
        else:
            print(f"📉 UNDER {123.5} is recommended ({prediction.total:.1f} predicted)")
            print(f"   Difference: {total_diff:.1f} points below market")
    else:
        print(f"⚖️  Total prediction ({prediction.total:.1f}) is close to market (123.5)")
        print(f"   Difference: {total_diff:+.1f} points - no strong recommendation")
    
    # Summary and recommendation
    print("\n" + "=" * 80)
    print("BETTING RECOMMENDATION SUMMARY")
    print("=" * 80)
    
    recommendations = []
    
    if meets_threshold and prediction.is_overvalue:
        if prediction.value_side == "away":
            recommendations.append(f"✓ STRONG: Bet Golden State +4.0 (overvalue detected)")
            if prediction.expected_value is not None:
                recommendations.append(f"  EV: ${prediction.expected_value:+.2f} per $100 ({prediction.ev_percentage:+.1f}%)")
        else:
            recommendations.append(f"✓ STRONG: Bet Philadelphia -4.0 (overvalue detected)")
            if prediction.expected_value is not None:
                recommendations.append(f"  EV: ${prediction.expected_value:+.2f} per $100 ({prediction.ev_percentage:+.1f}%)")
    elif meets_threshold:
        recommendations.append(f"✓ Spread: Our prediction ({prediction.spread:.1f}) is close to market")
    
    if meets_threshold:
        if abs(total_diff) >= 3.0:
            if total_diff > 0:
                recommendations.append(f"✓ STRONG: Bet OVER {123.5} - MASSIVE VALUE")
                recommendations.append(f"  Predicted: {prediction.total:.1f} vs Market: {123.5:.1f} ({total_diff:+.1f} pts)")
            else:
                recommendations.append(f"✓ STRONG: Bet UNDER {123.5}")
        else:
            recommendations.append(f"✓ Total: Our prediction ({prediction.total:.1f}) is close to market")
    else:
        recommendations.append("⚠️  Spread confidence too low for strong recommendations")
        recommendations.append(f"   However, total shows extreme discrepancy ({total_diff:+.1f} pts)")
    
    for rec in recommendations:
        print(rec)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
