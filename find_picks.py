#!/usr/bin/env python3
"""
Find Picks - College Basketball Betting Recommendations
Analyzes matchups and provides betting picks based on simulation data.
"""

from spread_analyzer import SpreadAnalyzer


def analyze_matchup(team1_config, team2_config, spread, num_sims=500):
    """
    Analyze a specific matchup and provide betting recommendation.
    
    Args:
        team1_config: Configuration for team 1 (favorite)
        team2_config: Configuration for team 2 (underdog)
        spread: Point spread (positive means team1 favored)
        num_sims: Number of simulations to run
    
    Returns:
        Dictionary with pick recommendation
    """
    analyzer = SpreadAnalyzer(team1_config, team2_config, num_simulations=num_sims)
    analyzer.run_simulations()
    
    stats = analyzer.get_statistics()
    optimal = analyzer.find_optimal_spread()
    analysis = analyzer.analyze_spread(spread)
    
    # Determine the pick
    team1_covers = analysis['team1_cover_pct']
    team2_covers = analysis['team2_cover_pct']
    
    # Calculate value
    spread_diff = spread - abs(optimal)
    
    pick = {
        'matchup': f"{team1_config['name']} vs {team2_config['name']}",
        'spread': spread,
        'team1_name': team1_config['name'],
        'team2_name': team2_config['name'],
        'team1_win_pct': stats['team1_win_pct'],
        'team2_win_pct': stats['team2_win_pct'],
        'optimal_spread': abs(optimal),
        'team1_covers_pct': team1_covers,
        'team2_covers_pct': team2_covers,
        'spread_diff': spread_diff,
        'recommendation': None,
        'confidence': None,
        'reasoning': None
    }
    
    # Determine recommendation
    if team1_covers >= 70:
        pick['recommendation'] = f"{team1_config['name']} -{spread}"
        pick['confidence'] = 'HIGH'
        pick['reasoning'] = f"Covers {team1_covers:.1f}% of the time"
    elif team2_covers >= 70:
        pick['recommendation'] = f"{team2_config['name']} +{spread}"
        pick['confidence'] = 'HIGH'
        pick['reasoning'] = f"Covers {team2_covers:.1f}% of the time"
    elif team1_covers >= 60:
        pick['recommendation'] = f"{team1_config['name']} -{spread}"
        pick['confidence'] = 'MEDIUM'
        pick['reasoning'] = f"Covers {team1_covers:.1f}% - slight edge"
    elif team2_covers >= 60:
        pick['recommendation'] = f"{team2_config['name']} +{spread}"
        pick['confidence'] = 'MEDIUM'
        pick['reasoning'] = f"Covers {team2_covers:.1f}% - slight edge"
    else:
        pick['recommendation'] = "AVOID"
        pick['confidence'] = 'LOW'
        pick['reasoning'] = "Too close to call - no edge"
    
    # Add value assessment
    if abs(spread_diff) >= 3:
        if spread_diff > 0:
            pick['value'] = f"Underdog getting {spread_diff:.1f} extra points - VALUE BET"
        else:
            pick['value'] = f"Favorite giving {abs(spread_diff):.1f} too many - TRAP BET"
    else:
        pick['value'] = "Fair spread - no significant value"
    
    return pick


def display_pick(pick):
    """Display a betting pick in formatted output."""
    print("\n" + "="*70)
    print(f"📊 {pick['matchup']}")
    print("="*70)
    
    print(f"\nSpread: {pick['team1_name']} -{pick['spread']} / {pick['team2_name']} +{pick['spread']}")
    print(f"Optimal Spread: {pick['team1_name']} -{pick['optimal_spread']:.1f}")
    
    print(f"\n🎲 Simulation Results:")
    print(f"  {pick['team1_name']} wins {pick['team1_win_pct']:.1f}% of games")
    print(f"  {pick['team2_name']} wins {pick['team2_win_pct']:.1f}% of games")
    
    print(f"\n📈 Coverage at {pick['spread']} spread:")
    print(f"  {pick['team1_name']} -{pick['spread']}: {pick['team1_covers_pct']:.1f}%")
    print(f"  {pick['team2_name']} +{pick['spread']}: {pick['team2_covers_pct']:.1f}%")
    
    print(f"\n💰 Value Assessment:")
    print(f"  {pick['value']}")
    
    print(f"\n🎯 PICK:")
    if pick['recommendation'] == 'AVOID':
        print(f"  ❌ {pick['recommendation']} - {pick['reasoning']}")
    elif pick['confidence'] == 'HIGH':
        print(f"  ✅ {pick['recommendation']}")
        print(f"  Confidence: {pick['confidence']} ({pick['reasoning']})")
    else:
        print(f"  ⚠️  {pick['recommendation']}")
        print(f"  Confidence: {pick['confidence']} ({pick['reasoning']})")
    
    print("="*70)


def find_todays_picks():
    """
    Example function showing how to analyze multiple games and find best picks.
    In a real scenario, you would input actual game data.
    """
    
    print("\n" + "="*70)
    print(" "*20 + "🏀 COLLEGE BASKETBALL PICKS 🏀")
    print("="*70)
    print("\nAnalyzing matchups to find the best betting opportunities...")
    
    # Example matchups (in real use, these would be actual games)
    matchups = [
        {
            'team1': {'name': 'Kansas', 'fg_percentage': 0.49, 'three_pt_percentage': 0.38, 'ft_percentage': 0.75},
            'team2': {'name': 'Texas Tech', 'fg_percentage': 0.46, 'three_pt_percentage': 0.35, 'ft_percentage': 0.71},
            'spread': 6.5
        },
        {
            'team1': {'name': 'UConn', 'fg_percentage': 0.51, 'three_pt_percentage': 0.40, 'ft_percentage': 0.77},
            'team2': {'name': 'Villanova', 'fg_percentage': 0.45, 'three_pt_percentage': 0.34, 'ft_percentage': 0.70},
            'spread': 8.5
        },
        {
            'team1': {'name': 'Arizona', 'fg_percentage': 0.48, 'three_pt_percentage': 0.37, 'ft_percentage': 0.74},
            'team2': {'name': 'UCLA', 'fg_percentage': 0.47, 'three_pt_percentage': 0.36, 'ft_percentage': 0.72},
            'spread': 3.5
        }
    ]
    
    all_picks = []
    
    for i, matchup in enumerate(matchups, 1):
        print(f"\n{'='*70}")
        print(f"Analyzing Game {i}/{len(matchups)}...")
        print(f"{'='*70}")
        
        pick = analyze_matchup(
            matchup['team1'],
            matchup['team2'],
            matchup['spread'],
            num_sims=300  # Using 300 for faster demo
        )
        
        all_picks.append(pick)
        display_pick(pick)
    
    # Show best picks summary
    print("\n" + "="*70)
    print(" "*25 + "📋 BEST PICKS SUMMARY")
    print("="*70)
    
    # Filter for picks with recommendations
    good_picks = [p for p in all_picks if p['recommendation'] != 'AVOID']
    
    if good_picks:
        # Sort by confidence (HIGH first, then MEDIUM)
        high_confidence = [p for p in good_picks if p['confidence'] == 'HIGH']
        medium_confidence = [p for p in good_picks if p['confidence'] == 'MEDIUM']
        
        if high_confidence:
            print("\n✅ HIGH CONFIDENCE PICKS:")
            for i, pick in enumerate(high_confidence, 1):
                print(f"\n{i}. {pick['recommendation']}")
                print(f"   {pick['reasoning']}")
                print(f"   {pick['value']}")
        
        if medium_confidence:
            print("\n⚠️  MEDIUM CONFIDENCE PICKS:")
            for i, pick in enumerate(medium_confidence, 1):
                print(f"\n{i}. {pick['recommendation']}")
                print(f"   {pick['reasoning']}")
                print(f"   {pick['value']}")
    else:
        print("\n❌ No strong picks found in today's games.")
        print("All matchups are too close to call or lack value.")
    
    print("\n" + "="*70)
    print("💡 TIP: Look for HIGH confidence picks with positive value")
    print("="*70)


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print(" "*15 + "COLLEGE BASKETBALL PICK FINDER")
    print("="*70)
    print("\nThis tool analyzes matchups and finds the best betting picks")
    print("based on statistical simulation and value analysis.")
    
    # Run the pick finder
    find_todays_picks()
    
    print("\n" + "="*70)
    print("To analyze a specific game, use:")
    print("  from find_picks import analyze_matchup")
    print("  pick = analyze_matchup(team1, team2, spread)")
    print("\nOr use spread_finder.py for interactive analysis")
    print("="*70)


if __name__ == "__main__":
    main()
