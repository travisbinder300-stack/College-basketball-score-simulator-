#!/usr/bin/env python3
"""
College Football Score Prediction System
Uses FEI (Fremeau Efficiency Index) methodology to predict game outcomes including spread and total
"""

import json
import math
import random
from typing import Dict, Tuple, List


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
    
    # Constants for Monte Carlo simulation
    DEFAULT_SIMULATIONS = 10000  # Number of simulations to run (Haralabos Voulgaris style)
    SCORE_VARIANCE = 7.0  # Standard deviation for score variance in simulations
    SCORE_RANGE_SIZE = 7  # Size of score ranges for distribution grouping (e.g., 0-6, 7-13, etc.)
    
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
    
    def simulate_game(self, team1: str, team2: str, neutral_site: bool = False, num_simulations: int = None) -> Dict:
        """
        Run Monte Carlo simulations for a game (Haralabos Voulgaris style)
        
        Args:
            team1: Home team (or Team 1 if neutral site)
            team2: Away team (or Team 2 if neutral site)
            neutral_site: Whether the game is at a neutral site
            num_simulations: Number of simulations to run (default: 10,000)
            
        Returns:
            Dictionary with simulation results including win probabilities, score distributions, 
            spread coverage, and over/under percentages
        """
        if num_simulations is None:
            num_simulations = self.DEFAULT_SIMULATIONS
            
        if team1 not in self.team_data or team2 not in self.team_data:
            return {"error": f"Team data not found for {team1} or {team2}"}
        
        # Get base prediction
        base_prediction = self.predict_game(team1, team2, neutral_site)
        if "error" in base_prediction:
            return base_prediction
        
        # Extract base predicted scores
        base_team1_score = base_prediction["predicted_scores"][team1]
        base_team2_score = base_prediction["predicted_scores"][team2]
        
        # Run simulations
        team1_wins = 0
        team2_wins = 0
        ties = 0
        team1_scores = []
        team2_scores = []
        margins = []
        totals = []
        
        for _ in range(num_simulations):
            # Add variance using normal distribution
            sim_team1_score = random.gauss(base_team1_score, self.SCORE_VARIANCE)
            sim_team2_score = random.gauss(base_team2_score, self.SCORE_VARIANCE)
            
            # Ensure non-negative scores
            sim_team1_score = max(0, sim_team1_score)
            sim_team2_score = max(0, sim_team2_score)
            
            # Record results
            team1_scores.append(sim_team1_score)
            team2_scores.append(sim_team2_score)
            
            # Determine winner
            if sim_team1_score > sim_team2_score:
                team1_wins += 1
                margin = sim_team1_score - sim_team2_score
            elif sim_team2_score > sim_team1_score:
                team2_wins += 1
                margin = sim_team2_score - sim_team1_score
            else:
                ties += 1
                margin = 0
            
            margins.append(margin)
            totals.append(sim_team1_score + sim_team2_score)
        
        # Calculate statistics
        team1_win_pct = (team1_wins / num_simulations) * 100
        team2_win_pct = (team2_wins / num_simulations) * 100
        tie_pct = (ties / num_simulations) * 100
        
        avg_team1_score = sum(team1_scores) / num_simulations
        avg_team2_score = sum(team2_scores) / num_simulations
        avg_margin = sum(margins) / num_simulations
        avg_total = sum(totals) / num_simulations
        
        # Calculate spread coverage (using base prediction spread)
        # Convention: spread is team2_score - team1_score
        # Negative spread means team1 is favored
        # team1 covers if actual margin beats the spread
        spread = base_prediction["spread"]
        team1_covers = sum(1 for i in range(num_simulations) 
                          if (team2_scores[i] - team1_scores[i]) < spread)
        spread_cover_pct = (team1_covers / num_simulations) * 100
        
        # Calculate over/under (using base prediction total)
        predicted_total = base_prediction["total_points"]
        overs = sum(1 for t in totals if t > predicted_total)
        over_pct = (overs / num_simulations) * 100
        under_pct = 100 - over_pct
        
        # Score distribution (group by ranges for readability)
        def get_score_distribution(scores):
            ranges = {}
            for score in scores:
                range_key = int(score // self.SCORE_RANGE_SIZE) * self.SCORE_RANGE_SIZE
                range_label = f"{range_key}-{range_key + self.SCORE_RANGE_SIZE - 1}"
                ranges[range_label] = ranges.get(range_label, 0) + 1
            # Convert to percentages and sort
            total = len(scores)
            return {k: round((v/total)*100, 1) for k, v in sorted(ranges.items(), 
                   key=lambda x: int(x[0].split('-')[0]))}
        
        return {
            "matchup": f"{team1} vs {team2}",
            "team_names": {
                "team1": team1,
                "team2": team2
            },
            "simulations_run": num_simulations,
            "base_prediction": base_prediction,
            "win_probabilities": {
                team1: round(team1_win_pct, 2),
                team2: round(team2_win_pct, 2),
                "tie": round(tie_pct, 2)
            },
            "average_scores": {
                team1: round(avg_team1_score, 1),
                team2: round(avg_team2_score, 1)
            },
            "average_margin": round(avg_margin, 1),
            "average_total": round(avg_total, 1),
            "spread_analysis": {
                "predicted_spread": round(spread, 1),
                f"{team1}_covers_spread_pct": round(spread_cover_pct, 1),
                f"{team2}_covers_spread_pct": round(100 - spread_cover_pct, 1)
            },
            "over_under_analysis": {
                "predicted_total": round(predicted_total, 1),
                "over_pct": round(over_pct, 1),
                "under_pct": round(under_pct, 1)
            },
            "score_distributions": {
                team1: get_score_distribution(team1_scores),
                team2: get_score_distribution(team2_scores)
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
    
    def display_simulation(self, simulation: Dict):
        """Pretty print simulation results"""
        if "error" in simulation:
            print(f"Error: {simulation['error']}")
            return
        
        print("\n" + "="*70)
        print(f"MONTE CARLO SIMULATION RESULTS (Haralabos Voulgaris Style)")
        print("="*70)
        print(f"\nMatchup: {simulation['matchup']}")
        print(f"Simulations Run: {simulation['simulations_run']:,}")
        
        print(f"\n{'WIN PROBABILITIES':^70}")
        print("-"*70)
        for team, prob in simulation['win_probabilities'].items():
            if team != 'tie':
                print(f"  {team}: {prob}%")
        if simulation['win_probabilities']['tie'] > 0:
            print(f"  Tie: {simulation['win_probabilities']['tie']}%")
        
        print(f"\n{'AVERAGE SIMULATED SCORES':^70}")
        print("-"*70)
        for team, score in simulation['average_scores'].items():
            print(f"  {team}: {score}")
        print(f"  Average Margin: {simulation['average_margin']} points")
        print(f"  Average Total: {simulation['average_total']} points")
        
        print(f"\n{'SPREAD ANALYSIS':^70}")
        print("-"*70)
        print(f"  Predicted Spread: {simulation['spread_analysis']['predicted_spread']}")
        team1_name = simulation['team_names']['team1']
        team2_name = simulation['team_names']['team2']
        print(f"  {team1_name} covers: {simulation['spread_analysis'][f'{team1_name}_covers_spread_pct']}%")
        print(f"  {team2_name} covers: {simulation['spread_analysis'][f'{team2_name}_covers_spread_pct']}%")
        
        print(f"\n{'OVER/UNDER ANALYSIS':^70}")
        print("-"*70)
        print(f"  Predicted Total: {simulation['over_under_analysis']['predicted_total']}")
        print(f"  Over hits: {simulation['over_under_analysis']['over_pct']}%")
        print(f"  Under hits: {simulation['over_under_analysis']['under_pct']}%")
        
        print(f"\n{'SCORE DISTRIBUTION (Top 5 ranges for each team)':^70}")
        print("-"*70)
        for team, distribution in simulation['score_distributions'].items():
            print(f"\n  {team}:")
            # Show top 5 most common score ranges
            sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:5]
            for score_range, pct in sorted_dist:
                print(f"    {score_range} points: {pct}%")
        
        print("\n" + "="*70 + "\n")


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
    
    # Monte Carlo Simulation Examples
    print("\n" + "="*70)
    print("MONTE CARLO SIMULATIONS (10,000 runs - Haralabos Voulgaris Style)")
    print("="*70)
    print("\nRunning 10,000 simulations for key matchups...")
    print("This adds variance to predictions and shows probability distributions.\n")
    
    # Simulation Example 1: Georgia vs Ohio State
    print("Simulating: Georgia vs Ohio State (Neutral Site)...")
    sim1 = predictor.simulate_game("Georgia", "Ohio State", neutral_site=True)
    predictor.display_simulation(sim1)
    
    # Simulation Example 2: Alabama vs Georgia
    print("Simulating: Alabama vs Georgia (Home game)...")
    sim2 = predictor.simulate_game("Alabama", "Georgia", neutral_site=False)
    predictor.display_simulation(sim2)
    
    # Interactive mode
    print("\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("\nEnter team matchups to get predictions or simulations")
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
            
            mode = input("Run simulation? (y/n, default=n): ").strip().lower()
            
            if mode == 'y':
                print("\nRunning 10,000 simulations...")
                simulation = predictor.simulate_game(team1, team2, neutral)
                predictor.display_simulation(simulation)
            else:
                prediction = predictor.predict_game(team1, team2, neutral)
                predictor.display_prediction(prediction)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
