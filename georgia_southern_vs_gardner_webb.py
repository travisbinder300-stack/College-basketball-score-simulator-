"""
Georgia Southern vs Gardner-Webb Simulation
Betting Lines: Georgia Southern -9.5, Gardner-Webb +9.5, Total 160.4

This simulation analyzes the Georgia Southern vs Gardner-Webb matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_georgia_southern_vs_gardner_webb():
    """
    Create Georgia Southern and Gardner-Webb teams with realistic 2024-25 statistics
    """
    
    # Georgia Southern Eagles - Stronger team, solid on both ends
    georgia_southern = TeamStats(
        name="Georgia Southern Eagles",
        offensive_efficiency=115.2,   # Good offense
        defensive_efficiency=99.8,    # Good defense
        pace=72.2,                     # Above average pace
        three_point_rate=0.39,         # 39% of shots are 3PT
        three_point_percentage=0.36,   # 36% from three
        two_point_percentage=0.53,     # 53% from two
        free_throw_rate=0.35,          # Average free throw rate
        free_throw_percentage=0.73,    # 73% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.31,   # 31% offensive rebound rate
        performance_variance=0.055     # 5.5% variance
    )
    
    # Gardner-Webb Bulldogs - Underdog, weaker team
    gardner_webb = TeamStats(
        name="Gardner-Webb Bulldogs",
        offensive_efficiency=107.8,    # Below average offense
        defensive_efficiency=105.5,    # Below average defense
        pace=70.5,                      # Average pace
        three_point_rate=0.37,          # 37% of shots are 3PT
        three_point_percentage=0.33,    # 33% from three
        two_point_percentage=0.50,      # 50% from two
        free_throw_rate=0.32,           # Below average free throw rate
        free_throw_percentage=0.71,     # 71% FT shooting
        turnover_rate=0.18,             # 18% turnover rate (higher)
        offensive_rebound_rate=0.28,    # 28% offensive rebound rate
        performance_variance=0.065      # 6.5% variance
    )
    
    return georgia_southern, gardner_webb


if __name__ == "__main__":
    print("\n" + "="*70)
    print("GEORGIA SOUTHERN vs GARDNER-WEBB SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Georgia Southern: -9.5")
    print("  Gardner-Webb: +9.5")
    print("  Total (Over/Under): 160.4")
    print("="*70 + "\n")
    
    # Create teams (Georgia Southern as team1, Gardner-Webb as team2)
    georgia_southern, gardner_webb = create_georgia_southern_vs_gardner_webb()
    
    # Run simulation
    simulator = GameSimulator(georgia_southern, gardner_webb)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Georgia Southern moneyline analysis (typical for -9.5 favorite is around -400 to -450)
    print("\n\nANALYSIS 1: Georgia Southern Moneyline (Favorite)")
    print("-" * 70)
    print("Typical odds for -9.5 favorite: -420")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-420)
    
    # Gardner-Webb moneyline analysis (typical for +9.5 underdog is around +320 to +350)
    print("\n\nANALYSIS 2: Gardner-Webb Moneyline (Underdog)")
    print("-" * 70)
    print("Typical odds for +9.5 underdog: +330")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+330)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 160.4
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
    georgia_southern_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                                  if (s1 - s2) > spread)
    gardner_webb_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                              if (s2 - s1 + spread) >= 0)
    
    georgia_southern_cover_pct = (georgia_southern_covers / results['num_simulations']) * 100
    gardner_webb_cover_pct = (gardner_webb_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Georgia Southern -9.5 / Gardner-Webb +9.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Georgia Southern)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Georgia Southern covers -9.5: {georgia_southern_cover_pct:.1f}% ({georgia_southern_covers:,} simulations)")
    print(f"Gardner-Webb covers +9.5: {gardner_webb_cover_pct:.1f}% ({gardner_webb_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    if georgia_southern_cover_pct > 50:
        print(f"\n\nGeorgia Southern -9.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Georgia Southern covers (happens {georgia_southern_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Georgia Southern -9.5',
            'team2_name': 'Gardner-Webb +9.5',
            'team1_win_pct': georgia_southern_cover_pct,
            'team2_win_pct': gardner_webb_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nGardner-Webb +9.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Gardner-Webb covers (happens {gardner_webb_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Gardner-Webb +9.5',
            'team2_name': 'Georgia Southern -9.5',
            'team1_win_pct': gardner_webb_cover_pct,
            'team2_win_pct': georgia_southern_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Georgia Southern: {results['team1_win_pct']:.1f}%")
    print(f"  Gardner-Webb: {results['team2_win_pct']:.1f}%")
    print(f"\nSpread:")
    print(f"  Georgia Southern covers -9.5: {georgia_southern_cover_pct:.1f}% of simulations")
    print(f"  Gardner-Webb covers +9.5: {gardner_webb_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Georgia Southern {results['team1_avg_score']:.1f} - Gardner-Webb {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Georgia Southern by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
