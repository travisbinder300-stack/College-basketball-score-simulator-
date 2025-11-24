#!/usr/bin/env python3
"""
College Basketball Score Simulator
A realistic college basketball game simulator with accurate scoring mechanics.
"""

import random
from typing import Dict, Tuple


class Team:
    """Represents a college basketball team with statistics."""
    
    def __init__(self, name: str, **stats):
        self.name = name
        self.score = 0
        self.fouls = 0
        self.timeouts = 4
        
        # Default statistics (realistic college basketball averages)
        self.fg_percentage = stats.get('fg_percentage', 0.45)  # Field goal %
        self.three_pt_percentage = stats.get('three_pt_percentage', 0.35)  # 3-point %
        self.ft_percentage = stats.get('ft_percentage', 0.72)  # Free throw %
        self.turnover_rate = stats.get('turnover_rate', 0.15)  # Turnover probability
        self.offensive_rebound_rate = stats.get('offensive_rebound_rate', 0.30)
        self.defensive_rebound_rate = stats.get('defensive_rebound_rate', 0.70)
        self.three_pt_attempt_rate = stats.get('three_pt_attempt_rate', 0.35)  # % of shots that are 3s
        self.steal_rate = stats.get('steal_rate', 0.08)
        self.block_rate = stats.get('block_rate', 0.05)
        
        # Game stats
        self.field_goals_made = 0
        self.field_goals_attempted = 0
        self.three_pointers_made = 0
        self.three_pointers_attempted = 0
        self.free_throws_made = 0
        self.free_throws_attempted = 0
        self.rebounds = 0
        self.assists = 0
        self.steals = 0
        self.blocks = 0
        self.turnovers = 0
    
    def attempt_shot(self, is_three_pointer: bool = False) -> Tuple[bool, int]:
        """
        Attempt a shot.
        Returns: (made, points_scored)
        """
        if is_three_pointer:
            self.three_pointers_attempted += 1
            made = random.random() < self.three_pt_percentage
            if made:
                self.three_pointers_made += 1
                self.score += 3
                return True, 3
            return False, 0
        else:
            self.field_goals_attempted += 1
            made = random.random() < self.fg_percentage
            if made:
                self.field_goals_made += 1
                # 2-point shot
                self.score += 2
                return True, 2
            return False, 0
    
    def attempt_free_throw(self) -> Tuple[bool, int]:
        """Attempt a free throw. Returns: (made, points_scored)"""
        self.free_throws_attempted += 1
        made = random.random() < self.ft_percentage
        if made:
            self.free_throws_made += 1
            self.score += 1
            return True, 1
        return False, 0
    
    def commit_turnover(self):
        """Record a turnover."""
        self.turnovers += 1
    
    def get_rebound(self):
        """Record a rebound."""
        self.rebounds += 1
    
    def get_stats(self) -> Dict:
        """Return comprehensive game statistics."""
        fg_pct = (self.field_goals_made / self.field_goals_attempted * 100) if self.field_goals_attempted > 0 else 0
        three_pct = (self.three_pointers_made / self.three_pointers_attempted * 100) if self.three_pointers_attempted > 0 else 0
        ft_pct = (self.free_throws_made / self.free_throws_attempted * 100) if self.free_throws_attempted > 0 else 0
        
        return {
            'name': self.name,
            'score': self.score,
            'fg': f"{self.field_goals_made}/{self.field_goals_attempted} ({fg_pct:.1f}%)",
            '3pt': f"{self.three_pointers_made}/{self.three_pointers_attempted} ({three_pct:.1f}%)",
            'ft': f"{self.free_throws_made}/{self.free_throws_attempted} ({ft_pct:.1f}%)",
            'rebounds': self.rebounds,
            'assists': self.assists,
            'steals': self.steals,
            'blocks': self.blocks,
            'turnovers': self.turnovers,
            'fouls': self.fouls
        }


class BasketballSimulator:
    """Simulates a college basketball game."""
    
    def __init__(self, team1: Team, team2: Team, verbose: bool = True):
        self.team1 = team1
        self.team2 = team2
        self.verbose = verbose
        self.possession_count = 0
    
    def log(self, message: str):
        """Log a game event."""
        if self.verbose:
            print(message)
    
    def simulate_possession(self, offense: Team, defense: Team) -> bool:
        """
        Simulate a single possession.
        Returns True if possession results in a score, False otherwise.
        """
        self.possession_count += 1
        
        # Check for turnover
        if random.random() < offense.turnover_rate:
            # Check if defense gets a steal
            if random.random() < defense.steal_rate:
                defense.steals += 1
                self.log(f"  {defense.name} steals the ball!")
            offense.commit_turnover()
            self.log(f"  {offense.name} turns the ball over!")
            return False
        
        # Decide shot type (3-pointer or 2-pointer)
        is_three = random.random() < offense.three_pt_attempt_rate
        
        # Attempt shot
        shot_type = "3-pointer" if is_three else "2-pointer"
        made, points = offense.attempt_shot(is_three)
        
        if made:
            # Randomly assign assist
            if random.random() < 0.60:  # 60% of made shots get assists
                offense.assists += 1
            self.log(f"  {offense.name} scores {points} points on a {shot_type}! Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}")
            return True
        else:
            # Check for block
            if random.random() < defense.block_rate:
                defense.blocks += 1
                self.log(f"  {defense.name} blocks the shot!")
            
            # Rebound battle
            if random.random() < offense.offensive_rebound_rate:
                offense.get_rebound()
                self.log(f"  {offense.name} gets the offensive rebound!")
                # Second chance - simplified (just attempt another shot)
                made2, points2 = offense.attempt_shot(False)  # Usually 2-point attempts
                if made2:
                    if random.random() < 0.40:
                        offense.assists += 1
                    self.log(f"  {offense.name} scores {points2} points on the putback! Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}")
                    return True
                else:
                    # Defense rebounds after putback attempt
                    defense.get_rebound()
            else:
                defense.get_rebound()
                self.log(f"  {defense.name} gets the defensive rebound.")
            
            return False
    
    def check_for_foul(self, team: Team) -> int:
        """
        Check if a foul occurs. Returns number of free throws awarded (0, 1, 2, or 3).
        """
        # Roughly 20% chance of a foul per possession
        if random.random() < 0.20:
            team.fouls += 1
            
            # Determine free throw situation
            foul_type = random.random()
            if foul_type < 0.50:
                return 2  # Shooting foul, 2 free throws
            elif foul_type < 0.60:
                return 1  # And-1 situation (already scored)
            elif foul_type < 0.65:
                return 3  # 3-point shooting foul
            else:
                return 0  # Non-shooting foul
        return 0
    
    def simulate_half(self, half_number: int) -> None:
        """Simulate one half of basketball (20 minutes)."""
        self.log(f"\n{'='*60}")
        self.log(f"{'HALF ' + str(half_number):^60}")
        self.log(f"{'='*60}\n")
        
        # College basketball: roughly 70 total possessions per half (35 per team)
        total_possessions = 70
        
        for i in range(total_possessions):
            # Alternate possessions
            if (i + half_number) % 2 == 0:
                offense = self.team1
                defense = self.team2
            else:
                offense = self.team2
                defense = self.team1
            
            self.log(f"\nPossession {i+1}: {offense.name} has the ball")
            
            # Check for foul before possession
            free_throws = self.check_for_foul(defense)
            if free_throws > 0:
                self.log(f"  Foul called on {defense.name}!")
                for ft in range(free_throws):
                    made, points = offense.attempt_free_throw()
                    if made:
                        self.log(f"  {offense.name} makes free throw {ft+1}! Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}")
                    else:
                        self.log(f"  {offense.name} misses free throw {ft+1}")
                        # Rebound after missed FT
                        if random.random() < 0.70:
                            defense.get_rebound()
                        else:
                            offense.get_rebound()
                continue
            
            # Regular possession
            self.simulate_possession(offense, defense)
        
        self.log(f"\n{'='*60}")
        self.log(f"End of Half {half_number}")
        self.log(f"{self.team1.name}: {self.team1.score}")
        self.log(f"{self.team2.name}: {self.team2.score}")
        self.log(f"{'='*60}\n")
    
    def simulate_game(self) -> Tuple[Team, Dict]:
        """
        Simulate a complete basketball game.
        Returns: (winning_team, game_summary)
        """
        self.log("\n" + "="*60)
        self.log(f"{'COLLEGE BASKETBALL SIMULATION':^60}")
        self.log(f"{self.team1.name:^30} vs {self.team2.name:^30}")
        self.log("="*60)
        
        # Simulate both halves
        self.simulate_half(1)
        self.simulate_half(2)
        
        # Check for overtime
        overtime_count = 0
        while self.team1.score == self.team2.score:
            overtime_count += 1
            self.log(f"\n{'='*60}")
            self.log(f"{'OVERTIME ' + str(overtime_count):^60}")
            self.log(f"{'='*60}\n")
            
            # Overtime: 10 possessions total (5 per team)
            for i in range(10):
                if i % 2 == 0:
                    self.simulate_possession(self.team1, self.team2)
                else:
                    self.simulate_possession(self.team2, self.team1)
        
        # Determine winner
        winner = self.team1 if self.team1.score > self.team2.score else self.team2
        loser = self.team2 if winner == self.team1 else self.team1
        
        # Print final results
        self.log("\n" + "="*60)
        self.log(f"{'FINAL SCORE':^60}")
        self.log("="*60)
        self.log(f"{self.team1.name}: {self.team1.score}")
        self.log(f"{self.team2.name}: {self.team2.score}")
        self.log(f"\nWinner: {winner.name}")
        self.log("="*60)
        
        # Print detailed stats
        self.print_box_score()
        
        game_summary = {
            'winner': winner.name,
            'final_score': f"{self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}",
            'overtime_periods': overtime_count,
            'total_possessions': self.possession_count,
            'team1_stats': self.team1.get_stats(),
            'team2_stats': self.team2.get_stats()
        }
        
        return winner, game_summary
    
    def print_box_score(self):
        """Print detailed box score."""
        self.log("\n" + "="*60)
        self.log(f"{'BOX SCORE':^60}")
        self.log("="*60)
        
        for team in [self.team1, self.team2]:
            stats = team.get_stats()
            self.log(f"\n{stats['name']}:")
            self.log(f"  Points: {stats['score']}")
            self.log(f"  Field Goals: {stats['fg']}")
            self.log(f"  3-Pointers: {stats['3pt']}")
            self.log(f"  Free Throws: {stats['ft']}")
            self.log(f"  Rebounds: {stats['rebounds']}")
            self.log(f"  Assists: {stats['assists']}")
            self.log(f"  Steals: {stats['steals']}")
            self.log(f"  Blocks: {stats['blocks']}")
            self.log(f"  Turnovers: {stats['turnovers']}")
            self.log(f"  Fouls: {stats['fouls']}")
        
        self.log("="*60)


def main():
    """Main function to run the simulator."""
    print("\n" + "="*60)
    print("COLLEGE BASKETBALL SCORE SIMULATOR")
    print("="*60)
    
    # Example: Create two teams with different strengths
    # Team 1: Strong offensive team
    team1 = Team(
        name="Blue Devils",
        fg_percentage=0.48,
        three_pt_percentage=0.38,
        ft_percentage=0.75,
        turnover_rate=0.12,
        offensive_rebound_rate=0.32,
        defensive_rebound_rate=0.72
    )
    
    # Team 2: Balanced team
    team2 = Team(
        name="Wildcats",
        fg_percentage=0.45,
        three_pt_percentage=0.35,
        ft_percentage=0.70,
        turnover_rate=0.14,
        offensive_rebound_rate=0.28,
        defensive_rebound_rate=0.68
    )
    
    # Create simulator and run game
    simulator = BasketballSimulator(team1, team2, verbose=True)
    winner, summary = simulator.simulate_game()
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    print(f"Winner: {winner.name}")
    print(f"Final Score: {summary['final_score']}")
    if summary['overtime_periods'] > 0:
        print(f"Overtime Periods: {summary['overtime_periods']}")
    print("="*60)


if __name__ == "__main__":
    main()
