#!/usr/bin/env python3
"""
College Basketball Score Predictor
Uses point spreads and totals to predict game outcomes
Based on statistical models similar to KenPom methodology
"""

import numpy as np
from dataclasses import dataclass
import json


@dataclass
class TeamStats:
    """Represents team statistics for prediction"""
    name: str
    offensive_efficiency: float  # Points per 100 possessions
    defensive_efficiency: float  # Points allowed per 100 possessions
    tempo: float  # Possessions per game
    recent_games_weight: float = 0.0  # Weight for recent form (0-1, 0=no weighting)
    recent_offensive_efficiency: float = None  # Last 5-10 games offensive efficiency
    recent_defensive_efficiency: float = None  # Last 5-10 games defensive efficiency
    
    def __post_init__(self):
        """Validate team statistics"""
        if self.offensive_efficiency <= 0:
            raise ValueError("Offensive efficiency must be positive")
        if self.defensive_efficiency <= 0:
            raise ValueError("Defensive efficiency must be positive")
        if self.tempo <= 0:
            raise ValueError("Tempo must be positive")
        if self.recent_games_weight < 0 or self.recent_games_weight > 1:
            raise ValueError("Recent games weight must be between 0 and 1")
        
        # Set recent efficiency to season average if not provided
        if self.recent_offensive_efficiency is None:
            self.recent_offensive_efficiency = self.offensive_efficiency
        if self.recent_defensive_efficiency is None:
            self.recent_defensive_efficiency = self.defensive_efficiency
    
    def get_weighted_offensive_efficiency(self) -> float:
        """Get offensive efficiency with recent form weighting"""
        if self.recent_games_weight == 0:
            return self.offensive_efficiency
        return (self.offensive_efficiency * (1 - self.recent_games_weight) + 
                self.recent_offensive_efficiency * self.recent_games_weight)
    
    def get_weighted_defensive_efficiency(self) -> float:
        """Get defensive efficiency with recent form weighting"""
        if self.recent_games_weight == 0:
            return self.defensive_efficiency
        return (self.defensive_efficiency * (1 - self.recent_games_weight) + 
                self.recent_defensive_efficiency * self.recent_games_weight)


@dataclass
class GamePrediction:
    """Represents a predicted game outcome"""
    home_team: str
    away_team: str
    predicted_home_score: float
    predicted_away_score: float
    point_spread: float  # Positive means home team favored
    total_points: float
    home_win_probability: float
    
    def __str__(self):
        """Format prediction for display"""
        favorite = self.home_team if self.point_spread > 0 else self.away_team
        spread_value = abs(self.point_spread)
        
        return f"""
Game Prediction:
{self.away_team} @ {self.home_team}
Predicted Score: {self.away_team} {self.predicted_away_score:.1f} - {self.home_team} {self.predicted_home_score:.1f}
Point Spread: {favorite} -{spread_value:.1f}
Total: {self.total_points:.1f}
Home Win Probability: {self.home_win_probability:.1%}
"""


class BasketballPredictor:
    """Predicts college basketball game scores using statistical models"""
    
    def __init__(self, home_court_advantage: float = 3.5, score_std_dev: float = 10.5):
        """
        Initialize predictor with configurable parameters
        
        Args:
            home_court_advantage: Points advantage for home team (typically 3-4 points)
            score_std_dev: Standard deviation for score variance in simulations (typically 10-12 points)
        """
        self.home_court_advantage = home_court_advantage
        self.national_avg_efficiency = 100.0  # NCAA D1 average
        self.score_std_dev = score_std_dev  # Calibratable variance parameter
        self.blowout_threshold = 15.0  # Efficiency gap indicating potential blowout
        self.blowout_variance_multiplier = 1.5  # Increase variance for potential blowouts
        
    def predict_game(
        self, 
        home_team: TeamStats, 
        away_team: TeamStats,
        neutral_site: bool = False
    ) -> GamePrediction:
        """
        Predict the outcome of a basketball game
        
        Args:
            home_team: Statistics for the home team
            away_team: Statistics for the away team
            neutral_site: Whether the game is at a neutral site
            
        Returns:
            GamePrediction with predicted scores and spread
        """
        # Calculate expected tempo (geometric mean of team tempos)
        expected_tempo = np.sqrt(home_team.tempo * away_team.tempo)
        
        # Calculate expected possessions (slightly fewer than tempo due to game dynamics)
        expected_possessions = expected_tempo * 0.98
        
        # Use weighted efficiencies (incorporates recent form if available)
        home_off_eff = home_team.get_weighted_offensive_efficiency()
        home_def_eff = home_team.get_weighted_defensive_efficiency()
        away_off_eff = away_team.get_weighted_offensive_efficiency()
        away_def_eff = away_team.get_weighted_defensive_efficiency()
        
        # Predict scores using efficiency ratings
        # Home team offense vs away team defense
        home_offensive_rating = (home_off_eff * 
                                self.national_avg_efficiency / 
                                away_def_eff)
        
        # Away team offense vs home team defense  
        away_offensive_rating = (away_off_eff * 
                                self.national_avg_efficiency / 
                                home_def_eff)
        
        # Convert to expected points
        predicted_home_score = (home_offensive_rating * expected_possessions / 100.0)
        predicted_away_score = (away_offensive_rating * expected_possessions / 100.0)
        
        # Add home court advantage if not neutral site
        if not neutral_site:
            predicted_home_score += self.home_court_advantage
        
        # Calculate spread and total
        point_spread = predicted_home_score - predicted_away_score
        total_points = predicted_home_score + predicted_away_score
        
        # Calculate win probability using logistic function
        # Rough approximation: 1 point spread ≈ 2.8% win probability change
        win_prob = 1 / (1 + np.exp(-point_spread / 3.5))
        
        return GamePrediction(
            home_team=home_team.name,
            away_team=away_team.name,
            predicted_home_score=predicted_home_score,
            predicted_away_score=predicted_away_score,
            point_spread=point_spread,
            total_points=total_points,
            home_win_probability=win_prob
        )
    
    def predict_from_spread_and_total(
        self,
        home_team_name: str,
        away_team_name: str,
        point_spread: float,
        total_points: float
    ) -> GamePrediction:
        """
        Predict game outcome using point spread and total
        
        Args:
            home_team_name: Name of home team
            away_team_name: Name of away team
            point_spread: Point spread (positive = home favored)
            total_points: Expected total points
            
        Returns:
            GamePrediction with calculated scores
        """
        # Calculate individual scores from spread and total
        # home_score + away_score = total
        # home_score - away_score = spread
        # Solving: home_score = (total + spread) / 2
        #         away_score = (total - spread) / 2
        
        predicted_home_score = (total_points + point_spread) / 2
        predicted_away_score = (total_points - point_spread) / 2
        
        # Calculate win probability
        win_prob = 1 / (1 + np.exp(-point_spread / 3.5))
        
        return GamePrediction(
            home_team=home_team_name,
            away_team=away_team_name,
            predicted_home_score=predicted_home_score,
            predicted_away_score=predicted_away_score,
            point_spread=point_spread,
            total_points=total_points,
            home_win_probability=win_prob
        )
    
    def simulate_game(
        self,
        prediction: GamePrediction,
        num_simulations: int = 1000,
        home_team_stats: TeamStats = None,
        away_team_stats: TeamStats = None
    ) -> dict:
        """
        Run Monte Carlo simulation of game outcome with blowout detection
        
        Args:
            prediction: Game prediction to simulate
            num_simulations: Number of simulations to run
            home_team_stats: Optional home team stats for blowout detection
            away_team_stats: Optional away team stats for blowout detection
            
        Returns:
            Dictionary with simulation statistics
        """
        # Use calibrated standard deviation
        score_std = self.score_std_dev
        
        # Blowout detection: increase variance if large efficiency gap exists
        if home_team_stats and away_team_stats:
            home_eff_net = (home_team_stats.get_weighted_offensive_efficiency() - 
                           home_team_stats.get_weighted_defensive_efficiency())
            away_eff_net = (away_team_stats.get_weighted_offensive_efficiency() - 
                           away_team_stats.get_weighted_defensive_efficiency())
            efficiency_gap = abs(home_eff_net - away_eff_net)
            
            # If efficiency gap exceeds threshold, increase variance
            if efficiency_gap > self.blowout_threshold:
                score_std *= self.blowout_variance_multiplier
        
        home_scores = np.random.normal(
            prediction.predicted_home_score, 
            score_std, 
            num_simulations
        )
        away_scores = np.random.normal(
            prediction.predicted_away_score, 
            score_std, 
            num_simulations
        )
        
        home_wins = np.sum(home_scores > away_scores)
        away_wins = num_simulations - home_wins
        
        return {
            'home_win_pct': home_wins / num_simulations,
            'away_win_pct': away_wins / num_simulations,
            'avg_home_score': np.mean(home_scores),
            'avg_away_score': np.mean(away_scores),
            'home_score_range': (np.percentile(home_scores, 5), 
                                np.percentile(home_scores, 95)),
            'away_score_range': (np.percentile(away_scores, 5), 
                                np.percentile(away_scores, 95)),
            'score_std_used': score_std  # Report variance used
        }


def load_team_data(filename: str) -> dict:
    """Load team statistics from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    teams = {}
    for team_name, stats in data.items():
        # Support optional recent form fields
        recent_weight = stats.get('recent_games_weight', 0.0)
        recent_off = stats.get('recent_offensive_efficiency', stats['offensive_efficiency'])
        recent_def = stats.get('recent_defensive_efficiency', stats['defensive_efficiency'])
        
        teams[team_name] = TeamStats(
            name=team_name,
            offensive_efficiency=stats['offensive_efficiency'],
            defensive_efficiency=stats['defensive_efficiency'],
            tempo=stats['tempo'],
            recent_games_weight=recent_weight,
            recent_offensive_efficiency=recent_off,
            recent_defensive_efficiency=recent_def
        )
    return teams


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Predict college basketball game scores'
    )
    parser.add_argument(
        '--mode',
        choices=['team_stats', 'spread_total'],
        required=True,
        help='Prediction mode: use team stats or spread/total'
    )
    parser.add_argument('--home', required=True, help='Home team name')
    parser.add_argument('--away', required=True, help='Away team name')
    parser.add_argument(
        '--team-data',
        help='JSON file with team statistics (required for team_stats mode)'
    )
    parser.add_argument(
        '--spread',
        type=float,
        help='Point spread, positive = home favored (required for spread_total mode)'
    )
    parser.add_argument(
        '--total',
        type=float,
        help='Expected total points (required for spread_total mode)'
    )
    parser.add_argument(
        '--neutral',
        action='store_true',
        help='Game at neutral site'
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run Monte Carlo simulation'
    )
    parser.add_argument(
        '--num-simulations',
        type=int,
        default=1000,
        help='Number of Monte Carlo simulations to run (default: 1000)'
    )
    
    args = parser.parse_args()
    
    predictor = BasketballPredictor()
    
    home_team_stats = None
    away_team_stats = None
    
    if args.mode == 'team_stats':
        if not args.team_data:
            parser.error('--team-data required for team_stats mode')
        
        teams = load_team_data(args.team_data)
        
        if args.home not in teams:
            print(f"Error: {args.home} not found in team data")
            return
        if args.away not in teams:
            print(f"Error: {args.away} not found in team data")
            return
        
        home_team_stats = teams[args.home]
        away_team_stats = teams[args.away]
        
        prediction = predictor.predict_game(
            home_team_stats,
            away_team_stats,
            neutral_site=args.neutral
        )
    else:  # spread_total mode
        if args.spread is None or args.total is None:
            parser.error('--spread and --total required for spread_total mode')
        
        prediction = predictor.predict_from_spread_and_total(
            args.home,
            args.away,
            args.spread,
            args.total
        )
    
    print(prediction)
    
    if args.simulate:
        print(f"\nRunning Monte Carlo Simulation ({args.num_simulations} games)...")
        sim_results = predictor.simulate_game(
            prediction, 
            num_simulations=args.num_simulations,
            home_team_stats=home_team_stats,
            away_team_stats=away_team_stats
        )
        print(f"Simulated Home Win %: {sim_results['home_win_pct']:.1%}")
        print(f"Simulated Away Win %: {sim_results['away_win_pct']:.1%}")
        print(f"Average Simulated Score: {args.away} {sim_results['avg_away_score']:.1f} - "
              f"{args.home} {sim_results['avg_home_score']:.1f}")
        print(f"Home Score 90% Range: {sim_results['home_score_range'][0]:.1f} - "
              f"{sim_results['home_score_range'][1]:.1f}")
        print(f"Away Score 90% Range: {sim_results['away_score_range'][0]:.1f} - "
              f"{sim_results['away_score_range'][1]:.1f}")
        if 'score_std_used' in sim_results:
            print(f"Score Variance Used: {sim_results['score_std_used']:.1f}")



if __name__ == '__main__':
    main()
