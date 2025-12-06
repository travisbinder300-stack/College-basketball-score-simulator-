"""
Rhode Island vs Providence Simulation
Betting Lines: Rhode Island +8, Providence -8, Total 159.5

This simulation analyzes the Rhode Island vs Providence matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_rhode_island_vs_providence():
    """
    Create Rhode Island and Providence teams with realistic 2024-25 statistics
    """
    
    # Providence Friars - Strong offensive team, up-tempo
    providence = TeamStats(
        name="Providence Friars",
        offensive_efficiency=116.5,   # Strong offense
        defensive_efficiency=100.2,   # Average defense
        pace=71.8,                     # Above average pace
        three_point_rate=0.40,         # 40% of shots are 3PT
        three_point_percentage=0.36,   # 36% from three
        two_point_percentage=0.54,     # 54% from two
        free_throw_rate=0.36,          # Good at drawing fouls
        free_throw_percentage=0.74,    # 74% FT shooting
        turnover_rate=0.15,            # 15% turnover rate
        offensive_rebound_rate=0.31,   # 31% offensive rebound rate
        performance_variance=0.06      # 6% variance
    )
    
    # Rhode Island Rams - Moderate offense and defense
    rhode_island = TeamStats(
        name="Rhode Island Rams",
        offensive_efficiency=109.5,    # Decent offense
        defensive_efficiency=103.8,    # Below average defense
        pace=70.2,                      # Average pace
        three_point_rate=0.37,          # 37% of shots are 3PT
        three_point_percentage=0.34,    # 34% from three
        two_point_percentage=0.51,      # 51% from two
        free_throw_rate=0.33,           # Average free throw rate
        free_throw_percentage=0.72,     # 72% FT shooting
        turnover_rate=0.17,             # 17% turnover rate
        offensive_rebound_rate=0.29,    # 29% offensive rebound rate
        performance_variance=0.06       # 6% variance
    )
    
    return providence, rhode_island


if __name__ == "__main__":
    print("\n" + "="*70)
    print("RHODE ISLAND vs PROVIDENCE SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Providence: -8")
    print("  Rhode Island: +8")
    print("  Total (Over/Under): 159.5")
    print("="*70 + "\n")
    
    # Create teams (Providence as team1, Rhode Island as team2)
    providence, rhode_island = create_rhode_island_vs_providence()
    
    # Run simulation
    simulator = GameSimulator(providence, rhode_island)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Providence moneyline analysis (typical for -8 favorite is around -350 to -400)
    print("\n\nANALYSIS 1: Providence Moneyline (Favorite)")
    print("-" * 70)
    print("Typical odds for -8 favorite: -360")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-360)
    
    # Rhode Island moneyline analysis (typical for +8 underdog is around +280 to +320)
    print("\n\nANALYSIS 2: Rhode Island Moneyline (Underdog)")
    print("-" * 70)
    print("Typical odds for +8 underdog: +285")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+285)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 159.5
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
    
    spread = 8.0
    providence_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s1 - s2) > spread)
    rhode_island_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                              if (s2 - s1 + spread) >= 0)
    
    providence_cover_pct = (providence_covers / results['num_simulations']) * 100
    rhode_island_cover_pct = (rhode_island_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Providence -8.0 / Rhode Island +8.0")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Providence)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Providence covers -8.0: {providence_cover_pct:.1f}% ({providence_covers:,} simulations)")
    print(f"Rhode Island covers +8.0: {rhode_island_cover_pct:.1f}% ({rhode_island_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    if providence_cover_pct > 50:
        print(f"\n\nProvidence -8.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Providence covers (happens {providence_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Providence -8.0',
            'team2_name': 'Rhode Island +8.0',
            'team1_win_pct': providence_cover_pct,
            'team2_win_pct': rhode_island_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nRhode Island +8.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Rhode Island covers (happens {rhode_island_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Rhode Island +8.0',
            'team2_name': 'Providence -8.0',
            'team1_win_pct': rhode_island_cover_pct,
            'team2_win_pct': providence_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Providence: {results['team1_win_pct']:.1f}%")
    print(f"  Rhode Island: {results['team2_win_pct']:.1f}%")
    print(f"\nSpread:")
    print(f"  Providence covers -8.0: {providence_cover_pct:.1f}% of simulations")
    print(f"  Rhode Island covers +8.0: {rhode_island_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Providence {results['team1_avg_score']:.1f} - Rhode Island {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Providence by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
