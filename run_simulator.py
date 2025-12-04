#!/usr/bin/env python3
"""
Main CLI interface for the College Basketball Score Simulator
Allows users to run different types of simulations.
"""

import sys
from basketball_simulator import Team, BasketballGame
from advanced_simulator import AdvancedTeam, AdvancedGame


def print_menu():
    """Display the main menu."""
    print("\n" + "="*70)
    print("COLLEGE BASKETBALL SCORE SIMULATOR")
    print("="*70)
    print("\nChoose a simulator:")
    print("  1. Basic Score Simulator")
    print("  2. Advanced Score Simulator (with detailed stats)")
    print("  3. Custom Match (Basic)")
    print("  4. Custom Match (Advanced)")
    print("  5. Exit")
    print("="*70)


def get_team_input(prompt):
    """Get team name and skill level from user."""
    print(f"\n{prompt}")
    name = input("  Team name: ").strip()
    if not name:
        name = "Team"
    
    while True:
        try:
            skill = input("  Skill level (30-90, default 60): ").strip()
            if not skill:
                skill = 60
            else:
                skill = int(skill)
            
            if 30 <= skill <= 90:
                return name, skill
            else:
                print("  Please enter a value between 30 and 90.")
        except ValueError:
            print("  Please enter a valid number.")


def run_basic_simulator():
    """Run the basic score simulator with preset teams."""
    print("\n" + "="*70)
    print("BASIC SCORE SIMULATOR")
    print("="*70)
    
    team1 = Team("Duke Blue Devils", skill_level=75)
    team2 = Team("North Carolina Tar Heels", skill_level=72)
    
    game = BasketballGame(team1, team2)
    game.simulate_game(verbose=True)
    game.print_final_score()


def run_advanced_simulator():
    """Run the advanced score simulator with preset teams."""
    print("\n" + "="*70)
    print("ADVANCED SCORE SIMULATOR")
    print("="*70)
    
    team1 = AdvancedTeam("Kentucky Wildcats", skill_level=78)
    team2 = AdvancedTeam("Kansas Jayhawks", skill_level=76)
    
    game = AdvancedGame(team1, team2)
    game.simulate_game(verbose=True)
    game.print_final_stats()


def run_custom_basic():
    """Run a custom basic simulation with user-defined teams."""
    print("\n" + "="*70)
    print("CUSTOM BASIC MATCH")
    print("="*70)
    
    name1, skill1 = get_team_input("Enter Team 1 details:")
    name2, skill2 = get_team_input("Enter Team 2 details:")
    
    team1 = Team(name1, skill_level=skill1)
    team2 = Team(name2, skill_level=skill2)
    
    game = BasketballGame(team1, team2)
    game.simulate_game(verbose=True)
    game.print_final_score()


def run_custom_advanced():
    """Run a custom advanced simulation with user-defined teams."""
    print("\n" + "="*70)
    print("CUSTOM ADVANCED MATCH")
    print("="*70)
    
    name1, skill1 = get_team_input("Enter Team 1 details:")
    name2, skill2 = get_team_input("Enter Team 2 details:")
    
    team1 = AdvancedTeam(name1, skill_level=skill1)
    team2 = AdvancedTeam(name2, skill_level=skill2)
    
    game = AdvancedGame(team1, team2)
    game.simulate_game(verbose=True)
    game.print_final_stats()


def main():
    """Main entry point for the CLI."""
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            run_basic_simulator()
        elif choice == '2':
            run_advanced_simulator()
        elif choice == '3':
            run_custom_basic()
        elif choice == '4':
            run_custom_advanced()
        elif choice == '5':
            print("\nThank you for using the Basketball Score Simulator!")
            print("Goodbye! 🏀\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 5.")
        
        # Ask if user wants to run another simulation
        print("\n" + "="*70)
        continue_choice = input("Run another simulation? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("\nThank you for using the Basketball Score Simulator!")
            print("Goodbye! 🏀\n")
            break


if __name__ == "__main__":
    main()
