#!/usr/bin/env python3
"""
College Football Score Simulator
A realistic college football game simulator with accurate scoring mechanics.

Enhanced for better real-game accuracy with:
- Game-to-game variance in team performance
- Home field advantage
- Momentum and scoring run mechanics
- Time of possession adjustments
- Different play types (rush, pass, special teams)
"""

import random
from typing import Dict, Tuple, List


class FootballTeam:
    """Represents a college football team with statistics."""
    
    def __init__(self, name: str, **stats):
        self.name = name
        self.score = 0
        self.timeouts = 3
        
        # Offensive statistics (realistic college football averages)
        self.pass_completion_pct = stats.get('pass_completion_pct', 0.60)  # Pass completion %
        self.yards_per_completion = stats.get('yards_per_completion', 12.0)  # Avg yards per completion
        self.rush_yards_per_carry = stats.get('rush_yards_per_carry', 4.5)  # Avg rush yards
        self.turnover_rate = stats.get('turnover_rate', 0.03)  # Turnover probability per play
        self.red_zone_td_pct = stats.get('red_zone_td_pct', 0.60)  # Red zone TD %
        self.field_goal_pct = stats.get('field_goal_pct', 0.75)  # FG success rate
        self.pass_play_rate = stats.get('pass_play_rate', 0.55)  # % of plays that are passes
        
        # Defensive statistics
        self.sack_rate = stats.get('sack_rate', 0.06)  # Probability of sack
        self.interception_rate = stats.get('interception_rate', 0.025)  # INT rate on pass plays
        self.fumble_recovery_rate = stats.get('fumble_recovery_rate', 0.50)  # Fumble recovery %
        
        # Special teams
        self.punt_avg = stats.get('punt_avg', 42.0)  # Avg punt distance
        self.kickoff_touchback_rate = stats.get('kickoff_touchback_rate', 0.65)
        self.kick_return_avg = stats.get('kick_return_avg', 22.0)
        
        # Advanced stats for realism
        self.home_field = stats.get('home_field', False)  # Is this team playing at home?
        self.pace_factor = stats.get('pace_factor', 1.0)  # 1.0 = average, affects plays per game
        
        # Game-day variance settings (simulate hot/cold performances)
        self.variance_enabled = stats.get('variance_enabled', True)
        self.game_variance = 0.0  # Set during game initialization
        
        # Momentum tracking
        self.current_momentum = 0.0  # -1.0 to 1.0, affects performance
        self.consecutive_scores = 0
        
        # Game stats
        self.touchdowns = 0
        self.field_goals = 0
        self.safeties = 0
        self.pass_attempts = 0
        self.pass_completions = 0
        self.pass_yards = 0
        self.rush_attempts = 0
        self.rush_yards = 0
        self.turnovers = 0
        self.sacks_allowed = 0
        self.first_downs = 0
        self.third_down_attempts = 0
        self.third_down_conversions = 0
        self.time_of_possession = 0  # In seconds
        self.punts = 0
        self.punt_yards = 0
    
    def initialize_game_variance(self):
        """
        Set random game-day variance to simulate hot/cold performances.
        This is called at the start of each game to vary team performance.
        """
        if self.variance_enabled:
            # Variance: -0.08 to +0.08 (8% better or worse)
            self.game_variance = random.gauss(0, 0.035)
            self.game_variance = max(-0.08, min(0.08, self.game_variance))
        else:
            self.game_variance = 0.0
    
    def get_effective_pass_pct(self) -> float:
        """Get pass completion percentage adjusted for variance, home field, and momentum."""
        base = self.pass_completion_pct + self.game_variance
        
        # Home field advantage: +3% to pass completion
        if self.home_field:
            base += 0.03
        
        # Momentum bonus: up to +5% when on a roll
        base += self.current_momentum * 0.05
        
        # Keep within realistic bounds
        return max(0.35, min(0.85, base))
    
    def get_effective_rush_yards(self) -> float:
        """Get rushing yards per carry adjusted for variance and momentum."""
        base = self.rush_yards_per_carry + (self.game_variance * 10)  # Scale variance to yards
        
        # Home field advantage: +0.3 yards per carry
        if self.home_field:
            base += 0.3
        
        # Momentum bonus: up to +1.0 yard per carry when hot
        base += self.current_momentum * 1.0
        
        return max(2.0, min(8.0, base))
    
    def get_effective_red_zone_pct(self) -> float:
        """Get red zone TD percentage adjusted for momentum."""
        base = self.red_zone_td_pct + self.game_variance
        
        # Home field slight boost
        if self.home_field:
            base += 0.05
        
        # Momentum affects red zone efficiency
        base += self.current_momentum * 0.10
        
        return max(0.40, min(0.90, base))
    
    def update_momentum(self, scored: bool, big_play: bool = False):
        """Update momentum based on scoring and big plays."""
        if scored:
            self.consecutive_scores += 1
            momentum_gain = 0.20
            if big_play:
                momentum_gain = 0.30
            if self.consecutive_scores >= 2:
                momentum_gain = 0.25
            self.current_momentum = min(1.0, self.current_momentum + momentum_gain)
        else:
            self.consecutive_scores = 0
            self.current_momentum = max(-1.0, self.current_momentum - 0.10)
    
    def attempt_pass(self, defense_sack_rate: float) -> Tuple[bool, int, str]:
        """
        Attempt a pass play.
        Returns: (completed, yards_gained, result_type)
        """
        self.pass_attempts += 1
        
        # Check for sack
        effective_sack_rate = defense_sack_rate
        if self.current_momentum < 0:
            effective_sack_rate += 0.02  # More sacks when cold
        
        if random.random() < effective_sack_rate:
            self.sacks_allowed += 1
            yards_lost = random.randint(4, 12)
            return False, -yards_lost, "sack"
        
        # Check for interception
        effective_int_rate = self.interception_rate
        if self.current_momentum < 0:
            effective_int_rate += 0.01
        
        if random.random() < effective_int_rate:
            self.turnovers += 1
            return False, 0, "interception"
        
        # Check for completion
        if random.random() < self.get_effective_pass_pct():
            self.pass_completions += 1
            # Yards gained varies based on play
            base_yards = self.yards_per_completion + (self.game_variance * 5)
            yards = int(random.gauss(base_yards, 6))
            yards = max(1, yards)
            
            # Chance for big play
            if random.random() < 0.08:  # 8% chance of big play
                yards = random.randint(25, 60)
            
            self.pass_yards += yards
            return True, yards, "completion"
        else:
            return False, 0, "incomplete"
    
    def attempt_rush(self) -> Tuple[bool, int, str]:
        """
        Attempt a rush play.
        Returns: (successful, yards_gained, result_type)
        """
        self.rush_attempts += 1
        
        # Check for fumble
        if random.random() < self.turnover_rate * 0.5:  # Fumbles less common than pass turnovers
            if random.random() > self.fumble_recovery_rate:
                self.turnovers += 1
                return False, 0, "fumble_lost"
        
        # Calculate yards gained
        base_yards = self.get_effective_rush_yards()
        yards = int(random.gauss(base_yards, 3))
        
        # Chance for negative play
        if random.random() < 0.15:
            yards = random.randint(-3, 1)
        
        # Chance for big run
        if random.random() < 0.05:
            yards = random.randint(15, 45)
        
        self.rush_yards += max(yards, -10)  # Cap negative yards
        return True, yards, "rush"
    
    def attempt_field_goal(self, distance: int) -> Tuple[bool, str]:
        """
        Attempt a field goal.
        Returns: (made, result_type)
        """
        # Adjust FG % based on distance
        base_pct = self.field_goal_pct
        
        if distance <= 30:
            adjusted_pct = base_pct + 0.15
        elif distance <= 40:
            adjusted_pct = base_pct + 0.05
        elif distance <= 50:
            adjusted_pct = base_pct - 0.10
        else:
            adjusted_pct = base_pct - 0.25
        
        # Home field helps kickers
        if self.home_field:
            adjusted_pct += 0.05
        
        adjusted_pct = max(0.20, min(0.95, adjusted_pct))
        
        if random.random() < adjusted_pct:
            self.field_goals += 1
            self.score += 3
            return True, "field_goal_good"
        else:
            return False, "field_goal_missed"
    
    def score_touchdown(self, extra_point: bool = True) -> int:
        """Score a touchdown and attempt extra point/2pt conversion."""
        self.touchdowns += 1
        self.score += 6
        
        if extra_point:
            # 94% PAT success rate
            if random.random() < 0.94:
                self.score += 1
                return 7
            return 6
        else:
            # 2-point conversion (48% success)
            if random.random() < 0.48:
                self.score += 2
                return 8
            return 6
    
    def punt(self) -> int:
        """Execute a punt. Returns net punt yards."""
        self.punts += 1
        base_punt = self.punt_avg + (self.game_variance * 5)
        punt_distance = int(random.gauss(base_punt, 6))
        punt_distance = max(25, min(65, punt_distance))
        self.punt_yards += punt_distance
        
        # Return yards
        if random.random() < 0.15:  # Fair catch
            return punt_distance
        else:
            return_yards = random.randint(5, 15)
            return punt_distance - return_yards
    
    def get_stats(self) -> Dict:
        """Return comprehensive game statistics."""
        pass_pct = (self.pass_completions / self.pass_attempts * 100) if self.pass_attempts > 0 else 0
        yards_per_rush = (self.rush_yards / self.rush_attempts) if self.rush_attempts > 0 else 0
        third_down_pct = (self.third_down_conversions / self.third_down_attempts * 100) if self.third_down_attempts > 0 else 0
        
        return {
            'name': self.name,
            'score': self.score,
            'touchdowns': self.touchdowns,
            'field_goals': self.field_goals,
            'passing': f"{self.pass_completions}/{self.pass_attempts} ({pass_pct:.1f}%)",
            'pass_yards': self.pass_yards,
            'rushing': f"{self.rush_attempts} carries",
            'rush_yards': self.rush_yards,
            'yards_per_rush': f"{yards_per_rush:.1f}",
            'total_yards': self.pass_yards + self.rush_yards,
            'turnovers': self.turnovers,
            'sacks_allowed': self.sacks_allowed,
            'first_downs': self.first_downs,
            'third_down': f"{self.third_down_conversions}/{self.third_down_attempts} ({third_down_pct:.1f}%)",
            'time_of_possession': f"{self.time_of_possession // 60}:{self.time_of_possession % 60:02d}"
        }


class FootballSimulator:
    """Simulates a college football game with enhanced realism."""
    
    def __init__(self, team1: FootballTeam, team2: FootballTeam, verbose: bool = True):
        self.team1 = team1
        self.team2 = team2
        self.verbose = verbose
        self.game_clock = 0  # Seconds into game
        self.quarter = 1
        self.play_count = 0
        
        # Initialize game-day variance for each team
        self.team1.initialize_game_variance()
        self.team2.initialize_game_variance()
        
        # Calculate effective pace
        self.game_pace = (self.team1.pace_factor + self.team2.pace_factor) / 2
    
    def log(self, message: str):
        """Log a game event."""
        if self.verbose:
            print(message)
    
    def simulate_drive(self, offense: FootballTeam, defense: FootballTeam, starting_position: int) -> Tuple[str, int]:
        """
        Simulate a single offensive drive.
        Returns: (result, ending_position)
        Result can be: "touchdown", "field_goal", "punt", "turnover", "downs", "end_half"
        """
        field_position = starting_position  # Yards from own goal line
        down = 1
        yards_to_go = 10
        drive_plays = 0
        drive_yards = 0
        
        while True:
            drive_plays += 1
            self.play_count += 1
            
            # Check for end of half/game (simplified time management)
            if drive_plays > 15:  # Prevent infinite drives
                offense.time_of_possession += 40 * drive_plays
                if field_position >= 65:
                    return "field_goal_attempt", field_position
                return "punt", field_position
            
            # Choose play type
            is_pass = random.random() < offense.pass_play_rate
            
            # Adjust play calling based on field position
            if field_position >= 80:  # Red zone
                is_pass = random.random() < 0.60  # More passes in red zone
            
            # Execute play
            if is_pass:
                success, yards, result = offense.attempt_pass(defense.sack_rate)
                
                if result == "interception":
                    offense.update_momentum(False)
                    defense.update_momentum(True)
                    self.log(f"  INTERCEPTION by {defense.name}!")
                    offense.time_of_possession += 30 * drive_plays
                    return "turnover", 100 - field_position
                elif result == "sack":
                    field_position = max(1, field_position + yards)  # yards is negative
                    yards_to_go -= yards  # Adds to yards to go
                else:
                    if success:
                        field_position = min(100, field_position + yards)
                        yards_to_go -= yards
                        drive_yards += yards
                        
                        if yards >= 15:
                            offense.update_momentum(True, big_play=True)
                            self.log(f"  Big play! {yards} yard completion for {offense.name}!")
            else:
                success, yards, result = offense.attempt_rush()
                
                if result == "fumble_lost":
                    offense.update_momentum(False)
                    defense.update_momentum(True)
                    self.log(f"  FUMBLE! {defense.name} recovers!")
                    offense.time_of_possession += 30 * drive_plays
                    return "turnover", 100 - field_position
                
                field_position = max(1, min(100, field_position + yards))
                yards_to_go -= yards
                drive_yards += yards
                
                if yards >= 15:
                    offense.update_momentum(True, big_play=True)
                    self.log(f"  Big run! {yards} yards for {offense.name}!")
            
            # Check for touchdown
            if field_position >= 100:
                points = offense.score_touchdown()
                offense.update_momentum(True)
                defense.update_momentum(False)
                offense.first_downs += 1
                self.log(f"  TOUCHDOWN {offense.name}! ({points} points)")
                offense.time_of_possession += 30 * drive_plays
                return "touchdown", 100
            
            # Check for first down
            if yards_to_go <= 0:
                offense.first_downs += 1
                down = 1
                yards_to_go = 10
                self.log(f"  First down {offense.name} at the {100 - field_position} yard line")
                continue
            
            # Advance down
            down += 1
            
            # Third down tracking
            if down == 3:
                offense.third_down_attempts += 1
            elif down == 4:
                # Check if converted on 3rd down
                if yards_to_go <= 0:
                    offense.third_down_conversions += 1
            
            # Fourth down decision
            if down > 4:
                offense.time_of_possession += 30 * drive_plays
                
                # Field goal range check (roughly inside 40 yard line = 60+ field position)
                if field_position >= 60:
                    # Attempt field goal
                    fg_distance = 100 - field_position + 17  # Add 17 for end zone + hold
                    made, result = offense.attempt_field_goal(fg_distance)
                    if made:
                        offense.update_momentum(True)
                        self.log(f"  FIELD GOAL GOOD! {offense.name} from {fg_distance} yards")
                        return "field_goal", field_position
                    else:
                        self.log(f"  Field goal MISSED from {fg_distance} yards")
                        return "missed_fg", field_position
                
                # Go for it on 4th down in certain situations
                if field_position >= 55 and yards_to_go <= 3:
                    # Go for it!
                    self.log(f"  {offense.name} going for it on 4th and {yards_to_go}")
                    if random.random() < offense.pass_play_rate:
                        success, yards, result = offense.attempt_pass(defense.sack_rate)
                    else:
                        success, yards, result = offense.attempt_rush()
                    
                    if success and yards >= yards_to_go:
                        offense.first_downs += 1
                        field_position += yards
                        down = 1
                        yards_to_go = 10
                        self.log(f"  CONVERTED! First down {offense.name}")
                        continue
                    else:
                        self.log(f"  Stopped! Turnover on downs")
                        return "downs", 100 - field_position
                
                # Punt
                punt_yards = offense.punt()
                self.log(f"  {offense.name} punts {punt_yards} yards")
                return "punt", 100 - field_position - punt_yards
        
        return "end_drive", field_position
    
    def simulate_quarter(self, quarter_num: int) -> None:
        """Simulate one quarter of football."""
        self.log(f"\n{'='*60}")
        self.log(f"{'QUARTER ' + str(quarter_num):^60}")
        self.log(f"{'='*60}\n")
        
        self.quarter = quarter_num
        
        # Determine number of possessions per quarter (varies by pace)
        # College football typically has about 11-13 possessions per team per game
        # So about 3 possessions per team per quarter on average
        base_possessions = 3
        possessions_per_team = int(base_possessions * self.game_pace)
        possessions_per_team = max(2, min(4, possessions_per_team + random.randint(-1, 1)))
        
        # Alternate possessions
        for i in range(possessions_per_team * 2):
            if i % 2 == 0:
                offense = self.team1
                defense = self.team2
            else:
                offense = self.team2
                defense = self.team1
            
            # Starting field position (after kickoff or after score)
            starting_pos = random.randint(20, 35)
            
            self.log(f"\n{offense.name} ball at their own {starting_pos} yard line")
            
            result, ending_pos = self.simulate_drive(offense, defense, starting_pos)
            
            self.log(f"  Drive result: {result}")
            self.log(f"  Score: {self.team1.name} {self.team1.score} - {self.team2.name} {self.team2.score}")
        
        self.log(f"\n{'='*60}")
        self.log(f"End of Quarter {quarter_num}")
        self.log(f"{self.team1.name}: {self.team1.score}")
        self.log(f"{self.team2.name}: {self.team2.score}")
        self.log(f"{'='*60}\n")
    
    def simulate_game(self) -> Tuple[FootballTeam, Dict]:
        """
        Simulate a complete football game.
        Returns: (winning_team, game_summary)
        """
        self.log("\n" + "="*60)
        self.log(f"{'COLLEGE FOOTBALL SIMULATION':^60}")
        self.log(f"{self.team1.name:^30} vs {self.team2.name:^30}")
        self.log("="*60)
        
        # Simulate all four quarters
        for quarter in range(1, 5):
            self.simulate_quarter(quarter)
        
        # Check for overtime
        overtime_count = 0
        while self.team1.score == self.team2.score:
            overtime_count += 1
            self.log(f"\n{'='*60}")
            self.log(f"{'OVERTIME ' + str(overtime_count):^60}")
            self.log(f"{'='*60}\n")
            
            # College OT rules: Each team gets possession from 25 yard line
            for offense in [self.team1, self.team2]:
                defense = self.team2 if offense == self.team1 else self.team1
                self.log(f"\n{offense.name} ball at the 25 yard line")
                result, _ = self.simulate_drive(offense, defense, 75)  # 75 = opponent's 25
                
                if self.team1.score != self.team2.score and offense == self.team2:
                    break  # Game over if team2 wins/loses in OT
        
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
            'total_plays': self.play_count,
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
            self.log(f"  Score: {stats['score']}")
            self.log(f"  Touchdowns: {stats['touchdowns']}")
            self.log(f"  Field Goals: {stats['field_goals']}")
            self.log(f"  Passing: {stats['passing']} for {stats['pass_yards']} yards")
            self.log(f"  Rushing: {stats['rushing']} for {stats['rush_yards']} yards ({stats['yards_per_rush']} avg)")
            self.log(f"  Total Yards: {stats['total_yards']}")
            self.log(f"  First Downs: {stats['first_downs']}")
            self.log(f"  Third Down: {stats['third_down']}")
            self.log(f"  Turnovers: {stats['turnovers']}")
            self.log(f"  Sacks Allowed: {stats['sacks_allowed']}")
            self.log(f"  Time of Possession: {stats['time_of_possession']}")
        
        self.log("="*60)


def main():
    """Main function to run the simulator."""
    print("\n" + "="*60)
    print("COLLEGE FOOTBALL SCORE SIMULATOR")
    print("="*60)
    
    # Example: Create two teams with different strengths
    # Team 1: Strong passing team
    team1 = FootballTeam(
        name="Tigers",
        pass_completion_pct=0.65,
        yards_per_completion=13.0,
        rush_yards_per_carry=4.0,
        turnover_rate=0.02,
        red_zone_td_pct=0.65,
        field_goal_pct=0.80,
        home_field=True
    )
    
    # Team 2: Balanced team
    team2 = FootballTeam(
        name="Bulldogs",
        pass_completion_pct=0.58,
        yards_per_completion=11.5,
        rush_yards_per_carry=5.0,
        turnover_rate=0.03,
        red_zone_td_pct=0.58,
        field_goal_pct=0.72
    )
    
    # Create simulator and run game
    simulator = FootballSimulator(team1, team2, verbose=True)
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
