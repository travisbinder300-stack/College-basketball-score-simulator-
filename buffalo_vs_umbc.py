"""
Buffalo vs UMBC Simulation
Betting Lines: Buffalo -3.5 (ML -162), UMBC +3.5 (ML +133), Total 145

This simulation analyzes the Buffalo vs UMBC matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_buffalo_vs_umbc():
    """
    Create Buffalo and UMBC teams with realistic statistics
    """
    
    # Buffalo Bulls - Solid mid-major with balanced attack
    buffalo = TeamStats(
        name="Buffalo Bulls",
        offensive_efficiency=111.5,    # Good offense
        defensive_efficiency=98.2,     # Good defense
        pace=69.5,                      # Moderate pace
        three_point_rate=0.38,          # 38% of shots are 3PT
        three_point_percentage=0.35,    # 35% from three
        two_point_percentage=0.52,      # 52% from two
        free_throw_rate=0.33,           # Average free throw rate
        free_throw_percentage=0.73,     # 73% FT shooting
        turnover_rate=0.16,             # 16% turnover rate
        offensive_rebound_rate=0.29,    # 29% offensive rebound rate
        performance_variance=0.06       # 6% variance
    )
    
    # UMBC Retrievers - Scrappy underdog, defensive-minded
    umbc = TeamStats(
        name="UMBC Retrievers",
        offensive_efficiency=105.8,     # Below average offense
        defensive_efficiency=101.5,     # Below average defense
        pace=68.8,                       # Slower pace
        three_point_rate=0.37,           # 37% of shots are 3PT
        three_point_percentage=0.33,     # 33% from three
        two_point_percentage=0.49,       # 49% from two
        free_throw_rate=0.32,            # Average free throw rate
        free_throw_percentage=0.71,      # 71% FT shooting
        turnover_rate=0.17,              # 17% turnover rate
        offensive_rebound_rate=0.27,     # 27% offensive rebound rate
        performance_variance=0.07        # 7% variance
    )
    
    return buffalo, umbc


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BUFFALO vs UMBC SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Buffalo: -3.5 (ML -162)")
    print("  UMBC: +3.5 (ML +133)")
    print("  Total (Over/Under): 145")
    print("="*70 + "\n")
    
    # Create teams (Buffalo as team1, UMBC as team2)
    buffalo, umbc = create_buffalo_vs_umbc()
    
    # Run simulation
    simulator = GameSimulator(buffalo, umbc)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Buffalo moneyline analysis
    print("\n\nANALYSIS 1: Buffalo Moneyline (Favorite)")
    print("-" * 70)
    print("Offered odds: -162")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-162)
    
    # UMBC moneyline analysis
    print("\n\nANALYSIS 2: UMBC Moneyline (Underdog)")
    print("-" * 70)
    print("Offered odds: +133")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+133)
    
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
    
    spread = 3.5
    buffalo_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s1 - s2) > spread)
    umbc_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s2 - s1 + spread) >= 0)
    
    buffalo_cover_pct = (buffalo_covers / results['num_simulations']) * 100
    umbc_cover_pct = (umbc_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Buffalo -3.5 / UMBC +3.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Buffalo)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Buffalo covers -3.5: {buffalo_cover_pct:.1f}% ({buffalo_covers:,} simulations)")
    print(f"UMBC covers +3.5: {umbc_cover_pct:.1f}% ({umbc_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = umbc_cover_pct >= 70 and buffalo_cover_pct < 60
    
    if buffalo_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nBuffalo -3.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Buffalo covers (happens {buffalo_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Buffalo -3.5',
            'team2_name': 'UMBC +3.5',
            'team1_win_pct': buffalo_cover_pct,
            'team2_win_pct': umbc_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    if umbc_cover_pct > 50:
        if not underdog_dominant or buffalo_cover_pct >= 50:
            print(f"\n\nUMBC +3.5 Analysis")
            print("-" * 70)
            print(f"Simulation suggests UMBC covers (happens {umbc_cover_pct:.1f}% of the time)")
            if underdog_dominant:
                print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'UMBC +3.5',
                'team2_name': 'Buffalo -3.5',
                'team1_win_pct': umbc_cover_pct,
                'team2_win_pct': buffalo_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
        else:
            print(f"\n\nUMBC +3.5 Analysis")
            print("-" * 70)
            print(f"Simulation suggests UMBC covers (happens {umbc_cover_pct:.1f}% of the time)")
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'UMBC +3.5',
                'team2_name': 'Buffalo -3.5',
                'team1_win_pct': umbc_cover_pct,
                'team2_win_pct': buffalo_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Buffalo: {results['team1_win_pct']:.1f}% (Offered: -162)")
    print(f"  UMBC: {results['team2_win_pct']:.1f}% (Offered: +133)")
    print(f"\nSpread:")
    print(f"  Buffalo covers -3.5: {buffalo_cover_pct:.1f}% of simulations")
    print(f"  UMBC covers +3.5: {umbc_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Buffalo {results['team1_avg_score']:.1f} - UMBC {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Buffalo by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
