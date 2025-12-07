"""
Iowa State vs Purdue Simulation
Betting Lines: Iowa State +6 (ML +215), Purdue -6 (ML -276), Total 153

This simulation analyzes the Iowa State vs Purdue matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_iowa_state_vs_purdue():
    """
    Create Iowa State and Purdue teams with realistic 2024-25 statistics
    """
    
    # Purdue Boilermakers - Strong offense and defense, methodical style
    purdue = TeamStats(
        name="Purdue Boilermakers",
        offensive_efficiency=119.5,   # Elite offense
        defensive_efficiency=94.8,    # Elite defense
        pace=68.5,                     # Slower, methodical pace
        three_point_rate=0.39,         # 39% of shots are 3PT
        three_point_percentage=0.37,   # 37% from three
        two_point_percentage=0.57,     # 57% from two (strong inside game)
        free_throw_rate=0.36,          # Good at drawing fouls
        free_throw_percentage=0.76,    # 76% FT shooting
        turnover_rate=0.14,            # 14% turnover rate (low)
        offensive_rebound_rate=0.31,   # 31% offensive rebound rate
        performance_variance=0.05      # 5% variance (consistent)
    )
    
    # Iowa State Cyclones - Up-tempo offense, solid defense
    iowa_state = TeamStats(
        name="Iowa State Cyclones",
        offensive_efficiency=113.2,    # Good offense
        defensive_efficiency=97.5,     # Good defense
        pace=71.8,                      # Faster pace
        three_point_rate=0.41,          # 41% of shots are 3PT
        three_point_percentage=0.36,    # 36% from three
        two_point_percentage=0.53,      # 53% from two
        free_throw_rate=0.34,           # Average free throw rate
        free_throw_percentage=0.74,     # 74% FT shooting
        turnover_rate=0.16,             # 16% turnover rate
        offensive_rebound_rate=0.29,    # 29% offensive rebound rate
        performance_variance=0.06       # 6% variance
    )
    
    return purdue, iowa_state


if __name__ == "__main__":
    print("\n" + "="*70)
    print("IOWA STATE vs PURDUE SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Purdue: -6 (ML -276)")
    print("  Iowa State: +6 (ML +215)")
    print("  Total (Over/Under): 153")
    print("="*70 + "\n")
    
    # Create teams (Purdue as team1, Iowa State as team2)
    purdue, iowa_state = create_iowa_state_vs_purdue()
    
    # Run simulation
    simulator = GameSimulator(purdue, iowa_state)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Purdue moneyline analysis
    print("\n\nANALYSIS 1: Purdue Moneyline (Favorite)")
    print("-" * 70)
    print("Offered odds: -276")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-276)
    
    # Iowa State moneyline analysis
    print("\n\nANALYSIS 2: Iowa State Moneyline (Underdog)")
    print("-" * 70)
    print("Offered odds: +215")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+215)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 153.0
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
    
    spread = 6.0
    purdue_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s1 - s2) > spread)
    iowa_state_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s2 - s1 + spread) >= 0)
    
    purdue_cover_pct = (purdue_covers / results['num_simulations']) * 100
    iowa_state_cover_pct = (iowa_state_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Purdue -6.0 / Iowa State +6.0")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Purdue)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Purdue covers -6.0: {purdue_cover_pct:.1f}% ({purdue_covers:,} simulations)")
    print(f"Iowa State covers +6.0: {iowa_state_cover_pct:.1f}% ({iowa_state_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = iowa_state_cover_pct >= 70 and purdue_cover_pct < 60
    
    if purdue_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nPurdue -6.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Purdue covers (happens {purdue_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Purdue -6.0',
            'team2_name': 'Iowa State +6.0',
            'team1_win_pct': purdue_cover_pct,
            'team2_win_pct': iowa_state_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    else:
        print(f"\n\nIowa State +6.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Iowa State covers (happens {iowa_state_cover_pct:.1f}% of the time)")
        if underdog_dominant:
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Iowa State +6.0',
            'team2_name': 'Purdue -6.0',
            'team1_win_pct': iowa_state_cover_pct,
            'team2_win_pct': purdue_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Purdue: {results['team1_win_pct']:.1f}% (Offered: -276)")
    print(f"  Iowa State: {results['team2_win_pct']:.1f}% (Offered: +215)")
    print(f"\nSpread:")
    print(f"  Purdue covers -6.0: {purdue_cover_pct:.1f}% of simulations")
    print(f"  Iowa State covers +6.0: {iowa_state_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Purdue {results['team1_avg_score']:.1f} - Iowa State {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Purdue by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
