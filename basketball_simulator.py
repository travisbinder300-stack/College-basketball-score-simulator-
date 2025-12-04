#!/usr/bin/env python3
"""
College Basketball Score Simulator
Simulates a college basketball game between two teams with realistic scoring mechanics.
"""

import random
import time


class Team:
    """Represents a college basketball team with stats and performance attributes."""
    
    def __init__(self, name, skill_level=50):
        """
        Initialize a team.
        
        Args:
            name: Team name
            skill_level: Overall team skill (0-100), affects shooting percentages
        """
        self.name = name
        self.skill_level = skill_level
        self.score = 0
        self.fouls = 0
        
        # Calculate shooting percentages based on skill level
        self.fg_percentage = 0.35 + (skill_level / 200)  # 35-85%
        self.three_pt_percentage = 0.25 + (skill_level / 250)  # 25-65%
        self.ft_percentage = 0.60 + (skill_level / 250)  # 60-100%
    
    def attempt_field_goal(self):
        """Attempt a 2-point field goal."""
        if random.random() < self.fg_percentage:
            self.score += 2
            return True, 2
        return False, 0
    
    def attempt_three_pointer(self):
        """Attempt a 3-point shot."""
        if random.random() < self.three_pt_percentage:
            self.score += 3
            return True, 3
        return False, 0
    
    def attempt_free_throw(self):
        """Attempt a free throw."""
        if random.random() < self.ft_percentage:
            self.score += 1
            return True, 1
        return False, 0
    
    def commit_foul(self):
        """Commit a foul."""
        self.fouls += 1


class BasketballGame:
    """Simulates a college basketball game."""
    
    def __init__(self, team1, team2, halves=2, minutes_per_half=20):
        """
        Initialize a basketball game.
        
        Args:
            team1: First Team object
            team2: Second Team object
            halves: Number of halves (default 2)
            minutes_per_half: Minutes per half (default 20)
        """
        self.team1 = team1
        self.team2 = team2
        self.halves = halves
        self.minutes_per_half = minutes_per_half
        self.current_half = 1
        self.time_remaining = minutes_per_half * 60  # in seconds
    
    def simulate_possession(self, offensive_team, defensive_team):
        """
        Simulate a single possession.
        
        Args:
            offensive_team: Team with the ball
            defensive_team: Team on defense
            
        Returns:
            tuple: (points_scored, description)
        """
        # Decide shot type
        shot_choice = random.random()
        
        # Check for foul
        if random.random() < 0.15:  # 15% chance of foul
            defensive_team.commit_foul()
            made1, pts1 = offensive_team.attempt_free_throw()
            made2, pts2 = offensive_team.attempt_free_throw()
            total_pts = pts1 + pts2
            if total_pts == 2:
                return total_pts, f"{offensive_team.name} made both free throws! +{total_pts}"
            elif total_pts == 1:
                return total_pts, f"{offensive_team.name} made 1 of 2 free throws. +{total_pts}"
            else:
                return 0, f"{offensive_team.name} missed both free throws."
        
        # Attempt shot
        if shot_choice < 0.3:  # 30% chance of 3-pointer
            made, points = offensive_team.attempt_three_pointer()
            if made:
                return points, f"{offensive_team.name} made a 3-pointer! +{points}"
            else:
                return 0, f"{offensive_team.name} missed a 3-pointer."
        else:  # 2-point attempt
            made, points = offensive_team.attempt_field_goal()
            if made:
                return points, f"{offensive_team.name} made a 2-pointer! +{points}"
            else:
                return 0, f"{offensive_team.name} missed a 2-pointer."
    
    def simulate_half(self, verbose=True):
        """Simulate one half of the game."""
        possessions = random.randint(30, 40)  # Typical possessions per half
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"HALF {self.current_half}")
            print(f"{'='*60}\n")
        
        for i in range(possessions):
            # Alternate possessions
            if i % 2 == 0:
                offensive, defensive = self.team1, self.team2
            else:
                offensive, defensive = self.team2, self.team1
            
            points, description = self.simulate_possession(offensive, defensive)
            
            if verbose and points > 0:
                print(f"{description}")
                print(f"Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}\n")
        
        if verbose:
            print(f"\nEnd of Half {self.current_half}")
            print(f"{self.team1.name}: {self.team1.score}")
            print(f"{self.team2.name}: {self.team2.score}")
    
    def simulate_game(self, verbose=True):
        """Simulate the entire game."""
        if verbose:
            print(f"\n{'*'*60}")
            print(f"COLLEGE BASKETBALL GAME")
            print(f"{self.team1.name} vs {self.team2.name}")
            print(f"{'*'*60}")
        
        for half in range(self.halves):
            self.current_half = half + 1
            self.simulate_half(verbose)
        
        # Check for overtime
        if self.team1.score == self.team2.score:
            if verbose:
                print("\n" + "="*60)
                print("OVERTIME!")
                print("="*60)
            self.simulate_overtime(verbose)
        
        return self.get_winner()
    
    def simulate_overtime(self, verbose=True):
        """Simulate overtime period."""
        overtime_possessions = 10
        
        for i in range(overtime_possessions):
            if self.team1.score != self.team2.score:
                break
            
            if i % 2 == 0:
                offensive, defensive = self.team1, self.team2
            else:
                offensive, defensive = self.team2, self.team1
            
            points, description = self.simulate_possession(offensive, defensive)
            
            if verbose and points > 0:
                print(f"{description}")
                print(f"Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}\n")
    
    def get_winner(self):
        """Return the winning team."""
        if self.team1.score > self.team2.score:
            return self.team1
        elif self.team2.score > self.team1.score:
            return self.team2
        else:
            return None
    
    def print_final_score(self):
        """Print the final score and winner."""
        print(f"\n{'*'*60}")
        print("FINAL SCORE")
        print(f"{'*'*60}")
        print(f"{self.team1.name}: {self.team1.score}")
        print(f"{self.team2.name}: {self.team2.score}")
        print(f"{'*'*60}")
        
        winner = self.get_winner()
        if winner:
            print(f"\n🏆 {winner.name} wins!")
        else:
            print("\n🤝 Game ended in a tie!")
        
        print(f"\nTeam Fouls:")
        print(f"{self.team1.name}: {self.team1.fouls}")
        print(f"{self.team2.name}: {self.team2.fouls}")


def main():
    """Main function to run a basketball game simulation."""
    print("College Basketball Score Simulator")
    print("="*60)
    
    # Create teams with different skill levels
    team1 = Team("Duke Blue Devils", skill_level=75)
    team2 = Team("North Carolina Tar Heels", skill_level=72)
    
    # Create and simulate game
    game = BasketballGame(team1, team2)
    game.simulate_game(verbose=True)
    game.print_final_score()


if __name__ == "__main__":
    main()
