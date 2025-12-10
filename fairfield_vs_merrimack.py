"""
Fairfield vs Merrimack Simulation
Betting Lines: Fairfield +2.5 ML +130, Merrimack -2.5 ML -145, Total 144.5
 
This simulation analyzes the Fairfield vs Merrimack matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_fairfield_vs_merrimack():
    """
    Create Fairfield and Merrimack teams with realistic 2024-25 statistics
    """
    
    # Merrimack Warriors - Competitive MAAC team
    merrimack = TeamStats(
        name="Merrimack Warriors",
        offensive_efficiency=106.8,    # Solid mid-major offense
        defensive_efficiency=102.5,    # Good defense
        pace=69.2,                     # Moderate pace
        three_point_rate=0.37,         # 37% of shots are 3PT
        three_point_percentage=0.34,   # 34% from three
        two_point_percentage=0.51,     # 51% from two
        free_throw_rate=0.34,          # Average free throw rate
        free_throw_percentage=0.72,    # 72% FT shooting
        turnover_rate=0.15,            # 15% turnover rate
        offensive_rebound_rate=0.29,   # 29% offensive rebound rate
        performance_variance=0.06      # 6% variance
    )
    
    # Fairfield Stags - Competitive MAAC team
    fairfield = TeamStats(
        name="Fairfield Stags",
        offensive_efficiency=105.5,    # Solid mid-major offense
        defensive_efficiency=103.8,    # Average defense
        pace=68.5,                     # Moderate-slow pace
        three_point_rate=0.39,         # 39% of shots are 3PT
        three_point_percentage=0.33,   # 33% from three
        two_point_percentage=0.50,     # 50% from two
        free_throw_rate=0.33,          # Average free throw rate
        free_throw_percentage=0.71,    # 71% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.28,   # 28% offensive rebound rate
        performance_variance=0.07      # 7% variance
    )
    
    return merrimack, fairfield


def main():
    """
    Run the Fairfield vs Merrimack simulation with betting analysis
    """
    print("=" * 70)
    print("FAIRFIELD @ MERRIMACK - MONTE CARLO SIMULATION")
    print("Betting Lines: Fairfield +2.5 ML +130, Merrimack -2.5 ML -145, Total 144.5")
    print("=" * 70)
    
    # Create teams
    merrimack, fairfield = create_fairfield_vs_merrimack()
    
    # Run simulation
    simulator = GameSimulator(merrimack, fairfield)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Betting analysis
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Merrimack moneyline analysis
    print("\n\nANALYSIS 1: Merrimack Moneyline (Favorite)")
    print("-" * 70)
    print("Offered odds: -145")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-145)
    
    # Fairfield moneyline analysis
    print("\n\nANALYSIS 2: Fairfield Moneyline (Underdog)")
    print("-" * 70)
    print("Offered odds: +130")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+130)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 144.5
    avg_total = results['team1_avg_score'] + results['team2_avg_score']
    
    # Count how many simulations went over/under
    over_count = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                     if (s1 + s2) > total_line)
    under_count = results['num_simulations'] - over_count
    
    over_pct = (over_count / results['num_simulations']) * 100
    under_pct = (under_count / results['num_simulations']) * 100
    
    print(f"\nTotal Line: {total_line}")
    print(f"Simulated Average Total: {avg_total:.1f}")
    print(f"Difference: {avg_total - total_line:+.1f} points")
    
    print(f"\n{'='*70}")
    print("OVER/UNDER SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Over {total_line}: {over_pct:.1f}% ({over_count:,} simulations)")
    print(f"Under {total_line}: {under_pct:.1f}% ({under_count:,} simulations)")
    
    # Kelly analysis for Over/Under (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR OVER/UNDER")
    print(f"{'='*70}")
    
    if over_pct > 50:
        print(f"\n\nOVER {total_line} Analysis")
        print("-" * 70)
        print(f"Simulation suggests OVER (occurs {over_pct:.1f}% of the time)")
        print("Typical Over odds: -110")
        
        # Create a temporary results dict for Over bet
        over_results = {
            'team1_name': f'OVER {total_line}',
            'team2_name': f'UNDER {total_line}',
            'team1_win_pct': over_pct,
            'team2_win_pct': under_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(over_results, team=1, american_odds=-110)
    else:
        print(f"\n\nUNDER {total_line} Analysis")
        print("-" * 70)
        print(f"Simulation suggests UNDER (occurs {under_pct:.1f}% of the time)")
        print("Typical Under odds: -110")
        
        # Create a temporary results dict for Under bet
        under_results = {
            'team1_name': f'UNDER {total_line}',
            'team2_name': f'OVER {total_line}',
            'team1_win_pct': under_pct,
            'team2_win_pct': over_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(under_results, team=1, american_odds=-110)
    
    # Spread analysis
    print("\n\n" + "="*70)
    print("SPREAD ANALYSIS")
    print("="*70)
    
    spread = 2.5
    
    # Count spread coverage
    merrimack_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                           if (s1 - s2) > spread)
    fairfield_covers = results['num_simulations'] - merrimack_covers
    
    merrimack_cover_pct = (merrimack_covers / results['num_simulations']) * 100
    fairfield_cover_pct = (fairfield_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Merrimack -{spread} / Fairfield +{spread}")
    print(f"Expected Margin: Merrimack by {results['avg_margin']:.1f} points")
    
    print(f"\n{'='*70}")
    print("SPREAD COVERAGE SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Merrimack -{spread}: {merrimack_cover_pct:.1f}% ({merrimack_covers:,} simulations)")
    print(f"Fairfield +{spread}: {fairfield_cover_pct:.1f}% ({fairfield_covers:,} simulations)")
    
    # Check for strong underdog value (suppress favorite if underdog 70%+ and favorite <60%)
    suppress_favorite = fairfield_cover_pct >= 70.0 and merrimack_cover_pct < 60.0
    
    # Kelly analysis for spreads
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Analyze both sides unless suppressed
    if not suppress_favorite and merrimack_cover_pct > 50:
        print(f"\n\nMerrimack -{spread} Analysis")
        print("-" * 70)
        print(f"Simulation suggests Merrimack covers (occurs {merrimack_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        merrimack_spread_results = {
            'team1_name': f'Merrimack -{spread}',
            'team2_name': f'Fairfield +{spread}',
            'team1_win_pct': merrimack_cover_pct,
            'team2_win_pct': fairfield_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(merrimack_spread_results, team=1, american_odds=-110)
    
    if fairfield_cover_pct > 50:
        print(f"\n\nFairfield +{spread} Analysis")
        print("-" * 70)
        print(f"Simulation suggests Fairfield covers (occurs {fairfield_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        if suppress_favorite:
            print("\n*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
        
        fairfield_spread_results = {
            'team1_name': f'Fairfield +{spread}',
            'team2_name': f'Merrimack -{spread}',
            'team1_win_pct': fairfield_cover_pct,
            'team2_win_pct': merrimack_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(fairfield_spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("DISCLAIMER")
    print("="*70)
    print("This is for educational purposes only. Gambling involves risk.")
    print("Never bet more than you can afford to lose. Gamble responsibly.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
