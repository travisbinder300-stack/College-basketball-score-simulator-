"""
Example: Custom Teams Simulation

This file demonstrates how to create your own custom teams and run simulations.
You can modify the statistics to match any real or hypothetical teams.
"""

from basketball_simulator import GameSimulator, TeamStats


def create_kentucky_vs_kansas():
    """
    Example: Kentucky (balanced powerhouse) vs Kansas (efficient offense)
    """
    
    kentucky = TeamStats(
        name="Kentucky Wildcats",
        offensive_efficiency=116.3,
        defensive_efficiency=96.8,
        pace=71.2,
        three_point_rate=0.39,
        three_point_percentage=0.37,
        two_point_percentage=0.54,
        free_throw_rate=0.36,
        free_throw_percentage=0.74,
        turnover_rate=0.16,
        offensive_rebound_rate=0.31,
        performance_variance=0.055
    )
    
    kansas = TeamStats(
        name="Kansas Jayhawks",
        offensive_efficiency=119.2,
        defensive_efficiency=98.5,
        pace=69.8,
        three_point_rate=0.41,
        three_point_percentage=0.38,
        two_point_percentage=0.55,
        free_throw_rate=0.37,
        free_throw_percentage=0.75,
        turnover_rate=0.15,
        offensive_rebound_rate=0.30,
        performance_variance=0.05
    )
    
    return kentucky, kansas


def create_gonzaga_vs_michigan():
    """
    Example: Gonzaga (high-powered offense) vs Michigan (defensive minded)
    """
    
    gonzaga = TeamStats(
        name="Gonzaga Bulldogs",
        offensive_efficiency=122.5,  # Elite offense
        defensive_efficiency=100.2,
        pace=73.8,  # Fast pace
        three_point_rate=0.43,
        three_point_percentage=0.39,
        two_point_percentage=0.58,
        free_throw_rate=0.40,
        free_throw_percentage=0.76,
        turnover_rate=0.14,
        offensive_rebound_rate=0.33,
        performance_variance=0.065
    )
    
    michigan = TeamStats(
        name="Michigan Wolverines",
        offensive_efficiency=112.8,
        defensive_efficiency=93.2,  # Elite defense
        pace=66.5,  # Slow pace
        three_point_rate=0.37,
        three_point_percentage=0.35,
        two_point_percentage=0.53,
        free_throw_rate=0.33,
        free_throw_percentage=0.73,
        turnover_rate=0.14,
        offensive_rebound_rate=0.29,
        performance_variance=0.045
    )
    
    return gonzaga, michigan


def create_upset_scenario():
    """
    Example: 15 seed vs 2 seed (March Madness upset scenario)
    """
    
    # 2 seed - Strong team
    strong_team = TeamStats(
        name="Arizona Wildcats (2 seed)",
        offensive_efficiency=117.8,
        defensive_efficiency=95.5,
        pace=70.5,
        three_point_rate=0.40,
        three_point_percentage=0.37,
        two_point_percentage=0.55,
        free_throw_rate=0.37,
        free_throw_percentage=0.74,
        turnover_rate=0.15,
        offensive_rebound_rate=0.31,
        performance_variance=0.05
    )
    
    # 15 seed - Underdog with a chance
    underdog = TeamStats(
        name="Vermont Catamounts (15 seed)",
        offensive_efficiency=108.5,
        defensive_efficiency=103.2,
        pace=67.2,
        three_point_rate=0.38,
        three_point_percentage=0.36,
        two_point_percentage=0.51,
        free_throw_rate=0.32,
        free_throw_percentage=0.72,
        turnover_rate=0.17,
        offensive_rebound_rate=0.28,
        performance_variance=0.08  # Higher variance - can have hot games
    )
    
    return strong_team, underdog


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CUSTOM TEAMS SIMULATION EXAMPLES")
    print("="*70)
    
    # Example 1: Kentucky vs Kansas
    print("\n\nEXAMPLE 1: Elite Matchup")
    print("-" * 70)
    team1, team2 = create_kentucky_vs_kansas()
    sim = GameSimulator(team1, team2)
    results1 = sim.run_simulation(num_simulations=10000)
    
    # Example 2: Gonzaga vs Michigan (contrasting styles)
    print("\n\n" + "="*70)
    print("\n\nEXAMPLE 2: Contrasting Styles (Fast Offense vs Slow Defense)")
    print("-" * 70)
    team3, team4 = create_gonzaga_vs_michigan()
    sim2 = GameSimulator(team3, team4)
    results2 = sim2.run_simulation(num_simulations=10000)
    
    # Example 3: Upset scenario
    print("\n\n" + "="*70)
    print("\n\nEXAMPLE 3: March Madness Upset Scenario (2 seed vs 15 seed)")
    print("-" * 70)
    team5, team6 = create_upset_scenario()
    sim3 = GameSimulator(team5, team6)
    results3 = sim3.run_simulation(num_simulations=10000)
    
    print("\n" + "="*70)
    print("SUMMARY OF ALL SIMULATIONS")
    print("="*70)
    print(f"\n1. {results1['team1_name']} vs {results1['team2_name']}")
    print(f"   Win Probability: {results1['team1_win_pct']:.1f}% vs {results1['team2_win_pct']:.1f}%")
    print(f"   Expected Score: {results1['team1_avg_score']:.1f} - {results1['team2_avg_score']:.1f}")
    
    print(f"\n2. {results2['team1_name']} vs {results2['team2_name']}")
    print(f"   Win Probability: {results2['team1_win_pct']:.1f}% vs {results2['team2_win_pct']:.1f}%")
    print(f"   Expected Score: {results2['team1_avg_score']:.1f} - {results2['team2_avg_score']:.1f}")
    
    print(f"\n3. {results3['team1_name']} vs {results3['team2_name']}")
    print(f"   Win Probability: {results3['team1_win_pct']:.1f}% vs {results3['team2_win_pct']:.1f}%")
    print(f"   Expected Score: {results3['team1_avg_score']:.1f} - {results3['team2_avg_score']:.1f}")
    print(f"   Upset Probability: {results3['team2_win_pct']:.1f}%")
    
    print("\n" + "="*70)
    print("\nAll simulations complete!")
    print("="*70 + "\n")
