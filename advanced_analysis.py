"""
Advanced Analysis Module for Billy Walters Framework
Includes Monte Carlo simulation and advanced metrics
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class GameSimulationResult:
    """Results from Monte Carlo simulation"""
    home_win_probability: float
    away_win_probability: float
    average_home_score: float
    average_away_score: float
    spread_distribution: List[float]
    total_distribution: List[float]


class MonteCarloSimulator:
    """
    Monte Carlo simulation for game outcomes
    Walters' Computer Group pioneered computer simulations for betting
    """
    
    def __init__(self, n_simulations: int = 10000):
        self.n_simulations = n_simulations
    
    def simulate_game(
        self,
        home_offensive_eff: float,
        home_defensive_eff: float,
        away_offensive_eff: float,
        away_defensive_eff: float,
        avg_tempo: float,
        home_court_advantage: float = 3.5
    ) -> GameSimulationResult:
        """
        Run Monte Carlo simulation of game outcomes
        
        Simulates variance in performance to get probability distributions
        """
        home_scores = []
        away_scores = []
        
        for _ in range(self.n_simulations):
            # Add variance to efficiencies (standard deviation ~5 points per 100 poss)
            home_off_var = np.random.normal(home_offensive_eff, 5)
            home_def_var = np.random.normal(home_defensive_eff, 5)
            away_off_var = np.random.normal(away_offensive_eff, 5)
            away_def_var = np.random.normal(away_defensive_eff, 5)
            
            # Add variance to tempo
            tempo_var = np.random.normal(avg_tempo, 3)
            
            # Calculate expected points for this simulation
            # Home team offense vs away team defense
            home_expected_eff = (home_off_var + away_def_var) / 2
            home_score = (home_expected_eff / 100) * tempo_var + home_court_advantage
            
            # Away team offense vs home team defense
            away_expected_eff = (away_off_var + home_def_var) / 2
            away_score = (away_expected_eff / 100) * tempo_var
            
            home_scores.append(home_score)
            away_scores.append(away_score)
        
        home_scores = np.array(home_scores)
        away_scores = np.array(away_scores)
        
        # Calculate probabilities
        home_wins = np.sum(home_scores > away_scores)
        home_win_prob = home_wins / self.n_simulations
        
        # Calculate spread distribution
        spread_distribution = home_scores - away_scores
        
        # Calculate total distribution
        total_distribution = home_scores + away_scores
        
        return GameSimulationResult(
            home_win_probability=home_win_prob,
            away_win_probability=1 - home_win_prob,
            average_home_score=np.mean(home_scores),
            average_away_score=np.mean(away_scores),
            spread_distribution=spread_distribution.tolist(),
            total_distribution=total_distribution.tolist()
        )
    
    def calculate_spread_probability(
        self,
        spread_distribution: List[float],
        market_spread: float,
        betting_home: bool = True
    ) -> float:
        """
        Calculate probability of covering the spread
        
        Args:
            spread_distribution: Distribution of home team margin
            market_spread: Market point spread (positive favors home)
            betting_home: True if betting on home team
        
        Returns:
            Probability of covering (0.0 to 1.0)
        """
        spreads = np.array(spread_distribution)
        
        if betting_home:
            # Home team needs to win by more than spread
            covers = np.sum(spreads > market_spread)
        else:
            # Away team needs to lose by less than spread (or win)
            covers = np.sum(spreads < market_spread)
        
        return covers / len(spreads)
    
    def calculate_total_probability(
        self,
        total_distribution: List[float],
        market_total: float,
        betting_over: bool = True
    ) -> float:
        """
        Calculate probability of covering the total
        
        Args:
            total_distribution: Distribution of total points
            market_total: Market over/under line
            betting_over: True if betting over
        
        Returns:
            Probability of covering (0.0 to 1.0)
        """
        totals = np.array(total_distribution)
        
        if betting_over:
            covers = np.sum(totals > market_total)
        else:
            covers = np.sum(totals < market_total)
        
        return covers / len(totals)


class AdvancedMetrics:
    """
    Advanced statistical metrics for team analysis
    Based on modern analytics used by professional bettors
    """
    
    @staticmethod
    def calculate_four_factors(
        efg_pct: float,  # Effective field goal %
        tov_pct: float,  # Turnover %
        orb_pct: float,  # Offensive rebound %
        ftr: float       # Free throw rate
    ) -> float:
        """
        Dean Oliver's Four Factors for team success
        Used in advanced analytics
        
        Weights: eFG% (40%), TOV% (25%), ORB% (20%), FTR (15%)
        """
        four_factor_score = (
            efg_pct * 0.40 +
            (1 - tov_pct) * 0.25 +  # Lower turnovers is better
            orb_pct * 0.20 +
            ftr * 0.15
        )
        return four_factor_score
    
    @staticmethod
    def calculate_pythagorean_expectation(
        points_for: float,
        points_against: float,
        exponent: float = 11.5
    ) -> float:
        """
        Pythagorean expectation for win percentage
        exponent = 11.5 is typical for college basketball
        
        Indicates if team is over/under-performing their scoring differential
        """
        return (points_for ** exponent) / (
            points_for ** exponent + points_against ** exponent
        )
    
    @staticmethod
    def calculate_consistency_score(results: List[float]) -> float:
        """
        Measure team consistency (lower is more consistent)
        Based on standard deviation of performance
        """
        if not results:
            return 0.0
        return np.std(results)
    
    @staticmethod
    def calculate_closing_ability(
        points_in_last_5_min: List[float],
        points_allowed_last_5_min: List[float]
    ) -> float:
        """
        Measure team's ability to close out close games
        Important for late-game situational betting
        """
        if not points_in_last_5_min or not points_allowed_last_5_min:
            return 0.0
        
        avg_scored = np.mean(points_in_last_5_min)
        avg_allowed = np.mean(points_allowed_last_5_min)
        
        closing_differential = avg_scored - avg_allowed
        return closing_differential


class LineMovementAnalyzer:
    """
    Analyze betting line movements
    Walters emphasizes tracking line movements at sharp books
    """
    
    @staticmethod
    def detect_sharp_action(
        opening_line: float,
        current_line: float,
        public_betting_pct: float
    ) -> Dict:
        """
        Detect if sharp bettors are moving the line
        
        Sharp action: Line moves against public money
        """
        line_movement = current_line - opening_line
        
        analysis = {
            'line_movement': line_movement,
            'sharp_action_detected': False,
            'sharp_side': None,
            'confidence': 0.0
        }
        
        # If line moves against public money, suggests sharp action
        if public_betting_pct > 0.65:  # Public heavily on one side
            if line_movement < 0:  # But line moved the other way
                analysis['sharp_action_detected'] = True
                analysis['sharp_side'] = 'underdog'
                analysis['confidence'] = abs(line_movement) * 0.1
        elif public_betting_pct < 0.35:
            if line_movement > 0:
                analysis['sharp_action_detected'] = True
                analysis['sharp_side'] = 'favorite'
                analysis['confidence'] = abs(line_movement) * 0.1
        
        return analysis
    
    @staticmethod
    def calculate_steam_move_impact(
        line_movement: float,
        time_elapsed_hours: float
    ) -> float:
        """
        Calculate impact of rapid line movement (steam)
        Fast, significant moves indicate sharp syndicate action
        """
        if time_elapsed_hours == 0:
            # Instant move indicates very strong steam
            return min(abs(line_movement), 3.0)
        
        # Points moved per hour
        movement_rate = abs(line_movement) / time_elapsed_hours
        
        # Steam typically moves 1+ point in under an hour
        if movement_rate >= 1.0:
            return min(movement_rate * 0.5, 3.0)  # Cap at 3 points impact
        
        return 0.0


class ValueFinder:
    """
    Identify value betting opportunities
    Core of Walters' approach: finding market inefficiencies
    """
    
    def __init__(self, min_edge: float = 0.03):
        self.min_edge = min_edge
    
    def find_value_opportunities(
        self,
        predictions: List[Dict],
        market_lines: List[Dict]
    ) -> List[Dict]:
        """
        Compare model predictions against market to find value
        
        Args:
            predictions: List of {game, predicted_spread, predicted_total}
            market_lines: List of {game, market_spread, market_total}
        
        Returns:
            List of value opportunities with edge calculations
        """
        opportunities = []
        
        for pred, market in zip(predictions, market_lines):
            # Spread value
            spread_diff = abs(pred['predicted_spread'] - market['market_spread'])
            spread_edge = spread_diff * 0.025  # Convert to probability edge
            
            if spread_edge >= self.min_edge:
                opportunities.append({
                    'game': pred['game'],
                    'bet_type': 'spread',
                    'predicted': pred['predicted_spread'],
                    'market': market['market_spread'],
                    'edge': spread_edge,
                    'difference': spread_diff
                })
            
            # Total value
            total_diff = abs(pred['predicted_total'] - market['market_total'])
            total_edge = total_diff * 0.025
            
            if total_edge >= self.min_edge:
                opportunities.append({
                    'game': pred['game'],
                    'bet_type': 'total',
                    'predicted': pred['predicted_total'],
                    'market': market['market_total'],
                    'edge': total_edge,
                    'difference': total_diff
                })
        
        # Sort by edge (highest first)
        opportunities.sort(key=lambda x: x['edge'], reverse=True)
        
        return opportunities
    
    def calculate_portfolio_edge(
        self,
        opportunities: List[Dict],
        correlation_matrix: np.ndarray = None
    ) -> float:
        """
        Calculate expected edge for portfolio of bets
        Accounts for correlation between games
        """
        if not opportunities:
            return 0.0
        
        # Simple case: average edge (assumes independence)
        if correlation_matrix is None:
            return np.mean([opp['edge'] for opp in opportunities])
        
        # Advanced: adjust for correlation
        edges = np.array([opp['edge'] for opp in opportunities])
        
        # Portfolio variance considers correlation
        # This is simplified - real implementation would be more complex
        portfolio_edge = np.mean(edges)
        
        return portfolio_edge


def demonstrate_advanced_features():
    """
    Demonstrate advanced analysis features
    """
    print("=" * 70)
    print("ADVANCED BILLY WALTERS FRAMEWORK FEATURES")
    print("=" * 70)
    print()
    
    # Monte Carlo Simulation
    print("MONTE CARLO SIMULATION")
    print("-" * 70)
    
    simulator = MonteCarloSimulator(n_simulations=10000)
    
    result = simulator.simulate_game(
        home_offensive_eff=115.5,
        home_defensive_eff=95.2,
        away_offensive_eff=112.3,
        away_defensive_eff=98.1,
        avg_tempo=71.0,
        home_court_advantage=3.5
    )
    
    print(f"Home Win Probability: {result.home_win_probability:.1%}")
    print(f"Away Win Probability: {result.away_win_probability:.1%}")
    print(f"Average Home Score: {result.average_home_score:.1f}")
    print(f"Average Away Score: {result.average_away_score:.1f}")
    print()
    
    # Spread probability
    market_spread = 5.5
    cover_prob = simulator.calculate_spread_probability(
        result.spread_distribution,
        market_spread,
        betting_home=True
    )
    print(f"Probability home team covers {market_spread}: {cover_prob:.1%}")
    print()
    
    # Advanced Metrics
    print("ADVANCED METRICS")
    print("-" * 70)
    
    metrics = AdvancedMetrics()
    
    four_factors = metrics.calculate_four_factors(
        efg_pct=0.545,
        tov_pct=0.18,
        orb_pct=0.32,
        ftr=0.35
    )
    print(f"Four Factors Score: {four_factors:.3f}")
    
    pythagorean = metrics.calculate_pythagorean_expectation(
        points_for=75.5,
        points_against=68.2
    )
    print(f"Pythagorean Win Expectation: {pythagorean:.1%}")
    print()
    
    # Line Movement Analysis
    print("LINE MOVEMENT ANALYSIS")
    print("-" * 70)
    
    analyzer = LineMovementAnalyzer()
    
    sharp_action = analyzer.detect_sharp_action(
        opening_line=-7.0,
        current_line=-5.5,
        public_betting_pct=0.75  # 75% of public on favorite
    )
    
    print(f"Sharp Action Detected: {sharp_action['sharp_action_detected']}")
    if sharp_action['sharp_action_detected']:
        print(f"Sharp Side: {sharp_action['sharp_side']}")
        print(f"Confidence: {sharp_action['confidence']:.1%}")
    print()
    
    print("=" * 70)
    print("These advanced features enhance the base Billy Walters framework")
    print("with modern analytical techniques used by professional betting syndicates.")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_advanced_features()
