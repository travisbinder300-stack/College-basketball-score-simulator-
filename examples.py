#!/usr/bin/env python3
"""
Example usage of NHL Analytics System
Demonstrates various ways to use the analytics API
"""

from nhl_analytics import NHLAnalytics
import json


def example_basic_spread():
    """Example: Get spread prediction for a single game"""
    print("\n" + "="*60)
    print("Example 1: Basic Spread Prediction")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    # Predict spread for Toronto vs Montreal
    result = analytics.predict_spread("TOR", "MTL")
    
    print(f"\nMatchup: {result['away_team']} @ {result['home_team']}")
    print(f"Predicted Spread: {result['predicted_spread']}")
    print(f"Interpretation: {result['interpretation']}")
    print(f"Confidence: {result['confidence_interval']['confidence_level']}")
    print(f"Range: [{result['confidence_interval']['lower']}, {result['confidence_interval']['upper']}]")


def example_basic_total():
    """Example: Get total prediction for a single game"""
    print("\n" + "="*60)
    print("Example 2: Basic Total Prediction")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    # Predict total for Boston vs Tampa Bay
    result = analytics.predict_total("BOS", "TBL")
    
    print(f"\nMatchup: {result['away_team']} @ {result['home_team']}")
    print(f"Predicted Total: {result['predicted_total']}")
    print(f"Interpretation: {result['interpretation']}")
    print(f"Expected {result['home_team']} goals: {result['home_expected_goals']}")
    print(f"Expected {result['away_team']} goals: {result['away_expected_goals']}")
    print(f"Confidence: {result['confidence_interval']['confidence_level']}")
    print(f"Range: [{result['confidence_interval']['lower']}, {result['confidence_interval']['upper']}]")


def example_full_analysis():
    """Example: Get complete analysis including both spread and total"""
    print("\n" + "="*60)
    print("Example 3: Full Game Analysis")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    # Get full analysis for Rangers vs Islanders
    result = analytics.get_full_analysis("NYR", "NYI")
    
    print(f"\n{result['matchup']}")
    print(f"Analysis Time: {result['timestamp']}")
    print(f"\nSpread: {result['spread_analysis']['predicted_spread']}")
    print(f"  {result['spread_analysis']['interpretation']}")
    print(f"Total: {result['total_analysis']['predicted_total']}")
    print(f"  {result['total_analysis']['interpretation']}")


def example_json_export():
    """Example: Export predictions as JSON"""
    print("\n" + "="*60)
    print("Example 4: JSON Export")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    # Get predictions
    spread = analytics.predict_spread("EDM", "CGY")
    total = analytics.predict_total("EDM", "CGY")
    
    # Combine into single JSON object
    predictions = {
        "matchup": f"{spread['away_team']} @ {spread['home_team']}",
        "spread": spread,
        "total": total
    }
    
    # Export as formatted JSON
    json_output = json.dumps(predictions, indent=2)
    print("\nJSON Output:")
    print(json_output)


def example_multiple_games():
    """Example: Analyze multiple games"""
    print("\n" + "="*60)
    print("Example 5: Multiple Game Analysis")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    # List of matchups to analyze
    games = [
        ("TOR", "MTL", "Battle of Ontario"),
        ("BOS", "NYR", "Original Six Matchup"),
        ("COL", "VGK", "Western Conference Battle"),
    ]
    
    print("\nToday's Predictions:\n")
    
    for home, away, description in games:
        analysis = analytics.get_full_analysis(home, away)
        
        print(f"{description}: {away} @ {home}")
        print(f"  Spread: {analysis['spread_analysis']['predicted_spread']} "
              f"({analysis['spread_analysis']['interpretation']})")
        print(f"  Total: {analysis['total_analysis']['predicted_total']} "
              f"({analysis['total_analysis']['interpretation']})")
        print()


def example_betting_recommendations():
    """Example: Generate betting recommendations based on confidence"""
    print("\n" + "="*60)
    print("Example 6: Betting Recommendations")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    games = [
        ("TOR", "MTL"),
        ("BOS", "TBL"),
        ("EDM", "CGY"),
    ]
    
    print("\nBetting Analysis (70% Confidence):\n")
    
    for home, away in games:
        spread = analytics.predict_spread(home, away)
        total = analytics.predict_total(home, away)
        
        print(f"{away} @ {home}")
        
        # Spread recommendation
        if spread['predicted_spread'] > 1.5:
            print(f"  Spread: Bet {home} to cover ({spread['predicted_spread']:.1f})")
        elif spread['predicted_spread'] < -1.5:
            print(f"  Spread: Bet {away} to cover ({abs(spread['predicted_spread']):.1f})")
        else:
            print(f"  Spread: Too close to call (pick 'em)")
        
        # Total recommendation
        print(f"  Total: Line around {total['predicted_total']:.1f}")
        print(f"    With 70% confidence: {total['confidence_interval']['lower']:.1f} - "
              f"{total['confidence_interval']['upper']:.1f}")
        print()


def example_underdog_value():
    """Example: Find underdog and overvalued spread opportunities"""
    print("\n" + "="*60)
    print("Example 7: Finding Underdog Value & Overvalued Spreads")
    print("="*60)
    
    analytics = NHLAnalytics()
    
    print("\nComparing predictions vs market spreads to find value:\n")
    
    # Simulated market spreads (real betting lines would come from sportsbooks)
    market_scenarios = [
        ("TOR", "MTL", 1.5, "Market: TOR -1.5"),
        ("BOS", "NYR", 2.0, "Market: BOS -2.0"),
        ("EDM", "CGY", -0.5, "Market: EDM +0.5 (underdog)"),
    ]
    
    for home, away, market_spread, description in market_scenarios:
        value = analytics.find_spread_value(home, away, market_spread)
        
        print(f"{away} @ {home}")
        print(f"  {description}")
        print(f"  Our Prediction: {value['predicted_spread']:+.2f}")
        print(f"  Spread Difference: {value['spread_difference']:+.2f} goals")
        print(f"  Underdog: {value['underdog']} (getting +{value['underdog_points']:.1f})")
        print(f"  ⚠️  {value['value_assessment']}")
        print(f"  💡 Recommendation: {value['recommended_bet']}")
        print()


def example_moneypuck_integration():
    """Example: Using MoneyPuck power rankings for enhanced predictions"""
    print("\n" + "="*60)
    print("Example 8: MoneyPuck Integration")
    print("="*60)
    
    print("\nComparing predictions with and without MoneyPuck:\n")
    
    # Standard mode
    analytics_standard = NHLAnalytics(use_moneypuck=False)
    spread_standard = analytics_standard.predict_spread("TOR", "BOS")
    
    print("Standard Mode (NHL API only):")
    print(f"  TOR vs BOS Spread: {spread_standard['predicted_spread']:+.2f}")
    print(f"  TOR Strength: {spread_standard['home_team_strength']:.2f}")
    print(f"  BOS Strength: {spread_standard['away_team_strength']:.2f}")
    print()
    
    # MoneyPuck mode
    analytics_mp = NHLAnalytics(use_moneypuck=True)
    spread_mp = analytics_mp.predict_spread("TOR", "BOS")
    
    print("MoneyPuck Mode (Enhanced with advanced analytics):")
    print(f"  TOR vs BOS Spread: {spread_mp['predicted_spread']:+.2f}")
    print(f"  TOR Strength: {spread_mp['home_team_strength']:.2f}")
    print(f"  BOS Strength: {spread_mp['away_team_strength']:.2f}")
    print()
    
    print("Benefits of MoneyPuck Integration:")
    print("  ✅ Incorporates Expected Goals (xG) metrics")
    print("  ✅ Considers advanced possession statistics")
    print("  ✅ Better reflects team performance trends")
    print("  ✅ Improves prediction accuracy")
    print()


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("NHL ANALYTICS - USAGE EXAMPLES")
    print("70% Confidence Level Predictions with Real Data")
    print("="*60)
    
    # Run all examples
    example_basic_spread()
    example_basic_total()
    example_full_analysis()
    example_json_export()
    example_multiple_games()
    example_betting_recommendations()
    example_underdog_value()
    example_moneypuck_integration()
    
    print("\n" + "="*60)
    print("Examples Complete!")
    print("="*60)
    print("\nNote: When connected to the internet, this system fetches")
    print("real-time NHL data from the official NHL API and optionally")
    print("MoneyPuck power rankings for enhanced predictions.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
