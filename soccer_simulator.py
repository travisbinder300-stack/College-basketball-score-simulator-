#!/usr/bin/env python3
"""
Soccer Score Simulator

This simulator generates realistic soccer match scores between two teams.
It uses team ratings and random variations to simulate match outcomes.
"""

import random
import argparse
from typing import Tuple, Dict


class Team:
    """Represents a soccer team with ratings and statistics."""
    
    def __init__(self, name: str, attack_rating: float = 5.0, defense_rating: float = 5.0):
        """
        Initialize a team.
        
        Args:
            name: Team name
            attack_rating: Offensive strength (0-10 scale)
            defense_rating: Defensive strength (0-10 scale)
        """
        self.name = name
        self.attack_rating = max(0, min(10, attack_rating))
        self.defense_rating = max(0, min(10, defense_rating))
    
    def __str__(self):
        return f"{self.name} (ATK: {self.attack_rating:.1f}, DEF: {self.defense_rating:.1f})"


class SoccerSimulator:
    """Simulates soccer matches between two teams."""
    
    def __init__(self):
        """Initialize the simulator."""
        self.home_advantage = 0.3  # Small boost for home team
    
    def calculate_expected_goals(self, attacking_team: Team, defending_team: Team, 
                                 is_home: bool = False) -> float:
        """
        Calculate expected goals for a team.
        
        Args:
            attacking_team: The attacking team
            defending_team: The defending team
            is_home: Whether the attacking team is playing at home
            
        Returns:
            Expected number of goals
        """
        # Base expected goals around 1.5 per team
        base_goals = 1.5
        
        # Attack vs Defense differential
        attack_advantage = (attacking_team.attack_rating - defending_team.defense_rating) / 10.0
        
        # Home advantage
        home_boost = self.home_advantage if is_home else 0
        
        # Calculate expected goals with some bounds
        expected = base_goals + attack_advantage + home_boost
        return max(0.5, min(4.0, expected))
    
    def simulate_goals(self, expected_goals: float) -> int:
        """
        Simulate actual goals scored using Poisson-like distribution.
        
        Args:
            expected_goals: Expected number of goals
            
        Returns:
            Actual goals scored
        """
        # Use exponential distribution for realistic soccer scoring
        goals = 0
        while random.random() < (expected_goals / (goals + 1)):
            goals += 1
            if goals >= 10:  # Reasonable upper bound
                break
        return goals
    
    def simulate_match(self, home_team: Team, away_team: Team, 
                      verbose: bool = True) -> Tuple[int, int]:
        """
        Simulate a match between two teams.
        
        Args:
            home_team: The home team
            away_team: The away team
            verbose: Whether to print detailed information
            
        Returns:
            Tuple of (home_score, away_score)
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"MATCH SIMULATION")
            print(f"{'='*60}")
            print(f"Home: {home_team}")
            print(f"Away: {away_team}")
            print(f"{'='*60}\n")
        
        # Calculate expected goals
        home_expected = self.calculate_expected_goals(home_team, away_team, is_home=True)
        away_expected = self.calculate_expected_goals(away_team, home_team, is_home=False)
        
        if verbose:
            print(f"Expected goals - {home_team.name}: {home_expected:.2f}, "
                  f"{away_team.name}: {away_expected:.2f}")
        
        # Simulate actual goals
        home_score = self.simulate_goals(home_expected)
        away_score = self.simulate_goals(away_expected)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"FINAL SCORE")
            print(f"{'='*60}")
            print(f"{home_team.name}: {home_score}")
            print(f"{away_team.name}: {away_score}")
            
            if home_score > away_score:
                print(f"\n🏆 {home_team.name} wins!")
            elif away_score > home_score:
                print(f"\n🏆 {away_team.name} wins!")
            else:
                print(f"\n🤝 Match ends in a draw!")
            print(f"{'='*60}\n")
        
        return home_score, away_score
    
    def simulate_multiple_matches(self, home_team: Team, away_team: Team, 
                                  num_matches: int = 10) -> Dict:
        """
        Simulate multiple matches and return statistics.
        
        Args:
            home_team: The home team
            away_team: The away team
            num_matches: Number of matches to simulate
            
        Returns:
            Dictionary with statistics
        """
        print(f"\n{'='*60}")
        print(f"SIMULATING {num_matches} MATCHES")
        print(f"{'='*60}")
        print(f"Home: {home_team.name}")
        print(f"Away: {away_team.name}")
        print(f"{'='*60}\n")
        
        results = {
            'home_wins': 0,
            'away_wins': 0,
            'draws': 0,
            'home_total_goals': 0,
            'away_total_goals': 0,
            'matches': []
        }
        
        for i in range(num_matches):
            home_score, away_score = self.simulate_match(home_team, away_team, verbose=False)
            results['matches'].append((home_score, away_score))
            results['home_total_goals'] += home_score
            results['away_total_goals'] += away_score
            
            if home_score > away_score:
                results['home_wins'] += 1
            elif away_score > home_score:
                results['away_wins'] += 1
            else:
                results['draws'] += 1
        
        # Print results
        print(f"Results Summary:")
        print(f"-" * 60)
        print(f"{home_team.name} wins: {results['home_wins']} "
              f"({results['home_wins']/num_matches*100:.1f}%)")
        print(f"{away_team.name} wins: {results['away_wins']} "
              f"({results['away_wins']/num_matches*100:.1f}%)")
        print(f"Draws: {results['draws']} ({results['draws']/num_matches*100:.1f}%)")
        print(f"\nAverage goals per match:")
        print(f"{home_team.name}: {results['home_total_goals']/num_matches:.2f}")
        print(f"{away_team.name}: {results['away_total_goals']/num_matches:.2f}")
        print(f"\nAll match scores:")
        for i, (home, away) in enumerate(results['matches'], 1):
            result = "W" if home > away else "L" if home < away else "D"
            print(f"  Match {i:2d}: {home_team.name} {home}-{away} {away_team.name} ({result})")
        print(f"{'='*60}\n")
        
        return results


def main():
    """Main function to run the soccer simulator."""
    parser = argparse.ArgumentParser(
        description='Soccer Score Simulator - Simulate soccer matches between teams'
    )
    parser.add_argument('--home', type=str, default='Home Team',
                       help='Name of the home team')
    parser.add_argument('--away', type=str, default='Away Team',
                       help='Name of the away team')
    parser.add_argument('--home-attack', type=float, default=5.0,
                       help='Home team attack rating (0-10, default: 5.0)')
    parser.add_argument('--home-defense', type=float, default=5.0,
                       help='Home team defense rating (0-10, default: 5.0)')
    parser.add_argument('--away-attack', type=float, default=5.0,
                       help='Away team attack rating (0-10, default: 5.0)')
    parser.add_argument('--away-defense', type=float, default=5.0,
                       help='Away team defense rating (0-10, default: 5.0)')
    parser.add_argument('--matches', type=int, default=1,
                       help='Number of matches to simulate (default: 1)')
    
    args = parser.parse_args()
    
    # Create teams
    home_team = Team(args.home, args.home_attack, args.home_defense)
    away_team = Team(args.away, args.away_attack, args.away_defense)
    
    # Create simulator
    simulator = SoccerSimulator()
    
    # Run simulation
    if args.matches == 1:
        simulator.simulate_match(home_team, away_team)
    else:
        simulator.simulate_multiple_matches(home_team, away_team, args.matches)


if __name__ == '__main__':
    main()
