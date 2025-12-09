"""
Columbia vs Stony Brook Simulation
Betting Lines: Columbia -4 (ML -186), Stony Brook +4 (ML +150), Total 146

This simulation analyzes the Columbia vs Stony Brook matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_columbia_vs_stony_brook():
    """
    Create Columbia and Stony Brook teams with realistic statistics
    """
    
    # Columbia Lions - Ivy League team with solid fundamentals
    columbia = TeamStats(
        name="Columbia Lions",
        offensive_efficiency=109.8,     # Decent offense
        defensive_efficiency=99.5,      # Good defense
        pace=67.2,                       # Slower, deliberate pace
        three_point_rate=0.36,           # 36% of shots are 3PT
        three_point_percentage=0.34,     # 34% from three
        two_point_percentage=0.51,       # 51% from two
        free_throw_rate=0.32,            # Average free throw rate
        free_throw_percentage=0.72,      # 72% FT shooting
        turnover_rate=0.16,              # 16% turnover rate
        offensive_rebound_rate=0.28,     # 28% offensive rebound rate
        performance_variance=0.06        # 6% variance
    )
    
    # Stony Brook Seawolves - America East competitor
    stony_brook = TeamStats(
        name="Stony Brook Seawolves",
        offensive_efficiency=106.2,      # Below average offense
        defensive_efficiency=101.8,      # Below average defense
        pace=66.5,                        # Slower pace
        three_point_rate=0.38,            # 38% of shots are 3PT
        three_point_percentage=0.33,      # 33% from three
        two_point_percentage=0.49,        # 49% from two
        free_throw_rate=0.31,             # Average free throw rate
        free_throw_percentage=0.70,       # 70% FT shooting
        turnover_rate=0.17,               # 17% turnover rate
        offensive_rebound_rate=0.27,      # 27% offensive rebound rate
        performance_variance=0.07         # 7% variance
    )
    
    return columbia, stony_brook


if __name__ == "__main__":
    print("\n" + "="*70)
    print("COLUMBIA vs STONY BROOK SIMULATION")
    print("="*70)
    print("\nBetting Lines:")
    print("  Columbia: -4 (ML -186)")
    print("  Stony Brook: +4 (ML +150)")
    print("  Total (Over/Under): 146")
    print("="*70 + "\n")
    
    # Create teams (Columbia as team1, Stony Brook as team2)
    columbia, stony_brook = create_columbia_vs_stony_brook()
    
    # Run simulation
    simulator = GameSimulator(columbia, stony_brook)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Analyze betting opportunities
    print("\n" + "="*70)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("="*70)
    
    # Columbia moneyline analysis
    print("\n\nANALYSIS 1: Columbia Moneyline (Favorite)")
    print("-" * 70)
    print("Offered odds: -186")
    KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=-186)
    
    # Stony Brook moneyline analysis
    print("\n\nANALYSIS 2: Stony Brook Moneyline (Underdog)")
    print("-" * 70)
    print("Offered odds: +150")
    KellyCriterion.analyze_betting_opportunity(results, team=2, american_odds=+150)
    
    # Total analysis
    print("\n\n" + "="*70)
    print("TOTAL (OVER/UNDER) ANALYSIS")
    print("="*70)
    
    total_line = 146.0
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
    
    spread = 4.0
    columbia_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                         if (s1 - s2) > spread)
    stony_brook_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                              if (s2 - s1 + spread) >= 0)
    
    columbia_cover_pct = (columbia_covers / results['num_simulations']) * 100
    stony_brook_cover_pct = (stony_brook_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Columbia -4.0 / Stony Brook +4.0")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Columbia)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Columbia covers -4.0: {columbia_cover_pct:.1f}% ({columbia_covers:,} simulations)")
    print(f"Stony Brook covers +4.0: {stony_brook_cover_pct:.1f}% ({stony_brook_covers:,} simulations)")
    
    # Kelly analysis for spread (typical odds are -110 for both sides)
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    # Check if underdog has significantly better coverage (70%+ vs favorite <60%)
    underdog_dominant = stony_brook_cover_pct >= 70 and columbia_cover_pct < 60
    
    if columbia_cover_pct > 50 and not underdog_dominant:
        print(f"\n\nColumbia -4.0 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Columbia covers (happens {columbia_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Columbia -4.0',
            'team2_name': 'Stony Brook +4.0',
            'team1_win_pct': columbia_cover_pct,
            'team2_win_pct': stony_brook_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    if stony_brook_cover_pct > 50:
        if not underdog_dominant or columbia_cover_pct >= 50:
            print(f"\n\nStony Brook +4.0 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Stony Brook covers (happens {stony_brook_cover_pct:.1f}% of the time)")
            if underdog_dominant:
                print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Stony Brook +4.0',
                'team2_name': 'Columbia -4.0',
                'team1_win_pct': stony_brook_cover_pct,
                'team2_win_pct': columbia_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
        else:
            print(f"\n\nStony Brook +4.0 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Stony Brook covers (happens {stony_brook_cover_pct:.1f}% of the time)")
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Stony Brook +4.0',
                'team2_name': 'Columbia -4.0',
                'team1_win_pct': stony_brook_cover_pct,
                'team2_win_pct': columbia_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nMoneyline:")
    print(f"  Columbia: {results['team1_win_pct']:.1f}% (Offered: -186)")
    print(f"  Stony Brook: {results['team2_win_pct']:.1f}% (Offered: +150)")
    print(f"\nSpread:")
    print(f"  Columbia covers -4.0: {columbia_cover_pct:.1f}% of simulations")
    print(f"  Stony Brook covers +4.0: {stony_brook_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Columbia {results['team1_avg_score']:.1f} - Stony Brook {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Columbia by {results['avg_margin']:.1f} points")
    print("\n" + "="*70 + "\n")
