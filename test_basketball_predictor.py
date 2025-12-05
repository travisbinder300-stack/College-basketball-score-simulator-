#!/usr/bin/env python3
"""
Tests for Basketball Predictor
"""

import unittest
import os
from basketball_predictor import (
    TeamStats, 
    BasketballPredictor, 
    GamePrediction,
    load_team_data
)


class TestTeamStats(unittest.TestCase):
    """Test TeamStats dataclass"""
    
    def test_valid_team_stats(self):
        """Test creating valid team statistics"""
        team = TeamStats(
            name="Duke",
            offensive_efficiency=115.0,
            defensive_efficiency=92.0,
            tempo=71.0
        )
        self.assertEqual(team.name, "Duke")
        self.assertEqual(team.offensive_efficiency, 115.0)
        self.assertEqual(team.defensive_efficiency, 92.0)
        self.assertEqual(team.tempo, 71.0)
    
    def test_invalid_offensive_efficiency(self):
        """Test that negative offensive efficiency raises error"""
        with self.assertRaises(ValueError):
            TeamStats(
                name="Test",
                offensive_efficiency=-10.0,
                defensive_efficiency=92.0,
                tempo=71.0
            )
    
    def test_invalid_defensive_efficiency(self):
        """Test that negative defensive efficiency raises error"""
        with self.assertRaises(ValueError):
            TeamStats(
                name="Test",
                offensive_efficiency=115.0,
                defensive_efficiency=-5.0,
                tempo=71.0
            )
    
    def test_invalid_tempo(self):
        """Test that negative tempo raises error"""
        with self.assertRaises(ValueError):
            TeamStats(
                name="Test",
                offensive_efficiency=115.0,
                defensive_efficiency=92.0,
                tempo=-1.0
            )


class TestBasketballPredictor(unittest.TestCase):
    """Test BasketballPredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = BasketballPredictor()
        self.home_team = TeamStats(
            name="Duke",
            offensive_efficiency=115.0,
            defensive_efficiency=92.0,
            tempo=71.0
        )
        self.away_team = TeamStats(
            name="North Carolina",
            offensive_efficiency=112.0,
            defensive_efficiency=94.0,
            tempo=73.0
        )
    
    def test_predict_game_basic(self):
        """Test basic game prediction"""
        prediction = self.predictor.predict_game(
            self.home_team,
            self.away_team
        )
        
        self.assertEqual(prediction.home_team, "Duke")
        self.assertEqual(prediction.away_team, "North Carolina")
        self.assertGreater(prediction.predicted_home_score, 0)
        self.assertGreater(prediction.predicted_away_score, 0)
        self.assertGreater(prediction.total_points, 0)
        self.assertGreaterEqual(prediction.home_win_probability, 0)
        self.assertLessEqual(prediction.home_win_probability, 1)
    
    def test_home_court_advantage(self):
        """Test that home court advantage affects scores"""
        home_prediction = self.predictor.predict_game(
            self.home_team,
            self.away_team,
            neutral_site=False
        )
        neutral_prediction = self.predictor.predict_game(
            self.home_team,
            self.away_team,
            neutral_site=True
        )
        
        # Home team should score more at home than at neutral site
        self.assertGreater(
            home_prediction.predicted_home_score,
            neutral_prediction.predicted_home_score
        )
        
        # Point spread should favor home team more at home
        self.assertGreater(
            home_prediction.point_spread,
            neutral_prediction.point_spread
        )
    
    def test_predict_from_spread_and_total(self):
        """Test prediction from spread and total"""
        prediction = self.predictor.predict_from_spread_and_total(
            home_team_name="Duke",
            away_team_name="North Carolina",
            point_spread=5.0,
            total_points=150.0
        )
        
        self.assertEqual(prediction.home_team, "Duke")
        self.assertEqual(prediction.away_team, "North Carolina")
        self.assertEqual(prediction.point_spread, 5.0)
        self.assertEqual(prediction.total_points, 150.0)
        
        # Verify math: home_score = (total + spread) / 2
        expected_home = (150.0 + 5.0) / 2
        expected_away = (150.0 - 5.0) / 2
        self.assertAlmostEqual(prediction.predicted_home_score, expected_home)
        self.assertAlmostEqual(prediction.predicted_away_score, expected_away)
        
        # Verify scores sum to total
        self.assertAlmostEqual(
            prediction.predicted_home_score + prediction.predicted_away_score,
            150.0
        )
    
    def test_spread_calculation(self):
        """Test that spread calculation is consistent"""
        prediction = self.predictor.predict_from_spread_and_total(
            "Team A", "Team B", 7.5, 140.0
        )
        
        calculated_spread = (
            prediction.predicted_home_score - prediction.predicted_away_score
        )
        self.assertAlmostEqual(calculated_spread, 7.5)
    
    def test_win_probability_spread_relationship(self):
        """Test that higher spread means higher win probability"""
        pred1 = self.predictor.predict_from_spread_and_total(
            "Team A", "Team B", 10.0, 150.0
        )
        pred2 = self.predictor.predict_from_spread_and_total(
            "Team A", "Team B", 5.0, 150.0
        )
        pred3 = self.predictor.predict_from_spread_and_total(
            "Team A", "Team B", -3.0, 150.0
        )
        
        # Larger positive spread = higher home win probability
        self.assertGreater(pred1.home_win_probability, pred2.home_win_probability)
        self.assertGreater(pred2.home_win_probability, pred3.home_win_probability)
    
    def test_simulate_game(self):
        """Test Monte Carlo simulation"""
        prediction = self.predictor.predict_from_spread_and_total(
            "Duke", "UNC", 5.0, 150.0
        )
        
        results = self.predictor.simulate_game(prediction, num_simulations=100)
        
        self.assertIn('home_win_pct', results)
        self.assertIn('away_win_pct', results)
        self.assertIn('avg_home_score', results)
        self.assertIn('avg_away_score', results)
        
        # Win percentages should sum to 1
        self.assertAlmostEqual(
            results['home_win_pct'] + results['away_win_pct'],
            1.0,
            places=5
        )
        
        # Average scores should be close to predicted scores
        self.assertAlmostEqual(
            results['avg_home_score'],
            prediction.predicted_home_score,
            delta=5.0
        )


class TestLoadTeamData(unittest.TestCase):
    """Test loading team data from JSON"""
    
    def test_load_example_teams(self):
        """Test loading the example teams file"""
        # Check if example_teams.json exists
        filepath = 'example_teams.json'
        if not os.path.exists(filepath):
            self.skipTest("example_teams.json not found")
        
        teams = load_team_data(filepath)
        
        self.assertIsInstance(teams, dict)
        self.assertGreater(len(teams), 0)
        
        # Check that all teams are TeamStats objects
        for team_name, team_stats in teams.items():
            self.assertIsInstance(team_stats, TeamStats)
            self.assertEqual(team_stats.name, team_name)
            self.assertGreater(team_stats.offensive_efficiency, 0)
            self.assertGreater(team_stats.defensive_efficiency, 0)
            self.assertGreater(team_stats.tempo, 0)


class TestGamePrediction(unittest.TestCase):
    """Test GamePrediction output formatting"""
    
    def test_prediction_str_format(self):
        """Test that prediction formats correctly"""
        prediction = GamePrediction(
            home_team="Duke",
            away_team="UNC",
            predicted_home_score=77.5,
            predicted_away_score=72.5,
            point_spread=5.0,
            total_points=150.0,
            home_win_probability=0.65
        )
        
        output = str(prediction)
        self.assertIn("Duke", output)
        self.assertIn("UNC", output)
        self.assertIn("77.5", output)
        self.assertIn("72.5", output)


if __name__ == '__main__':
    unittest.main()
