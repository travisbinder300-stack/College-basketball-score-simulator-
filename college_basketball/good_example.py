#!/usr/bin/env python3
"""
Complete Example: College Basketball Spread Analysis
Demonstrates all features of the spread analyzer with real-world scenarios.
"""

try:
    from .spread_analyzer import SpreadAnalyzer
except ImportError:
    from spread_analyzer import SpreadAnalyzer


def example_scenario():
    """
    Real-world example: Duke vs UNC rivalry game
    Shows how to find value bets and avoid trap bets
    """
    
    print("\n" + "="*70)
    print(" "*15 + "COMPREHENSIVE SPREAD ANALYSIS EXAMPLE")
    print(" "*20 + "Duke vs UNC Rivalry Game")
    print("="*70)
    
    # Team configurations based on typical season stats
    duke = {
        'name': 'Duke Blue Devils',
        'fg_percentage': 0.49,        # Strong shooting
        'three_pt_percentage': 0.39,  # Above-average 3PT shooting
        'ft_percentage': 0.76,        # Good free throw shooting
        'turnover_rate': 0.12,        # Low turnovers
        'offensive_rebound_rate': 0.32,
        'defensive_rebound_rate': 0.72
    }
    
    unc = {
        'name': 'UNC Tar Heels',
        'fg_percentage': 0.46,        # Good shooting
        'three_pt_percentage': 0.36,  # Average 3PT shooting
        'ft_percentage': 0.71,        # Decent free throws
        'turnover_rate': 0.14,        # Average turnovers
        'offensive_rebound_rate': 0.28,
        'defensive_rebound_rate': 0.68
    }
    
    print("\n📊 TEAM STATISTICS")
    print("-"*70)
    print(f"{duke['name']}:")
    print(f"  FG%: {duke['fg_percentage']*100:.1f}% | 3PT%: {duke['three_pt_percentage']*100:.1f}% | FT%: {duke['ft_percentage']*100:.1f}%")
    print(f"\n{unc['name']}:")
    print(f"  FG%: {unc['fg_percentage']*100:.1f}% | 3PT%: {unc['three_pt_percentage']*100:.1f}% | FT%: {unc['ft_percentage']*100:.1f}%")
    
    # Run simulations
    print("\n" + "="*70)
    print("🎲 RUNNING 1000 GAME SIMULATIONS")
    print("="*70)
    
    analyzer = SpreadAnalyzer(duke, unc, num_simulations=1000)
    analyzer.run_simulations()
    
    # Get overall statistics
    stats = analyzer.get_statistics()
    optimal = analyzer.find_optimal_spread()
    
    print("\n📈 SIMULATION RESULTS")
    print("-"*70)
    print(f"{duke['name']}:")
    print(f"  Wins: {stats['team1_wins']} ({stats['team1_win_pct']:.1f}%)")
    print(f"  Average Score: {stats['team1_avg_score']:.1f} PPG")
    print(f"  Score Range: {stats['team1_min_score']}-{stats['team1_max_score']}")
    
    print(f"\n{unc['name']}:")
    print(f"  Wins: {stats['team2_wins']} ({stats['team2_win_pct']:.1f}%)")
    print(f"  Average Score: {stats['team2_avg_score']:.1f} PPG")
    print(f"  Score Range: {stats['team2_min_score']}-{stats['team2_max_score']}")
    
    print(f"\n⚖️  Optimal Spread: {duke['name']} -{abs(optimal):.1f}")
    print(f"   (This is the 'true' line based on simulation)")
    
    # Test common betting scenarios
    print("\n" + "="*70)
    print("💰 BETTING SCENARIOS - Which Spreads Should You Take?")
    print("="*70)
    
    test_spreads = [3.0, 5.0, 7.0, 10.0, 12.0]
    
    print("\nTesting various point spreads:\n")
    for spread in test_spreads:
        analysis = analyzer.analyze_spread(spread)
        duke_covers = analysis['team1_cover_pct']
        unc_covers = analysis['team2_cover_pct']
        
        print(f"Spread: {duke['name']} -{spread:.0f} / {unc['name']} +{spread:.0f}")
        print(f"  {duke['name']} covers: {duke_covers:.1f}%")
        print(f"  {unc['name']} covers: {unc_covers:.1f}%")
        
        # Determine recommendation
        if duke_covers >= 70:
            print(f"  ✓ BET {duke['name']} -{spread:.0f} (HIGH CONFIDENCE)")
        elif unc_covers >= 70:
            print(f"  ✓ BET {unc['name']} +{spread:.0f} (HIGH CONFIDENCE)")
        elif duke_covers >= 60:
            print(f"  ⚠ LEAN {duke['name']} -{spread:.0f} (MEDIUM CONFIDENCE)")
        elif unc_covers >= 60:
            print(f"  ⚠ LEAN {unc['name']} +{spread:.0f} (MEDIUM CONFIDENCE)")
        else:
            print(f"  ❌ AVOID - Too close to call")
        print()
    
    # Show overvalued spreads (value bets)
    print("\n" + "="*70)
    print("💎 VALUE BETS (Overvalued Spreads)")
    print("="*70)
    print("These are spreads where the underdog is getting TOO MANY points\n")
    
    overvalued = analyzer.find_overvalued_spreads()
    
    if overvalued:
        print(f"Found {len(overvalued)} value betting opportunities:\n")
        
        # Show top 5 value bets
        for i, bet in enumerate(overvalued[:5], 1):
            print(f"{i}. BET: {bet['underdog']} +{abs(bet['spread']):.1f}")
            print(f"   Coverage: {bet['underdog_covers_pct']:.1f}%")
            print(f"   Extra Points: {bet['extra_points']:.1f} more than needed")
            print(f"   Value Rating: {bet['value_rating']}")
            
            if bet['value_rating'] == 'EXCELLENT':
                print(f"   🎯 EXCELLENT VALUE - Strong recommendation!")
            print()
        
        # Highlight the best value
        best = overvalued[0]
        print("-"*70)
        print("🏆 BEST VALUE BET:")
        print(f"   {best['underdog']} +{abs(best['spread']):.1f}")
        print(f"   Covers {best['underdog_covers_pct']:.1f}% of the time")
        print(f"   Getting {best['extra_points']:.1f} extra points!")
        print("-"*70)
    else:
        print("No significant value bets found in this matchup.")
    
    # Show undervalued spreads (trap bets)
    print("\n" + "="*70)
    print("⚠️  TRAP BETS (Undervalued Spreads)")
    print("="*70)
    print("These are spreads where the favorite is giving TOO MANY points\n")
    
    undervalued = analyzer.find_undervalued_spreads()
    
    if undervalued:
        print(f"Found {len(undervalued)} trap bets to AVOID:\n")
        
        # Show top 3 trap bets
        for i, bet in enumerate(undervalued[:3], 1):
            print(f"{i}. AVOID: {bet['favorite']} -{abs(bet['spread']):.1f}")
            print(f"   Only covers: {bet['favorite_covers_pct']:.1f}%")
            print(f"   Points Short: {bet['points_short']:.1f} less than optimal")
            print(f"   Risk Rating: {bet['risk_rating']}")
            print(f"   🚫 {bet['advice']}")
            print()
        
        # Highlight the worst bet
        worst = undervalued[0]
        print("-"*70)
        print("🚫 WORST BET (Biggest Trap):")
        print(f"   AVOID {worst['favorite']} -{abs(worst['spread']):.1f}")
        print(f"   Only covers {worst['favorite_covers_pct']:.1f}% of the time")
        print(f"   💡 Better option: Bet {worst['underdog']} +{abs(worst['spread']):.1f} instead")
        print("-"*70)
    else:
        print("No significant trap bets found in this matchup.")
    
    # Summary and recommendations
    print("\n" + "="*70)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("="*70)
    
    print(f"\n1. True Market Line: {duke['name']} -{abs(optimal):.1f}")
    print(f"   (Based on {analyzer.num_simulations} simulations)")
    
    print(f"\n2. {duke['name']} wins {stats['team1_win_pct']:.1f}% of games")
    print(f"   Average margin: {stats['avg_point_diff']:.1f} points")
    
    if overvalued:
        print(f"\n3. Best Value Bet:")
        best = overvalued[0]
        print(f"   ✓ {best['underdog']} +{abs(best['spread']):.1f} ({best['underdog_covers_pct']:.1f}% coverage)")
    
    if undervalued:
        print(f"\n4. Trap to Avoid:")
        worst = undervalued[0]
        print(f"   ✗ {worst['favorite']} -{abs(worst['spread']):.1f} (only {worst['favorite_covers_pct']:.1f}% coverage)")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    print("✓ Overvalued spreads = Underdog getting extra points = VALUE BETS")
    print("✗ Undervalued spreads = Favorite giving too many = TRAP BETS")
    print("⚖️  Optimal spread = The 'true' line based on team strength")
    print("="*70)
    
    print("\n💡 HOW TO USE THIS INFORMATION:")
    print("-"*70)
    print("1. Compare these results to actual betting lines")
    print("2. Look for lines that differ significantly from the optimal spread")
    print("3. Take value bets where underdogs get extra points")
    print("4. Avoid trap bets where favorites can't cover")
    print("5. The higher the coverage %, the more confident the bet")
    print("="*70)


def quick_comparison():
    """Quick example comparing three matchup scenarios."""
    
    print("\n\n" + "="*70)
    print(" "*10 + "BONUS: QUICK COMPARISON OF 3 MATCHUPS")
    print("="*70)
    
    matchups = [
        {
            'name': 'Even Matchup',
            'team1': {'name': 'Team A', 'fg_percentage': 0.46, 'three_pt_percentage': 0.36},
            'team2': {'name': 'Team B', 'fg_percentage': 0.46, 'three_pt_percentage': 0.36}
        },
        {
            'name': 'Close Matchup',
            'team1': {'name': 'Favorite', 'fg_percentage': 0.48, 'three_pt_percentage': 0.38},
            'team2': {'name': 'Underdog', 'fg_percentage': 0.45, 'three_pt_percentage': 0.34}
        },
        {
            'name': 'Mismatch',
            'team1': {'name': 'Elite', 'fg_percentage': 0.52, 'three_pt_percentage': 0.42},
            'team2': {'name': 'Weak', 'fg_percentage': 0.40, 'three_pt_percentage': 0.28}
        }
    ]
    
    for matchup in matchups:
        print(f"\n{matchup['name']}: {matchup['team1']['name']} vs {matchup['team2']['name']}")
        print("-"*70)
        
        analyzer = SpreadAnalyzer(matchup['team1'], matchup['team2'], num_simulations=200)
        analyzer.run_simulations()
        
        stats = analyzer.get_statistics()
        optimal = analyzer.find_optimal_spread()
        
        print(f"Result: {matchup['team1']['name']} wins {stats['team1_win_pct']:.0f}%")
        print(f"Optimal Spread: {matchup['team1']['name']} -{abs(optimal):.1f}")
        
        # Check a 7-point spread
        analysis = analyzer.analyze_spread(7.0)
        print(f"\nAt 7-point spread:")
        print(f"  {matchup['team1']['name']} -{7}: {analysis['team1_cover_pct']:.0f}% coverage")
        print(f"  {matchup['team2']['name']} +{7}: {analysis['team2_cover_pct']:.0f}% coverage")


if __name__ == "__main__":
    # Run the comprehensive example
    example_scenario()
    
    # Run the quick comparison
    quick_comparison()
    
    print("\n" + "="*70)
    print("Example complete! Use spread_finder.py for interactive analysis.")
    print("="*70)
    print()
