"""
Clemson vs BYU Simulation
Betting Lines: BYU -5.5 (ML -220), Clemson +5.5 (ML +180), Total 147

This simulation analyzes the Clemson vs BYU matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_clemson_vs_byu():
    """
    Create Clemson and BYU teams with realistic statistics
    """
    
    # BYU Cougars - Strong offensive team with solid defense
    byu = TeamStats(
        name="BYU Cougars",
        offensive_efficiency=113.2,    # Strong offense
        defensive_efficiency=99.8,     # Good defense
        pace=71.2,                      # Above average pace
        three_point_rate=0.39,          # 39% of shots are 3PT
        three_point_percentage=0.36,    # 36% from three
        two_point_percentage=0.53,      # 53% from two
        free_throw_rate=0.34,           # Good free throw rate
        free_throw_percentage=0.75,     # 75% FT shooting
        turnover_rate=0.15,             # 15% turnover rate
        offensive_rebound_rate=0.31,    # 31% offensive rebound rate
        performance_variance=0.06       # 6% variance
    )
    
    # Clemson Tigers - Balanced team, competitive underdog
    clemson = TeamStats(
        name="Clemson Tigers",
        offensive_efficiency=108.5,     # Decent offense
        defensive_efficiency=102.3,     # Average defense
        pace=70.5,                       # Moderate pace
        three_point_rate=0.37,           # 37% of shots are 3PT
        three_point_percentage=0.34,     # 34% from three
        two_point_percentage=0.50,       # 50% from two
        free_throw_rate=0.32,            # Average free throw rate
        free_throw_percentage=0.72,      # 72% FT shooting
        turnover_rate=0.16,              # 16% turnover rate
        offensive_rebound_rate=0.28,     # 28% offensive rebound rate
        performance_variance=0.07        # 7% variance
    )
    
    return byu, clemson


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BYU vs CLEMSON SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  BYU: -5.5 (ML -220)")
    print("  Clemson: +5.5 (ML +180)")
    print("  Total (Over/Under): 147")
    print("="*70 + "\n")
    
    # Create teams (BYU as team1, Clemson as team2)
    byu, clemson = create_clemson_vs_byu()
    
    # Run simulation
    simulator = GameSimulator(byu, clemson)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # BYU moneyline analysis
    print("\n\nANALYSIS 1: BYU Moneyline (Favorite)")
    print("-" * 70)
    print("Offered odds: -220")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-220)
    
    # Clemson moneyline analysis
    print("\n\nANALYSIS 2: Clemson Moneyline (Underdog)")
    print("-" * 70)
    print("Offered odds: +180")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+180)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 147.0
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
    
    spread = 5.5
    byu_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s1 - s2) > spread)
    clemson_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s2 - s1 + spread) >= 0)
    
    byu_cover_pct = (byu_covers / results['num_simulations']) * 100
    clemson_cover_pct = (clemson_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: BYU -5.5 / Clemson +5.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (BYU)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"BYU covers -5.5: {byu_cover_pct:.1f}% ({byu_covers:,} simulations)")
    print(f"Clemson covers +5.5: {clemson_cover_pct:.1f}% ({clemson_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = clemson_cover_pct >= 70 and byu_cover_pct < 60
    
    if byu_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nBYU -5.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests BYU covers (happens {byu_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'BYU -5.5',
            'team2_name': 'Clemson +5.5',
            'team1_win_pct': byu_cover_pct,
            'team2_win_pct': clemson_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    if clemson_cover_pct > 50:
        if not underdog_dominant or byu_cover_pct >= 50:
            print(f"\n\nClemson +5.5 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Clemson covers (happens {clemson_cover_pct:.1f}% of the time)")
            if underdog_dominant:
                print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Clemson +5.5',
                'team2_name': 'BYU -5.5',
                'team1_win_pct': clemson_cover_pct,
                'team2_win_pct': byu_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
        else:
            print(f"\n\nClemson +5.5 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Clemson covers (happens {clemson_cover_pct:.1f}% of the time)")
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Clemson +5.5',
                'team2_name': 'BYU -5.5',
                'team1_win_pct': clemson_cover_pct,
                'team2_win_pct': byu_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  BYU: {results['team1_win_pct']:.1f}% (Offered: -220)")
    print(f"  Clemson: {results['team2_win_pct']:.1f}% (Offered: +180)")
    print(f"\nSpread:")
    print(f"  BYU covers -5.5: {byu_cover_pct:.1f}% of simulations")
    print(f"  Clemson covers +5.5: {clemson_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: BYU {results['team1_avg_score']:.1f} - Clemson {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: BYU by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
