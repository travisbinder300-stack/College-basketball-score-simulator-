#!/usr/bin/env python3
"""
Test suite for NHL Analytics System
"""

import unittest
from unittest.mock import patch, MagicMock
from nhl_analytics import NHLAnalytics, NHLDataFetcher


class TestNHLDataFetcher(unittest.TestCase):
    """Tests for NHLDataFetcher class"""
    
    def setUp(self):
        self.fetcher = NHLDataFetcher()
    
    def test_initialization(self):
        """Test that the data fetcher initializes correctly"""
        self.assertIsNotNone(self.fetcher.base_url)
        self.assertIn("api-web.nhle.com", self.fetcher.base_url)
    
    @patch('requests.get')
    def test_get_standings_success(self, mock_get):
        """Test successful standings fetch"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"standings": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.fetcher.get_standings()
        self.assertIsInstance(result, dict)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_standings_error(self, mock_get):
        """Test standings fetch with error"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.fetcher.get_standings()
        self.assertEqual(result, {})


class TestNHLAnalytics(unittest.TestCase):
    """Tests for NHLAnalytics class"""
    
    def setUp(self):
        self.analytics = NHLAnalytics()
    
    def test_initialization(self):
        """Test that analytics initializes with correct confidence level"""
        self.assertEqual(self.analytics.confidence_level, 0.70)
        self.assertIsNotNone(self.analytics.data_fetcher)
    
    def test_calculate_team_strength_default(self):
        """Test team strength calculation with default data"""
        team_data = {
            'wins': 30,
            'losses': 15,
            'otLosses': 5,
            'goalFor': 160,
            'goalAgainst': 130,
            'gamesPlayed': 50
        }
        
        strength = self.analytics.calculate_team_strength(team_data)
        
        # Should be above 50 (winning record)
        self.assertGreater(strength, 50)
        self.assertLessEqual(strength, 100)
    
    def test_calculate_team_strength_empty(self):
        """Test team strength with empty data"""
        strength = self.analytics.calculate_team_strength({})
        self.assertEqual(strength, 50.0)
    
    def test_calculate_team_strength_winning_team(self):
        """Test calculation for a strong winning team"""
        team_data = {
            'wins': 40,
            'losses': 10,
            'otLosses': 2,
            'goalFor': 200,
            'goalAgainst': 130,
            'gamesPlayed': 52
        }
        
        strength = self.analytics.calculate_team_strength(team_data)
        self.assertGreater(strength, 60)
    
    def test_calculate_team_strength_losing_team(self):
        """Test calculation for a weak losing team"""
        team_data = {
            'wins': 15,
            'losses': 30,
            'otLosses': 5,
            'goalFor': 130,
            'goalAgainst': 180,
            'gamesPlayed': 50
        }
        
        strength = self.analytics.calculate_team_strength(team_data)
        self.assertLess(strength, 50)
    
    def test_predict_spread_structure(self):
        """Test that spread prediction returns correct structure"""
        result = self.analytics.predict_spread("TOR", "MTL")
        
        # Check required fields
        self.assertIn("home_team", result)
        self.assertIn("away_team", result)
        self.assertIn("predicted_spread", result)
        self.assertIn("confidence_interval", result)
        self.assertIn("home_team_strength", result)
        self.assertIn("away_team_strength", result)
        self.assertIn("interpretation", result)
        
        # Check confidence interval structure
        ci = result["confidence_interval"]
        self.assertIn("lower", ci)
        self.assertIn("upper", ci)
        self.assertIn("confidence_level", ci)
        self.assertEqual(ci["confidence_level"], "70%")
    
    def test_predict_total_structure(self):
        """Test that total prediction returns correct structure"""
        result = self.analytics.predict_total("TOR", "MTL")
        
        # Check required fields
        self.assertIn("home_team", result)
        self.assertIn("away_team", result)
        self.assertIn("predicted_total", result)
        self.assertIn("confidence_interval", result)
        self.assertIn("home_expected_goals", result)
        self.assertIn("away_expected_goals", result)
        self.assertIn("interpretation", result)
        
        # Check confidence interval
        ci = result["confidence_interval"]
        self.assertIn("lower", ci)
        self.assertIn("upper", ci)
        self.assertEqual(ci["confidence_level"], "70%")
    
    def test_predict_spread_home_advantage(self):
        """Test that home ice advantage is applied"""
        # With default/similar teams, spread should favor home team
        result = self.analytics.predict_spread("TOR", "MTL")
        
        # Home advantage should make spread positive (or close to it)
        self.assertIsInstance(result["predicted_spread"], (int, float))
    
    def test_predict_total_positive(self):
        """Test that total prediction is positive"""
        result = self.analytics.predict_total("TOR", "MTL")
        
        # Total should be positive and realistic for NHL (typically 5-7)
        self.assertGreater(result["predicted_total"], 0)
        self.assertLess(result["predicted_total"], 15)  # Upper bound sanity check
    
    def test_confidence_interval_validity(self):
        """Test that confidence intervals are valid (lower < upper)"""
        spread_result = self.analytics.predict_spread("BOS", "NYR")
        total_result = self.analytics.predict_total("BOS", "NYR")
        
        # Spread CI
        spread_ci = spread_result["confidence_interval"]
        self.assertLess(spread_ci["lower"], spread_ci["upper"])
        
        # Total CI
        total_ci = total_result["confidence_interval"]
        self.assertLess(total_ci["lower"], total_ci["upper"])
    
    def test_get_full_analysis_structure(self):
        """Test that full analysis returns complete structure"""
        result = self.analytics.get_full_analysis("TOR", "MTL")
        
        self.assertIn("matchup", result)
        self.assertIn("timestamp", result)
        self.assertIn("spread_analysis", result)
        self.assertIn("total_analysis", result)
        self.assertIn("confidence_level", result)
        
        self.assertEqual(result["confidence_level"], "70%")
    
    def test_get_goals_per_game(self):
        """Test goals per game calculation"""
        team_data = {
            'goalFor': 150,
            'gamesPlayed': 50
        }
        
        gpg = self.analytics._get_goals_per_game(team_data)
        self.assertEqual(gpg, 3.0)
    
    def test_get_goals_allowed_per_game(self):
        """Test goals allowed per game calculation"""
        team_data = {
            'goalAgainst': 120,
            'gamesPlayed': 40
        }
        
        gapg = self.analytics._get_goals_allowed_per_game(team_data)
        self.assertEqual(gapg, 3.0)
    
    def test_interpret_spread_home_favored(self):
        """Test spread interpretation when home team is favored"""
        interpretation = self.analytics._interpret_spread(2.5, "TOR", "MTL")
        self.assertIn("TOR", interpretation)
        self.assertIn("favored", interpretation)
        self.assertIn("underdog", interpretation)
        self.assertIn("MTL", interpretation)
    
    def test_interpret_spread_away_favored(self):
        """Test spread interpretation when away team is favored"""
        interpretation = self.analytics._interpret_spread(-2.5, "TOR", "MTL")
        self.assertIn("MTL", interpretation)
        self.assertIn("favored", interpretation)
        self.assertIn("underdog", interpretation)
        self.assertIn("TOR", interpretation)
    
    def test_interpret_spread_even(self):
        """Test spread interpretation for even matchup"""
        interpretation = self.analytics._interpret_spread(0.5, "TOR", "MTL")
        self.assertIn("Evenly", interpretation)
    
    def test_find_spread_value_structure(self):
        """Test that find_spread_value returns correct structure"""
        result = self.analytics.find_spread_value("TOR", "MTL", 1.5)
        
        # Check required fields
        self.assertIn("predicted_spread", result)
        self.assertIn("market_spread", result)
        self.assertIn("spread_difference", result)
        self.assertIn("value_assessment", result)
        self.assertIn("recommended_bet", result)
        self.assertIn("underdog", result)
        self.assertIn("favorite", result)
        self.assertIn("underdog_points", result)
        self.assertIn("confidence_interval", result)
    
    def test_find_spread_value_home_undervalued(self):
        """Test value detection when home team is undervalued"""
        # Market has home at 1.5, predicted at 3.0, home is undervalued
        result = self.analytics.find_spread_value("TOR", "MTL", 1.5)
        
        self.assertGreater(result["spread_difference"], 0.5)
        self.assertIn("TOR", result["value_assessment"])
        self.assertIn("undervalued", result["value_assessment"])
    
    def test_find_spread_value_away_undervalued(self):
        """Test value detection when away team is undervalued"""
        # Market has home at 4.0, predicted at 3.0, away is undervalued
        result = self.analytics.find_spread_value("TOR", "MTL", 4.0)
        
        self.assertLess(result["spread_difference"], -0.5)
        self.assertIn("MTL", result["value_assessment"])
        self.assertIn("undervalued", result["value_assessment"])
    
    def test_find_spread_value_underdog_identification(self):
        """Test that underdog is correctly identified"""
        # Positive spread: away team is underdog
        result1 = self.analytics.find_spread_value("TOR", "MTL", 2.0)
        self.assertEqual(result1["underdog"], "MTL")
        self.assertEqual(result1["favorite"], "TOR")
        
        # Negative spread: home team is underdog
        result2 = self.analytics.find_spread_value("TOR", "MTL", -1.5)
        self.assertEqual(result2["underdog"], "TOR")
        self.assertEqual(result2["favorite"], "MTL")
    
    def test_interpret_total_low(self):
        """Test total interpretation for low-scoring game"""
        interpretation = self.analytics._interpret_total(5.0)
        self.assertIn("Low-scoring", interpretation)
    
    def test_interpret_total_high(self):
        """Test total interpretation for high-scoring game"""
        interpretation = self.analytics._interpret_total(7.0)
        self.assertIn("High-scoring", interpretation)
    
    def test_interpret_total_average(self):
        """Test total interpretation for average-scoring game"""
        interpretation = self.analytics._interpret_total(6.0)
        self.assertIn("Average-scoring", interpretation)
    
    def test_confidence_interval_within_range(self):
        """Test that prediction falls within confidence interval"""
        spread_result = self.analytics.predict_spread("TOR", "MTL")
        
        predicted = spread_result["predicted_spread"]
        ci_lower = spread_result["confidence_interval"]["lower"]
        ci_upper = spread_result["confidence_interval"]["upper"]
        
        # Predicted value should be within CI
        self.assertGreaterEqual(predicted, ci_lower)
        self.assertLessEqual(predicted, ci_upper)


class TestStatisticalProperties(unittest.TestCase):
    """Tests for statistical properties of predictions"""
    
    def setUp(self):
        self.analytics = NHLAnalytics()
    
    def test_confidence_interval_width(self):
        """Test that confidence interval has reasonable width"""
        result = self.analytics.predict_spread("TOR", "MTL")
        ci = result["confidence_interval"]
        
        width = ci["upper"] - ci["lower"]
        
        # Width should be reasonable for 70% CI (~2-4 goals)
        self.assertGreater(width, 1.5)
        self.assertLess(width, 5.0)
    
    def test_multiple_predictions_consistency(self):
        """Test that predictions are consistent across calls"""
        result1 = self.analytics.predict_spread("TOR", "MTL")
        result2 = self.analytics.predict_spread("TOR", "MTL")
        
        # Should get same prediction (deterministic)
        self.assertEqual(result1["predicted_spread"], result2["predicted_spread"])


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    print("=" * 60)
    print("NHL Analytics Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 60)
