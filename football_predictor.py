#!/usr/bin/env python3
"""
College Football Score Prediction System
Uses FEI (Fremeau Efficiency Index) methodology to predict game outcomes including spread and total
"""

import json
import math
from typing import Dict, Tuple


class FootballPredictor:
    """
    Predicts college football game scores using efficiency metrics similar to FEI
    """
    
    # Constants for prediction calculations
    HOME_FIELD_ADVANTAGE = 3  # Points added for home team
    MIN_EFFICIENCY = 0.01  # Minimum efficiency value to prevent division by zero
    BASE_CONFIDENCE = 50  # Base confidence percentage
    MAX_CONFIDENCE = 95  # Maximum confidence percentage
    CONFIDENCE_MULTIPLIER = 100  # Multiplier for FEI difference in confidence calculation
    
    def __init__(self):
        # Sample FEI-style data (2022 season metrics)
        # FEI represents team efficiency on a scale where higher is better
        # OFEI = Offensive Efficiency, DFEI = Defensive Efficiency
        self.team_data = {
            "Georgia": {
                "fei": 0.825,
                "ofei": 0.780,
                "dfei": 0.870,
                "avg_points": 38.2,
                "avg_allowed": 12.8
            },
            "Ohio State": {
                "fei": 0.810,
                "ofei": 0.850,
                "dfei": 0.770,
                "avg_points": 44.0,
                "avg_allowed": 19.5
            },
            "Michigan": {
                "fei": 0.795,
                "ofei": 0.760,
                "dfei": 0.830,
                "avg_points": 35.4,
                "avg_allowed": 15.2
            },
            "TCU": {
                "fei": 0.720,
                "ofei": 0.710,
                "dfei": 0.730,
                "avg_points": 32.8,
                "avg_allowed": 24.3
            },
            "Alabama": {
                "fei": 0.800,
                "ofei": 0.820,
                "dfei": 0.780,
                "avg_points": 37.5,
                "avg_allowed": 18.7
            },
            "Tennessee": {
                "fei": 0.775,
                "ofei": 0.800,
                "dfei": 0.750,
                "avg_points": 41.2,
                "avg_allowed": 22.4
            },
            "Penn State": {
                "fei": 0.755,
                "ofei": 0.740,
                "dfei": 0.770,
                "avg_points": 31.9,
                "avg_allowed": 17.8
            },
            "Clemson": {
                "fei": 0.745,
                "ofei": 0.720,
                "dfei": 0.770,
                "avg_points": 33.5,
                "avg_allowed": 19.2
            },
            "USC": {
                "fei": 0.740,
                "ofei": 0.770,
                "dfei": 0.710,
                "avg_points": 38.8,
                "avg_allowed": 25.6
            },
            "Kansas State": {
                "fei": 0.715,
                "ofei": 0.690,
                "dfei": 0.740,
                "avg_points": 31.2,
                "avg_allowed": 21.5
            }
        }
    
    def _calculate_team_score(self, offensive_factor: float, defensive_factor: float, base_score: float) -> float:
        """
        Calculate predicted score for a team based on offensive/defensive matchup
        
        Args:
            offensive_factor: Team's offensive efficiency
            defensive_factor: Opponent's defensive efficiency
            base_score: Team's average points per game
            
        Returns:
            Predicted raw score before home field adjustment
        """
        safe_defensive_factor = max(defensive_factor, self.MIN_EFFICIENCY)
        return base_score * (offensive_factor / safe_defensive_factor)
    
    def predict_game(self, team1: str, team2: str, neutral_site: bool = False) -> Dict:
        """
        Predict the outcome of a game between two teams
        
        Args:
            team1: Home team (or Team 1 if neutral site)
            team2: Away team (or Team 2 if neutral site)
            neutral_site: Whether the game is at a neutral site
            
        Returns:
            Dictionary with prediction results including winner, scores, spread, and total
        """
        if team1 not in self.team_data or team2 not in self.team_data:
            return {"error": f"Team data not found for {team1} or {team2}"}
        
        t1_data = self.team_data[team1]
        t2_data = self.team_data[team2]
        
        # Home field advantage
        home_advantage = 0 if neutral_site else self.HOME_FIELD_ADVANTAGE
        
        # Calculate expected scores based on offensive efficiency vs defensive efficiency
        team1_score = self._calculate_team_score(
            t1_data["ofei"], 
            t2_data["dfei"], 
            t1_data["avg_points"]
        ) + home_advantage
        
        team2_score = self._calculate_team_score(
            t2_data["ofei"],
            t1_data["dfei"],
            t2_data["avg_points"]
        )
        
        # Round to nearest 0.5 for realistic scores
        team1_final = round(team1_score * 2) / 2
        team2_final = round(team2_score * 2) / 2
        
        # Calculate spread (negative means team1 is favored)
        spread = team2_final - team1_final
        
        # Calculate total points
        total = team1_final + team2_final
        
        # Determine winner
        if team1_final > team2_final:
            winner = team1
            margin = team1_final - team2_final
        elif team2_final > team1_final:
            winner = team2
            margin = team2_final - team1_final
        else:
            winner = "TIE"
            margin = 0
        
        # Calculate confidence based on FEI difference
        fei_diff = abs(t1_data["fei"] - t2_data["fei"])
        confidence = min(self.MAX_CONFIDENCE, self.BASE_CONFIDENCE + (fei_diff * self.CONFIDENCE_MULTIPLIER))
        
        return {
            "matchup": f"{team1} vs {team2}",
            "location": "Neutral Site" if neutral_site else f"{team1} (Home)",
            "predicted_winner": winner,
            "predicted_scores": {
                team1: team1_final,
                team2: team2_final
            },
            "margin_of_victory": round(margin, 1),
            "spread": round(spread, 1),
            "total_points": round(total, 1),
            "confidence": round(confidence, 1),
            "team_names": {
                "team1": team1,
                "team2": team2
            },
            "team_efficiency": {
                team1: {
                    "fei": t1_data["fei"],
                    "ofei": t1_data["ofei"],
                    "dfei": t1_data["dfei"]
                },
                team2: {
                    "fei": t2_data["fei"],
                    "ofei": t2_data["ofei"],
                    "dfei": t2_data["dfei"]
                }
            }
        }
    
    def get_available_teams(self):
        """Return list of teams with data available"""
        return sorted(list(self.team_data.keys()))
    
    def display_prediction(self, prediction: Dict):
        """Pretty print a prediction"""
        if "error" in prediction:
            print(f"Error: {prediction['error']}")
            return
        
        print("\n" + "="*60)
        print(f"COLLEGE FOOTBALL GAME PREDICTION")
        print("="*60)
        print(f"\nMatchup: {prediction['matchup']}")
        print(f"Location: {prediction['location']}")
        print(f"\nPredicted Winner: {prediction['predicted_winner']}")
        print(f"Margin of Victory: {prediction['margin_of_victory']} points")
        print(f"\nPredicted Scores:")
        for team, score in prediction['predicted_scores'].items():
            print(f"  {team}: {score}")
        print(f"\nBetting Lines:")
        print(f"  Spread: {prediction['spread']} (negative means {prediction['team_names']['team1']} favored)")
        print(f"  Total (Over/Under): {prediction['total_points']}")
        print(f"\nConfidence: {prediction['confidence']}%")
        print(f"\nTeam Efficiency Metrics (FEI):")
        for team, metrics in prediction['team_efficiency'].items():
            print(f"  {team}:")
            print(f"    Overall FEI: {metrics['fei']:.3f}")
            print(f"    Offensive FEI: {metrics['ofei']:.3f}")
            print(f"    Defensive FEI: {metrics['dfei']:.3f}")
        print("="*60 + "\n")


def main():
    """Main function to demonstrate the prediction system"""
    predictor = FootballPredictor()
    
    print("College Football Score Prediction System")
    print("Using FEI (Fremeau Efficiency Index) Methodology")
    print("\nAvailable Teams:", ", ".join(predictor.get_available_teams()))
    
    # Example predictions
    print("\n" + "="*60)
    print("EXAMPLE PREDICTIONS")
    print("="*60)
    
    # Example 1: Georgia vs Ohio State (neutral site - playoff scenario)
    prediction1 = predictor.predict_game("Georgia", "Ohio State", neutral_site=True)
    predictor.display_prediction(prediction1)
    
    # Example 2: Michigan vs Alabama (neutral site)
    prediction2 = predictor.predict_game("Michigan", "Alabama", neutral_site=True)
    predictor.display_prediction(prediction2)
    
    # Example 3: Tennessee at Georgia (home game)
    prediction3 = predictor.predict_game("Georgia", "Tennessee", neutral_site=False)
    predictor.display_prediction(prediction3)
    
    # Interactive mode
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nEnter team matchups to get predictions")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            team1 = input("Enter home team (or first team): ").strip()
            if team1.lower() == 'quit':
                break
            
            team2 = input("Enter away team (or second team): ").strip()
            if team2.lower() == 'quit':
                break
            
            neutral = input("Neutral site? (y/n): ").strip().lower() == 'y'
            
            prediction = predictor.predict_game(team1, team2, neutral)
            predictor.display_prediction(prediction)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
