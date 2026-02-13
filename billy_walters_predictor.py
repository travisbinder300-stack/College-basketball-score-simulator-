"""
College Basketball Prediction System using Billy Walters Framework
Based on methodologies from "Gambler: Secrets from a Life at Risk"
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TeamStats:
    """Team statistics for power rating calculation"""
    name: str
    offensive_efficiency: float  # Points per 100 possessions
    defensive_efficiency: float  # Points allowed per 100 possessions
    tempo: float  # Possessions per game
    recent_form: List[str]  # Last 5 games: 'W' or 'L'
    strength_of_schedule: float  # Opponent average power rating
    injuries: List[str] = None  # List of injured key players
    
    def __post_init__(self):
        if self.injuries is None:
            self.injuries = []


class PowerRatings:
    """
    Billy Walters' Power Ratings System
    
    Creates numeric values representing team strength.
    The power rating represents how many points a team would be
    favored by against an average team on a neutral court.
    """
    
    def __init__(self):
        self.ratings: Dict[str, float] = {}
        self.national_average_efficiency = 100.0
        
    def calculate_base_rating(self, stats: TeamStats) -> float:
        """
        Calculate base power rating from efficiency metrics
        
        Formula inspired by Walters' emphasis on offensive and defensive balance
        """
        # Net efficiency (points scored - points allowed per 100 possessions)
        net_efficiency = stats.offensive_efficiency - stats.defensive_efficiency
        
        # Normalize against national average
        normalized_rating = (net_efficiency / 10.0)  # Scale to reasonable range
        
        return normalized_rating
    
    def adjust_for_schedule_strength(self, base_rating: float, sos: float) -> float:
        """Adjust rating based on strength of schedule"""
        # Stronger schedule faced = boost rating slightly
        sos_adjustment = sos * 0.2  # 20% weight to SOS
        return base_rating + sos_adjustment
    
    def adjust_for_recent_form(self, rating: float, recent_form: List[str]) -> float:
        """
        Adjust for recent performance trend
        Walters emphasizes recent form as indicator of current team state
        """
        if not recent_form:
            return rating
        
        wins = recent_form.count('W')
        win_pct = wins / len(recent_form)
        
        # Bonus/penalty based on recent performance
        # Hot teams get small boost, cold teams get penalty
        form_adjustment = (win_pct - 0.5) * 2.0  # Range: -1 to +1
        
        return rating + form_adjustment
    
    def adjust_for_injuries(self, rating: float, injuries: List[str]) -> float:
        """
        Account for key player injuries
        Walters emphasizes assessing exact impact of injuries on lines
        """
        # Simple model: each key injury reduces rating
        injury_penalty = len(injuries) * 1.5
        return rating - injury_penalty
    
    def calculate_power_rating(self, stats: TeamStats) -> float:
        """
        Calculate comprehensive power rating for a team
        Incorporates multiple factors per Walters' methodology
        """
        # Start with base efficiency rating
        rating = self.calculate_base_rating(stats)
        
        # Apply adjustments
        rating = self.adjust_for_schedule_strength(rating, stats.strength_of_schedule)
        rating = self.adjust_for_recent_form(rating, stats.recent_form)
        rating = self.adjust_for_injuries(rating, stats.injuries)
        
        return rating
    
    def update_rating(self, team_name: str, stats: TeamStats):
        """Update power rating for a team"""
        self.ratings[team_name] = self.calculate_power_rating(stats)
    
    def get_rating(self, team_name: str) -> Optional[float]:
        """Get power rating for a team"""
        return self.ratings.get(team_name)


class GameFactors:
    """
    Game-specific factors that affect predictions
    Based on Walters' analysis of situational advantages
    """
    
    # Home court advantage varies by level and venue
    HOME_COURT_ADVANTAGE = 3.5  # Points, typical college basketball HCA
    
    @staticmethod
    def calculate_travel_fatigue(miles_traveled: float, days_rest: int) -> float:
        """
        Calculate fatigue factor from travel
        Walters emphasizes travel schedules and time zones
        """
        if days_rest >= 3:
            return 0.0  # Well rested
        
        # Penalty for long travel with short rest
        travel_penalty = 0.0
        if miles_traveled > 1000:
            travel_penalty = 1.0
        elif miles_traveled > 500:
            travel_penalty = 0.5
        
        # Rest factor
        rest_factor = (3 - days_rest) * 0.5
        
        return travel_penalty + rest_factor
    
    @staticmethod
    def calculate_motivation_factor(
        is_rivalry: bool,
        is_conference_game: bool,
        revenge_game: bool
    ) -> float:
        """
        Psychological factors affecting performance
        Walters considers motivational factors
        """
        motivation = 0.0
        
        if is_rivalry:
            motivation += 1.5
        if is_conference_game:
            motivation += 0.5
        if revenge_game:
            motivation += 1.0
            
        return motivation
    
    @staticmethod
    def calculate_situational_adjustment(
        home_team_desperate: bool,
        away_team_coasting: bool
    ) -> float:
        """
        Situation-based adjustments
        Teams fighting for tournament berth vs teams already in
        """
        adjustment = 0.0
        
        if home_team_desperate:
            adjustment += 2.0  # Extra motivation for must-win
        if away_team_coasting:
            adjustment += 1.5  # Away team may not be fully engaged
            
        return adjustment


class BankrollManagement:
    """
    Billy Walters' Bankroll Management System
    Conservative approach: only risk 1-3% per bet
    """
    
    def __init__(self, total_bankroll: float):
        self.total_bankroll = total_bankroll
        self.min_bet_pct = 0.01  # 1% minimum
        self.max_bet_pct = 0.03  # 3% maximum
        self.current_bankroll = total_bankroll
        
    def calculate_bet_size(self, edge: float, confidence: float) -> float:
        """
        Calculate optimal bet size based on edge and confidence
        
        Args:
            edge: Expected value advantage (0.0 to 1.0)
            confidence: Confidence in the prediction (0.0 to 1.0)
        
        Returns:
            Bet size in dollars
        """
        # Kelly Criterion approach, but capped at max_bet_pct
        # Walters uses modified Kelly for risk management
        
        if edge <= 0:
            return 0.0
        
        # Scale bet size by edge and confidence
        bet_fraction = min(edge * confidence * 0.1, self.max_bet_pct)
        bet_fraction = max(bet_fraction, self.min_bet_pct)
        
        bet_size = self.current_bankroll * bet_fraction
        
        return round(bet_size, 2)
    
    def update_bankroll(self, result: float):
        """Update bankroll after bet result (positive for win, negative for loss)"""
        self.current_bankroll += result
    
    def get_current_bankroll(self) -> float:
        """Get current bankroll"""
        return self.current_bankroll
    
    def should_bet(self, edge: float, min_edge: float = 0.03) -> bool:
        """
        Determine if bet has sufficient edge
        Walters: Never bet without clear edge
        """
        return edge >= min_edge


class PredictionEngine:
    """
    Main prediction engine using Billy Walters' framework
    Combines power ratings, game factors, and situational analysis
    """
    
    def __init__(self, power_ratings: PowerRatings):
        self.power_ratings = power_ratings
        
    def predict_spread(
        self,
        home_team: str,
        away_team: str,
        is_neutral_site: bool = False,
        miles_traveled: float = 0.0,
        days_rest_home: int = 3,
        days_rest_away: int = 3,
        is_rivalry: bool = False,
        is_conference_game: bool = False,
        revenge_game: bool = False,
        home_team_desperate: bool = False,
        away_team_coasting: bool = False
    ) -> Tuple[float, str]:
        """
        Predict the point spread for a game
        
        Returns:
            (spread, favorite): Spread in points and name of favored team
        """
        # Get base power ratings
        home_rating = self.power_ratings.get_rating(home_team)
        away_rating = self.power_ratings.get_rating(away_team)
        
        if home_rating is None or away_rating is None:
            raise ValueError(f"Missing power ratings for teams")
        
        # Start with power rating differential
        spread = home_rating - away_rating
        
        # Add home court advantage if not neutral
        if not is_neutral_site:
            spread += GameFactors.HOME_COURT_ADVANTAGE
        
        # Adjust for travel fatigue (penalizes away team typically)
        away_fatigue = GameFactors.calculate_travel_fatigue(miles_traveled, days_rest_away)
        spread += away_fatigue
        
        # Adjust for motivation
        motivation = GameFactors.calculate_motivation_factor(
            is_rivalry, is_conference_game, revenge_game
        )
        spread += motivation
        
        # Situational adjustments
        situational = GameFactors.calculate_situational_adjustment(
            home_team_desperate, away_team_coasting
        )
        spread += situational
        
        # Determine favorite
        if spread > 0:
            favorite = home_team
            spread = abs(spread)
        else:
            favorite = away_team
            spread = abs(spread)
        
        return round(spread, 1), favorite
    
    def predict_total(
        self,
        home_team: str,
        away_team: str,
        home_stats: TeamStats,
        away_stats: TeamStats
    ) -> float:
        """
        Predict total points (over/under) for a game
        Based on team tempos and efficiencies
        """
        # Average possessions
        avg_tempo = (home_stats.tempo + away_stats.tempo) / 2
        
        # Expected efficiency for each team
        # When good offense meets good defense, adjust
        home_expected_eff = (
            home_stats.offensive_efficiency + 
            away_stats.defensive_efficiency
        ) / 2
        
        away_expected_eff = (
            away_stats.offensive_efficiency + 
            home_stats.defensive_efficiency
        ) / 2
        
        # Calculate expected points
        home_points = (home_expected_eff / 100) * avg_tempo
        away_points = (away_expected_eff / 100) * avg_tempo
        
        total = home_points + away_points
        
        return round(total, 1)
    
    def calculate_edge(
        self,
        predicted_spread: float,
        market_spread: float
    ) -> float:
        """
        Calculate betting edge
        Walters' key insight: bet when your line differs significantly from market
        
        Returns edge as a decimal (0.05 = 5% edge)
        """
        # Difference between our prediction and the market
        difference = abs(predicted_spread - market_spread)
        
        # Convert point difference to win probability edge
        # Rough approximation: 1 point = ~2.5% win probability
        edge = difference * 0.025
        
        return edge
    
    def get_betting_recommendation(
        self,
        predicted_spread: float,
        predicted_favorite: str,
        market_spread: float,
        market_favorite: str,
        bankroll_manager: BankrollManagement,
        confidence: float = 0.7
    ) -> Dict:
        """
        Generate betting recommendation following Walters' principles
        
        Returns:
            Dictionary with recommendation details
        """
        edge = self.calculate_edge(predicted_spread, market_spread)
        
        recommendation = {
            'predicted_spread': predicted_spread,
            'predicted_favorite': predicted_favorite,
            'market_spread': market_spread,
            'market_favorite': market_favorite,
            'edge': edge,
            'should_bet': False,
            'bet_size': 0.0,
            'bet_side': None,
            'reasoning': ''
        }
        
        # Check if there's sufficient edge
        if not bankroll_manager.should_bet(edge):
            recommendation['reasoning'] = (
                f"Insufficient edge ({edge:.1%}). "
                f"Walters principle: Only bet with clear advantage (>3%)."
            )
            return recommendation
        
        # Determine which side to bet
        if predicted_favorite == market_favorite:
            # Same favorite, compare spreads
            if predicted_spread > market_spread:
                # We think favorite wins by more - bet the favorite
                recommendation['bet_side'] = f"{market_favorite} -{market_spread}"
            else:
                # Market has favorite winning by more - bet the underdog
                recommendation['bet_side'] = f"Underdog +{market_spread}"
        else:
            # Different favorites - significant disagreement
            # Bet our predicted favorite
            recommendation['bet_side'] = f"{predicted_favorite} (outright)"
            edge *= 1.5  # Increase edge for disagreement on favorite
        
        # Calculate bet size
        bet_size = bankroll_manager.calculate_bet_size(edge, confidence)
        
        recommendation['should_bet'] = True
        recommendation['bet_size'] = bet_size
        recommendation['reasoning'] = (
            f"Edge of {edge:.1%} detected. "
            f"Model disagrees with market by {abs(predicted_spread - market_spread):.1f} points. "
            f"Recommended bet: ${bet_size:.2f} ({(bet_size/bankroll_manager.current_bankroll)*100:.1f}% of bankroll)"
        )
        
        return recommendation


def create_example_prediction():
    """
    Example usage of the Billy Walters framework
    """
    print("=" * 70)
    print("BILLY WALTERS COLLEGE BASKETBALL PREDICTION SYSTEM")
    print("Based on 'Gambler: Secrets from a Life at Risk'")
    print("=" * 70)
    print()
    
    # Initialize power ratings system
    pr = PowerRatings()
    
    # Example: Duke vs UNC
    duke_stats = TeamStats(
        name="Duke",
        offensive_efficiency=115.5,
        defensive_efficiency=95.2,
        tempo=70.5,
        recent_form=['W', 'W', 'L', 'W', 'W'],
        strength_of_schedule=2.5,
        injuries=[]
    )
    
    unc_stats = TeamStats(
        name="UNC",
        offensive_efficiency=112.3,
        defensive_efficiency=98.1,
        tempo=72.8,
        recent_form=['W', 'L', 'W', 'W', 'L'],
        strength_of_schedule=2.2,
        injuries=["Starting PG"]
    )
    
    # Calculate power ratings
    pr.update_rating("Duke", duke_stats)
    pr.update_rating("UNC", unc_stats)
    
    print("POWER RATINGS")
    print("-" * 70)
    print(f"Duke: {pr.get_rating('Duke'):+.1f}")
    print(f"UNC:  {pr.get_rating('UNC'):+.1f}")
    print()
    
    # Create prediction engine
    engine = PredictionEngine(pr)
    
    # Predict spread for game at Duke (home)
    predicted_spread, favorite = engine.predict_spread(
        home_team="Duke",
        away_team="UNC",
        is_neutral_site=False,
        miles_traveled=20,  # Short distance (rivalry)
        days_rest_home=3,
        days_rest_away=2,
        is_rivalry=True,
        is_conference_game=True,
        revenge_game=True  # UNC lost earlier meeting
    )
    
    print("GAME PREDICTION")
    print("-" * 70)
    print(f"Matchup: Duke vs UNC (at Duke)")
    print(f"Predicted Spread: {favorite} -{predicted_spread}")
    print()
    
    # Predict total
    predicted_total = engine.predict_total("Duke", "UNC", duke_stats, unc_stats)
    print(f"Predicted Total: {predicted_total}")
    print()
    
    # Bankroll management
    bankroll = BankrollManagement(total_bankroll=10000)
    
    # Compare to market (example market line)
    market_spread = 5.5
    market_favorite = "Duke"
    
    print("BETTING ANALYSIS")
    print("-" * 70)
    print(f"Market Line: {market_favorite} -{market_spread}")
    print(f"Our Line:    {favorite} -{predicted_spread}")
    print()
    
    # Get recommendation
    recommendation = engine.get_betting_recommendation(
        predicted_spread=predicted_spread,
        predicted_favorite=favorite,
        market_spread=market_spread,
        market_favorite=market_favorite,
        bankroll_manager=bankroll,
        confidence=0.75
    )
    
    print("RECOMMENDATION")
    print("-" * 70)
    print(f"Should Bet: {recommendation['should_bet']}")
    if recommendation['should_bet']:
        print(f"Bet Side: {recommendation['bet_side']}")
        print(f"Bet Size: ${recommendation['bet_size']:.2f}")
        print(f"Edge: {recommendation['edge']:.1%}")
    print(f"\nReasoning: {recommendation['reasoning']}")
    print()
    
    print("=" * 70)
    print("KEY PRINCIPLES FROM BILLY WALTERS:")
    print("=" * 70)
    print("1. Only bet when you have a clear mathematical edge (>3%)")
    print("2. Strict bankroll management - never risk more than 1-3% per bet")
    print("3. Build detailed power ratings from comprehensive data")
    print("4. Account for all game factors: travel, rest, motivation, injuries")
    print("5. Line shop across multiple sportsbooks for best value")
    print("6. Don't chase losses - be disciplined and patient")
    print("7. Exploit market inefficiencies, don't follow public trends")
    print("=" * 70)


if __name__ == "__main__":
    create_example_prediction()
