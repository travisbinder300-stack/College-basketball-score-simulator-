"""
Sam Houston vs Texas Southern Simulation
Betting Lines: Sam Houston -6.5, Texas Southern +6.5, Total 159.5

This simulation analyzes the Sam Houston vs Texas Southern matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_sam_houston_vs_texas_southern():
    """
    Create Sam Houston and Texas Southern teams with realistic 2024-25 statistics
    """
    
    # Sam Houston Bearkats - Solid mid-major program
    sam_houston = TeamStats(
        name="Sam Houston Bearkats",
        offensive_efficiency=113.8,   # Good offense
        defensive_efficiency=100.5,   # Average defense
        pace=71.2,                     # Average pace
        three_point_rate=0.38,         # 38% of shots are 3PT
        three_point_percentage=0.35,   # 35% from three
        two_point_percentage=0.52,     # 52% from two
        free_throw_rate=0.34,          # Average free throw rate
        free_throw_percentage=0.73,    # 73% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.30,   # 30% offensive rebound rate
        performance_variance=0.055     # 5.5% variance
    )
    
    # Texas Southern Tigers - SWAC team, typically weaker competition
    texas_southern = TeamStats(
        name="Texas Southern Tigers",
        offensive_efficiency=106.5,    # Below average offense
        defensive_efficiency=107.2,    # Below average defense
        pace=70.8,                      # Average pace
        three_point_rate=0.36,          # 36% of shots are 3PT
        three_point_percentage=0.32,    # 32% from three
        two_point_percentage=0.49,      # 49% from two
        free_throw_rate=0.31,           # Below average free throw rate
        free_throw_percentage=0.70,     # 70% FT shooting
        turnover_rate=0.18,             # 18% turnover rate (higher)
        offensive_rebound_rate=0.28,    # 28% offensive rebound rate
        performance_variance=0.065      # 6.5% variance
    )
    
    return sam_houston, texas_southern


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SAM HOUSTON vs TEXAS SOUTHERN SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Sam Houston: -6.5")
    print("  Texas Southern: +6.5")
    print("  Total (Over/Under): 159.5")
    print("="*70 + "\n")
    
    # Create teams (Sam Houston as team1, Texas Southern as team2)
    sam_houston, texas_southern = create_sam_houston_vs_texas_southern()
    
    # Run simulation
    simulator = GameSimulator(sam_houston, texas_southern)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Sam Houston moneyline analysis (typical for -6.5 favorite is around -280 to -300)
    print("\n\nANALYSIS 1: Sam Houston Moneyline (Favorite)")
    print("-" * 70)
    print("Typical odds for -6.5 favorite: -285")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-285)
    
    # Texas Southern moneyline analysis (typical for +6.5 underdog is around +230 to +250)
    print("\n\nANALYSIS 2: Texas Southern Moneyline (Underdog)")
    print("-" * 70)
    print("Typical odds for +6.5 underdog: +235")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+235)
    
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
    sam_houston_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                             if (s1 - s2) > spread)
    texas_southern_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                                if (s2 - s1 + spread) >= 0)
    
    sam_houston_cover_pct = (sam_houston_covers / results['num_simulations']) * 100
    texas_southern_cover_pct = (texas_southern_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Sam Houston -6.5 / Texas Southern +6.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Sam Houston)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Sam Houston covers -6.5: {sam_houston_cover_pct:.1f}% ({sam_houston_covers:,} simulations)")
    print(f"Texas Southern covers +6.5: {texas_southern_cover_pct:.1f}% ({texas_southern_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    if sam_houston_cover_pct > 50:
        print(f"\n\nSam Houston -6.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Sam Houston covers (happens {sam_houston_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Sam Houston -6.5',
            'team2_name': 'Texas Southern +6.5',
            'team1_win_pct': sam_houston_cover_pct,
            'team2_win_pct': texas_southern_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nTexas Southern +6.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Texas Southern covers (happens {texas_southern_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Texas Southern +6.5',
            'team2_name': 'Sam Houston -6.5',
            'team1_win_pct': texas_southern_cover_pct,
            'team2_win_pct': sam_houston_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Sam Houston: {results['team1_win_pct']:.1f}%")
    print(f"  Texas Southern: {results['team2_win_pct']:.1f}%")
    print(f"\nSpread:")
    print(f"  Sam Houston covers -6.5: {sam_houston_cover_pct:.1f}% of simulations")
    print(f"  Texas Southern covers +6.5: {texas_southern_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Sam Houston {results['team1_avg_score']:.1f} - Texas Southern {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Sam Houston by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
