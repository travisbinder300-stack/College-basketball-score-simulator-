#!/usr/bin/env python3
"""
NBA Spread and Total Analysis System
Provides predictions with confidence levels of 70% or higher
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime


@dataclass
class Team:
    """Represents an NBA team with statistics"""
    name: str
    offensive_rating: float  # Points per 100 possessions
    defensive_rating: float  # Points allowed per 100 possessions
    pace: float  # Possessions per game
    win_percentage: float  # Current season win percentage
    recent_form: float  # Last 10 games performance (0-1)


@dataclass
class Game:
    """Represents an NBA game matchup"""
    home_team: Team
    away_team: Team
    date: str
    market_spread: float = None  # Market/betting line spread (positive = home favored)


@dataclass
class Prediction:
    """Represents a prediction with confidence"""
    game: Game
    spread: float  # Positive means home team favored
    total: float  # Total points over/under
    spread_confidence: float  # 0-100%
    total_confidence: float  # 0-100%
    spread_value: float = None  # Difference between predicted and market spread
    is_overvalue: bool = False  # True if significant value exists
    value_side: str = None  # "home" or "away" - which side has value
    
    def __str__(self):
        result = f"""
Game: {self.game.away_team.name} @ {self.game.home_team.name} ({self.game.date})
Spread: {self.game.home_team.name} {self.spread:+.1f} (Confidence: {self.spread_confidence:.1f}%)
Total: {self.total:.1f} points (Confidence: {self.total_confidence:.1f}%)"""
        
        if self.is_overvalue and self.spread_value is not None:
            result += f"""
*** OVERVALUE OPPORTUNITY ***
Market Spread: {self.game.home_team.name} {self.game.market_spread:+.1f}
Value Difference: {abs(self.spread_value):.1f} points
Recommended Bet: {self.value_side.upper()} side ({self.game.home_team.name if self.value_side == 'home' else self.game.away_team.name})"""
        
        return result + "\n"


class NBAAnalyzer:
    """Analyzes NBA games for spread and total predictions"""
    
    def __init__(self, min_confidence: float = 70.0):
        self.min_confidence = min_confidence
    
    def calculate_spread(self, game: Game) -> Tuple[float, float]:
        """
        Calculate the spread prediction and confidence level
        
        Returns:
            Tuple of (spread, confidence)
            - spread: positive means home team favored
            - confidence: percentage (0-100)
        """
        home = game.home_team
        away = game.away_team
        
        # Net rating difference
        net_rating_diff = (home.offensive_rating - home.defensive_rating) - \
                         (away.offensive_rating - away.defensive_rating)
        
        # Home court advantage (typically 3-4 points in NBA)
        home_court_advantage = 3.5
        
        # Win percentage factor
        win_pct_diff = (home.win_percentage - away.win_percentage) * 10
        
        # Recent form factor
        form_diff = (home.recent_form - away.recent_form) * 5
        
        # Calculate spread
        spread = (net_rating_diff * 0.15 + 
                 home_court_advantage + 
                 win_pct_diff * 0.3 +
                 form_diff * 0.2)
        
        # Calculate confidence based on consistency factors
        # Higher confidence when there's clear differentiation
        rating_diff_magnitude = abs(net_rating_diff)
        win_pct_diff_magnitude = abs(home.win_percentage - away.win_percentage)
        form_diff_magnitude = abs(home.recent_form - away.recent_form)
        
        # Base confidence
        base_confidence = 65.0
        
        # Add confidence based on clear advantages
        confidence = base_confidence + \
                    (rating_diff_magnitude * 0.8) + \
                    (win_pct_diff_magnitude * 15) + \
                    (form_diff_magnitude * 10)
        
        # Cap confidence at 95%
        confidence = min(confidence, 95.0)
        
        return spread, confidence
    
    def calculate_total(self, game: Game) -> Tuple[float, float]:
        """
        Calculate the total points prediction and confidence level
        
        Returns:
            Tuple of (total, confidence)
            - total: predicted total points
            - confidence: percentage (0-100)
        """
        home = game.home_team
        away = game.away_team
        
        # Calculate expected pace (average of both teams)
        expected_pace = (home.pace + away.pace) / 2
        
        # Calculate expected points per possession
        home_expected_ppg = (home.offensive_rating / 100) * expected_pace
        away_expected_ppg = (away.offensive_rating / 100) * expected_pace
        
        # Adjust for defensive ratings
        home_points_allowed = (away.defensive_rating / 100) * expected_pace
        away_points_allowed = (home.defensive_rating / 100) * expected_pace
        
        # Average the offensive and defensive projections
        home_projected = (home_expected_ppg + away_points_allowed) / 2
        away_projected = (away_expected_ppg + home_points_allowed) / 2
        
        total = home_projected + away_projected
        
        # Calculate confidence based on pace and rating consistency
        pace_similarity = 1 - (abs(home.pace - away.pace) / max(home.pace, away.pace))
        
        # Higher confidence when both teams have similar pace
        base_confidence = 65.0
        pace_confidence_bonus = pace_similarity * 15
        
        # Add confidence based on consistent offensive/defensive ratings
        rating_consistency = (home.offensive_rating + away.offensive_rating + 
                            home.defensive_rating + away.defensive_rating) / 4
        
        # Teams with ratings closer to league average (110) are more predictable
        rating_confidence_bonus = 15 - (abs(rating_consistency - 110) * 0.1)
        
        confidence = base_confidence + pace_confidence_bonus + max(0, rating_confidence_bonus)
        
        # Cap confidence at 95%
        confidence = min(confidence, 95.0)
        
        return total, confidence
    
    def detect_overvalue(self, prediction: Prediction, min_value_threshold: float = 2.5) -> Prediction:
        """
        Detect if there's overvalue in the spread compared to market line
        
        Args:
            prediction: The prediction object to analyze
            min_value_threshold: Minimum point difference to consider as overvalue (default 2.5)
        
        Returns:
            Updated prediction with overvalue information
        """
        if prediction.game.market_spread is None:
            return prediction
        
        # Calculate value: difference between our predicted spread and market spread
        # Positive value means our prediction is higher than market (home team undervalued by market)
        # Negative value means our prediction is lower than market (away team undervalued by market)
        spread_value = prediction.spread - prediction.game.market_spread
        
        # Determine if there's significant overvalue
        is_overvalue = abs(spread_value) >= min_value_threshold
        
        # Determine which side has value
        value_side = None
        if is_overvalue:
            if spread_value > 0:
                # Our prediction favors home more than market does
                # Value is on the home team
                value_side = "home"
            else:
                # Our prediction favors away more than market does (or favors home less)
                # Value is on the away team
                value_side = "away"
        
        prediction.spread_value = spread_value
        prediction.is_overvalue = is_overvalue
        prediction.value_side = value_side
        
        return prediction
    
    def analyze_game(self, game: Game) -> Prediction:
        """Analyze a game and return predictions"""
        spread, spread_confidence = self.calculate_spread(game)
        total, total_confidence = self.calculate_total(game)
        
        prediction = Prediction(
            game=game,
            spread=spread,
            total=total,
            spread_confidence=spread_confidence,
            total_confidence=total_confidence
        )
        
        # Check for overvalue if market spread is available
        if game.market_spread is not None:
            prediction = self.detect_overvalue(prediction)
        
        return prediction
    
    def analyze_games(self, games: List[Game]) -> List[Prediction]:
        """
        Analyze multiple games and filter by minimum confidence
        
        Returns only predictions where both spread and total confidence
        meet the minimum threshold
        """
        predictions = []
        
        for game in games:
            prediction = self.analyze_game(game)
            
            # Only include predictions that meet confidence threshold
            if (prediction.spread_confidence >= self.min_confidence and 
                prediction.total_confidence >= self.min_confidence):
                predictions.append(prediction)
        
        return predictions
    
    def find_overvalue_spreads(self, games: List[Game], min_value_threshold: float = 2.5) -> List[Prediction]:
        """
        Find games with overvalue spread opportunities
        
        Args:
            games: List of games to analyze
            min_value_threshold: Minimum point difference to consider as overvalue
        
        Returns:
            List of predictions with overvalue opportunities that meet confidence threshold
        """
        predictions = self.analyze_games(games)
        
        # Filter for only overvalue opportunities
        overvalue_predictions = [p for p in predictions if p.is_overvalue]
        
        return overvalue_predictions


def create_sample_teams() -> Dict[str, Team]:
    """Create sample NBA teams with realistic statistics"""
    teams = {
        "Lakers": Team(
            name="Los Angeles Lakers",
            offensive_rating=115.2,
            defensive_rating=108.5,
            pace=101.2,
            win_percentage=0.650,
            recent_form=0.70
        ),
        "Celtics": Team(
            name="Boston Celtics",
            offensive_rating=118.5,
            defensive_rating=110.2,
            pace=98.5,
            win_percentage=0.700,
            recent_form=0.80
        ),
        "Warriors": Team(
            name="Golden State Warriors",
            offensive_rating=116.8,
            defensive_rating=112.3,
            pace=103.5,
            win_percentage=0.580,
            recent_form=0.60
        ),
        "Nets": Team(
            name="Brooklyn Nets",
            offensive_rating=113.5,
            defensive_rating=115.2,
            pace=100.8,
            win_percentage=0.450,
            recent_form=0.40
        ),
        "Bucks": Team(
            name="Milwaukee Bucks",
            offensive_rating=117.2,
            defensive_rating=109.8,
            pace=99.5,
            win_percentage=0.680,
            recent_form=0.75
        ),
        "Suns": Team(
            name="Phoenix Suns",
            offensive_rating=114.8,
            defensive_rating=111.5,
            pace=100.2,
            win_percentage=0.620,
            recent_form=0.70
        ),
        "Heat": Team(
            name="Miami Heat",
            offensive_rating=112.5,
            defensive_rating=107.8,
            pace=97.5,
            win_percentage=0.590,
            recent_form=0.65
        ),
        "Nuggets": Team(
            name="Denver Nuggets",
            offensive_rating=119.2,
            defensive_rating=113.5,
            pace=102.8,
            win_percentage=0.710,
            recent_form=0.85
        )
    }
    return teams


def create_sample_games(teams: Dict[str, Team]) -> List[Game]:
    """Create sample game matchups with market spreads"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    games = [
        Game(teams["Lakers"], teams["Celtics"], today, market_spread=1.5),  # Market slightly favors Lakers
        Game(teams["Warriors"], teams["Nets"], today, market_spread=8.0),  # Market heavily favors Warriors
        Game(teams["Bucks"], teams["Suns"], today, market_spread=4.0),  # Market moderately favors Bucks
        Game(teams["Heat"], teams["Nuggets"], today, market_spread=-2.5),  # Market favors Nuggets (away)
        Game(teams["Lakers"], teams["Nets"], today, market_spread=3.5),  # Market moderately favors Lakers
        Game(teams["Celtics"], teams["Warriors"], today, market_spread=7.0),  # Market heavily favors Celtics
    ]
    
    return games


def main():
    """Main function to demonstrate NBA analysis"""
    print("=" * 80)
    print("NBA SPREAD AND TOTAL ANALYSIS WITH OVERVALUE DETECTION")
    print("Minimum Confidence: 70%")
    print("=" * 80)
    print()
    
    # Create analyzer with 70% minimum confidence
    analyzer = NBAAnalyzer(min_confidence=70.0)
    
    # Create sample data
    teams = create_sample_teams()
    games = create_sample_games(teams)
    
    # Analyze games
    predictions = analyzer.analyze_games(games)
    
    # Display results
    print(f"Analyzed {len(games)} games")
    print(f"Found {len(predictions)} predictions meeting 70%+ confidence threshold")
    print()
    
    if predictions:
        print("HIGH CONFIDENCE PREDICTIONS (70%+ confidence):")
        print("=" * 80)
        
        for i, pred in enumerate(predictions, 1):
            print(f"\nPrediction #{i}:")
            print(pred)
    else:
        print("No predictions met the 70% confidence threshold.")
    
    # Summary statistics
    if predictions:
        avg_spread_conf = sum(p.spread_confidence for p in predictions) / len(predictions)
        avg_total_conf = sum(p.total_confidence for p in predictions) / len(predictions)
        
        print("\nSUMMARY STATISTICS:")
        print("=" * 80)
        print(f"Average Spread Confidence: {avg_spread_conf:.1f}%")
        print(f"Average Total Confidence: {avg_total_conf:.1f}%")
        print(f"Highest Spread Confidence: {max(p.spread_confidence for p in predictions):.1f}%")
        print(f"Highest Total Confidence: {max(p.total_confidence for p in predictions):.1f}%")
    
    # Find and display overvalue opportunities
    overvalue_predictions = analyzer.find_overvalue_spreads(games, min_value_threshold=2.5)
    
    print("\n" + "=" * 80)
    print("OVERVALUE SPREAD OPPORTUNITIES")
    print("=" * 80)
    print(f"Found {len(overvalue_predictions)} overvalue opportunities (≥2.5 point difference)")
    print()
    
    if overvalue_predictions:
        print("RECOMMENDED BETS (High confidence + significant value):")
        print("=" * 80)
        
        for i, pred in enumerate(overvalue_predictions, 1):
            print(f"\nOvervalue Bet #{i}:")
            print(pred)
    else:
        print("No overvalue opportunities found with current thresholds.")


if __name__ == "__main__":
    main()
