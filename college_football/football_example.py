#!/usr/bin/env python3
"""
College Football Simulator Examples
Demonstrates how to use the football simulator and spread analyzer.
"""

try:
    from football_simulator import FootballTeam, FootballSimulator
    from football_spread_analyzer import FootballSpreadAnalyzer
    from football_find_picks import analyze_matchup, print_quick_analysis
except ImportError:
    from .football_simulator import FootballTeam, FootballSimulator
    from .football_spread_analyzer import FootballSpreadAnalyzer
    from .football_find_picks import analyze_matchup, print_quick_analysis


def example_basic_game():
    """Run a basic game simulation between two teams."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Game Simulation")
    print("="*70)
    
    # Create two teams
    team1 = FootballTeam(
        name="LSU Tigers",
        pass_completion_pct=0.64,
        yards_per_completion=13.0,
        rush_yards_per_carry=4.8,
        turnover_rate=0.025,
        red_zone_td_pct=0.65,
        field_goal_pct=0.78,
        home_field=True  # Playing at home
    )
    
    team2 = FootballTeam(
        name="Florida Gators",
        pass_completion_pct=0.60,
        yards_per_completion=12.0,
        rush_yards_per_carry=4.2,
        turnover_rate=0.03,
        red_zone_td_pct=0.58,
        field_goal_pct=0.75
    )
    
    # Run simulation
    simulator = FootballSimulator(team1, team2, verbose=True)
    winner, summary = simulator.simulate_game()
    
    print(f"\n{'='*70}")
    print(f"Game Result: {summary['final_score']}")
    print(f"Winner: {winner.name}")
    print(f"{'='*70}")


def example_spread_analysis():
    """Analyze spreads for a matchup."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Spread Analysis")
    print("="*70)
    
    # Configure teams
    team1_config = {
        'name': 'Georgia Bulldogs',
        'pass_completion_pct': 0.65,
        'yards_per_completion': 13.5,
        'rush_yards_per_carry': 5.2,
        'turnover_rate': 0.02,
        'red_zone_td_pct': 0.70,
        'field_goal_pct': 0.82,
        'home_field': True
    }
    
    team2_config = {
        'name': 'Tennessee Volunteers',
        'pass_completion_pct': 0.62,
        'yards_per_completion': 12.5,
        'rush_yards_per_carry': 4.5,
        'turnover_rate': 0.028,
        'red_zone_td_pct': 0.62,
        'field_goal_pct': 0.76
    }
    
    # Run spread analysis
    analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=1000)
    analyzer.run_simulations()
    
    # Test different spreads
    spreads = [3.0, 7.0, 10.0, 14.0]
    
    print("\nSpread Coverage Analysis:")
    print("-" * 60)
    print(f"{'Spread':<15} {'Georgia':<20} {'Tennessee':<20} {'Pick'}")
    print("-" * 60)
    
    for spread in spreads:
        analysis = analyzer.analyze_spread(spread)
        pick = f"Georgia -{spread}" if analysis['team1_cover_pct'] > analysis['team2_cover_pct'] else f"Tennessee +{spread}"
        conf = analysis['confidence']
        print(f"Georgia -{spread:<8} {analysis['team1_cover_pct']:.1f}%{' ':14} {analysis['team2_cover_pct']:.1f}%{' ':14} {pick} ({conf})")
    
    # Show optimal spread
    optimal = analyzer.find_optimal_spread()
    print(f"\nOptimal Spread: Georgia -{optimal:.1f}")
    
    # Print full report for one spread
    print("\n" + "-"*60)
    analyzer.print_report(spread=7.0, total=52.5)


def example_find_value_picks():
    """Find value picks in a big mismatch."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Finding Value Picks in a Mismatch")
    print("="*70)
    
    # Create a big mismatch (top team vs small school)
    team1_config = {
        'name': 'Alabama',
        'pass_completion_pct': 0.68,
        'yards_per_completion': 14.0,
        'rush_yards_per_carry': 5.5,
        'turnover_rate': 0.018,
        'red_zone_td_pct': 0.75,
        'field_goal_pct': 0.85,
        'home_field': True
    }
    
    team2_config = {
        'name': 'Middle Tennessee',
        'pass_completion_pct': 0.55,
        'yards_per_completion': 10.5,
        'rush_yards_per_carry': 3.5,
        'turnover_rate': 0.04,
        'red_zone_td_pct': 0.50,
        'field_goal_pct': 0.68
    }
    
    # Run analysis
    analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=1000)
    analyzer.run_simulations()
    
    stats = analyzer.get_statistics()
    optimal = analyzer.find_optimal_spread()
    
    print(f"\nMatchup Analysis:")
    print(f"Alabama win rate: {stats['team1_win_pct']:.1f}%")
    print(f"Average scores: Alabama {stats['team1_avg_score']:.1f} - Middle Tennessee {stats['team2_avg_score']:.1f}")
    print(f"Optimal spread: Alabama -{optimal:.1f}")
    
    # Test large spreads
    print("\n" + "="*70)
    print("LARGE SPREAD ANALYSIS")
    print("="*70)
    
    large_spreads = [21.0, 24.5, 28.0, 31.5, 35.0, 38.5]
    
    print(f"\n{'Spread':<15} {'Alabama Covers':<20} {'MT Covers':<20} {'Confidence'}")
    print("-" * 70)
    
    for spread in large_spreads:
        analysis = analyzer.analyze_spread(spread)
        if analysis['team2_cover_pct'] > analysis['team1_cover_pct']:
            conf = analysis['confidence']
            print(f"Alabama -{spread:<8} {analysis['team1_cover_pct']:.1f}%{' ':14} {analysis['team2_cover_pct']:.1f}%{' ':14} MT +{spread} ({conf})")
        else:
            conf = analysis['confidence']
            print(f"Alabama -{spread:<8} {analysis['team1_cover_pct']:.1f}%{' ':14} {analysis['team2_cover_pct']:.1f}%{' ':14} Alabama -{spread} ({conf})")
    
    # Find where underdog has value
    print("\n" + "="*70)
    print("VALUE PICK ANALYSIS")
    print("="*70)
    
    print(f"\nMiddle Tennessee starts having value (60%+ coverage) at approximately +{optimal + 7:.1f}")
    print(f"High confidence (70%+ coverage) at approximately +{optimal + 12:.1f}")


def example_rivalry_game():
    """Analyze a close rivalry game."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Rivalry Game Analysis")
    print("="*70)
    
    team1_config = {
        'name': 'Ohio State',
        'pass_completion_pct': 0.63,
        'yards_per_completion': 12.5,
        'rush_yards_per_carry': 4.8,
        'turnover_rate': 0.025,
        'red_zone_td_pct': 0.65,
        'field_goal_pct': 0.80
    }
    
    team2_config = {
        'name': 'Michigan',
        'pass_completion_pct': 0.61,
        'yards_per_completion': 12.0,
        'rush_yards_per_carry': 5.0,
        'turnover_rate': 0.028,
        'red_zone_td_pct': 0.62,
        'field_goal_pct': 0.78,
        'home_field': True
    }
    
    print_quick_analysis(team1_config, team2_config, spread=3.5, total=47.5, num_sims=500)


def example_over_under():
    """Analyze over/under totals."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Over/Under Analysis")
    print("="*70)
    
    # High-scoring teams
    team1_config = {
        'name': 'Oklahoma',
        'pass_completion_pct': 0.68,
        'yards_per_completion': 14.0,
        'rush_yards_per_carry': 5.0,
        'turnover_rate': 0.025,
        'red_zone_td_pct': 0.68,
        'field_goal_pct': 0.78,
        'pace_factor': 1.1  # Faster pace
    }
    
    team2_config = {
        'name': 'Texas',
        'pass_completion_pct': 0.65,
        'yards_per_completion': 13.5,
        'rush_yards_per_carry': 4.8,
        'turnover_rate': 0.028,
        'red_zone_td_pct': 0.65,
        'field_goal_pct': 0.76,
        'pace_factor': 1.05
    }
    
    analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=1000)
    analyzer.run_simulations()
    
    stats = analyzer.get_statistics()
    
    print(f"\nAverage Combined Score: {stats['avg_total']:.1f}")
    
    # Test different totals
    totals = [50.5, 55.5, 60.5, 65.5]
    
    print(f"\n{'Total':<10} {'Over %':<15} {'Under %':<15} {'Pick'}")
    print("-" * 50)
    
    for total in totals:
        total_analysis = analyzer.analyze_total(total)
        pick = f"Over {total}" if total_analysis['over_pct'] > total_analysis['under_pct'] else f"Under {total}"
        print(f"{total:<10} {total_analysis['over_pct']:.1f}%{' ':9} {total_analysis['under_pct']:.1f}%{' ':9} {pick} ({total_analysis['confidence']})")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" "*10 + "🏈 COLLEGE FOOTBALL SIMULATOR EXAMPLES 🏈")
    print("="*70)
    
    # Run examples (skip verbose game for cleaner output)
    # example_basic_game()  # Uncomment to see full game simulation
    
    example_spread_analysis()
    example_find_value_picks()
    example_rivalry_game()
    example_over_under()
    
    print("\n" + "="*70)
    print(" "*20 + "EXAMPLES COMPLETE")
    print("="*70)
    print("\nTo run a single game with full output: python3 football_simulator.py")
    print("To analyze spreads: python3 football_spread_analyzer.py")
    print("To find picks: python3 football_find_picks.py")
    print("="*70)


if __name__ == "__main__":
    main()
