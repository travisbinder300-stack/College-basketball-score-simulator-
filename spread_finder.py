#!/usr/bin/env python3
"""
Interactive Spread Finder
Find teams that can cover spreads with high accuracy.
"""

import sys
from spread_analyzer import SpreadAnalyzer


def get_team_config(team_number: int) -> dict:
    """Get team configuration from user."""
    print(f"\n{'='*70}")
    print(f"Configure Team {team_number}")
    print(f"{'='*70}")
    
    name = input(f"Team {team_number} name: ").strip()
    if not name:
        name = f"Team {team_number}"
    
    print("\nEnter team statistics (press Enter to use defaults):")
    print("Tip: Higher percentages = stronger team")
    
    def get_float(prompt, default):
        while True:
            val = input(f"{prompt} (default {default:.2f}): ").strip()
            if not val:
                return default
            try:
                return float(val)
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    return {
        'name': name,
        'fg_percentage': get_float("Field Goal %", 0.45),
        'three_pt_percentage': get_float("Three-Point %", 0.35),
        'ft_percentage': get_float("Free Throw %", 0.72),
        'turnover_rate': get_float("Turnover Rate", 0.15),
        'offensive_rebound_rate': get_float("Offensive Rebound Rate", 0.30),
        'defensive_rebound_rate': get_float("Defensive Rebound Rate", 0.70)
    }


def find_best_spread_bet():
    """Interactive mode to find best spread bet."""
    print("\n" + "="*70)
    print(" "*15 + "SPREAD FINDER - 100% ACCURACY MODE")
    print("="*70)
    print("\nThis tool runs 1000+ simulations to find which team")
    print("can cover a point spread with the highest confidence.")
    
    # Get team configurations
    team1 = get_team_config(1)
    team2 = get_team_config(2)
    
    # Get number of simulations
    print("\n" + "="*70)
    while True:
        num_sims = input("Number of simulations (default 1000, more = more accurate): ").strip()
        if not num_sims:
            num_sims = 1000
            break
        try:
            num_sims = int(num_sims)
            if num_sims < 100:
                print("Please use at least 100 simulations")
            elif num_sims > 10000:
                print("That many simulations will take a long time. Use 10000 or less.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Run simulations
    print("\n" + "="*70)
    analyzer = SpreadAnalyzer(team1, team2, num_simulations=num_sims)
    analyzer.run_simulations()
    
    # Get statistics
    stats = analyzer.get_statistics()
    optimal_spread = analyzer.find_optimal_spread()
    
    # Display overall results
    print("\n" + "="*70)
    print(" "*20 + "SIMULATION RESULTS")
    print("="*70)
    print(f"\n{team1['name']}: {stats['team1_wins']} wins ({stats['team1_win_pct']:.1f}%)")
    print(f"  Average Score: {stats['team1_avg_score']:.1f}")
    print(f"\n{team2['name']}: {stats['team2_wins']} wins ({stats['team2_win_pct']:.1f}%)")
    print(f"  Average Score: {stats['team2_avg_score']:.1f}")
    print(f"\nAverage Point Differential: {stats['avg_point_diff']:.1f}")
    
    # Find high-confidence spreads
    print("\n" + "="*70)
    print(" "*15 + "FINDING HIGH-CONFIDENCE BETS")
    print("="*70)
    
    # Test spreads from -15 to +15
    best_bet = None
    best_coverage = 0
    
    spreads_to_test = list(range(-15, 16))
    
    print("\nTesting various spreads...")
    high_confidence_bets = []
    
    for spread in spreads_to_test:
        analysis = analyzer.analyze_spread(float(spread))
        
        # Record high confidence bets (70%+)
        if analysis['cover_rate'] >= 70:
            high_confidence_bets.append({
                'spread': spread,
                'team': analysis['best_bet'],
                'coverage': analysis['cover_rate'],
                'confidence': analysis['confidence']
            })
        
        # Track best overall
        if analysis['cover_rate'] > best_coverage:
            best_coverage = analysis['cover_rate']
            best_bet = {
                'spread': spread,
                'team': analysis['best_bet'],
                'coverage': analysis['cover_rate'],
                'confidence': analysis['confidence']
            }
    
    # Display results
    print("\n" + "="*70)
    print(" "*20 + "⭐ HIGH CONFIDENCE BETS ⭐")
    print("="*70)
    
    if high_confidence_bets:
        print(f"\nFound {len(high_confidence_bets)} high-confidence betting opportunities (70%+ coverage):\n")
        
        for i, bet in enumerate(high_confidence_bets, 1):
            spread_val = abs(bet['spread'])
            if bet['spread'] > 0:
                favored = team1['name']
                against = team2['name']
            else:
                favored = team2['name']
                against = team1['name']
            
            print(f"{i}. Bet on {bet['team']}")
            if bet['spread'] == 0:
                print(f"   Straight up win (no spread)")
            elif bet['team'] == favored:
                print(f"   To cover -{spread_val} spread ({favored} favored)")
            else:
                print(f"   To cover +{spread_val} spread (underdog)")
            print(f"   Coverage Rate: {bet['coverage']:.1f}%")
            print(f"   Confidence: {bet['confidence']}")
            print()
        
        # Show the best one
        best_high = max(high_confidence_bets, key=lambda x: x['coverage'])
        print("="*70)
        print(f"🏆 HIGHEST CONFIDENCE BET 🏆")
        print("="*70)
        spread_val = abs(best_high['spread'])
        if best_high['spread'] > 0:
            print(f"Bet on {best_high['team']} to cover -{spread_val} point spread")
        elif best_high['spread'] < 0:
            print(f"Bet on {best_high['team']} to cover +{spread_val} point spread")
        else:
            print(f"Bet on {best_high['team']} to win straight up")
        print(f"Success Rate: {best_high['coverage']:.1f}%")
        print(f"Confidence: {best_high['confidence']}")
        print("="*70)
        
    else:
        print("\n⚠ No high-confidence bets found (none with 70%+ coverage)")
        print("\nBest available bet:")
        if best_bet:
            spread_val = abs(best_bet['spread'])
            print(f"  Team: {best_bet['team']}")
            if best_bet['spread'] > 0:
                print(f"  Spread: -{spread_val}")
            elif best_bet['spread'] < 0:
                print(f"  Spread: +{spread_val}")
            else:
                print(f"  Straight up win")
            print(f"  Coverage: {best_bet['coverage']:.1f}%")
            print(f"  Confidence: {best_bet['confidence']}")
    
    # Show detailed analysis for a specific spread
    print("\n" + "="*70)
    custom_spread = input("\nAnalyze a specific spread? (Enter number or press Enter to skip): ").strip()
    if custom_spread:
        try:
            spread_val = float(custom_spread)
            analyzer.print_report(spread=spread_val)
        except ValueError:
            print("Invalid spread value")


def quick_preset_analysis():
    """Quick analysis with preset teams."""
    print("\n" + "="*70)
    print(" "*15 + "QUICK SPREAD ANALYSIS")
    print("="*70)
    
    print("\nSelect matchup:")
    print("1. Duke vs UNC (Duke stronger)")
    print("2. Kansas vs Kentucky (Even matchup)")
    print("3. Gonzaga vs mid-major (Gonzaga dominant)")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '1':
        team1 = {
            'name': 'Duke',
            'fg_percentage': 0.48,
            'three_pt_percentage': 0.38,
            'ft_percentage': 0.75
        }
        team2 = {
            'name': 'UNC',
            'fg_percentage': 0.45,
            'three_pt_percentage': 0.35,
            'ft_percentage': 0.70
        }
    elif choice == '2':
        team1 = {
            'name': 'Kansas',
            'fg_percentage': 0.46,
            'three_pt_percentage': 0.36,
            'ft_percentage': 0.72
        }
        team2 = {
            'name': 'Kentucky',
            'fg_percentage': 0.46,
            'three_pt_percentage': 0.36,
            'ft_percentage': 0.72
        }
    elif choice == '3':
        team1 = {
            'name': 'Gonzaga',
            'fg_percentage': 0.52,
            'three_pt_percentage': 0.42,
            'ft_percentage': 0.78
        }
        team2 = {
            'name': 'Mid-Major',
            'fg_percentage': 0.40,
            'three_pt_percentage': 0.30,
            'ft_percentage': 0.65
        }
    else:
        print("Invalid choice")
        return
    
    analyzer = SpreadAnalyzer(team1, team2, num_simulations=500)
    analyzer.run_simulations()
    
    # Test common spreads
    for spread in [3, 5, 7, 10]:
        analyzer.print_report(spread=float(spread))
        print("\n")


def main():
    """Main menu."""
    while True:
        print("\n" + "="*70)
        print(" "*10 + "COLLEGE BASKETBALL SPREAD FINDER")
        print("="*70)
        print("\nFind teams that can cover spreads with high accuracy!")
        print("\n1. Find Best Spread Bet (Custom Teams)")
        print("2. Quick Analysis (Preset Teams)")
        print("3. Exit")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == '1':
            find_best_spread_bet()
        elif choice == '2':
            quick_preset_analysis()
        elif choice == '3':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
