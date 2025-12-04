#!/usr/bin/env python3
"""
Advanced College Basketball Score Simulator
Enhanced version with detailed player statistics, momentum system, and advanced features.
"""

import random


class Player:
    """Represents an individual basketball player."""
    
    def __init__(self, name, position, skill_level=50):
        """
        Initialize a player.
        
        Args:
            name: Player name
            position: Position (PG, SG, SF, PF, C)
            skill_level: Player skill (0-100)
        """
        self.name = name
        self.position = position
        self.skill_level = skill_level
        self.points = 0
        self.rebounds = 0
        self.assists = 0
        self.steals = 0
        self.blocks = 0
        self.fouls = 0


class AdvancedTeam:
    """Advanced team with roster, momentum, and detailed statistics."""
    
    def __init__(self, name, skill_level=50):
        """
        Initialize an advanced team.
        
        Args:
            name: Team name
            skill_level: Overall team skill (0-100)
        """
        self.name = name
        self.skill_level = skill_level
        self.score = 0
        self.fouls = 0
        self.momentum = 0  # -10 to +10, affects performance
        self.timeouts_remaining = 4
        
        # Statistics
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
        
        # Create roster
        self.roster = self._create_roster()
        
        # Base shooting percentages
        self.base_fg_pct = 0.35 + (skill_level / 200)
        self.base_3pt_pct = 0.25 + (skill_level / 250)
        self.base_ft_pct = 0.60 + (skill_level / 250)
    
    def _create_roster(self):
        """Create a basic roster of players."""
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        roster = []
        for i, pos in enumerate(positions):
            skill_variation = random.randint(-10, 10)
            player_skill = max(30, min(90, self.skill_level + skill_variation))
            player = Player(f"Player {i+1}", pos, player_skill)
            roster.append(player)
        return roster
    
    def get_effective_percentage(self, base_pct):
        """Calculate effective percentage with momentum modifier."""
        momentum_modifier = self.momentum * 0.02  # +/- 2% per momentum point
        return max(0.1, min(0.95, base_pct + momentum_modifier))
    
    def attempt_shot(self, shot_type='2pt'):
        """
        Attempt a shot.
        
        Args:
            shot_type: '2pt', '3pt', or 'ft'
            
        Returns:
            tuple: (made, points)
        """
        if shot_type == '3pt':
            self.three_pointers_attempted += 1
            pct = self.get_effective_percentage(self.base_3pt_pct)
            if random.random() < pct:
                self.three_pointers_made += 1
                self.score += 3
                self.update_momentum(1)
                return True, 3
            self.update_momentum(-0.5)
            return False, 0
            
        elif shot_type == 'ft':
            self.free_throws_attempted += 1
            pct = self.get_effective_percentage(self.base_ft_pct)
            if random.random() < pct:
                self.free_throws_made += 1
                self.score += 1
                return True, 1
            return False, 0
            
        else:  # 2pt
            self.field_goals_attempted += 1
            pct = self.get_effective_percentage(self.base_fg_pct)
            if random.random() < pct:
                self.field_goals_made += 1
                self.score += 2
                self.update_momentum(1)
                return True, 2
            self.update_momentum(-0.5)
            return False, 0
    
    def update_momentum(self, change):
        """Update team momentum."""
        self.momentum = max(-10, min(10, self.momentum + change))
    
    def add_rebound(self):
        """Add a rebound."""
        self.rebounds += 1
    
    def add_assist(self):
        """Add an assist."""
        self.assists += 1
    
    def add_steal(self):
        """Add a steal."""
        self.steals += 1
        self.update_momentum(1.5)
    
    def add_block(self):
        """Add a block."""
        self.blocks += 1
        self.update_momentum(1)
    
    def add_turnover(self):
        """Add a turnover."""
        self.turnovers += 1
        self.update_momentum(-1.5)
    
    def commit_foul(self):
        """Commit a foul."""
        self.fouls += 1
    
    def use_timeout(self):
        """Use a timeout (resets momentum)."""
        if self.timeouts_remaining > 0:
            self.timeouts_remaining -= 1
            self.momentum = 0
            return True
        return False
    
    def get_stats_summary(self):
        """Get formatted statistics summary."""
        fg_pct = (self.field_goals_made / self.field_goals_attempted * 100) if self.field_goals_attempted > 0 else 0
        three_pct = (self.three_pointers_made / self.three_pointers_attempted * 100) if self.three_pointers_attempted > 0 else 0
        ft_pct = (self.free_throws_made / self.free_throws_attempted * 100) if self.free_throws_attempted > 0 else 0
        
        return {
            'score': self.score,
            'fg': f"{self.field_goals_made}-{self.field_goals_attempted} ({fg_pct:.1f}%)",
            '3pt': f"{self.three_pointers_made}-{self.three_pointers_attempted} ({three_pct:.1f}%)",
            'ft': f"{self.free_throws_made}-{self.free_throws_attempted} ({ft_pct:.1f}%)",
            'rebounds': self.rebounds,
            'assists': self.assists,
            'steals': self.steals,
            'blocks': self.blocks,
            'turnovers': self.turnovers,
            'fouls': self.fouls
        }


class AdvancedGame:
    """Advanced basketball game simulation with detailed mechanics."""
    
    def __init__(self, team1, team2, halves=2, minutes_per_half=20):
        """
        Initialize an advanced game.
        
        Args:
            team1: First AdvancedTeam object
            team2: Second AdvancedTeam object
            halves: Number of halves (default 2)
            minutes_per_half: Minutes per half (default 20)
        """
        self.team1 = team1
        self.team2 = team2
        self.halves = halves
        self.minutes_per_half = minutes_per_half
        self.current_half = 1
        self.play_by_play = []
    
    def simulate_possession(self, offensive_team, defensive_team):
        """
        Simulate a possession with advanced mechanics.
        
        Args:
            offensive_team: Team with the ball
            defensive_team: Team on defense
            
        Returns:
            tuple: (points_scored, description)
        """
        # Check for turnover
        if random.random() < 0.12:  # 12% turnover rate
            offensive_team.add_turnover()
            
            # Check for steal
            if random.random() < 0.5:
                defensive_team.add_steal()
                return 0, f"💨 {defensive_team.name} steals the ball!"
            return 0, f"❌ {offensive_team.name} turnover"
        
        # Check for foul
        if random.random() < 0.18:  # 18% foul rate
            defensive_team.commit_foul()
            
            # Free throws
            made1, pts1 = offensive_team.attempt_shot('ft')
            made2, pts2 = offensive_team.attempt_shot('ft')
            total_pts = pts1 + pts2
            
            if total_pts == 2:
                return total_pts, f"🎯 {offensive_team.name} makes both free throws! +{total_pts}"
            elif total_pts == 1:
                return total_pts, f"🎯 {offensive_team.name} makes 1-of-2 FT. +{total_pts}"
            else:
                return 0, f"❌ {offensive_team.name} misses both free throws"
        
        # Determine shot type
        shot_choice = random.random()
        
        if shot_choice < 0.35:  # 35% chance of 3-pointer
            made, points = offensive_team.attempt_shot('3pt')
            
            if not made:
                # Rebound
                if random.random() < 0.7:
                    defensive_team.add_rebound()
                else:
                    offensive_team.add_rebound()
                return 0, f"❌ {offensive_team.name} missed 3-pointer"
            
            # Check for assist
            if random.random() < 0.6:
                offensive_team.add_assist()
                return points, f"🔥 {offensive_team.name} 3-POINTER! +{points} (assist)"
            return points, f"🔥 {offensive_team.name} 3-POINTER! +{points}"
            
        else:  # 2-point attempt
            # Check for block
            if random.random() < 0.08:
                defensive_team.add_block()
                return 0, f"🚫 {defensive_team.name} BLOCK!"
            
            made, points = offensive_team.attempt_shot('2pt')
            
            if not made:
                # Rebound
                if random.random() < 0.7:
                    defensive_team.add_rebound()
                else:
                    offensive_team.add_rebound()
                return 0, f"❌ {offensive_team.name} missed 2-pointer"
            
            # Check for assist
            if random.random() < 0.5:
                offensive_team.add_assist()
                return points, f"🏀 {offensive_team.name} scores! +{points} (assist)"
            return points, f"🏀 {offensive_team.name} scores! +{points}"
    
    def should_call_timeout(self, team, opponent):
        """Determine if team should call timeout based on momentum."""
        if team.timeouts_remaining > 0:
            # Call timeout if losing by 8+ and opponent has momentum > 5
            score_diff = opponent.score - team.score
            if score_diff >= 8 and opponent.momentum >= 5:
                return True
        return False
    
    def simulate_half(self, verbose=True):
        """Simulate one half of the game."""
        possessions = random.randint(32, 42)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"HALF {self.current_half}")
            print(f"{'='*70}\n")
        
        for i in range(possessions):
            # Alternate possessions
            if i % 2 == 0:
                offensive, defensive = self.team1, self.team2
            else:
                offensive, defensive = self.team2, self.team1
            
            # Check for timeout
            if self.should_call_timeout(offensive, defensive):
                if offensive.use_timeout():
                    if verbose:
                        print(f"⏱️  {offensive.name} calls TIMEOUT")
            
            points, description = self.simulate_possession(offensive, defensive)
            
            if verbose:
                print(f"{description}")
                if points > 0:
                    print(f"   Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}")
                    print(f"   Momentum: {self.team1.name} [{self.team1.momentum:+.1f}] | {self.team2.name} [{self.team2.momentum:+.1f}]\n")
        
        if verbose:
            print(f"\n{'─'*70}")
            print(f"End of Half {self.current_half}")
            print(f"{self.team1.name}: {self.team1.score} | {self.team2.name}: {self.team2.score}")
            print(f"{'─'*70}")
    
    def simulate_game(self, verbose=True):
        """Simulate the entire game."""
        if verbose:
            print(f"\n{'*'*70}")
            print(f"ADVANCED COLLEGE BASKETBALL SIMULATOR")
            print(f"{self.team1.name} vs {self.team2.name}")
            print(f"{'*'*70}")
        
        for half in range(self.halves):
            self.current_half = half + 1
            self.simulate_half(verbose)
        
        # Check for overtime
        if self.team1.score == self.team2.score:
            if verbose:
                print(f"\n{'='*70}")
                print("OVERTIME!")
                print(f"{'='*70}")
            self.simulate_overtime(verbose)
        
        return self.get_winner()
    
    def simulate_overtime(self, verbose=True):
        """Simulate overtime period."""
        overtime_possessions = 12
        
        for i in range(overtime_possessions):
            if self.team1.score != self.team2.score:
                break
            
            if i % 2 == 0:
                offensive, defensive = self.team1, self.team2
            else:
                offensive, defensive = self.team2, self.team1
            
            points, description = self.simulate_possession(offensive, defensive)
            
            if verbose:
                print(f"{description}")
                if points > 0:
                    print(f"   Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}\n")
    
    def get_winner(self):
        """Return the winning team."""
        if self.team1.score > self.team2.score:
            return self.team1
        elif self.team2.score > self.team1.score:
            return self.team2
        return None
    
    def print_final_stats(self):
        """Print comprehensive final statistics."""
        print(f"\n{'*'*70}")
        print("FINAL SCORE")
        print(f"{'*'*70}")
        print(f"{self.team1.name}: {self.team1.score}")
        print(f"{self.team2.name}: {self.team2.score}")
        print(f"{'*'*70}")
        
        winner = self.get_winner()
        if winner:
            margin = abs(self.team1.score - self.team2.score)
            print(f"\n🏆 {winner.name} wins by {margin} points!")
        else:
            print("\n🤝 Game ended in a tie!")
        
        # Print detailed stats
        print(f"\n{'='*70}")
        print("DETAILED STATISTICS")
        print(f"{'='*70}")
        
        stats1 = self.team1.get_stats_summary()
        stats2 = self.team2.get_stats_summary()
        
        print(f"\n{self.team1.name}:")
        print(f"  Field Goals: {stats1['fg']}")
        print(f"  3-Pointers: {stats1['3pt']}")
        print(f"  Free Throws: {stats1['ft']}")
        print(f"  Rebounds: {stats1['rebounds']}")
        print(f"  Assists: {stats1['assists']}")
        print(f"  Steals: {stats1['steals']}")
        print(f"  Blocks: {stats1['blocks']}")
        print(f"  Turnovers: {stats1['turnovers']}")
        print(f"  Fouls: {stats1['fouls']}")
        
        print(f"\n{self.team2.name}:")
        print(f"  Field Goals: {stats2['fg']}")
        print(f"  3-Pointers: {stats2['3pt']}")
        print(f"  Free Throws: {stats2['ft']}")
        print(f"  Rebounds: {stats2['rebounds']}")
        print(f"  Assists: {stats2['assists']}")
        print(f"  Steals: {stats2['steals']}")
        print(f"  Blocks: {stats2['blocks']}")
        print(f"  Turnovers: {stats2['turnovers']}")
        print(f"  Fouls: {stats2['fouls']}")


def main():
    """Main function to run an advanced game simulation."""
    print("Advanced College Basketball Score Simulator")
    print("="*70)
    
    # Create teams with different skill levels
    team1 = AdvancedTeam("Kentucky Wildcats", skill_level=78)
    team2 = AdvancedTeam("Kansas Jayhawks", skill_level=76)
    
    # Create and simulate game
    game = AdvancedGame(team1, team2)
    game.simulate_game(verbose=True)
    game.print_final_stats()


if __name__ == "__main__":
    main()
