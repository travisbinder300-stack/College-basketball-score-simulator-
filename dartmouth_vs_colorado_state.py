"""
Dartmouth vs Colorado State Simulation
Betting Lines: Colorado State -21, Dartmouth +21, Total 152

This simulation analyzes a potential blowout scenario where an elite team (Colorado State)
faces a weaker opponent (Dartmouth) - showcasing how the simulator handles large spreads.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_dartmouth_vs_colorado_state():
    """
    Create Dartmouth and Colorado State teams with realistic statistics
    This represents a significant mismatch between programs
    """
    
    # Colorado State Rams - Strong Mountain West team with elite defense and solid offense
    colorado_state = TeamStats(
        name="Colorado State Rams",
        offensive_efficiency=115.8,     # Very strong offense
        defensive_efficiency=94.2,      # Elite defense
        pace=70.5,                      # Moderate-fast pace
        three_point_rate=0.40,          # 40% of shots are 3PT
        three_point_percentage=0.37,    # 37% from three (good)
        two_point_percentage=0.54,      # 54% from two (excellent)
        free_throw_rate=0.35,           # Good at drawing fouls
        free_throw_percentage=0.75,     # 75% FT shooting
        turnover_rate=0.14,             # Low turnover rate (disciplined)
        offensive_rebound_rate=0.32,    # 32% offensive rebound rate
        performance_variance=0.05       # Low variance (consistent)
    )
    
    # Dartmouth Big Green - Ivy League team, significant step down in competition level
    dartmouth = TeamStats(
        name="Dartmouth Big Green",
        offensive_efficiency=100.5,     # Well below average offense
        defensive_efficiency=108.8,     # Poor defense
        pace=68.2,                      # Slower pace
        three_point_rate=0.36,          # 36% of shots are 3PT
        three_point_percentage=0.31,    # 31% from three (below average)
        two_point_percentage=0.47,      # 47% from two (poor)
        free_throw_rate=0.30,           # Struggles to draw fouls
        free_throw_percentage=0.69,     # 69% FT shooting
        turnover_rate=0.18,             # 18% turnover rate (high)
        offensive_rebound_rate=0.25,    # 25% offensive rebound rate
        performance_variance=0.08       # Higher variance (inconsistent)
    )
    
    return colorado_state, dartmouth


def main():
    """Run the Dartmouth vs Colorado State simulation with betting analysis"""
    
    print("=" * 80)
    print("DARTMOUTH VS COLORADO STATE SIMULATION")
    print("=" * 80)
    print("\nBetting Lines:")
    print("  Spread: Colorado State -21 / Dartmouth +21")
    print("  Moneyline: Colorado State (estimated -5000) / Dartmouth (estimated +1800)")
    print("  Total: 152")
    print("=" * 80)
    print()
    
    # Create teams
    colorado_state, dartmouth = create_dartmouth_vs_colorado_state()
    
    # Initialize simulator
    simulator = GameSimulator(colorado_state, dartmouth)
    
    # Run simulation
    print("Running 10,000 simulations...")
    results = simulator.run_simulation(num_simulations=10000)
    
    # Betting Analysis with Kelly Criterion
    print("\n" + "=" * 80)
    print("BETTING ANALYSIS WITH KELLY CRITERION")
    print("=" * 80)
    
    # Moneyline Analysis
    print("\n--- MONEYLINE ANALYSIS ---")
    print(f"\nColorado State Win Probability: {results['team1_win_pct']:.1f}%")
    print("  Estimated Odds: -5000 (implied 98.04%)")
    KellyCriterion.analyze_betting_opportunity(
        results, 
        team=1, 
        american_odds=-5000
    )
    
    print(f"\nDartmouth Win Probability: {results['team2_win_pct']:.1f}%")
    print("  Estimated Odds: +1800 (implied 5.26%)")
    KellyCriterion.analyze_betting_opportunity(
        results, 
        team=2, 
        american_odds=+1800
    )
    
    # Spread Analysis (Colorado State -21 / Dartmouth +21)
    print("\n--- SPREAD ANALYSIS ---")
    spread = 21.0
    
    colorado_state_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                        if (s1 - s2) > spread)
    dartmouth_covers = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                            if (s2 - s1 + spread) >= 0)
    
    colorado_state_cover_pct = (colorado_state_covers / results['num_simulations']) * 100
    dartmouth_cover_pct = (dartmouth_covers / results['num_simulations']) * 100
    
    print(f"\nSpread: Colorado State -21 / Dartmouth +21")
    print(f"Average Margin: {results['avg_margin']:.1f} points (Colorado State)")
    
    print(f"\n{'='*70}")
    print("SPREAD SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Colorado State covers -21: {colorado_state_cover_pct:.1f}% ({colorado_state_covers:,} simulations)")
    print(f"Dartmouth covers +21: {dartmouth_cover_pct:.1f}% ({dartmouth_covers:,} simulations)")
    
    # Check for suppression logic
    underdog_dominant = dartmouth_cover_pct >= 70 and colorado_state_cover_pct < 60
    
    # Kelly analysis for spread
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR SPREAD")
    print(f"{'='*70}")
    
    if colorado_state_cover_pct > 50 and not underdog_dominant:
        print(f"\nColorado State -21 Analysis")
        print("-" * 70)
        print(f"Simulation suggests Colorado State covers (happens {colorado_state_cover_pct:.1f}% of the time)")
        print("Typical spread odds: -110")
        
        spread_results = {
            'team1_name': 'Colorado State -21',
            'team2_name': 'Dartmouth +21',
            'team1_win_pct': colorado_state_cover_pct,
            'team2_win_pct': dartmouth_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    if dartmouth_cover_pct > 50:
        if not underdog_dominant or colorado_state_cover_pct >= 50:
            print(f"\nDartmouth +21 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Dartmouth covers (happens {dartmouth_cover_pct:.1f}% of the time)")
            if underdog_dominant:
                print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Dartmouth +21',
                'team2_name': 'Colorado State -21',
                'team1_win_pct': dartmouth_cover_pct,
                'team2_win_pct': colorado_state_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
        else:
            print(f"\nDartmouth +21 Analysis")
            print("-" * 70)
            print(f"Simulation suggests Dartmouth covers (happens {dartmouth_cover_pct:.1f}% of the time)")
            print("*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
            print("Typical spread odds: -110")
            
            spread_results = {
                'team1_name': 'Dartmouth +21',
                'team2_name': 'Colorado State -21',
                'team1_win_pct': dartmouth_cover_pct,
                'team2_win_pct': colorado_state_cover_pct,
                'num_simulations': results['num_simulations']
            }
            KellyCriterion.analyze_betting_opportunity(spread_results, team=1, american_odds=-110)
    
    # Total Analysis (152)
    print("\n--- TOTAL ANALYSIS (O/U 152) ---")
    total_line = 152.0
    
    over_count = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                     if (s1 + s2) > total_line)
    under_count = results['num_simulations'] - over_count
    
    over_pct = (over_count / results['num_simulations']) * 100
    under_pct = (under_count / results['num_simulations']) * 100
    
    avg_total = results['team1_avg_score'] + results['team2_avg_score']
    
    print(f"\nTotal Line: {total_line}")
    print(f"Simulated Average Total: {avg_total:.1f}")
    print(f"Difference: {avg_total - total_line:+.1f} points")
    
    print(f"\n{'='*70}")
    print("OVER/UNDER SIMULATION RESULTS")
    print(f"{'='*70}")
    print(f"Over {total_line}: {over_pct:.1f}% ({over_count:,} simulations)")
    print(f"Under {total_line}: {under_pct:.1f}% ({under_count:,} simulations)")
    
    # Kelly analysis for Over/Under
    print(f"\n{'='*70}")
    print("KELLY CRITERION FOR OVER/UNDER")
    print(f"{'='*70}")
    
    if over_pct > 50:
        print(f"\nOVER {total_line} Analysis")
        print("-" * 70)
        print(f"Simulation suggests OVER (occurs {over_pct:.1f}% of the time)")
        print("Typical Over odds: -110")
        
        over_results = {
            'team1_name': f'OVER {total_line}',
            'team2_name': f'UNDER {total_line}',
            'team1_win_pct': over_pct,
            'team2_win_pct': under_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(over_results, team=1, american_odds=-110)
    else:
        print(f"\nUNDER {total_line} Analysis")
        print("-" * 70)
        print(f"Simulation suggests UNDER (occurs {under_pct:.1f}% of the time)")
        print("Typical Under odds: -110")
        
        under_results = {
            'team1_name': f'UNDER {total_line}',
            'team2_name': f'OVER {total_line}',
            'team1_win_pct': under_pct,
            'team2_win_pct': over_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(under_results, team=1, american_odds=-110)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nMoneyline:")
    print(f"  Colorado State: {results['team1_win_pct']:.1f}% (Estimated: -5000)")
    print(f"  Dartmouth: {results['team2_win_pct']:.1f}% (Estimated: +1800)")
    print(f"\nSpread:")
    print(f"  Colorado State covers -21: {colorado_state_cover_pct:.1f}% of simulations")
    print(f"  Dartmouth covers +21: {dartmouth_cover_pct:.1f}% of simulations")
    print(f"\nTotal:")
    print(f"  Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"  Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"\nExpected Final Score: Colorado State {results['team1_avg_score']:.1f} - Dartmouth {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Colorado State by {results['avg_margin']:.1f} points")
    print()
    print("This represents a significant mismatch where Colorado State is heavily favored.")
    print("The 21-point spread reflects the talent differential between programs.")
    print("=" * 80)
    
    # Responsible gambling reminder
    print("\n" + "!" * 80)
    print("REMINDER: This simulation is for educational and entertainment purposes only.")
    print("Past performance and simulations do not guarantee future results.")
    print("Always gamble responsibly and within your means.")
    print("!" * 80)


if __name__ == "__main__":
    main()
