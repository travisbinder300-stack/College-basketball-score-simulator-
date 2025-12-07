"""
Dayton vs Virginia Simulation
Betting Lines: Dayton +6.5, Virginia -6.5, Total 145

This simulation analyzes the Dayton vs Virginia matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_dayton_vs_virginia():
    """
    Create Dayton and Virginia teams with realistic 2024-25 statistics
    """
    
    # Virginia Cavaliers - Elite defense, slower pace (classic Tony Bennett style)
    virginia = TeamStats(
        name="Virginia Cavaliers",
        offensive_efficiency=110.2,   # Good offense
        defensive_efficiency=91.5,    # Elite defense
        pace=63.8,                     # Very slow pace (pack line defense)
        three_point_rate=0.35,         # 35% of shots are 3PT
        three_point_percentage=0.36,   # 36% from three
        two_point_percentage=0.52,     # 52% from two
        free_throw_rate=0.30,          # Average free throw rate
        free_throw_percentage=0.72,    # 72% FT shooting
        turnover_rate=0.13,            # 13% turnover rate (low)
        offensive_rebound_rate=0.28,   # 28% offensive rebound rate
        performance_variance=0.04      # 4% variance (very consistent)
    )
    
    # Dayton Flyers - Balanced offense and defense, moderate pace
    dayton = TeamStats(
        name="Dayton Flyers",
        offensive_efficiency=112.8,    # Good offense
        defensive_efficiency=98.5,     # Good defense
        pace=69.5,                      # Moderate pace
        three_point_rate=0.38,          # 38% of shots are 3PT
        three_point_percentage=0.35,    # 35% from three
        two_point_percentage=0.53,      # 53% from two
        free_throw_rate=0.33,           # Average free throw rate
        free_throw_percentage=0.73,     # 73% FT shooting
        turnover_rate=0.16,             # 16% turnover rate
        offensive_rebound_rate=0.30,    # 30% offensive rebound rate
        performance_variance=0.055      # 5.5% variance
    )
    
    return virginia, dayton


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DAYTON vs VIRGINIA SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Virginia: -6.5")
    print("  Dayton: +6.5")
    print("  Total (Over/Under): 145")
    print("="*70 + "\n")
    
    # Create teams (Virginia as team1, Dayton as team2)
    virginia, dayton = create_dayton_vs_virginia()
    
    # Run simulation
    simulator = GameSimulator(virginia, dayton)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Virginia moneyline analysis (typical for -6.5 favorite is around -250 to -280)
    print("\n\nANALYSIS 1: Virginia Moneyline (Favorite)")
    print("-" * 70)
    print("Typical odds for -6.5 favorite: -260")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-260)
    
    # Dayton moneyline analysis (typical for +6.5 underdog is around +210 to +230)
    print("\n\nANALYSIS 2: Dayton Moneyline (Underdog)")
    print("-" * 70)
    print("Typical odds for +6.5 underdog: +215")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+215)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 145.0
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
    
    spread = 6.5
    virginia_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                          if (s1 - s2) > spread)
    dayton_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s2 - s1 + spread) >= 0)
    
    virginia_cover_pct = (virginia_covers / results['num_simulations']) * 100
    dayton_cover_pct = (dayton_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Virginia -6.5 / Dayton +6.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Virginia)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Virginia covers -6.5: {virginia_cover_pct:.1f}% ({virginia_covers:,} simulations)")
    print(f"Dayton covers +6.5: {dayton_cover_pct:.1f}% ({dayton_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    if virginia_cover_pct > 50:
        print(f"\n\nVirginia -6.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Virginia covers (happens {virginia_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Virginia -6.5',
            'team2_name': 'Dayton +6.5',
            'team1_win_pct': virginia_cover_pct,
            'team2_win_pct': dayton_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nDayton +6.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Dayton covers (happens {dayton_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Dayton +6.5',
            'team2_name': 'Virginia -6.5',
            'team1_win_pct': dayton_cover_pct,
            'team2_win_pct': virginia_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Virginia: {results['team1_win_pct']:.1f}%")
    print(f"  Dayton: {results['team2_win_pct']:.1f}%")
    print(f"\nSpread:")
    print(f"  Virginia covers -6.5: {virginia_cover_pct:.1f}% of simulations")
    print(f"  Dayton covers +6.5: {dayton_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Virginia {results['team1_avg_score']:.1f} - Dayton {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Virginia by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
