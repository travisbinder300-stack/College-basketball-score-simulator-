"""
Jackson State vs Houston Simulation
Betting Lines: Houston -38.5, Jackson State +38.5, Total 155

This simulation analyzes an extreme blowout scenario where a national powerhouse (Houston)
faces a significantly weaker opponent (Jackson State) - showcasing the simulator's ability 
to identify value even in highly lopsided matchups.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_jackson_state_vs_houston():
    """
    Create Jackson State and Houston teams with realistic statistics
    This represents an extreme mismatch - Houston is a national title contender
    """
    
    # Houston Cougars - Elite national program with dominant defense and offense
    houston = TeamStats(
        name="Houston Cougars",
        offensive_efficiency=122.5,     # Elite offense (Top 5 nationally)
        defensive_efficiency=88.2,      # Dominant defense (Top 3 nationally)
        pace=72.8,                      # Fast pace
        three_point_rate=0.42,          # 42% of shots are 3PT
        three_point_percentage=0.38,    # 38% from three (very good)
        two_point_percentage=0.57,      # 57% from two (elite)
        free_throw_rate=0.40,           # Excellent at drawing fouls
        free_throw_percentage=0.76,     # 76% FT shooting
        turnover_rate=0.12,             # Very low turnover rate (disciplined)
        offensive_rebound_rate=0.38,    # 38% offensive rebound rate (elite)
        performance_variance=0.04       # Very low variance (extremely consistent)
    )
    
    # Jackson State Tigers - SWAC team, major step down in competition
    jackson_state = TeamStats(
        name="Jackson State Tigers",
        offensive_efficiency=94.8,      # Well below average offense
        defensive_efficiency=115.5,     # Very poor defense
        pace=66.5,                      # Slow pace
        three_point_rate=0.34,          # 34% of shots are 3PT
        three_point_percentage=0.28,    # 28% from three (very poor)
        two_point_percentage=0.44,      # 44% from two (very poor)
        free_throw_rate=0.28,           # Struggles to draw fouls
        free_throw_percentage=0.65,     # 65% FT shooting (poor)
        turnover_rate=0.21,             # 21% turnover rate (very high)
        offensive_rebound_rate=0.24,    # 24% offensive rebound rate (poor)
        performance_variance=0.10       # High variance (very inconsistent)
    )
    
    return houston, jackson_state


def main():
    print("=" * 80)
    print("JACKSON STATE vs HOUSTON - MONTE CARLO SIMULATION")
    print("Extreme Blowout Scenario Analysis")
    print("=" * 80)
    print()
    
    # Create teams
    houston, jackson_state = create_jackson_state_vs_houston()
    
    # Create simulator
    simulator = GameSimulator(houston, jackson_state)
    
    # Run simulation
    print("Running 10,000 Monte Carlo simulations...")
    print()
    results = simulator.simulate_season(num_games=10000)
    
    # Display results
    simulator.print_results(results)
    
    # Betting Lines
    spread = 38.5
    total = 155
    
    print("\n" + "=" * 80)
    print("BETTING ANALYSIS")
    print("=" * 80)
    
    # Spread Analysis
    print(f"\n{'SPREAD ANALYSIS':-^80}")
    print(f"\nOffered Line: Houston -{spread} / Jackson State +{spread}")
    print(f"Expected Margin: Houston by {results['avg_margin']:.1f} points")
    
    team1_covers = sum(1 for margin in results['margins'] if margin > spread)
    team2_covers = sum(1 for margin in results['margins'] if margin < spread)
    
    team1_cover_pct = (team1_covers / len(results['margins'])) * 100
    team2_cover_pct = (team2_covers / len(results['margins'])) * 100
    
    print(f"\nHouston covers -{spread}: {team1_cover_pct:.1f}% of simulations")
    print(f"Jackson State covers +{spread}: {team2_cover_pct:.1f}% of simulations")
    
    # Check for spread suppression (70%+ underdog vs <60% favorite)
    suppress_favorite = team2_cover_pct >= 70.0 and team1_cover_pct < 60.0
    
    if suppress_favorite:
        print(f"\n*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
    
    # Houston spread analysis
    if not suppress_favorite:
        print(f"\nHouston -{spread}:")
        KellyCriterion.analyze_betting_opportunity(
            results,
            team=1,
            bet_type='spread',
            spread=spread,
            american_odds=-110
        )
    
    # Jackson State spread analysis
    print(f"\nJackson State +{spread}:")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=2,
        bet_type='spread',
        spread=-spread,
        american_odds=-110
    )
    
    # Total Analysis
    print(f"\n{'TOTAL ANALYSIS':-^80}")
    print(f"\nOffered Total: {total}")
    print(f"Expected Total: {results['avg_total']:.1f} points")
    
    over_count = sum(1 for total_pts in results['totals'] if total_pts > total)
    under_count = sum(1 for total_pts in results['totals'] if total_pts < total)
    
    over_pct = (over_count / len(results['totals'])) * 100
    under_pct = (under_count / len(results['totals'])) * 100
    
    print(f"\nOver {total}: {over_pct:.1f}% of simulations")
    print(f"Under {total}: {under_pct:.1f}% of simulations")
    
    # Over analysis
    print(f"\nOver {total}:")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=None,
        bet_type='over',
        total=total,
        american_odds=-110
    )
    
    # Under analysis
    print(f"\nUnder {total}:")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=None,
        bet_type='under',
        total=total,
        american_odds=-110
    )
    
    # Moneyline Analysis
    print(f"\n{'MONEYLINE ANALYSIS':-^80}")
    print(f"\nHouston win probability: {results['team1_win_pct']:.1f}%")
    print(f"Jackson State win probability: {results['team2_win_pct']:.1f}%")
    
    # Estimate moneyline odds (Houston heavily favored)
    houston_ml = -10000  # Extreme favorite
    jackson_state_ml = +5000  # Extreme underdog
    
    print(f"\nEstimated Moneyline Odds:")
    print(f"Houston: {houston_ml}")
    print(f"Jackson State: {jackson_state_ml:+d}")
    
    print(f"\nHouston ML {houston_ml}:")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=1,
        bet_type='moneyline',
        american_odds=houston_ml
    )
    
    print(f"\nJackson State ML {jackson_state_ml:+d}:")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=2,
        bet_type='moneyline',
        american_odds=jackson_state_ml
    )
    
    # Summary
    print("\n" + "=" * 80)
    print("KEY INSIGHTS - EXTREME BLOWOUT SCENARIO")
    print("=" * 80)
    print(f"\nExpected Final Score: Houston {results['avg_team1_score']:.1f} - Jackson State {results['avg_team2_score']:.1f}")
    print(f"Spread Differential: {spread - results['avg_margin']:.1f} points")
    print(f"Total Differential: {total - results['avg_total']:.1f} points")
    print("\nThis extreme mismatch demonstrates how the simulator identifies market")
    print("inefficiencies even in heavily lopsided matchups where one team is vastly superior.")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
