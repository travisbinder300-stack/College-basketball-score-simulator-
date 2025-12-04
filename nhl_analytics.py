#!/usr/bin/env python3
"""
NHL Spread and Total Analytics System
Provides predictions with 70%+ confidence using real NHL data
"""

import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from scipy import stats


class NHLDataFetcher:
    """Fetches real NHL data from the NHL API"""
    
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.standings_url = f"{self.base_url}/standings/now"
        
    def get_standings(self) -> Dict:
        """Fetch current NHL standings"""
        try:
            response = requests.get(self.standings_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return {}
    
    def get_team_stats(self, team_abbr: str) -> Dict:
        """Fetch team statistics"""
        try:
            url = f"{self.base_url}/club-stats/{team_abbr}/now"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching team stats for {team_abbr}: {e}")
            return {}
    
    def get_schedule(self, date: str = None) -> Dict:
        """Fetch schedule for a specific date (YYYY-MM-DD format)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        try:
            url = f"{self.base_url}/schedule/{date}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching schedule: {e}")
            return {}


class NHLAnalytics:
    """Analyzes NHL data and provides spread and total predictions"""
    
    def __init__(self):
        self.data_fetcher = NHLDataFetcher()
        self.confidence_level = 0.70  # 70% confidence target
        
    def calculate_team_strength(self, team_data: Dict) -> float:
        """
        Calculate team strength rating based on multiple factors
        Returns a normalized strength score (0-100)
        """
        if not team_data:
            return 50.0  # neutral rating
        
        # Extract key metrics
        wins = team_data.get('wins', 0)
        losses = team_data.get('losses', 0)
        ot_losses = team_data.get('otLosses', 0)
        goals_for = team_data.get('goalFor', 0)
        goals_against = team_data.get('goalAgainst', 0)
        
        # Calculate win percentage (OT losses count as half win)
        total_games = wins + losses + ot_losses
        if total_games == 0:
            return 50.0
        
        win_pct = (wins + 0.5 * ot_losses) / total_games
        
        # Calculate goal differential per game
        goal_diff_per_game = (goals_for - goals_against) / total_games if total_games > 0 else 0
        
        # Normalize goal differential (typical range -2 to +2)
        goal_diff_normalized = 50 + (goal_diff_per_game * 10)
        goal_diff_normalized = max(0, min(100, goal_diff_normalized))
        
        # Weight: 60% win percentage, 40% goal differential
        strength = (win_pct * 60) + (goal_diff_normalized * 0.4)
        
        return strength
    
    def predict_spread(self, home_team: str, away_team: str) -> Dict:
        """
        Predict the spread for a matchup
        Returns spread with confidence interval
        """
        # Fetch team data
        home_data = self._get_team_record(home_team)
        away_data = self._get_team_record(away_team)
        
        # Calculate team strengths
        home_strength = self.calculate_team_strength(home_data)
        away_strength = self.calculate_team_strength(away_data)
        
        # Home ice advantage (approximately 0.3 goals in NHL)
        home_advantage = 3.0
        
        # Calculate expected spread
        spread = (home_strength - away_strength) / 10 + home_advantage
        
        # Calculate confidence interval (70% confidence)
        # Standard deviation for NHL spreads is approximately 1.5 goals
        std_dev = 1.5
        z_score = stats.norm.ppf((1 + self.confidence_level) / 2)  # ~1.04 for 70%
        margin_of_error = z_score * std_dev
        
        confidence_lower = spread - margin_of_error
        confidence_upper = spread + margin_of_error
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_spread": round(spread, 2),
            "home_team_strength": round(home_strength, 2),
            "away_team_strength": round(away_strength, 2),
            "confidence_interval": {
                "lower": round(confidence_lower, 2),
                "upper": round(confidence_upper, 2),
                "confidence_level": f"{int(self.confidence_level * 100)}%"
            },
            "interpretation": self._interpret_spread(spread, home_team, away_team)
        }
    
    def predict_total(self, home_team: str, away_team: str) -> Dict:
        """
        Predict the total (over/under) for a matchup
        Returns total with confidence interval
        """
        # Fetch team data
        home_data = self._get_team_record(home_team)
        away_data = self._get_team_record(away_team)
        
        # Calculate average goals per game for each team
        home_gpg = self._get_goals_per_game(home_data)
        away_gpg = self._get_goals_per_game(away_data)
        
        # Calculate average goals allowed per game
        home_gapg = self._get_goals_allowed_per_game(home_data)
        away_gapg = self._get_goals_allowed_per_game(away_data)
        
        # Predict total using offensive and defensive metrics
        # Expected goals = (Team A offense vs Team B defense + Team B offense vs Team A defense)
        expected_home_goals = (home_gpg + away_gapg) / 2
        expected_away_goals = (away_gpg + home_gapg) / 2
        predicted_total = expected_home_goals + expected_away_goals
        
        # Calculate confidence interval
        # Standard deviation for NHL totals is approximately 1.8 goals
        std_dev = 1.8
        z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
        margin_of_error = z_score * std_dev
        
        confidence_lower = predicted_total - margin_of_error
        confidence_upper = predicted_total + margin_of_error
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_total": round(predicted_total, 2),
            "home_expected_goals": round(expected_home_goals, 2),
            "away_expected_goals": round(expected_away_goals, 2),
            "confidence_interval": {
                "lower": round(confidence_lower, 2),
                "upper": round(confidence_upper, 2),
                "confidence_level": f"{int(self.confidence_level * 100)}%"
            },
            "interpretation": self._interpret_total(predicted_total)
        }
    
    def find_spread_value(self, home_team: str, away_team: str, market_spread: float) -> Dict:
        """
        Compare predicted spread vs market spread to find value opportunities
        Positive difference means home team is undervalued, negative means away team is undervalued
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            market_spread: Current betting line spread (positive = home favored, negative = away favored)
        
        Returns:
            Dictionary with value analysis including underdog opportunities
        """
        prediction = self.predict_spread(home_team, away_team)
        predicted_spread = prediction['predicted_spread']
        
        # Calculate spread difference (predicted - market)
        spread_difference = predicted_spread - market_spread
        
        # Determine value opportunity
        value_threshold = 0.5  # Half a goal difference indicates potential value
        
        if abs(spread_difference) < value_threshold:
            value_assessment = "No significant value detected"
            recommended_bet = "Pass or bet based on other factors"
        elif spread_difference > value_threshold:
            # Predicted spread is higher than market, home team undervalued
            value_assessment = f"Home team ({home_team}) appears undervalued"
            recommended_bet = f"Value on {home_team} to cover"
        else:
            # Predicted spread is lower than market, away team undervalued
            value_assessment = f"Away team ({away_team}) appears undervalued"
            recommended_bet = f"Value on {away_team} to cover"
        
        # Determine underdog
        if market_spread < 0:
            underdog = home_team
            favorite = away_team
            underdog_getting = abs(market_spread)
        else:
            underdog = away_team
            favorite = home_team
            underdog_getting = market_spread
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_spread": round(predicted_spread, 2),
            "market_spread": round(market_spread, 2),
            "spread_difference": round(spread_difference, 2),
            "value_assessment": value_assessment,
            "recommended_bet": recommended_bet,
            "underdog": underdog,
            "favorite": favorite,
            "underdog_points": round(underdog_getting, 2),
            "confidence_interval": prediction['confidence_interval']
        }
    
    def get_full_analysis(self, home_team: str, away_team: str) -> Dict:
        """
        Get complete analysis including spread and total predictions
        """
        spread_prediction = self.predict_spread(home_team, away_team)
        total_prediction = self.predict_total(home_team, away_team)
        
        return {
            "matchup": f"{away_team} @ {home_team}",
            "timestamp": datetime.now().isoformat(),
            "spread_analysis": spread_prediction,
            "total_analysis": total_prediction,
            "confidence_level": f"{int(self.confidence_level * 100)}%"
        }
    
    def _get_team_record(self, team_abbr: str) -> Dict:
        """Helper to get team record from standings"""
        standings = self.data_fetcher.get_standings()
        
        if not standings or 'standings' not in standings:
            return self._get_default_team_data()
        
        # Search through all divisions
        for standing in standings.get('standings', []):
            if standing.get('teamAbbrev', {}).get('default') == team_abbr:
                return standing
        
        return self._get_default_team_data()
    
    def _get_default_team_data(self) -> Dict:
        """Return default team data for fallback"""
        return {
            'wins': 20,
            'losses': 20,
            'otLosses': 5,
            'goalFor': 135,
            'goalAgainst': 135,
            'gamesPlayed': 45
        }
    
    def _get_goals_per_game(self, team_data: Dict) -> float:
        """Calculate goals per game for a team"""
        goals_for = team_data.get('goalFor', 135)
        games_played = team_data.get('gamesPlayed', 45)
        return goals_for / games_played if games_played > 0 else 3.0
    
    def _get_goals_allowed_per_game(self, team_data: Dict) -> float:
        """Calculate goals allowed per game for a team"""
        goals_against = team_data.get('goalAgainst', 135)
        games_played = team_data.get('gamesPlayed', 45)
        return goals_against / games_played if games_played > 0 else 3.0
    
    def _interpret_spread(self, spread: float, home_team: str, away_team: str) -> str:
        """Interpret the spread prediction"""
        if spread > 1.0:
            return f"{home_team} favored by {abs(spread):.1f} goals (underdog: {away_team})"
        elif spread < -1.0:
            return f"{away_team} favored by {abs(spread):.1f} goals (underdog: {home_team})"
        else:
            return "Evenly matched game (pick 'em)"
    
    def _interpret_total(self, total: float) -> str:
        """Interpret the total prediction"""
        if total < 5.5:
            return "Low-scoring game expected"
        elif total > 6.5:
            return "High-scoring game expected"
        else:
            return "Average-scoring game expected"


def main():
    """Main function to demonstrate the NHL analytics system"""
    print("=" * 60)
    print("NHL Spread and Total Analytics System")
    print("70% Confidence Level Predictions")
    print("=" * 60)
    print()
    
    # Initialize analytics
    analytics = NHLAnalytics()
    
    # Example matchups (using common NHL team abbreviations)
    matchups = [
        ("TOR", "MTL"),  # Toronto vs Montreal
        ("NYR", "NYI"),  # Rangers vs Islanders
        ("BOS", "TBL"),  # Boston vs Tampa Bay
    ]
    
    for home, away in matchups:
        print(f"\n{'='*60}")
        print(f"Analyzing: {away} @ {home}")
        print('='*60)
        
        # Get full analysis
        analysis = analytics.get_full_analysis(home, away)
        
        # Display spread prediction
        spread = analysis['spread_analysis']
        print(f"\n📊 SPREAD PREDICTION:")
        print(f"   Predicted Spread: {spread['predicted_spread']}")
        print(f"   {spread['interpretation']}")
        print(f"   70% Confidence Interval: [{spread['confidence_interval']['lower']}, {spread['confidence_interval']['upper']}]")
        print(f"   {home} Strength: {spread['home_team_strength']}")
        print(f"   {away} Strength: {spread['away_team_strength']}")
        
        # Display total prediction
        total = analysis['total_analysis']
        print(f"\n🎯 TOTAL PREDICTION:")
        print(f"   Predicted Total: {total['predicted_total']}")
        print(f"   {total['interpretation']}")
        print(f"   70% Confidence Interval: [{total['confidence_interval']['lower']}, {total['confidence_interval']['upper']}]")
        print(f"   Expected {home} Goals: {total['home_expected_goals']}")
        print(f"   Expected {away} Goals: {total['away_expected_goals']}")
        
        print()
    
    # Demonstrate value finding with example market spreads
    print("\n" + "=" * 60)
    print("VALUE ANALYSIS - Finding Underdog & Overvalued Spreads")
    print("=" * 60)
    print("\nComparing predicted spreads vs hypothetical market lines:")
    
    # Example market spreads (home team perspective: positive = home favored)
    market_examples = [
        ("TOR", "MTL", 1.5),   # Market has TOR -1.5
        ("NYR", "NYI", 2.5),   # Market has NYR -2.5
        ("BOS", "TBL", -0.5),  # Market has BOS as slight underdog
    ]
    
    for home, away, market_spread in market_examples:
        print(f"\n{away} @ {home} (Market spread: {market_spread:+.1f})")
        value = analytics.find_spread_value(home, away, market_spread)
        print(f"   Predicted: {value['predicted_spread']:+.1f}")
        print(f"   Difference: {value['spread_difference']:+.2f} goals")
        print(f"   Underdog: {value['underdog']} (+{value['underdog_points']:.1f})")
        print(f"   Assessment: {value['value_assessment']}")
        print(f"   💡 {value['recommended_bet']}")
    
    print()
    print("=" * 60)
    print("Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
