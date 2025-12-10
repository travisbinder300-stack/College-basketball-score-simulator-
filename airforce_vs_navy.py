"""
Air Force vs Navy Simulation
Betting Lines: Air Force +9.5, Navy -9.5, Total 137.0

This simulation analyzes the Air Force vs Navy matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_airforce_vs_navy():
    """
    Create Air Force and Navy teams with realistic 2024-25 statistics
    """
    
    # Navy Midshipmen - Disciplined, defensive-minded service academy
    navy = TeamStats(
        name="Navy Midshipmen",
        offensive_efficiency=102.5,    # Below-average offense
        defensive_efficiency=98.2,     # Good defense
        pace=64.5,                     # Very slow, methodical pace
        three_point_rate=0.33,         # 33% of shots are 3PT
        three_point_percentage=0.33,   # 33% from three
        two_point_percentage=0.51,     # 51% from two
        free_throw_rate=0.32,          # Average free throw rate
        free_throw_percentage=0.71,    # 71% FT shooting
        turnover_rate=0.15,            # 15% turnover rate (disciplined)
        offensive_rebound_rate=0.28,   # 28% offensive rebound rate
        performance_variance=0.05      # 5% variance (consistent)
    )
    
    # Air Force Falcons - Up-tempo for a service academy, solid fundamentals
    airforce = TeamStats(
        name="Air Force Falcons",
        offensive_efficiency=98.8,     # Below-average offense
        defensive_efficiency=102.5,    # Below-average defense
        pace=66.2,                     # Slow pace
        three_point_rate=0.36,         # 36% of shots are 3PT
        three_point_percentage=0.32,   # 32% from three
        two_point_percentage=0.49,     # 49% from two
        free_throw_rate=0.30,          # Below-average free throw rate
        free_throw_percentage=0.70,    # 70% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.27,   # 27% offensive rebound rate
        performance_variance=0.06      # 6% variance
    )
    
    return navy, airforce


if __name__ == "__main__":
    print("\n" + "="*70)
    print("AIR FORCE vs NAVY SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Navy: -9.5")
    print("  Air Force: +9.5")
    print("  Total (Over/Under): 137.0")
    print("="*70 + "\n")
    
    # Create teams (Navy as team1, Air Force as team2)
    navy, airforce = create_airforce_vs_navy()
    
    # Run simulation
    simulator = GameSimulator(navy, airforce)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Navy moneyline analysis (would need odds for full analysis)
    print("\n\nANALYSIS 1: Navy Moneyline (Favorite)")
    print("-" * 70)
    print("Offered odds: -400 (estimated)")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-400)
    
    # Air Force moneyline analysis
    print("\n\nANALYSIS 2: Air Force Moneyline (Underdog)")
    print("-" * 70)
    print("Offered odds: +310 (estimated)")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+310)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 137.0
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
    
    spread = 9.5
    navy_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s1 - s2) > spread)
    airforce_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s2 - s1 + spread) >= 0)
    
    navy_cover_pct = (navy_covers / results['num_simulations']) * 100
    airforce_cover_pct = (airforce_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Navy -9.5 / Air Force +9.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Navy)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Navy covers -9.5: {navy_cover_pct:.1f}% ({navy_covers:,} simulations)")
    print(f"Air Force covers +9.5: {airforce_cover_pct:.1f}% ({airforce_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = airforce_cover_pct >= 70 and navy_cover_pct < 60
    
    if navy_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nNavy -9.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Navy covers (happens {navy_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Navy -9.5',
            'team2_name': 'Air Force +9.5',
            'team1_win_pct': navy_cover_pct,
            'team2_win_pct': airforce_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nAir Force +9.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Air Force covers (happens {airforce_cover_pct:.1f}% of the time)")
        if underdog_dominant:
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Air Force +9.5',
            'team2_name': 'Navy -9.5',
            'team1_win_pct': airforce_cover_pct,
            'team2_win_pct': navy_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Navy: {results['team1_win_pct']:.1f}%")
    print(f"  Air Force: {results['team2_win_pct']:.1f}%")
    print(f"\nSpread:")
    print(f"  Navy covers -9.5: {navy_cover_pct:.1f}% of simulations")
    print(f"  Air Force covers +9.5: {airforce_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Navy {results['team1_avg_score']:.1f} - Air Force {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Navy by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
