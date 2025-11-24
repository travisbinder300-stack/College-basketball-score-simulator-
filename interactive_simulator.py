#!/usr/bin/env python3
"""
Interactive College Basketball Score Simulator
Allows users to customize teams and run simulations.
"""

import sys
from basketball_simulator import Team, BasketballSimulator


def get_float_input(prompt: str, default: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Get validated float input from user."""
    while True:
        try:
            value = input(f"{prompt} (default {default:.2f}): ").strip()
            if not value:
                return default
            value = float(value)
            if min_val <= value <= max_val:
                return value
            print(f"Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_team_input(team_number: int) -> Team:
    """Get team configuration from user input."""
    print(f"\n{'='*60}")
    print(f"Configure Team {team_number}")
    print(f"{'='*60}")
    
    name = input(f"Team {team_number} name: ").strip()
    if not name:
        name = f"Team {team_number}"
    
    print("\nEnter team statistics (press Enter to use defaults):")
    print("Note: Percentages should be entered as decimals (e.g., 0.45 for 45%)")
    
    fg_percentage = get_float_input("Field Goal Percentage", 0.45, 0.20, 0.70)
    three_pt_percentage = get_float_input("Three-Point Percentage", 0.35, 0.15, 0.50)
    ft_percentage = get_float_input("Free Throw Percentage", 0.72, 0.50, 0.95)
    turnover_rate = get_float_input("Turnover Rate", 0.15, 0.05, 0.30)
    offensive_rebound_rate = get_float_input("Offensive Rebound Rate", 0.30, 0.15, 0.45)
    defensive_rebound_rate = get_float_input("Defensive Rebound Rate", 0.70, 0.55, 0.85)
    three_pt_attempt_rate = get_float_input("Three-Point Attempt Rate", 0.35, 0.20, 0.60)
    steal_rate = get_float_input("Steal Rate", 0.08, 0.03, 0.15)
    block_rate = get_float_input("Block Rate", 0.05, 0.02, 0.12)
    
    return Team(
        name=name,
        fg_percentage=fg_percentage,
        three_pt_percentage=three_pt_percentage,
        ft_percentage=ft_percentage,
        turnover_rate=turnover_rate,
        offensive_rebound_rate=offensive_rebound_rate,
        defensive_rebound_rate=defensive_rebound_rate,
        three_pt_attempt_rate=three_pt_attempt_rate,
        steal_rate=steal_rate,
        block_rate=block_rate
    )


def quick_simulation():
    """Run a quick simulation with preset teams."""
    print("\nRunning quick simulation with preset teams...")
    
    team1 = Team(
        name="Duke Blue Devils",
        fg_percentage=0.48,
        three_pt_percentage=0.38,
        ft_percentage=0.75,
        turnover_rate=0.12,
        offensive_rebound_rate=0.32,
        defensive_rebound_rate=0.72
    )
    
    team2 = Team(
        name="Kentucky Wildcats",
        fg_percentage=0.45,
        three_pt_percentage=0.35,
        ft_percentage=0.70,
        turnover_rate=0.14,
        offensive_rebound_rate=0.28,
        defensive_rebound_rate=0.68
    )
    
    simulator = BasketballSimulator(team1, team2, verbose=True)
    winner, summary = simulator.simulate_game()
    
    return winner, summary


def custom_simulation():
    """Run a custom simulation with user-defined teams."""
    print("\nCustom Simulation Mode")
    print("Configure both teams with custom statistics.\n")
    
    team1 = get_team_input(1)
    team2 = get_team_input(2)
    
    print("\n" + "="*60)
    print("Starting simulation...")
    print("="*60)
    
    verbose = input("\nShow detailed play-by-play? (y/n, default y): ").strip().lower()
    verbose = verbose != 'n'
    
    simulator = BasketballSimulator(team1, team2, verbose=verbose)
    winner, summary = simulator.simulate_game()
    
    return winner, summary


def multiple_simulations():
    """Run multiple simulations and show aggregate results."""
    print("\nMultiple Simulations Mode")
    
    try:
        num_games = int(input("How many games to simulate? (default 10): ").strip() or "10")
        if num_games < 1 or num_games > 1000:
            print("Please enter a number between 1 and 1000. Using default of 10.")
            num_games = 10
    except ValueError:
        print("Invalid input. Using default of 10 games.")
        num_games = 10
    
    print("\nUsing preset teams for multiple simulations...")
    
    team1_config = {
        'name': "Blue Devils",
        'fg_percentage': 0.48,
        'three_pt_percentage': 0.38,
        'ft_percentage': 0.75,
        'turnover_rate': 0.12,
        'offensive_rebound_rate': 0.32,
        'defensive_rebound_rate': 0.72
    }
    
    team2_config = {
        'name': "Wildcats",
        'fg_percentage': 0.45,
        'three_pt_percentage': 0.35,
        'ft_percentage': 0.70,
        'turnover_rate': 0.14,
        'offensive_rebound_rate': 0.28,
        'defensive_rebound_rate': 0.68
    }
    
    team1_wins = 0
    team2_wins = 0
    total_team1_score = 0
    total_team2_score = 0
    overtime_games = 0
    
    print(f"\nSimulating {num_games} games...")
    
    for i in range(num_games):
        team1 = Team(**team1_config)
        team2 = Team(**team2_config)
        
        simulator = BasketballSimulator(team1, team2, verbose=False)
        winner, summary = simulator.simulate_game()
        
        if winner.name == team1_config['name']:
            team1_wins += 1
        else:
            team2_wins += 1
        
        total_team1_score += team1.score
        total_team2_score += team2.score
        
        if summary['overtime_periods'] > 0:
            overtime_games += 1
        
        # Show progress
        if (i + 1) % max(1, num_games // 10) == 0:
            print(f"  Completed {i + 1}/{num_games} games...")
    
    print("\n" + "="*60)
    print(f"AGGREGATE RESULTS ({num_games} games)")
    print("="*60)
    print(f"{team1_config['name']} wins: {team1_wins} ({team1_wins/num_games*100:.1f}%)")
    print(f"{team2_config['name']} wins: {team2_wins} ({team2_wins/num_games*100:.1f}%)")
    print(f"\nAverage score:")
    print(f"  {team1_config['name']}: {total_team1_score/num_games:.1f}")
    print(f"  {team2_config['name']}: {total_team2_score/num_games:.1f}")
    print(f"\nGames went to overtime: {overtime_games} ({overtime_games/num_games*100:.1f}%)")
    print("="*60)


def main():
    """Main function for interactive simulator."""
    print("\n" + "="*60)
    print("COLLEGE BASKETBALL SCORE SIMULATOR - Interactive Mode")
    print("="*60)
    
    while True:
        print("\nSelect simulation mode:")
        print("1. Quick Simulation (preset teams)")
        print("2. Custom Simulation (define your own teams)")
        print("3. Multiple Simulations (aggregate statistics)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            quick_simulation()
        elif choice == '2':
            custom_simulation()
        elif choice == '3':
            multiple_simulations()
        elif choice == '4':
            print("\nThank you for using the College Basketball Simulator!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
        
        # Ask if user wants to run another simulation
        again = input("\nRun another simulation? (y/n): ").strip().lower()
        if again != 'y':
            print("\nThank you for using the College Basketball Simulator!")
            break


if __name__ == "__main__":
    main()
