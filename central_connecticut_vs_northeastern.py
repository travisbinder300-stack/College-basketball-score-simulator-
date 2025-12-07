"""
Central Connecticut State vs Northeastern Simulation
Betting Lines: Central Connecticut State +2.5 ML +140, Northeastern -2.5 ML -160, Total 160
 
This simulation analyzes the Central Connecticut State vs Northeastern matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_ccsu_vs_northeastern():
    """
    Create Central Connecticut State and Northeastern teams with realistic 2024-25 statistics
    """
    
    # Northeastern Huskies - Strong CAA program
    northeastern = TeamStats(
        name="Northeastern Huskies",
        offensive_efficiency=109.2,    # Strong mid-major offense
        defensive_efficiency=101.8,    # Good defense
        pace=70.5,                     # Moderate-fast pace
        three_point_rate=0.38,         # 38% of shots are 3PT
        three_point_percentage=0.35,   # 35% from three
        two_point_percentage=0.52,     # 52% from two
        free_throw_rate=0.35,          # Good free throw rate
        free_throw_percentage=0.74,    # 74% FT shooting
        turnover_rate=0.14,            # 14% turnover rate - disciplined
        offensive_rebound_rate=0.30,   # 30% offensive rebound rate
        performance_variance=0.06      # 6% variance
    )
    
    # Central Connecticut State Blue Devils - NEC team
    ccsu = TeamStats(
        name="Central Connecticut State Blue Devils",
        offensive_efficiency=106.5,    # Decent mid-major offense
        defensive_efficiency=104.2,    # Average defense
        pace=69.8,                     # Moderate pace
        three_point_rate=0.36,         # 36% of shots are 3PT
        three_point_percentage=0.33,   # 33% from three
        two_point_percentage=0.50,     # 50% from two
        free_throw_rate=0.33,          # Average free throw rate
        free_throw_percentage=0.70,    # 70% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.28,   # 28% offensive rebound rate
        performance_variance=0.07      # 7% variance
    )
    
    return northeastern, ccsu


def analyze_betting_lines(results, spread):
    """
    Analyze betting opportunities for both spread and total
    """
    print("\n" + "="*80)
    print("BETTING LINE ANALYSIS")
    print("="*80)
    
    # Moneyline Analysis
    print("\n" + "-"*80)
    print("MONEYLINE ANALYSIS")
    print("-"*80)
    
    # Northeastern ML -160
    print("\nNortheastern ML -160:")
    northeastern_ml_odds = -160
    KellyCriterion.analyze_betting_opportunity(
        results, 
        team=1, 
        american_odds=northeastern_ml_odds
    )
    
    # CCSU ML +140
    print("\nCentral Connecticut State ML +140:")
    ccsu_ml_odds = +140
    KellyCriterion.analyze_betting_opportunity(
        results, 
        team=2, 
        american_odds=ccsu_ml_odds
    )
    
    # Spread Analysis
    print("\n" + "-"*80)
    print(f"SPREAD ANALYSIS (Northeastern -{abs(spread)} / CCSU +{abs(spread)})")
    print("-"*80)
    
    # Calculate spread coverage from simulation scores
    northeastern_covers = 0
    ccsu_covers = 0
    for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']):
        margin = s1 - s2  # Positive means Northeastern wins by more
        if margin > abs(spread):  # Northeastern covers
            northeastern_covers += 1
        if margin < abs(spread):  # CCSU covers
            ccsu_covers += 1
    
    northeastern_cover_pct = (northeastern_covers / results['num_simulations']) * 100
    ccsu_cover_pct = (ccsu_covers / results['num_simulations']) * 100
    
    print(f"\nNortheastern covers -{abs(spread)}: {northeastern_cover_pct:.1f}% of simulations")
    print(f"CCSU covers +{abs(spread)}: {ccsu_cover_pct:.1f}% of simulations")
    
    # Check for strong underdog value (suppress favorite if underdog dominant)
    suppress_favorite = ccsu_cover_pct >= 70.0 and northeastern_cover_pct < 60.0
    
    if suppress_favorite:
        print(f"\n*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
    
    # Northeastern spread
    if not suppress_favorite:
        print(f"\nNortheastern -{abs(spread)}:")
        spread_results = {
            'team1_name': f'Northeastern -{abs(spread)}',
            'team2_name': f'CCSU +{abs(spread)}',
            'team1_win_pct': northeastern_cover_pct,
            'team2_win_pct': ccsu_cover_pct,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(
            spread_results,
            team=1,
            american_odds=-110
        )
    
    # CCSU spread
    print(f"\nCentral Connecticut State +{abs(spread)}:")
    spread_results = {
        'team1_name': f'CCSU +{abs(spread)}',
        'team2_name': f'Northeastern -{abs(spread)}',
        'team1_win_pct': ccsu_cover_pct,
        'team2_win_pct': northeastern_cover_pct,
        'num_simulations': results['num_simulations']
    }
    KellyCriterion.analyze_betting_opportunity(
        spread_results,
        team=1,
        american_odds=-110
    )
    
    # Total Analysis
    print("\n" + "-"*80)
    print("TOTAL (OVER/UNDER) ANALYSIS - 160")
    print("-"*80)
    
    total_line = 160.0
    over_count = sum(1 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores']) 
                     if (s1 + s2) > total_line)
    under_count = results['num_simulations'] - over_count
    over_pct = (over_count / results['num_simulations']) * 100
    under_pct = (under_count / results['num_simulations']) * 100
    
    avg_total = results['team1_avg_score'] + results['team2_avg_score']
    
    print(f"\nOver {total_line}: {over_pct:.1f}% of simulations")
    print(f"Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"Expected total: {avg_total:.1f} points")
    
    # Over analysis
    print(f"\nOver {total_line}:")
    over_results = {
        'team1_name': f'Over {total_line}',
        'team2_name': f'Under {total_line}',
        'team1_win_pct': over_pct,
        'team2_win_pct': under_pct,
        'num_simulations': results['num_simulations']
    }
    KellyCriterion.analyze_betting_opportunity(
        over_results,
        team=1,
        american_odds=-110
    )
    
    # Under analysis
    print(f"\nUnder {total_line}:")
    under_results = {
        'team1_name': f'Under {total_line}',
        'team2_name': f'Over {total_line}',
        'team1_win_pct': under_pct,
        'team2_win_pct': over_pct,
        'num_simulations': results['num_simulations']
    }
    KellyCriterion.analyze_betting_opportunity(
        under_results,
        team=1,
        american_odds=-110
    )


def main():
    print("="*80)
    print("CENTRAL CONNECTICUT STATE vs NORTHEASTERN - GAME SIMULATION")
    print("="*80)
    print("\nBetting Lines:")
    print("  Spread: CCSU +2.5 / Northeastern -2.5")
    print("  Moneyline: CCSU +140 / Northeastern -160")
    print("  Total: 160")
    print("="*80)
    
    # Create teams
    northeastern, ccsu = create_ccsu_vs_northeastern()
    
    # Run simulation
    print("\nRunning 10,000 simulations...")
    simulator = GameSimulator(northeastern, ccsu)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Print basic results
    print("\n" + "="*80)
    print("SIMULATION RESULTS")
    print("="*80)
    print(f"\nExpected Score: Northeastern {results['team1_avg_score']:.1f} - CCSU {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: Northeastern by {results['avg_margin']:.1f} points")
    print(f"\nWin Probabilities:")
    print(f"  Northeastern: {results['team1_win_pct']:.1f}%")
    print(f"  CCSU: {results['team2_win_pct']:.1f}%")
    
    # Analyze betting lines
    spread = -2.5  # Northeastern favored by 2.5
    analyze_betting_lines(results, spread)
    
    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
