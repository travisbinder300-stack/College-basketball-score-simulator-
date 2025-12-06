"""
Advanced Usage Examples for Soccer Simulator

This file demonstrates advanced features and use cases for the soccer simulator.
"""

from soccer_simulator import Team, SoccerSimulator, load_teams_from_file


def example_1_basic_match():
    """Example 1: Basic match simulation"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Match Simulation")
    print("=" * 80)
    
    team_a = Team("Team A", offensive_rating=1.20, defensive_rating=0.95)
    team_b = Team("Team B", offensive_rating=1.15, defensive_rating=1.00)
    
    simulator = SoccerSimulator()
    simulator.print_simulation_report(team_a, team_b, num_simulations=10000)


def example_2_league_comparison():
    """Example 2: Compare different league characteristics"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Different League Characteristics")
    print("=" * 80)
    
    team_a = Team("Team A", offensive_rating=1.30, defensive_rating=0.90)
    team_b = Team("Team B", offensive_rating=1.25, defensive_rating=0.95)
    
    # Premier League (lower scoring)
    print("\n--- PREMIER LEAGUE STYLE (avg 2.75 goals/game) ---")
    pl_sim = SoccerSimulator(league_avg_goals=2.75, home_advantage=0.3)
    results_pl = pl_sim.simulate_matches(team_a, team_b, num_simulations=10000)
    print(f"Expected total goals: {results_pl['avg_total_goals']:.2f}")
    print(f"Home win prob: {results_pl['home_win_prob']:.1%}")
    
    # Bundesliga (higher scoring)
    print("\n--- BUNDESLIGA STYLE (avg 3.10 goals/game) ---")
    bl_sim = SoccerSimulator(league_avg_goals=3.10, home_advantage=0.3)
    results_bl = bl_sim.simulate_matches(team_a, team_b, num_simulations=10000)
    print(f"Expected total goals: {results_bl['avg_total_goals']:.2f}")
    print(f"Home win prob: {results_bl['home_win_prob']:.1%}")
    
    # Serie A (more defensive)
    print("\n--- SERIE A STYLE (avg 2.65 goals/game) ---")
    sa_sim = SoccerSimulator(league_avg_goals=2.65, home_advantage=0.25)
    results_sa = sa_sim.simulate_matches(team_a, team_b, num_simulations=10000)
    print(f"Expected total goals: {results_sa['avg_total_goals']:.2f}")
    print(f"Home win prob: {results_sa['home_win_prob']:.1%}")


def example_3_odds_analysis():
    """Example 3: Betting odds analysis for value finding"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Betting Odds Analysis")
    print("=" * 80)
    
    home_team = Team("Home Team", offensive_rating=1.25, defensive_rating=0.90)
    away_team = Team("Away Team", offensive_rating=1.30, defensive_rating=0.85)
    
    simulator = SoccerSimulator()
    odds_data = simulator.calculate_match_odds(home_team, away_team, num_simulations=10000)
    
    print(f"\nMatch: {odds_data['home_team']} vs {odds_data['away_team']}")
    print(f"Simulations: {odds_data['simulations']:,}")
    
    print("\n--- FAIR ODDS (No Margin) ---")
    print(f"Home Win: {odds_data['decimal_odds']['home_win']} ({odds_data['probabilities']['home_win']})")
    print(f"Draw:     {odds_data['decimal_odds']['draw']} ({odds_data['probabilities']['draw']})")
    print(f"Away Win: {odds_data['decimal_odds']['away_win']} ({odds_data['probabilities']['away_win']})")
    
    print("\n--- EXPECTED GOALS ---")
    print(f"Home xG: {odds_data['expected_goals']['home']}")
    print(f"Away xG: {odds_data['expected_goals']['away']}")
    
    print("\n--- MOST LIKELY SCORES ---")
    for i, (score, prob) in enumerate(odds_data['most_likely_scores'][:5], 1):
        print(f"{i}. {score} - {prob}")
    
    # Compare with hypothetical bookmaker odds
    print("\n--- VALUE BET ANALYSIS ---")
    print("If bookmaker offers odds of 2.50 for home win:")
    fair_decimal = odds_data['decimal_odds']['home_win']
    bookmaker_decimal = 2.50
    
    if bookmaker_decimal > fair_decimal:
        value = ((bookmaker_decimal / fair_decimal) - 1) * 100
        print(f"✓ VALUE BET! Bookmaker odds are {value:.1f}% higher than fair odds")
    else:
        value = ((fair_decimal / bookmaker_decimal) - 1) * 100
        print(f"✗ NO VALUE. Fair odds are {value:.1f}% higher than bookmaker odds")


def example_4_over_under_analysis():
    """Example 4: Over/Under goals analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Over/Under Goals Analysis")
    print("=" * 80)
    
    team_a = Team("Attacking Team", offensive_rating=1.40, defensive_rating=1.10)
    team_b = Team("Defensive Team", offensive_rating=1.00, defensive_rating=0.85)
    
    simulator = SoccerSimulator()
    results = simulator.simulate_matches(team_a, team_b, num_simulations=10000)
    
    print(f"\nMatch: {team_a.name} (Home) vs {team_b.name} (Away)")
    print(f"Expected total goals: {results['avg_total_goals']:.2f}")
    
    # Calculate over/under probabilities
    total_goals = [h + a for h, a in zip(results['home_goals'], results['away_goals'])]
    
    thresholds = [1.5, 2.5, 3.5, 4.5]
    print("\n--- OVER/UNDER PROBABILITIES ---")
    for threshold in thresholds:
        over_count = sum(1 for g in total_goals if g > threshold)
        under_count = sum(1 for g in total_goals if g < threshold)
        over_prob = over_count / len(total_goals)
        under_prob = under_count / len(total_goals)
        
        print(f"\nOver {threshold} goals: {over_prob:.1%} (Decimal odds: {1/over_prob:.2f})")
        print(f"Under {threshold} goals: {under_prob:.1%} (Decimal odds: {1/under_prob:.2f})")


def example_5_home_advantage_impact():
    """Example 5: Impact of home advantage"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Home Advantage Impact Analysis")
    print("=" * 80)
    
    team_a = Team("Team A", offensive_rating=1.20, defensive_rating=1.00)
    team_b = Team("Team B", offensive_rating=1.20, defensive_rating=1.00)
    
    print("\nTwo evenly matched teams (both 1.20 OFF, 1.00 DEF)")
    
    home_advantages = [0.0, 0.2, 0.3, 0.4]
    
    for ha in home_advantages:
        simulator = SoccerSimulator(home_advantage=ha)
        results = simulator.simulate_matches(team_a, team_b, num_simulations=10000)
        
        print(f"\n--- Home Advantage: {ha:.0%} ---")
        print(f"Home win: {results['home_win_prob']:.1%}")
        print(f"Draw:     {results['draw_prob']:.1%}")
        print(f"Away win: {results['away_win_prob']:.1%}")
        print(f"Home xG:  {results['home_xg']:.2f}")
        print(f"Away xG:  {results['away_xg']:.2f}")


def example_6_neutral_venue():
    """Example 6: Neutral venue simulation (no home advantage)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Neutral Venue Simulation")
    print("=" * 80)
    
    team_a = Team("Team A", offensive_rating=1.35, defensive_rating=0.85)
    team_b = Team("Team B", offensive_rating=1.25, defensive_rating=0.95)
    
    # Neutral venue = no home advantage
    simulator = SoccerSimulator(home_advantage=0.0)
    
    print("\nNeutral venue (e.g., Cup Final, International Tournament)")
    simulator.print_simulation_report(team_a, team_b, num_simulations=10000)


def example_7_load_from_file():
    """Example 7: Load teams from configuration file"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Load Teams from Configuration File")
    print("=" * 80)
    
    try:
        teams = load_teams_from_file('teams_example.json')
        
        print(f"\nLoaded {len(teams)} teams from configuration file:")
        for team in teams[:5]:  # Show first 5
            print(f"  {team}")
        
        # Simulate a match between first two teams
        if len(teams) >= 2:
            print(f"\nSimulating match between loaded teams:")
            simulator = SoccerSimulator()
            simulator.print_simulation_report(teams[0], teams[1], num_simulations=10000)
    except FileNotFoundError:
        print("\nteams_example.json not found. Create it to use this feature.")


def example_8_season_simulation():
    """Example 8: Simulate multiple matches (mini season)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Mini Season Simulation")
    print("=" * 80)
    
    teams = [
        Team("Team A", offensive_rating=1.40, defensive_rating=0.80),
        Team("Team B", offensive_rating=1.30, defensive_rating=0.90),
        Team("Team C", offensive_rating=1.20, defensive_rating=1.00),
        Team("Team D", offensive_rating=1.10, defensive_rating=1.10)
    ]
    
    simulator = SoccerSimulator()
    
    print("\nSimulating round-robin tournament (each team plays each other once):")
    print("\n" + "-" * 80)
    
    standings = {team.name: {'points': 0, 'gf': 0, 'ga': 0, 'played': 0} for team in teams}
    
    for i, home_team in enumerate(teams):
        for away_team in teams[i+1:]:
            # Simulate the match once
            home_goals, away_goals = simulator.simulate_single_match(home_team, away_team)
            
            print(f"{home_team.name} {home_goals} - {away_goals} {away_team.name}")
            
            # Update standings
            standings[home_team.name]['played'] += 1
            standings[away_team.name]['played'] += 1
            standings[home_team.name]['gf'] += home_goals
            standings[home_team.name]['ga'] += away_goals
            standings[away_team.name]['gf'] += away_goals
            standings[away_team.name]['ga'] += home_goals
            
            if home_goals > away_goals:
                standings[home_team.name]['points'] += 3
            elif away_goals > home_goals:
                standings[away_team.name]['points'] += 3
            else:
                standings[home_team.name]['points'] += 1
                standings[away_team.name]['points'] += 1
    
    # Print standings
    print("\n" + "-" * 80)
    print("FINAL STANDINGS")
    print("-" * 80)
    print(f"{'Team':<20} {'P':>3} {'Pts':>4} {'GF':>4} {'GA':>4} {'GD':>4}")
    print("-" * 80)
    
    sorted_standings = sorted(standings.items(), 
                             key=lambda x: (x[1]['points'], x[1]['gf'] - x[1]['ga']), 
                             reverse=True)
    
    for team_name, stats in sorted_standings:
        gd = stats['gf'] - stats['ga']
        print(f"{team_name:<20} {stats['played']:>3} {stats['points']:>4} "
              f"{stats['gf']:>4} {stats['ga']:>4} {gd:>+4}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "SOCCER SIMULATOR - ADVANCED EXAMPLES" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    
    examples = [
        example_1_basic_match,
        example_2_league_comparison,
        example_3_odds_analysis,
        example_4_over_under_analysis,
        example_5_home_advantage_impact,
        example_6_neutral_venue,
        example_7_load_from_file,
        example_8_season_simulation
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\nError in example {i}: {e}")
        
        if i < len(examples):
            input("\n[Press Enter to continue to next example...]")


if __name__ == "__main__":
    main()
