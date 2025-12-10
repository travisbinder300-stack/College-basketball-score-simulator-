"""
Detroit vs Cleveland State Simulation
Betting Lines: Detroit +2.5, Cleveland State -2.5, Total 162.5

This simulation analyzes the Detroit vs Cleveland State matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_detroit_vs_cleveland_state():
    """
    Create Detroit and Cleveland State teams with realistic 2024-25 statistics
    """
    
    # Cleveland State Vikings - Solid balanced team
    cleveland_state = TeamStats(
        name="Cleveland State Vikings",
        offensive_efficiency=112.5,   # Good offense
        defensive_efficiency=101.2,   # Average defense
        pace=70.8,                     # Average pace
        three_point_rate=0.38,         # 38% of shots are 3PT
        three_point_percentage=0.35,   # 35% from three
        two_point_percentage=0.52,     # 52% from two
        free_throw_rate=0.34,          # Average free throw rate
        free_throw_percentage=0.73,    # 73% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.30,   # 30% offensive rebound rate
        performance_variance=0.055     # 5.5% variance
    )
    
    # Detroit Mercy Titans - Similar caliber team
    detroit = TeamStats(
        name="Detroit Mercy Titans",
        offensive_efficiency=111.2,    # Good offense
        defensive_efficiency=102.5,    # Average defense
        pace=71.5,                      # Slightly faster pace
        three_point_rate=0.39,          # 39% of shots are 3PT
        three_point_percentage=0.35,    # 35% from three
        two_point_percentage=0.52,      # 52% from two
        free_throw_rate=0.35,           # Average free throw rate
        free_throw_percentage=0.72,     # 72% FT shooting
        turnover_rate=0.17,             # 17% turnover rate
        offensive_rebound_rate=0.29,    # 29% offensive rebound rate
        performance_variance=0.06       # 6% variance
    )
    
    return cleveland_state, detroit


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DETROIT vs CLEVELAND STATE SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Cleveland State: -2.5")
    print("  Detroit: +2.5")
    print("  Total (Over/Under): 162.5")
    print("="*70 + "\n")
    
    # Create teams (Cleveland State as team1, Detroit as team2)
    cleveland_state, detroit = create_detroit_vs_cleveland_state()
    
    # Run simulation
    simulator = GameSimulator(cleveland_state, detroit)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Cleveland State moneyline analysis (typical for -2.5 favorite is around -140 to -150)
    print("\n\nANALYSIS 1: Cleveland State Moneyline (Favorite)")
    print("-" * 70)
    print("Typical odds for -2.5 favorite: -145")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-145)
    
    # Detroit moneyline analysis (typical for +2.5 underdog is around +120 to +130)
    print("\n\nANALYSIS 2: Detroit Moneyline (Underdog)")
    print("-" * 70)
    print("Typical odds for +2.5 underdog: +125")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+125)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 162.5
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
    cleveland_state_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                                 if (s1 - s2) > spread)
    detroit_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                         if (s2 - s1 + spread) >= 0)
    
    cleveland_state_cover_pct = (cleveland_state_covers / results['num_simulations']) * 100
    detroit_cover_pct = (detroit_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Cleveland State -2.5 / Detroit +2.5")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Cleveland State)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Cleveland State covers -2.5: {cleveland_state_cover_pct:.1f}% ({cleveland_state_covers:,} simulations)")
    print(f"Detroit covers +2.5: {detroit_cover_pct:.1f}% ({detroit_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = detroit_cover_pct >= 70 and cleveland_state_cover_pct < 60
    
    if cleveland_state_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nCleveland State -2.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Cleveland State covers (happens {cleveland_state_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Cleveland State -2.5',
            'team2_name': 'Detroit +2.5',
            'team1_win_pct': cleveland_state_cover_pct,
            'team2_win_pct': detroit_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nDetroit +2.5 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Detroit covers (happens {detroit_cover_pct:.1f}% of the time)")
        if underdog_dominant:
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Detroit +2.5',
            'team2_name': 'Cleveland State -2.5',
            'team1_win_pct': detroit_cover_pct,
            'team2_win_pct': cleveland_state_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Cleveland State: {results['team1_win_pct']:.1f}%")
    print(f"  Detroit: {results['team2_win_pct']:.1f}%")
    print(f"\nSpread:")
    print(f"  Cleveland State covers -2.5: {cleveland_state_cover_pct:.1f}% of simulations")
    print(f"  Detroit covers +2.5: {detroit_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Cleveland State {results['team1_avg_score']:.1f} - Detroit {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Cleveland State by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
