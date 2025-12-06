"""
College Basketball Game Simulator - Haralabos Voulgaris Style

This simulator uses advanced analytics similar to Haralabos Voulgaris's approach:
- Offensive and Defensive Efficiency ratings (points per 100 possessions)
- Pace factor (possessions per 40 minutes)
- Shot distribution and efficiency by type
- Variance and randomness in performance
- Monte Carlo simulation with 10,000 iterations

The simulator models basketball at the possession level, using:
1. Team efficiency metrics to determine scoring probability
2. Shot type distribution (2PT, 3PT, FT)
3. Turnover rates
4. Offensive rebounding rates
5. Game-to-game variance in shooting
"""

import random
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import statistics


@dataclass
class TeamStats:
    """
    Team statistics following advanced analytics principles
    All efficiency metrics are per 100 possessions (Voulgaris style)
    """
    name: str
    # Efficiency metrics (points per 100 possessions)
    offensive_efficiency: float  # Offensive rating (points scored per 100 possessions)
    defensive_efficiency: float  # Defensive rating (points allowed per 100 possessions)
    
    # Pace and tempo
    pace: float  # Possessions per 40 minutes
    
    # Shot distribution and efficiency
    three_point_rate: float  # Percentage of FGA that are 3-pointers (0.0 - 1.0)
    three_point_percentage: float  # 3PT shooting percentage (0.0 - 1.0)
    two_point_percentage: float  # 2PT shooting percentage (0.0 - 1.0)
    free_throw_rate: float  # Free throw attempts per FGA
    free_throw_percentage: float  # FT shooting percentage (0.0 - 1.0)
    
    # Possession factors
    turnover_rate: float  # Turnovers per 100 possessions (0.0 - 1.0)
    offensive_rebound_rate: float  # Percentage of missed shots rebounded (0.0 - 1.0)
    
    # Variance factor (standard deviation for game-to-game performance)
    performance_variance: float = 0.05  # Default 5% variance


class PossessionSimulator:
    """
    Simulates individual possessions using probabilistic models
    """
    
    def __init__(self, offensive_team: TeamStats, defensive_team: TeamStats):
        self.offense = offensive_team
        self.defense = defensive_team
        # Calculate expected points per possession based on efficiency
        league_avg_efficiency = 105.0
        # Adjust offensive efficiency based on defensive strength
        off_adj = self.offense.offensive_efficiency / league_avg_efficiency
        def_adj = self.defense.defensive_efficiency / league_avg_efficiency
        # Expected points = offensive efficiency adjusted by opponent defense
        self.expected_ppp = (self.offense.offensive_efficiency / 100.0) * (2.0 - def_adj) * 0.75
    
    def simulate_possession(self, game_variance: float = 0.0) -> int:
        """
        Simulate a single possession and return points scored
        Incorporates variance factor for realistic game-to-game fluctuations
        """
        # Apply variance to shooting percentages (hot/cold shooting nights)
        variance_multiplier = 1.0 + np.random.normal(0, abs(game_variance))
        
        # Check for turnover first (dead possession)
        if random.random() < self.offense.turnover_rate * 0.75:
            return 0  # Turnover - no points
        
        # Apply defensive adjustment to shooting
        league_avg_def = 105.0
        def_factor = 1.0 - ((self.defense.defensive_efficiency - league_avg_def) / league_avg_def) * 0.12
        
        # Track if we get an offensive rebound for second chance
        second_chance = False
        
        # Determine shot type
        if random.random() < self.offense.three_point_rate:
            # Three-point attempt
            three_pt_pct = self.offense.three_point_percentage * variance_multiplier * def_factor
            three_pt_pct = max(0.28, min(0.48, three_pt_pct))
            
            if random.random() < three_pt_pct:
                # Made 3-pointer
                return 3
            else:
                # Missed 3-pointer, check for offensive rebound (lower rate on 3s)
                if random.random() < self.offense.offensive_rebound_rate * 0.38:
                    second_chance = True
        else:
            # Two-point attempt
            two_pt_pct = self.offense.two_point_percentage * variance_multiplier * def_factor
            two_pt_pct = max(0.45, min(0.65, two_pt_pct))
            
            if random.random() < two_pt_pct:
                # Made 2-pointer, check for and-one
                if random.random() < 0.075:
                    return 2 + (1 if random.random() < self.offense.free_throw_percentage else 0)
                return 2
            else:
                # Missed 2-pointer, check for foul or offensive rebound
                if random.random() < self.offense.free_throw_rate * 0.22:
                    # Shooting foul - 2 free throws
                    ft_made = sum(1 for _ in range(2) if random.random() < self.offense.free_throw_percentage)
                    return ft_made
                elif random.random() < self.offense.offensive_rebound_rate * 0.45:
                    second_chance = True
        
        # Second chance points from offensive rebounds
        if second_chance:
            # Putback attempt - usually close to the basket
            if random.random() < 0.62:  # Good chance to score on putback
                return 2
            # Could also draw a foul
            elif random.random() < 0.18:
                ft_made = sum(1 for _ in range(2) if random.random() < self.offense.free_throw_percentage)
                return ft_made
        
        return 0


class GameSimulator:
    """
    Simulates complete games using possession-by-possession model
    """
    
    def __init__(self, team1: TeamStats, team2: TeamStats):
        self.team1 = team1
        self.team2 = team2
        
    def calculate_game_pace(self) -> float:
        """
        Calculate expected pace based on both teams' tempo preferences
        Faster team has slightly more influence (Voulgaris insight)
        """
        return (self.team1.pace + self.team2.pace) / 2.0 + np.random.normal(0, 3.0)
    
    def simulate_single_game(self) -> Tuple[int, int]:
        """
        Simulate one game and return final scores (team1_score, team2_score)
        """
        # Calculate number of possessions for the game
        # Pace is possessions per 40 minutes PER TEAM
        # So if average pace is 70, each team gets ~70 possessions
        pace = self.calculate_game_pace()
        # Add some variance but keep within reasonable bounds
        possessions_per_team = int(pace + np.random.normal(0, 3.0))
        possessions_per_team = max(60, min(80, possessions_per_team))
        
        # Each team gets roughly the same number (teams alternate possessions)
        team1_possessions = possessions_per_team + random.randint(-1, 1)
        team2_possessions = possessions_per_team + random.randint(-1, 1)
        
        # Apply game-specific variance (hot/cold shooting)
        team1_variance = np.random.normal(0, self.team1.performance_variance)
        team2_variance = np.random.normal(0, self.team2.performance_variance)
        
        # Simulate all possessions
        sim1 = PossessionSimulator(self.team1, self.team2)
        sim2 = PossessionSimulator(self.team2, self.team1)
        
        team1_score = sum(sim1.simulate_possession(team1_variance) for _ in range(team1_possessions))
        team2_score = sum(sim2.simulate_possession(team2_variance) for _ in range(team2_possessions))
        
        return team1_score, team2_score
    
    def run_simulation(self, num_simulations: int = 10000) -> Dict:
        """
        Run Monte Carlo simulation with specified number of iterations
        Returns comprehensive statistics about the matchup
        """
        print(f"\n{'='*70}")
        print(f"COLLEGE BASKETBALL GAME SIMULATOR - HARALABOS VOULGARIS STYLE")
        print(f"{'='*70}")
        print(f"\nMatchup: {self.team1.name} vs {self.team2.name}")
        print(f"Simulations: {num_simulations:,}")
        print(f"\nTeam Statistics:")
        print(f"\n{self.team1.name}:")
        print(f"  Offensive Efficiency: {self.team1.offensive_efficiency:.1f} pts/100 poss")
        print(f"  Defensive Efficiency: {self.team1.defensive_efficiency:.1f} pts/100 poss")
        print(f"  Pace: {self.team1.pace:.1f} poss/40 min")
        print(f"\n{self.team2.name}:")
        print(f"  Offensive Efficiency: {self.team2.offensive_efficiency:.1f} pts/100 poss")
        print(f"  Defensive Efficiency: {self.team2.defensive_efficiency:.1f} pts/100 poss")
        print(f"  Pace: {self.team2.pace:.1f} poss/40 min")
        
        print(f"\n{'='*70}")
        print("RUNNING SIMULATIONS...")
        print(f"{'='*70}\n")
        
        team1_scores = []
        team2_scores = []
        team1_wins = 0
        team2_wins = 0
        
        # Run simulations
        for i in range(num_simulations):
            if (i + 1) % 2000 == 0:
                print(f"Completed {i + 1:,} / {num_simulations:,} simulations...")
            
            score1, score2 = self.simulate_single_game()
            team1_scores.append(score1)
            team2_scores.append(score2)
            
            if score1 > score2:
                team1_wins += 1
            else:
                team2_wins += 1
        
        # Calculate statistics
        team1_win_pct = (team1_wins / num_simulations) * 100
        team2_win_pct = (team2_wins / num_simulations) * 100
        
        avg_score1 = statistics.mean(team1_scores)
        avg_score2 = statistics.mean(team2_scores)
        median_score1 = statistics.median(team1_scores)
        median_score2 = statistics.median(team2_scores)
        stdev_score1 = statistics.stdev(team1_scores)
        stdev_score2 = statistics.stdev(team2_scores)
        
        # Calculate score distribution
        margin_of_victory = [s1 - s2 for s1, s2 in zip(team1_scores, team2_scores)]
        avg_mov = statistics.mean(margin_of_victory)
        
        # Percentile outcomes
        team1_scores_sorted = sorted(team1_scores)
        team2_scores_sorted = sorted(team2_scores)
        
        results = {
            'team1_name': self.team1.name,
            'team2_name': self.team2.name,
            'num_simulations': num_simulations,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'team1_win_pct': team1_win_pct,
            'team2_win_pct': team2_win_pct,
            'team1_avg_score': avg_score1,
            'team2_avg_score': avg_score2,
            'team1_median_score': median_score1,
            'team2_median_score': median_score2,
            'team1_stdev': stdev_score1,
            'team2_stdev': stdev_score2,
            'avg_margin': avg_mov,
            'team1_10th_percentile': team1_scores_sorted[int(num_simulations * 0.10)],
            'team1_90th_percentile': team1_scores_sorted[int(num_simulations * 0.90)],
            'team2_10th_percentile': team2_scores_sorted[int(num_simulations * 0.10)],
            'team2_90th_percentile': team2_scores_sorted[int(num_simulations * 0.90)],
            'all_team1_scores': team1_scores,
            'all_team2_scores': team2_scores,
        }
        
        # Print results
        print(f"\n{'='*70}")
        print("SIMULATION RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Win Probability:")
        print(f"  {self.team1.name}: {team1_win_pct:.1f}%  ({team1_wins:,} wins)")
        print(f"  {self.team2.name}: {team2_win_pct:.1f}%  ({team2_wins:,} wins)")
        
        print(f"\nProjected Scores:")
        print(f"  {self.team1.name}: {avg_score1:.1f} ± {stdev_score1:.1f} (median: {median_score1:.0f})")
        print(f"  {self.team2.name}: {avg_score2:.1f} ± {stdev_score2:.1f} (median: {median_score2:.0f})")
        
        print(f"\nExpected Margin of Victory: {abs(avg_mov):.1f} points ({self.team1.name if avg_mov > 0 else self.team2.name})")
        
        print(f"\nScore Ranges (10th-90th percentile):")
        print(f"  {self.team1.name}: {results['team1_10th_percentile']:.0f} - {results['team1_90th_percentile']:.0f}")
        print(f"  {self.team2.name}: {results['team2_10th_percentile']:.0f} - {results['team2_90th_percentile']:.0f}")
        
        print(f"\n{'='*70}\n")
        
        return results


def create_example_teams() -> Tuple[TeamStats, TeamStats]:
    """
    Create example teams with realistic college basketball statistics
    Team1: Elite offensive team (Duke-style)
    Team2: Strong defensive team (Virginia-style)
    """
    
    # Elite offensive team - high efficiency, fast pace
    team1 = TeamStats(
        name="Duke Blue Devils",
        offensive_efficiency=118.5,  # Elite offense
        defensive_efficiency=98.2,   # Good defense
        pace=72.5,                    # Above average pace
        three_point_rate=0.42,        # 42% of shots are 3PT
        three_point_percentage=0.38,  # 38% from three
        two_point_percentage=0.56,    # 56% from two
        free_throw_rate=0.38,         # Good at drawing fouls
        free_throw_percentage=0.75,   # 75% FT shooting
        turnover_rate=0.16,           # 16% turnover rate
        offensive_rebound_rate=0.32,  # 32% offensive rebound rate
        performance_variance=0.06     # 6% game-to-game variance
    )
    
    # Strong defensive team - slow pace, efficient
    team2 = TeamStats(
        name="Virginia Cavaliers",
        offensive_efficiency=110.2,   # Good offense
        defensive_efficiency=91.5,    # Elite defense
        pace=63.8,                     # Very slow pace
        three_point_rate=0.35,         # 35% of shots are 3PT
        three_point_percentage=0.36,   # 36% from three
        two_point_percentage=0.52,     # 52% from two
        free_throw_rate=0.30,          # Average free throw rate
        free_throw_percentage=0.72,    # 72% FT shooting
        turnover_rate=0.13,            # 13% turnover rate (low)
        offensive_rebound_rate=0.28,   # 28% offensive rebound rate
        performance_variance=0.04      # 4% variance (more consistent)
    )
    
    return team1, team2


if __name__ == "__main__":
    # Create example teams
    team1, team2 = create_example_teams()
    
    # Create simulator
    simulator = GameSimulator(team1, team2)
    
    # Run 10,000 simulations (Voulgaris style Monte Carlo)
    results = simulator.run_simulation(num_simulations=10000)
    
    print("Simulation complete! Results saved in memory.")
    print("\nVoulgaris-Style Insights:")
    print("- This simulation uses possession-level modeling")
    print("- Efficiency ratings are adjusted for opponent strength")
    print("- Game-to-game variance captures 'hot/cold' shooting nights")
    print("- Pace factor determines total number of possessions")
    print("- All percentages and distributions are probabilistic\n")
