"""
Coppin State vs St. Joseph's Simulation
Betting Lines: St. Joseph's -21.5, Coppin State +21.5, Total 148

This simulation analyzes a potential blowout scenario where an Atlantic 10 team (St. Joseph's)
faces a MEAC opponent (Coppin State) - showcasing significant competitive mismatch.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_coppin_state_vs_st_josephs():
    """
    Create Coppin State and St. Joseph's teams with realistic statistics
    This represents a significant mismatch between programs
    """
    
    # St. Joseph's Hawks - Competitive Atlantic 10 team with strong defense
    st_josephs = TeamStats(
        name="St. Joseph's Hawks",
        offensive_efficiency=114.5,     # Strong offense
        defensive_efficiency=95.8,      # Elite defense
        pace=69.8,                      # Moderate pace
        three_point_rate=0.39,          # 39% of shots are 3PT
        three_point_percentage=0.36,    # 36% from three (good)
        two_point_percentage=0.53,      # 53% from two (very good)
        free_throw_rate=0.34,           # Good at drawing fouls
        free_throw_percentage=0.74,     # 74% FT shooting
        turnover_rate=0.15,             # Low turnover rate (disciplined)
        offensive_rebound_rate=0.31,    # 31% offensive rebound rate
        performance_variance=0.06       # Low variance (consistent)
    )
    
    # Coppin State Eagles - Struggling MEAC program
    coppin_state = TeamStats(
        name="Coppin State Eagles",
        offensive_efficiency=98.2,      # Poor offense
        defensive_efficiency=110.5,     # Very poor defense
        pace=67.5,                      # Slower pace
        three_point_rate=0.35,          # 35% of shots are 3PT
        three_point_percentage=0.30,    # 30% from three (poor)
        two_point_percentage=0.46,      # 46% from two (very poor)
        free_throw_rate=0.29,           # Struggles to draw fouls
        free_throw_percentage=0.67,     # 67% FT shooting
        turnover_rate=0.19,             # 19% turnover rate (very high)
        offensive_rebound_rate=0.24,    # 24% offensive rebound rate
        performance_variance=0.09       # Higher variance (very inconsistent)
    )
    
    return st_josephs, coppin_state


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ST. JOSEPH'S vs COPPIN STATE SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  St. Joseph's: -21.5 (ML -10000)")
    print("  Coppin State: +21.5 (ML +2500)")
    print("  Total (Over/Under): 148")
    print("="*70 + "\n")
    
    # Create teams (St. Joseph's as team1, Coppin State as team2)
    st_josephs, coppin_state = create_coppin_state_vs_st_josephs()
    
    # Run simulation
    simulator = GameSimulator(st_josephs, coppin_state)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # St. Joseph's moneyline analysis
    print("\n\nANALYSIS 1: St. Joseph's Moneyline (Heavy Favorite)")
    print("-" * 70)
    print("Estimated odds: -10000 (extremely prohibitive)")
    print("Note: Moneyline has no value at these odds")
    
    # Coppin State moneyline analysis
    print("\n\nANALYSIS 2: Coppin State Moneyline (Heavy Underdog)")
    print("-" * 70)
    print("Estimated odds: +2500")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+2500)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 148.0
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
    
    spread = 21.5
    st_josephs_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s1 - s2) > spread)
    coppin_state_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s2 - s1 + spread) >= 0)
    
    st_josephs_cover_pct = (st_josephs_covers / results['num_simulations']) * 100
    coppin_state_cover_pct = (coppin_state_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: St. Joseph's -21.5 / Coppin State +21.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (St. Joseph's)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"St. Joseph's covers -21.5: {st_josephs_cover_pct:.1f}% ({st_josephs_covers:,} simulations)")
    print(f"Coppin State covers +21.5: {coppin_state_cover_pct:.1f}% ({coppin_state_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = coppin_state_cover_pct >= 70 and st_josephs_cover_pct < 60
    
    if st_josephs_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nSt. Joseph's -21.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests St. Joseph's covers (happens {st_josephs_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': "St. Joseph's -21.5",
            'team2_name': 'Coppin State +21.5',
            'team1_win_pct': st_josephs_cover_pct,
            'team2_win_pct': coppin_state_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    if coppin_state_cover_pct > 50:
        if not underdog_dominant or st_josephs_cover_pct >= 50:
            print(f"\n\nCoppin State +21.5 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Coppin State covers (happens {coppin_state_cover_pct:.1f}% of the time)")
            if underdog_dominant:
                print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Coppin State +21.5',
                'team2_name': "St. Joseph's -21.5",
                'team1_win_pct': coppin_state_cover_pct,
                'team2_win_pct': st_josephs_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
        else:
            print(f"\n\nCoppin State +21.5 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Coppin State covers (happens {coppin_state_cover_pct:.1f}% of the time)")
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Coppin State +21.5',
                'team2_name': "St. Joseph's -21.5",
                'team1_win_pct': coppin_state_cover_pct,
                'team2_win_pct': st_josephs_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  St. Joseph's: {results['team1_win_pct']:.1f}% (Estimated: -10000)")
    print(f"  Coppin State: {results['team2_win_pct']:.1f}% (Estimated: +2500)")
    print(f"\nSpread:")
    print(f"  St. Joseph's covers -21.5: {st_josephs_cover_pct:.1f}% of simulations")
    print(f"  Coppin State covers +21.5: {coppin_state_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: St. Joseph's {results['team1_avg_score']:.1f} - Coppin State {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: St. Joseph's by {results['avg_margin']:.1f} points")
    print("\nThis blowout scenario demonstrates market inefficiencies in large-spread games.")
    print("\n" + "="*70 + "\n")
