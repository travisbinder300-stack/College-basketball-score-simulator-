#!/usr/bin/env python3
"""
Example usage of the College Basketball Score Simulator.
Demonstrates various ways to use the simulator.
"""

try:
    from .basketball_simulator import Team, BasketballSimulator
except ImportError:
    from basketball_simulator import Team, BasketballSimulator


def example_1_basic_simulation():
    """Example 1: Basic simulation with default statistics."""
    print("="*60)
    print("Example 1: Basic Simulation")
    print("="*60)
    
    team1 = Team("North Carolina")
    team2 = Team("Duke")
    
    simulator = BasketballSimulator(team1, team2, verbose=False)
    winner, summary = simulator.simulate_game()
    
    print(f"\nFinal Score: {summary['final_score']}")
    print(f"Winner: {winner.name}")
    print(f"Overtime Periods: {summary['overtime_periods']}")


def example_2_custom_teams():
    """Example 2: Custom teams with different strengths."""
    print("\n" + "="*60)
    print("Example 2: Custom Team Statistics")
    print("="*60)
    
    # Create a strong offensive team
    offensive_team = Team(
        name="Offensive Powerhouse",
        fg_percentage=0.52,
        three_pt_percentage=0.42,
        ft_percentage=0.80,
        turnover_rate=0.10
    )
    
    # Create a defensive-minded team
    defensive_team = Team(
        name="Defensive Specialists",
        fg_percentage=0.42,
        three_pt_percentage=0.32,
        ft_percentage=0.68,
        turnover_rate=0.12,
        steal_rate=0.12,
        block_rate=0.08,
        defensive_rebound_rate=0.75
    )
    
    simulator = BasketballSimulator(offensive_team, defensive_team, verbose=False)
    winner, summary = simulator.simulate_game()
    
    print(f"\nFinal Score: {summary['final_score']}")
    print(f"Winner: {winner.name}")
    
    # Print detailed stats
    print("\nTeam Statistics:")
    for team_stats in [summary['team1_stats'], summary['team2_stats']]:
        print(f"\n{team_stats['name']}:")
        print(f"  Score: {team_stats['score']}")
        print(f"  FG: {team_stats['fg']}")
        print(f"  3PT: {team_stats['3pt']}")
        print(f"  FT: {team_stats['ft']}")
        print(f"  Steals: {team_stats['steals']}")
        print(f"  Blocks: {team_stats['blocks']}")


def example_3_multiple_games():
    """Example 3: Run multiple simulations for statistical analysis."""
    print("\n" + "="*60)
    print("Example 3: Multiple Game Simulation (Season Series)")
    print("="*60)
    
    team1_config = {
        'name': "Kentucky",
        'fg_percentage': 0.48,
        'three_pt_percentage': 0.38,
        'ft_percentage': 0.75
    }
    
    team2_config = {
        'name': "Louisville",
        'fg_percentage': 0.46,
        'three_pt_percentage': 0.36,
        'ft_percentage': 0.72
    }
    
    num_games = 20
    team1_wins = 0
    total_team1_score = 0
    total_team2_score = 0
    
    print(f"\nSimulating {num_games} games between {team1_config['name']} and {team2_config['name']}...\n")
    
    for i in range(num_games):
        team1 = Team(**team1_config)
        team2 = Team(**team2_config)
        
        simulator = BasketballSimulator(team1, team2, verbose=False)
        winner, _ = simulator.simulate_game()
        
        total_team1_score += team1.score
        total_team2_score += team2.score
        
        if winner.name == team1_config['name']:
            team1_wins += 1
            result = "W"
        else:
            result = "L"
        
        print(f"Game {i+1:2d}: {result} - {team1.score:2d} - {team2.score:2d}")
    
    team2_wins = num_games - team1_wins
    
    print(f"\n{'='*60}")
    print("Season Series Results:")
    print(f"  {team1_config['name']}: {team1_wins} wins ({team1_wins/num_games*100:.1f}%)")
    print(f"  {team2_config['name']}: {team2_wins} wins ({team2_wins/num_games*100:.1f}%)")
    print(f"\nAverage Scores:")
    print(f"  {team1_config['name']}: {total_team1_score/num_games:.1f} PPG")
    print(f"  {team2_config['name']}: {total_team2_score/num_games:.1f} PPG")


def example_4_detailed_output():
    """Example 4: Simulation with detailed play-by-play."""
    print("\n" + "="*60)
    print("Example 4: Detailed Play-by-Play (First Few Possessions)")
    print("="*60)
    
    team1 = Team("UCLA", fg_percentage=0.50)
    team2 = Team("USC", fg_percentage=0.48)
    
    # This will show full play-by-play
    simulator = BasketballSimulator(team1, team2, verbose=True)
    winner, summary = simulator.simulate_game()


def example_5_conference_tournament():
    """Example 5: Simulate a mini tournament."""
    print("\n" + "="*60)
    print("Example 5: Conference Tournament Simulation")
    print("="*60)
    
    teams_config = [
        {'name': "Seed #1", 'fg_percentage': 0.50, 'three_pt_percentage': 0.40, 'ft_percentage': 0.78},
        {'name': "Seed #2", 'fg_percentage': 0.48, 'three_pt_percentage': 0.38, 'ft_percentage': 0.75},
        {'name': "Seed #3", 'fg_percentage': 0.46, 'three_pt_percentage': 0.36, 'ft_percentage': 0.72},
        {'name': "Seed #4", 'fg_percentage': 0.44, 'three_pt_percentage': 0.34, 'ft_percentage': 0.70},
    ]
    
    print("\nSemifinals:")
    print("-" * 40)
    
    # Semifinal 1
    team1 = Team(**teams_config[0])
    team2 = Team(**teams_config[3])
    simulator = BasketballSimulator(team1, team2, verbose=False)
    finalist1, game1 = simulator.simulate_game()
    print(f"Game 1: {game1['final_score']} - Winner: {finalist1.name}")
    
    # Semifinal 2
    team3 = Team(**teams_config[1])
    team4 = Team(**teams_config[2])
    simulator = BasketballSimulator(team3, team4, verbose=False)
    finalist2, game2 = simulator.simulate_game()
    print(f"Game 2: {game2['final_score']} - Winner: {finalist2.name}")
    
    # Championship
    print("\nChampionship Game:")
    print("-" * 40)
    
    # Recreate winning teams for championship
    finalist1_config = next(t for t in teams_config if t['name'] == finalist1.name)
    finalist2_config = next(t for t in teams_config if t['name'] == finalist2.name)
    
    team_final1 = Team(**finalist1_config)
    team_final2 = Team(**finalist2_config)
    
    simulator = BasketballSimulator(team_final1, team_final2, verbose=False)
    champion, championship = simulator.simulate_game()
    
    print(f"Championship: {championship['final_score']}")
    print(f"\n🏆 TOURNAMENT CHAMPION: {champion.name} 🏆")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("COLLEGE BASKETBALL SIMULATOR - EXAMPLES")
    print("="*60)
    
    # Run examples (comment out example_4 for brevity)
    example_1_basic_simulation()
    example_2_custom_teams()
    example_3_multiple_games()
    # example_4_detailed_output()  # Uncomment to see full play-by-play
    example_5_conference_tournament()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
