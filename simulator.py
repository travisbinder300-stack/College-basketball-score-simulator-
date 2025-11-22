#!/usr/bin/env python3
"""
College Basketball Score Simulator

This module simulates college basketball games between two teams,
generating realistic scores based on team statistics and random events.
"""

import random
import argparse
from typing import Dict, Tuple


class Team:
    """Represents a college basketball team with performance statistics."""
    
    def __init__(self, name: str, offense_rating: float = 50.0, 
                 defense_rating: float = 50.0, three_point_pct: float = 0.35,
                 free_throw_pct: float = 0.75):
        """
        Initialize a basketball team.
        
        Args:
            name: Team name
            offense_rating: Offensive skill (0-100, higher is better)
            defense_rating: Defensive skill (0-100, higher is better)
            three_point_pct: Three-point shooting percentage (0.0-1.0)
            free_throw_pct: Free throw shooting percentage (0.0-1.0)
        """
        self.name = name
        self.offense_rating = max(0, min(100, offense_rating))
        self.defense_rating = max(0, min(100, defense_rating))
        self.three_point_pct = max(0.0, min(1.0, three_point_pct))
        self.free_throw_pct = max(0.0, min(1.0, free_throw_pct))
        
    def __str__(self) -> str:
        return f"{self.name} (OFF: {self.offense_rating:.1f}, DEF: {self.defense_rating:.1f})"


class BasketballSimulator:
    """Simulates college basketball games."""
    
    def __init__(self, home_team: Team, away_team: Team, verbose: bool = False):
        """
        Initialize the simulator.
        
        Args:
            home_team: Home team
            away_team: Away team
            verbose: If True, print play-by-play details
        """
        self.home_team = home_team
        self.away_team = away_team
        self.verbose = verbose
        self.home_score = 0
        self.away_score = 0
        
    def simulate_possession(self, offensive_team: Team, defensive_team: Team) -> int:
        """
        Simulate a single possession.
        
        Args:
            offensive_team: Team on offense
            defensive_team: Team on defense
            
        Returns:
            Points scored on this possession (0, 1, 2, or 3)
        """
        # Check for turnover (relatively rare in college basketball)
        turnover_rate = 0.15 + (defensive_team.defense_rating - offensive_team.offense_rating) / 300
        turnover_rate = max(0.10, min(0.25, turnover_rate))
        
        if random.random() < turnover_rate:
            # Turnover - no points
            return 0
        
        # Decide shot type
        shot_type = random.random()
        
        if shot_type < 0.30:  # 30% chance of 3-point attempt
            if random.random() < offensive_team.three_point_pct:
                if self.verbose:
                    print(f"  {offensive_team.name} scores a 3-pointer!")
                return 3
            else:
                if self.verbose:
                    print(f"  {offensive_team.name} misses a 3-pointer")
                return 0
                
        elif shot_type < 0.80:  # 50% chance of 2-point attempt
            # 2-point shots have higher success rate
            two_point_success = 0.48 + (offensive_team.offense_rating - defensive_team.defense_rating) / 200
            two_point_success = max(0.35, min(0.65, two_point_success))
            if random.random() < two_point_success:
                if self.verbose:
                    print(f"  {offensive_team.name} scores a 2-pointer!")
                return 2
            else:
                if self.verbose:
                    print(f"  {offensive_team.name} misses a 2-pointer")
                return 0
                
        else:  # 20% chance of free throws (from foul)
            # Typically get 2 free throw attempts
            points = 0
            if random.random() < offensive_team.free_throw_pct:
                points += 1
            if random.random() < offensive_team.free_throw_pct:
                points += 1
            if self.verbose:
                print(f"  {offensive_team.name} scores {points} point(s) from free throws")
            return points
    
    def simulate_game(self, total_possessions: int = 140) -> Tuple[int, int]:
        """
        Simulate a full game.
        
        Args:
            total_possessions: Total number of possessions in the game
                             (approximately 70 per team for a typical college game)
        
        Returns:
            Tuple of (home_score, away_score)
        """
        self.home_score = 0
        self.away_score = 0
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"GAME START: {self.home_team.name} vs {self.away_team.name}")
            print(f"{'='*60}\n")
        
        # Simulate alternating possessions
        for possession_num in range(total_possessions):
            if possession_num % 2 == 0:
                # Home team possession
                points = self.simulate_possession(self.home_team, self.away_team)
                self.home_score += points
            else:
                # Away team possession
                points = self.simulate_possession(self.away_team, self.home_team)
                self.away_score += points
                
            # Show periodic score updates
            if self.verbose and (possession_num + 1) % 20 == 0:
                print(f"\n--- After {possession_num + 1} possessions ---")
                print(f"{self.home_team.name}: {self.home_score}")
                print(f"{self.away_team.name}: {self.away_score}\n")
        
        return self.home_score, self.away_score
    
    def print_final_score(self):
        """Print the final game result."""
        print(f"\n{'='*60}")
        print("FINAL SCORE")
        print(f"{'='*60}")
        print(f"{self.home_team.name:30s} {self.home_score:3d}")
        print(f"{self.away_team.name:30s} {self.away_score:3d}")
        print(f"{'='*60}")
        
        if self.home_score > self.away_score:
            print(f"\n{self.home_team.name} wins by {self.home_score - self.away_score} points!")
        elif self.away_score > self.home_score:
            print(f"\n{self.away_team.name} wins by {self.away_score - self.home_score} points!")
        else:
            print("\nThe game is tied!")


def create_sample_teams() -> Dict[str, Team]:
    """Create a set of sample college basketball teams."""
    teams = {
        'duke': Team('Duke Blue Devils', offense_rating=85, defense_rating=80, 
                    three_point_pct=0.38, free_throw_pct=0.78),
        'unc': Team('North Carolina Tar Heels', offense_rating=82, defense_rating=75,
                   three_point_pct=0.36, free_throw_pct=0.75),
        'kentucky': Team('Kentucky Wildcats', offense_rating=88, defense_rating=85,
                        three_point_pct=0.37, free_throw_pct=0.76),
        'kansas': Team('Kansas Jayhawks', offense_rating=84, defense_rating=78,
                      three_point_pct=0.39, free_throw_pct=0.77),
        'villanova': Team('Villanova Wildcats', offense_rating=86, defense_rating=82,
                         three_point_pct=0.40, free_throw_pct=0.80),
        'gonzaga': Team('Gonzaga Bulldogs', offense_rating=87, defense_rating=79,
                       three_point_pct=0.38, free_throw_pct=0.79),
        'alabama_state': Team('Alabama State Hornets', offense_rating=55, defense_rating=52,
                             three_point_pct=0.32, free_throw_pct=0.68),
        'iupui': Team('IUPUI Jaguars', offense_rating=53, defense_rating=50,
                     three_point_pct=0.31, free_throw_pct=0.67),
        'campbell': Team('Campbell Fighting Camels', offense_rating=54, defense_rating=51,
                        three_point_pct=0.33, free_throw_pct=0.69),
        'ut_arlington': Team('UT Arlington Mavericks', offense_rating=56, defense_rating=53,
                            three_point_pct=0.34, free_throw_pct=0.70),
        'ball_state': Team('Ball State Cardinals', offense_rating=57, defense_rating=54,
                          three_point_pct=0.35, free_throw_pct=0.71),
        'indiana_state': Team('Indiana State Sycamores', offense_rating=55, defense_rating=52,
                             three_point_pct=0.33, free_throw_pct=0.69),
        'njit': Team('NJIT Highlanders', offense_rating=52, defense_rating=49,
                    three_point_pct=0.32, free_throw_pct=0.68),
        'navy': Team('Navy Midshipmen', offense_rating=56, defense_rating=54,
                    three_point_pct=0.34, free_throw_pct=0.71),
    }
    return teams


def main():
    """Main entry point for the simulator."""
    parser = argparse.ArgumentParser(
        description='Simulate college basketball games',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s duke unc                    # Simulate Duke vs UNC
  %(prog)s duke unc --verbose          # Show play-by-play
  %(prog)s duke unc --games 10         # Simulate 10 games
  %(prog)s --list-teams                # Show all available teams
        """
    )
    parser.add_argument('home_team', nargs='?', help='Home team name')
    parser.add_argument('away_team', nargs='?', help='Away team name')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show play-by-play details')
    parser.add_argument('--games', '-g', type=int, default=1,
                       help='Number of games to simulate (default: 1)')
    parser.add_argument('--list-teams', '-l', action='store_true',
                       help='List all available teams')
    
    args = parser.parse_args()
    
    teams = create_sample_teams()
    
    # List teams if requested
    if args.list_teams:
        print("\nAvailable Teams:")
        print("=" * 60)
        for key, team in sorted(teams.items()):
            print(f"  {key:15s} - {team}")
        print("=" * 60)
        return
    
    # Validate team arguments
    if not args.home_team or not args.away_team:
        parser.error("Both home_team and away_team are required (use --list-teams to see options)")
    
    home_key = args.home_team.lower()
    away_key = args.away_team.lower()
    
    if home_key not in teams:
        print(f"Error: Unknown home team '{args.home_team}'")
        print(f"Use --list-teams to see available teams")
        return
    
    if away_key not in teams:
        print(f"Error: Unknown away team '{args.away_team}'")
        print(f"Use --list-teams to see available teams")
        return
    
    home_team = teams[home_key]
    away_team = teams[away_key]
    
    # Simulate the requested number of games
    if args.games == 1:
        simulator = BasketballSimulator(home_team, away_team, args.verbose)
        simulator.simulate_game()
        simulator.print_final_score()
    else:
        print(f"\nSimulating {args.games} games between {home_team.name} and {away_team.name}...")
        print("=" * 60)
        
        home_wins = 0
        away_wins = 0
        total_home_score = 0
        total_away_score = 0
        
        for game_num in range(args.games):
            simulator = BasketballSimulator(home_team, away_team, verbose=False)
            home_score, away_score = simulator.simulate_game()
            
            total_home_score += home_score
            total_away_score += away_score
            
            if home_score > away_score:
                home_wins += 1
            elif away_score > home_score:
                away_wins += 1
            
            if args.verbose:
                print(f"Game {game_num + 1}: {home_team.name} {home_score}, "
                      f"{away_team.name} {away_score}")
        
        print(f"\nResults from {args.games} games:")
        print("=" * 60)
        print(f"{home_team.name:30s} {home_wins} wins")
        print(f"{away_team.name:30s} {away_wins} wins")
        print(f"\nAverage Score:")
        print(f"{home_team.name:30s} {total_home_score / args.games:.1f}")
        print(f"{away_team.name:30s} {total_away_score / args.games:.1f}")
        print("=" * 60)


if __name__ == '__main__':
    main()
