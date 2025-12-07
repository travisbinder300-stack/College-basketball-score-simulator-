"""
Duke vs Michigan State Simulation
Betting Lines: Duke -1.0, Michigan State +1.0, Total 141.5

This simulation analyzes the Duke vs Michigan State matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_duke_vs_michigan_state():
    """
    Create Duke and Michigan State teams with realistic 2024-25 statistics
    """
    
    # Duke Blue Devils - High-powered offense, solid defense
    duke = TeamStats(
        name="Duke Blue Devils",
        offensive_efficiency=118.5,  # Elite offense
        defensive_efficiency=98.2,   # Good defense
        pace=72.5,                    # Above average pace
        three_point_rate=0.42,        # 42% of shots are 3PT
        three_point_percentage=0.38,  # 38% from three
        two_point_percentage=0.56,    # 56% from two
        free_throw_rate=0.38,         # Good at drawing fouls
        free_throw_percentage=0.75,   # 75% FT shooting
        turnover_rate=0.16,           # 16% turnover rate
        offensive_rebound_rate=0.32,  # 32% offensive rebound rate
        performance_variance=0.06     # 6% game-to-game variance
    )
    
    # Michigan State Spartans - Balanced team, strong defense
    michigan_state = TeamStats(
        name="Michigan State Spartans",
        offensive_efficiency=114.8,   # Good offense
        defensive_efficiency=96.5,    # Strong defense
        pace=70.2,                     # Average pace
        three_point_rate=0.38,         # 38% of shots are 3PT
        three_point_percentage=0.36,   # 36% from three
        two_point_percentage=0.54,     # 54% from two
        free_throw_rate=0.35,          # Average free throw rate
        free_throw_percentage=0.73,    # 73% FT shooting
        turnover_rate=0.15,            # 15% turnover rate
        offensive_rebound_rate=0.30,   # 30% offensive rebound rate
        performance_variance=0.05      # 5% variance (consistent)
    )
    
    return duke, michigan_state


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DUKE vs MICHIGAN STATE SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Duke: -1.0 (slight favorite)")
    print("  Michigan State: +1.0")
    print("  Total (Over/Under): 141.5")
    print("="*70 + "\n")
    
    # Create teams
    duke, michigan_state = create_duke_vs_michigan_state()
    
    # Run simulation
    simulator = GameSimulator(duke, michigan_state)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Duke moneyline analysis
    # -1.0 spread typically correlates to around -110 to -115 moneyline odds
    print("\n\nANALYSIS 1: Duke Moneyline")
    print("-" * 70)
    print("Typical odds for -1.0 favorite: -110")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-110)
    
    # Michigan State moneyline analysis
    print("\n\nANALYSIS 2: Michigan State Moneyline")
    print("-" * 70)
    print("Typical odds for +1.0 underdog: -110")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=-110)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 141.5
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
        KellyCriterion.analyze_betting_opportunity(over_results, team=1, american_odds=-110, is_total=True)
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
        KellyCriterion.analyze_betting_opportunity(under_results, team=1, american_odds=-110, is_total=True)
    
    # Spread analysis
    print("\n\n" + "="*70)
    print("SPREAD ANALYSIS")
    print("="*70)
    
    spread = 1.0
    duke_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                      if (s1 - s2) > spread)
    msu_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                     if (s2 - s1 + spread) >= 0)
    
    duke_cover_pct = (duke_covers / results['num_simulations']) * 100
    msu_cover_pct = (msu_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Duke -1.0 / Michigan State +1.0")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Duke)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Duke covers -1.0: {duke_cover_pct:.1f}% ({duke_covers:,} simulations)")
    print(f"Michigan State covers +1.0: {msu_cover_pct:.1f}% ({msu_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    if duke_cover_pct > 50:
        print(f"\n\nDuke -1.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Duke covers (happens {duke_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Duke -1.0',
            'team2_name': 'Michigan State +1.0',
            'team1_win_pct': duke_cover_pct,
            'team2_win_pct': msu_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nMichigan State +1.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Michigan State covers (happens {msu_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Michigan State +1.0',
            'team2_name': 'Duke -1.0',
            'team1_win_pct': msu_cover_pct,
            'team2_win_pct': duke_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline: Duke {results['team1_win_pct']:.1f}% vs Michigan State {results['team2_win_pct']:.1f}%")
    print(f"Spread: Duke covers -1.0 {duke_cover_pct:.1f}% of the time")
    print(f"Total: Over {total_line} hits {over_pct:.1f}% of the time")
    print(f"Expected Final Score: Duke {results['team1_avg_score']:.1f} - Michigan State {results['team2_avg_score']:.1f}")
    print("\n" + "="*70 + "\n")
