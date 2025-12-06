#!/usr/bin/env python3
"""
NBA 10,000 Game Simulator with Haralabos Voulgaris-style Analytics and Kelly Betting Strategy

This simulator uses advanced basketball analytics including:
- Four Factors (eFG%, TOV%, ORB%, FT Rate)
- Pace-adjusted efficiency ratings
- Pythagorean win expectation
- Kelly Criterion for optimal bet sizing
"""

import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import statistics


@dataclass
class TeamStats:
    """Team statistics using advanced metrics"""
    name: str
    offensive_rating: float  # Points per 100 possessions
    defensive_rating: float  # Points allowed per 100 possessions
    pace: float  # Possessions per game
    efg_pct: float  # Effective field goal percentage
    tov_pct: float  # Turnover percentage
    orb_pct: float  # Offensive rebound percentage
    ft_rate: float  # Free throw rate (FTA/FGA)
    
    def net_rating(self) -> float:
        """Net rating (offensive - defensive)"""
        return self.offensive_rating - self.defensive_rating


@dataclass
class GameResult:
    """Result of a simulated game"""
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    home_win: bool
    margin: int


@dataclass
class BettingOpportunity:
    """Betting opportunity with Kelly Criterion sizing"""
    game: GameResult
    true_prob: float  # Model's probability
    market_odds: float  # Market implied probability
    kelly_fraction: float  # Recommended bet size
    expected_value: float  # Expected value of bet


class NBASimulator:
    """NBA Game Simulator using Haralabos Voulgaris-style analytics"""
    
    def __init__(self, home_court_advantage: float = 3.5):
        """
        Initialize simulator
        
        Args:
            home_court_advantage: Points added to home team (default ~3.5 points)
        """
        self.home_court_advantage = home_court_advantage
        self.random = random.Random()
        
    def simulate_game(self, home_team: TeamStats, away_team: TeamStats, 
                     seed: Optional[int] = None) -> GameResult:
        """
        Simulate a single game using advanced metrics
        
        Args:
            home_team: Home team statistics
            away_team: Away team statistics
            seed: Random seed for reproducibility
            
        Returns:
            GameResult with final score
        """
        if seed is not None:
            self.random.seed(seed)
        
        # Calculate expected pace (geometric mean of both teams' pace)
        game_pace = math.sqrt(home_team.pace * away_team.pace)
        
        # Adjust for home court advantage
        home_adj_off = home_team.offensive_rating + self.home_court_advantage / 2
        home_adj_def = home_team.defensive_rating - self.home_court_advantage / 2
        
        # Calculate expected points using offensive/defensive ratings
        # Account for opponent strength
        home_expected = (home_adj_off + away_team.defensive_rating) / 2 * (game_pace / 100)
        away_expected = (away_team.offensive_rating + home_adj_def) / 2 * (game_pace / 100)
        
        # Add variance based on four factors
        home_variance = self._calculate_variance(home_team, away_team)
        away_variance = self._calculate_variance(away_team, home_team)
        
        # Simulate final scores with normal distribution
        home_score = max(0, int(self.random.gauss(home_expected, home_variance)))
        away_score = max(0, int(self.random.gauss(away_expected, away_variance)))
        
        return GameResult(
            home_team=home_team.name,
            away_team=away_team.name,
            home_score=home_score,
            away_score=away_score,
            home_win=home_score > away_score,
            margin=home_score - away_score
        )
    
    def _calculate_variance(self, team: TeamStats, opponent: TeamStats) -> float:
        """
        Calculate scoring variance based on four factors
        
        Higher variance for:
        - Higher turnover rates
        - Lower eFG%
        - Higher pace
        """
        base_variance = 12.0  # Base standard deviation
        
        # Adjust for team characteristics
        tov_factor = 1 + (team.tov_pct / 100) * 0.5
        efg_factor = 1 + (0.5 - team.efg_pct) * 0.3
        pace_factor = team.pace / 100
        
        return base_variance * tov_factor * efg_factor * pace_factor
    
    def calculate_win_probability(self, home_team: TeamStats, 
                                  away_team: TeamStats) -> float:
        """
        Calculate win probability using Pythagorean expectation
        
        Args:
            home_team: Home team statistics
            away_team: Away team statistics
            
        Returns:
            Home team win probability (0-1)
        """
        # Adjust ratings for home court
        home_net = home_team.net_rating() + self.home_court_advantage
        away_net = away_team.net_rating()
        
        # Use log5 method for win probability
        # This accounts for strength of schedule
        exponent = 11.5  # NBA exponent
        
        home_pythag = home_net ** exponent / (home_net ** exponent + away_net ** exponent) if away_net != 0 else 0.5
        
        # Bound between reasonable limits
        return max(0.01, min(0.99, home_pythag))
    
    def simulate_multiple_games(self, home_team: TeamStats, away_team: TeamStats,
                               num_simulations: int = 10000) -> Dict[str, float]:
        """
        Run multiple simulations of the same matchup
        
        Args:
            home_team: Home team statistics
            away_team: Away team statistics
            num_simulations: Number of games to simulate
            
        Returns:
            Dictionary with simulation results
        """
        results = []
        home_wins = 0
        total_home_score = 0
        total_away_score = 0
        margins = []
        
        for i in range(num_simulations):
            game = self.simulate_game(home_team, away_team)
            results.append(game)
            
            if game.home_win:
                home_wins += 1
            
            total_home_score += game.home_score
            total_away_score += game.away_score
            margins.append(game.margin)
        
        return {
            'home_win_pct': home_wins / num_simulations,
            'avg_home_score': total_home_score / num_simulations,
            'avg_away_score': total_away_score / num_simulations,
            'avg_margin': statistics.mean(margins),
            'median_margin': statistics.median(margins),
            'margin_stdev': statistics.stdev(margins) if len(margins) > 1 else 0,
            'games_simulated': num_simulations
        }


class KellyBetting:
    """Kelly Criterion betting strategy implementation"""
    
    @staticmethod
    def calculate_kelly_fraction(true_prob: float, odds: float, 
                                 kelly_fraction: float = 0.25) -> float:
        """
        Calculate Kelly Criterion bet size
        
        Args:
            true_prob: Your estimated probability of winning (0-1)
            odds: Decimal odds (e.g., 2.0 for even money)
            kelly_fraction: Fraction of Kelly to bet (0.25 = quarter Kelly)
            
        Returns:
            Fraction of bankroll to bet (0-1)
        """
        if true_prob <= 0 or true_prob >= 1 or odds <= 1:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds - 1, p = win probability, q = 1 - p
        b = odds - 1
        q = 1 - true_prob
        
        full_kelly = (b * true_prob - q) / b
        
        # Only bet if positive expected value
        if full_kelly <= 0:
            return 0.0
        
        # Use fractional Kelly for safety
        return min(full_kelly * kelly_fraction, 0.2)  # Cap at 20% of bankroll
    
    @staticmethod
    def expected_value(true_prob: float, odds: float, bet_size: float = 1.0) -> float:
        """
        Calculate expected value of a bet
        
        Args:
            true_prob: Your estimated probability of winning
            odds: Decimal odds
            bet_size: Size of bet
            
        Returns:
            Expected value
        """
        win_amount = (odds - 1) * bet_size
        lose_amount = -bet_size
        
        ev = (true_prob * win_amount) + ((1 - true_prob) * lose_amount)
        return ev
    
    @staticmethod
    def find_betting_edges(simulator: NBASimulator, home_team: TeamStats,
                          away_team: TeamStats, market_home_odds: float,
                          num_simulations: int = 10000) -> Optional[BettingOpportunity]:
        """
        Find betting opportunities using simulation
        
        Args:
            simulator: NBASimulator instance
            home_team: Home team stats
            away_team: Away team stats
            market_home_odds: Market odds for home team
            num_simulations: Number of simulations to run
            
        Returns:
            BettingOpportunity if edge found, None otherwise
        """
        # Run simulations
        results = simulator.simulate_multiple_games(home_team, away_team, num_simulations)
        true_prob = results['home_win_pct']
        
        # Calculate market implied probability
        market_prob = 1 / market_home_odds
        
        # Calculate Kelly fraction
        kelly = KellyBetting.calculate_kelly_fraction(true_prob, market_home_odds)
        
        # Calculate expected value
        ev = KellyBetting.expected_value(true_prob, market_home_odds, 1.0)
        
        if kelly > 0:
            game = simulator.simulate_game(home_team, away_team)
            return BettingOpportunity(
                game=game,
                true_prob=true_prob,
                market_odds=market_prob,
                kelly_fraction=kelly,
                expected_value=ev
            )
        
        return None


def create_sample_teams() -> List[TeamStats]:
    """Create sample NBA teams with realistic statistics"""
    teams = [
        TeamStats(
            name="Elite Contender",
            offensive_rating=118.5,
            defensive_rating=110.2,
            pace=99.5,
            efg_pct=0.565,
            tov_pct=12.5,
            orb_pct=26.5,
            ft_rate=0.245
        ),
        TeamStats(
            name="Good Playoff Team",
            offensive_rating=115.2,
            defensive_rating=112.8,
            pace=98.2,
            efg_pct=0.545,
            tov_pct=13.8,
            orb_pct=24.2,
            ft_rate=0.235
        ),
        TeamStats(
            name="Average Team",
            offensive_rating=112.5,
            defensive_rating=112.5,
            pace=97.5,
            efg_pct=0.535,
            tov_pct=14.2,
            orb_pct=23.0,
            ft_rate=0.225
        ),
        TeamStats(
            name="Below Average Team",
            offensive_rating=109.8,
            defensive_rating=115.2,
            pace=96.8,
            efg_pct=0.520,
            tov_pct=15.1,
            orb_pct=21.5,
            ft_rate=0.218
        ),
        TeamStats(
            name="Rebuilding Team",
            offensive_rating=106.5,
            defensive_rating=117.8,
            pace=100.2,
            efg_pct=0.505,
            tov_pct=16.2,
            orb_pct=20.8,
            ft_rate=0.210
        )
    ]
    return teams


def run_10000_game_simulation():
    """Run the full 10,000 game simulation with Kelly betting analysis"""
    print("=" * 80)
    print("NBA 10,000 GAME SIMULATOR")
    print("Haralabos Voulgaris-Style Analytics with Kelly Betting Strategy")
    print("=" * 80)
    print()
    
    # Initialize simulator
    simulator = NBASimulator(home_court_advantage=3.5)
    teams = create_sample_teams()
    
    print("SAMPLE TEAMS:")
    print("-" * 80)
    for team in teams:
        print(f"{team.name:25s} | ORtg: {team.offensive_rating:5.1f} | "
              f"DRtg: {team.defensive_rating:5.1f} | Net: {team.net_rating():+5.1f} | "
              f"Pace: {team.pace:4.1f}")
    print()
    
    # Example matchup: Elite vs Good team
    home_team = teams[0]  # Elite Contender
    away_team = teams[1]  # Good Playoff Team
    
    print("=" * 80)
    print(f"SIMULATING: {home_team.name} (HOME) vs {away_team.name} (AWAY)")
    print("=" * 80)
    print()
    
    # Run 10,000 simulations
    print("Running 10,000 game simulations...")
    results = simulator.simulate_multiple_games(home_team, away_team, 10000)
    
    print()
    print("SIMULATION RESULTS:")
    print("-" * 80)
    print(f"Home Win Percentage:     {results['home_win_pct']:.1%}")
    print(f"Average Home Score:      {results['avg_home_score']:.1f}")
    print(f"Average Away Score:      {results['avg_away_score']:.1f}")
    print(f"Average Margin:          {results['avg_margin']:+.1f}")
    print(f"Median Margin:           {results['median_margin']:+.1f}")
    print(f"Margin Std Deviation:    {results['margin_stdev']:.1f}")
    print()
    
    # Kelly Betting Analysis
    print("=" * 80)
    print("KELLY BETTING STRATEGY ANALYSIS")
    print("=" * 80)
    print()
    
    # Example: Market has home team at -200 (1.5 decimal odds, 66.7% implied)
    market_odds = 1.67  # Decimal odds
    market_implied = 1 / market_odds
    
    print(f"Market Odds (Home Team): {market_odds:.2f} (Implied Prob: {market_implied:.1%})")
    print(f"Model Probability:       {results['home_win_pct']:.1%}")
    print()
    
    # Calculate Kelly
    kelly = KellyBetting.calculate_kelly_fraction(results['home_win_pct'], market_odds, 0.25)
    ev = KellyBetting.expected_value(results['home_win_pct'], market_odds, 100)
    
    if kelly > 0:
        print(f"✓ BETTING EDGE DETECTED!")
        print(f"  Quarter-Kelly Bet Size:  {kelly:.2%} of bankroll")
        print(f"  Expected Value (per $100): ${ev:.2f}")
        print(f"  Edge:                    {(results['home_win_pct'] - market_implied):.1%}")
    else:
        print(f"✗ NO BETTING EDGE")
        print(f"  Model prob < Market prob")
    
    print()
    
    # Run additional matchups
    print("=" * 80)
    print("ADDITIONAL MATCHUP SIMULATIONS (1,000 games each)")
    print("=" * 80)
    print()
    
    matchups = [
        (teams[0], teams[4]),  # Elite vs Rebuilding
        (teams[2], teams[2]),  # Average vs Average
        (teams[3], teams[1]),  # Below Avg vs Good
    ]
    
    for home, away in matchups:
        quick_results = simulator.simulate_multiple_games(home, away, 1000)
        print(f"{home.name} vs {away.name}")
        print(f"  Home Win %: {quick_results['home_win_pct']:.1%} | "
              f"Avg Score: {quick_results['avg_home_score']:.1f}-{quick_results['avg_away_score']:.1f} | "
              f"Avg Margin: {quick_results['avg_margin']:+.1f}")
        print()
    
    print("=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_10000_game_simulation()
