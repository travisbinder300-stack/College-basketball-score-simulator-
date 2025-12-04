#!/usr/bin/env python3
"""
Analyze specific NBA game: Boston Celtics vs Washington Wizards
Market Line: Boston -8.5, Total: 228.5
"""

from nba_analysis import Team, Game, NBAAnalyzer
from datetime import datetime


def main():
    """Analyze Boston vs Washington game with provided market data"""
    
    print("=" * 80)
    print("SPECIFIC GAME ANALYSIS: BOSTON CELTICS VS WASHINGTON WIZARDS")
    print("Market Data: Boston -8.5 (home), Total: 228.5")
    print("=" * 80)
    print()
    
    # Create teams with realistic 2024-25 season statistics
    # Boston Celtics - Strong contender with high offensive and defensive ratings
    celtics = Team(
        name="Boston Celtics",
        offensive_rating=120.5,  # Elite offense
        defensive_rating=109.8,  # Strong defense
        pace=99.2,
        win_percentage=0.720,    # Strong team
        recent_form=0.80         # Good recent performance
    )
    
    # Washington Wizards - Rebuilding team with weaker statistics
    wizards = Team(
        name="Washington Wizards",
        offensive_rating=110.2,  # Below average offense
        defensive_rating=118.5,  # Weak defense
        pace=100.5,
        win_percentage=0.250,    # Struggling team
        recent_form=0.30         # Poor recent performance
    )
    
    # Create game with market spread (-8.5 means Boston favored by 8.5)
    # Convention: positive spread = home favored, so Boston at home = +8.5
    today = datetime.now().strftime("%Y-%m-%d")
    game = Game(
        home_team=celtics,
        away_team=wizards,
        date=today,
        market_spread=8.5  # Boston favored by 8.5
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
    print(f"Market Spread:     Boston -{game.market_spread}")
    print(f"Predicted Spread:  Boston -{prediction.spread:.1f}")
    print(f"Spread Difference: {abs(prediction.spread - game.market_spread):.1f} points")
    print()
    print(f"Market Total:      {228.5:.1f} points")
    print(f"Predicted Total:   {prediction.total:.1f} points")
    print(f"Total Difference:  {abs(prediction.total - 228.5):.1f} points")
    
    # Overvalue analysis
    if prediction.is_overvalue:
        print("\n🔥 OVERVALUE OPPORTUNITY DETECTED!")
        print("=" * 80)
        print(f"Value Difference: {abs(prediction.spread_value):.1f} points")
        print(f"Recommended Bet: {prediction.value_side.upper()} side")
        if prediction.value_side == "home":
            print(f"  → Bet on Boston Celtics (market undervalues them)")
        else:
            print(f"  → Bet on Washington Wizards (market overvalues Boston)")
    else:
        print("\n⚠️  NO SIGNIFICANT OVERVALUE DETECTED")
        print("=" * 80)
        if prediction.spread_value is not None:
            print(f"Spread difference ({abs(prediction.spread_value):.1f} pts) is below 2.5 point threshold")
            if abs(prediction.spread_value) > 0:
                if prediction.spread_value > 0:
                    print(f"Slight value on Boston Celtics (+{prediction.spread_value:.1f} pts)")
                else:
                    print(f"Slight value on Washington Wizards ({prediction.spread_value:.1f} pts)")
    
    # Total points analysis
    print("\nTOTAL POINTS ANALYSIS:")
    print("=" * 80)
    total_diff = prediction.total - 228.5
    if abs(total_diff) >= 3.0:
        if total_diff > 0:
            print(f"📈 OVER {228.5} is recommended ({prediction.total:.1f} predicted)")
            print(f"   Difference: +{total_diff:.1f} points above market")
        else:
            print(f"📉 UNDER {228.5} is recommended ({prediction.total:.1f} predicted)")
            print(f"   Difference: {total_diff:.1f} points below market")
    else:
        print(f"⚖️  Total prediction ({prediction.total:.1f}) is close to market (228.5)")
        print(f"   Difference: {total_diff:+.1f} points - no strong recommendation")
    
    # Summary and recommendation
    print("\n" + "=" * 80)
    print("BETTING RECOMMENDATION SUMMARY")
    print("=" * 80)
    
    recommendations = []
    
    if meets_threshold and prediction.is_overvalue:
        if prediction.value_side == "away":
            recommendations.append(f"✓ STRONG: Bet Washington +8.5 (overvalue detected)")
        else:
            recommendations.append(f"✓ STRONG: Bet Boston -8.5 (overvalue detected)")
    elif meets_threshold:
        recommendations.append(f"✓ Spread: Our prediction ({prediction.spread:.1f}) is close to market")
    
    if meets_threshold:
        if abs(total_diff) >= 3.0:
            if total_diff > 0:
                recommendations.append(f"✓ STRONG: Bet OVER {228.5}")
            else:
                recommendations.append(f"✓ STRONG: Bet UNDER {228.5}")
        else:
            recommendations.append(f"✓ Total: Our prediction ({prediction.total:.1f}) is close to market")
    else:
        recommendations.append("⚠️  Confidence too low - no strong recommendations")
    
    for rec in recommendations:
        print(rec)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
