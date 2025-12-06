"""
Soccer 10,000 Game Simulator - Haralabos Voulgaris Style

This simulator uses advanced statistical modeling inspired by Haralabos Voulgaris's
analytical approach to sports betting and predictions. Key features:
- Poisson distribution for goal modeling
- Team strength ratings (offensive & defensive)
- Monte Carlo simulations (10,000+ games)
- Expected goals (xG) calculations
- Match outcome probabilities
"""

import numpy as np
from scipy.stats import poisson
import pandas as pd
from typing import Dict, List, Tuple
import json


class Team:
    """Represents a soccer team with offensive and defensive ratings."""
    
    def __init__(self, name: str, offensive_rating: float, defensive_rating: float):
        """
        Initialize a team with performance ratings.
        
        Args:
            name: Team name
            offensive_rating: Offensive strength (higher = better attack, typical range: 0.8-1.5)
            defensive_rating: Defensive strength (lower = better defense, typical range: 0.8-1.5)
        """
        self.name = name
        self.offensive_rating = offensive_rating
        self.defensive_rating = defensive_rating
    
    def __repr__(self):
        return f"Team({self.name}, OFF: {self.offensive_rating:.2f}, DEF: {self.defensive_rating:.2f})"


class SoccerSimulator:
    """
    Haralabos Voulgaris-style soccer simulator using Poisson distribution.
    
    This simulator models soccer matches using statistical analysis similar to
    methods used by professional sports bettors and analysts.
    """
    
    def __init__(self, league_avg_goals: float = 2.7, home_advantage: float = 0.3):
        """
        Initialize the simulator.
        
        Args:
            league_avg_goals: Average goals per game in the league (typical: 2.5-2.9)
            home_advantage: Home field advantage factor (typical: 0.2-0.4)
        """
        self.league_avg_goals = league_avg_goals
        self.home_advantage = home_advantage
        
    def calculate_expected_goals(self, attacking_team: Team, defending_team: Team, 
                                 is_home: bool = False) -> float:
        """
        Calculate expected goals (xG) for a team in a match.
        
        Uses the formula: xG = League_Avg * Attack_Strength * Defense_Weakness * Home_Factor
        
        Args:
            attacking_team: The team attacking
            defending_team: The team defending
            is_home: Whether the attacking team is playing at home
            
        Returns:
            Expected goals for the attacking team
        """
        base_xg = (self.league_avg_goals / 2) * attacking_team.offensive_rating * defending_team.defensive_rating
        
        if is_home:
            base_xg *= (1 + self.home_advantage)
            
        return base_xg
    
    def simulate_single_match(self, home_team: Team, away_team: Team) -> Tuple[int, int]:
        """
        Simulate a single match using Poisson distribution.
        
        Args:
            home_team: The home team
            away_team: The away team
            
        Returns:
            Tuple of (home_goals, away_goals)
        """
        home_xg = self.calculate_expected_goals(home_team, away_team, is_home=True)
        away_xg = self.calculate_expected_goals(away_team, home_team, is_home=False)
        
        # Use Poisson distribution to sample actual goals
        home_goals = poisson.rvs(home_xg)
        away_goals = poisson.rvs(away_xg)
        
        return home_goals, away_goals
    
    def simulate_matches(self, home_team: Team, away_team: Team, 
                        num_simulations: int = 10000) -> Dict:
        """
        Run Monte Carlo simulation of multiple matches.
        
        Args:
            home_team: The home team
            away_team: The away team
            num_simulations: Number of simulations to run
            
        Returns:
            Dictionary containing simulation results and statistics
        """
        results = {
            'home_wins': 0,
            'draws': 0,
            'away_wins': 0,
            'home_goals': [],
            'away_goals': [],
            'score_lines': {}
        }
        
        for _ in range(num_simulations):
            home_goals, away_goals = self.simulate_single_match(home_team, away_team)
            
            results['home_goals'].append(home_goals)
            results['away_goals'].append(away_goals)
            
            # Track outcomes
            if home_goals > away_goals:
                results['home_wins'] += 1
            elif home_goals < away_goals:
                results['away_wins'] += 1
            else:
                results['draws'] += 1
            
            # Track score lines
            scoreline = f"{home_goals}-{away_goals}"
            results['score_lines'][scoreline] = results['score_lines'].get(scoreline, 0) + 1
        
        # Calculate probabilities and statistics
        results['home_win_prob'] = results['home_wins'] / num_simulations
        results['draw_prob'] = results['draws'] / num_simulations
        results['away_win_prob'] = results['away_wins'] / num_simulations
        
        results['avg_home_goals'] = np.mean(results['home_goals'])
        results['avg_away_goals'] = np.mean(results['away_goals'])
        results['avg_total_goals'] = results['avg_home_goals'] + results['avg_away_goals']
        
        # Expected goals
        results['home_xg'] = self.calculate_expected_goals(home_team, away_team, is_home=True)
        results['away_xg'] = self.calculate_expected_goals(away_team, home_team, is_home=False)
        
        # Sort score lines by frequency
        results['top_scorelines'] = sorted(
            results['score_lines'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return results
    
    @staticmethod
    def _probability_to_decimal_odds(probability: float) -> float:
        """
        Convert probability to decimal odds.
        
        Args:
            probability: Probability of outcome (0-1)
            
        Returns:
            Decimal odds (1/probability)
        """
        return 1 / probability if probability > 0 else float('inf')
    
    def calculate_match_odds(self, home_team: Team, away_team: Team, 
                            num_simulations: int = 10000) -> Dict:
        """
        Calculate betting odds based on simulation results.
        
        Args:
            home_team: The home team
            away_team: The away team
            num_simulations: Number of simulations to run
            
        Returns:
            Dictionary containing decimal and fractional odds
        """
        results = self.simulate_matches(home_team, away_team, num_simulations)
        
        # Calculate decimal odds (1/probability)
        home_decimal = self._probability_to_decimal_odds(results['home_win_prob'])
        draw_decimal = self._probability_to_decimal_odds(results['draw_prob'])
        away_decimal = self._probability_to_decimal_odds(results['away_win_prob'])
        
        return {
            'home_team': home_team.name,
            'away_team': away_team.name,
            'simulations': num_simulations,
            'probabilities': {
                'home_win': f"{results['home_win_prob']:.1%}",
                'draw': f"{results['draw_prob']:.1%}",
                'away_win': f"{results['away_win_prob']:.1%}"
            },
            'decimal_odds': {
                'home_win': round(home_decimal, 2),
                'draw': round(draw_decimal, 2),
                'away_win': round(away_decimal, 2)
            },
            'expected_goals': {
                'home': round(results['home_xg'], 2),
                'away': round(results['away_xg'], 2)
            },
            'simulated_averages': {
                'home_goals': round(results['avg_home_goals'], 2),
                'away_goals': round(results['avg_away_goals'], 2),
                'total_goals': round(results['avg_total_goals'], 2)
            },
            'most_likely_scores': [
                (score, f"{(count/num_simulations):.1%}")
                for score, count in results['top_scorelines']
            ]
        }
    
    def print_simulation_report(self, home_team: Team, away_team: Team, 
                               num_simulations: int = 10000):
        """
        Print a comprehensive simulation report.
        
        Args:
            home_team: The home team
            away_team: The away team
            num_simulations: Number of simulations to run
        """
        print("=" * 80)
        print(f"SOCCER MATCH SIMULATOR - Haralabos Voulgaris Style")
        print("=" * 80)
        print(f"\nMatch: {home_team.name} (Home) vs {away_team.name} (Away)")
        print(f"Simulations: {num_simulations:,}")
        print(f"\nTeam Ratings:")
        print(f"  {home_team.name}: Offensive={home_team.offensive_rating:.2f}, Defensive={home_team.defensive_rating:.2f}")
        print(f"  {away_team.name}: Offensive={away_team.offensive_rating:.2f}, Defensive={away_team.defensive_rating:.2f}")
        
        results = self.simulate_matches(home_team, away_team, num_simulations)
        
        print(f"\n" + "-" * 80)
        print("EXPECTED GOALS (xG)")
        print("-" * 80)
        print(f"  {home_team.name}: {results['home_xg']:.2f}")
        print(f"  {away_team.name}: {results['away_xg']:.2f}")
        
        print(f"\n" + "-" * 80)
        print("MATCH OUTCOME PROBABILITIES")
        print("-" * 80)
        print(f"  {home_team.name} Win: {results['home_win_prob']:.1%}")
        print(f"  Draw:           {results['draw_prob']:.1%}")
        print(f"  {away_team.name} Win: {results['away_win_prob']:.1%}")
        
        print(f"\n" + "-" * 80)
        print("DECIMAL ODDS (Fair Odds - No Margin)")
        print("-" * 80)
        home_odds = self._probability_to_decimal_odds(results['home_win_prob'])
        draw_odds = self._probability_to_decimal_odds(results['draw_prob'])
        away_odds = self._probability_to_decimal_odds(results['away_win_prob'])
        print(f"  {home_team.name} Win: {home_odds:.2f}")
        print(f"  Draw:           {draw_odds:.2f}")
        print(f"  {away_team.name} Win: {away_odds:.2f}")
        
        print(f"\n" + "-" * 80)
        print("SIMULATED AVERAGES")
        print("-" * 80)
        print(f"  {home_team.name} Goals: {results['avg_home_goals']:.2f}")
        print(f"  {away_team.name} Goals: {results['avg_away_goals']:.2f}")
        print(f"  Total Goals: {results['avg_total_goals']:.2f}")
        
        print(f"\n" + "-" * 80)
        print("TOP 10 MOST LIKELY SCORELINES")
        print("-" * 80)
        for i, (scoreline, count) in enumerate(results['top_scorelines'], 1):
            prob = count / num_simulations
            print(f"  {i:2d}. {scoreline:5s} - {prob:6.2%} ({count:,} occurrences)")
        
        print("\n" + "=" * 80)


def load_teams_from_file(filename: str) -> List[Team]:
    """
    Load teams from a JSON configuration file.
    
    Args:
        filename: Path to JSON file containing team data
        
    Returns:
        List of Team objects
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return [Team(team['name'], team['offensive_rating'], team['defensive_rating']) 
            for team in data['teams']]


def main():
    """Main function demonstrating the simulator."""
    
    # Example teams with realistic ratings
    # Premier League example: Manchester City vs Liverpool
    man_city = Team("Manchester City", offensive_rating=1.45, defensive_rating=0.75)
    liverpool = Team("Liverpool", offensive_rating=1.40, defensive_rating=0.80)
    
    # Create simulator with Premier League parameters
    simulator = SoccerSimulator(league_avg_goals=2.75, home_advantage=0.3)
    
    # Run simulation
    simulator.print_simulation_report(man_city, liverpool, num_simulations=10000)
    
    print("\n" + "=" * 80)
    print("Additional Examples:")
    print("=" * 80)
    
    # More examples
    barcelona = Team("Barcelona", offensive_rating=1.35, defensive_rating=0.85)
    real_madrid = Team("Real Madrid", offensive_rating=1.38, defensive_rating=0.82)
    
    print("\n")
    simulator.print_simulation_report(barcelona, real_madrid, num_simulations=10000)
    
    # Example with underdog
    print("\n")
    big_team = Team("Top Team", offensive_rating=1.50, defensive_rating=0.70)
    small_team = Team("Underdog Team", offensive_rating=0.85, defensive_rating=1.30)
    
    simulator.print_simulation_report(big_team, small_team, num_simulations=10000)


if __name__ == "__main__":
    main()
