#!/usr/bin/env python3
"""
Unit tests for NBA Spread and Total Analysis System
"""

import unittest
from nba_analysis import Team, Game, NBAAnalyzer, Prediction


class TestNBAAnalyzer(unittest.TestCase):
    """Test cases for NBA Analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = NBAAnalyzer(min_confidence=70.0)
        
        # Create test teams
        self.strong_team = Team(
            name="Strong Team",
            offensive_rating=120.0,
            defensive_rating=105.0,
            pace=100.0,
            win_percentage=0.750,
            recent_form=0.90
        )
        
        self.weak_team = Team(
            name="Weak Team",
            offensive_rating=108.0,
            defensive_rating=118.0,
            pace=98.0,
            win_percentage=0.300,
            recent_form=0.30
        )
        
        self.average_team = Team(
            name="Average Team",
            offensive_rating=112.0,
            defensive_rating=112.0,
            pace=99.0,
            win_percentage=0.500,
            recent_form=0.50
        )
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes with correct min confidence"""
        self.assertEqual(self.analyzer.min_confidence, 70.0)
        
        analyzer_80 = NBAAnalyzer(min_confidence=80.0)
        self.assertEqual(analyzer_80.min_confidence, 80.0)
    
    def test_spread_calculation_returns_tuple(self):
        """Test that spread calculation returns a tuple of (spread, confidence)"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        spread, confidence = self.analyzer.calculate_spread(game)
        
        self.assertIsInstance(spread, float)
        self.assertIsInstance(confidence, float)
    
    def test_spread_confidence_in_range(self):
        """Test that spread confidence is between 0 and 100"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        spread, confidence = self.analyzer.calculate_spread(game)
        
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 100.0)
    
    def test_strong_vs_weak_high_confidence(self):
        """Test that strong vs weak matchup produces high confidence"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        spread, confidence = self.analyzer.calculate_spread(game)
        
        # Strong vs weak should produce high confidence
        self.assertGreater(confidence, 75.0)
    
    def test_total_calculation_returns_tuple(self):
        """Test that total calculation returns a tuple of (total, confidence)"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        total, confidence = self.analyzer.calculate_total(game)
        
        self.assertIsInstance(total, float)
        self.assertIsInstance(confidence, float)
    
    def test_total_confidence_in_range(self):
        """Test that total confidence is between 0 and 100"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        total, confidence = self.analyzer.calculate_total(game)
        
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 100.0)
    
    def test_total_points_reasonable(self):
        """Test that total points prediction is in reasonable range"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        total, confidence = self.analyzer.calculate_total(game)
        
        # NBA game totals typically between 180-240 points
        self.assertGreater(total, 180.0)
        self.assertLess(total, 250.0)
    
    def test_analyze_game_returns_prediction(self):
        """Test that analyze_game returns a Prediction object"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        prediction = self.analyzer.analyze_game(game)
        
        self.assertIsInstance(prediction, Prediction)
        self.assertEqual(prediction.game, game)
        self.assertIsInstance(prediction.spread, float)
        self.assertIsInstance(prediction.total, float)
        self.assertIsInstance(prediction.spread_confidence, float)
        self.assertIsInstance(prediction.total_confidence, float)
    
    def test_analyze_games_filters_by_confidence(self):
        """Test that analyze_games filters predictions by min confidence"""
        games = [
            Game(self.strong_team, self.weak_team, "2025-12-04"),
            Game(self.average_team, self.average_team, "2025-12-04"),
        ]
        
        # With 70% threshold
        analyzer_70 = NBAAnalyzer(min_confidence=70.0)
        predictions_70 = analyzer_70.analyze_games(games)
        
        # With 95% threshold (should filter out most/all)
        analyzer_95 = NBAAnalyzer(min_confidence=95.0)
        predictions_95 = analyzer_95.analyze_games(games)
        
        # 70% threshold should have more predictions than 95%
        self.assertGreaterEqual(len(predictions_70), len(predictions_95))
        
        # All predictions should meet threshold
        for pred in predictions_70:
            self.assertGreaterEqual(pred.spread_confidence, 70.0)
            self.assertGreaterEqual(pred.total_confidence, 70.0)
    
    def test_home_court_advantage(self):
        """Test that home team has advantage in spread"""
        game_home = Game(self.average_team, self.average_team, "2025-12-04")
        spread, _ = self.analyzer.calculate_spread(game_home)
        
        # With identical teams, home team should be favored (positive spread)
        self.assertGreater(spread, 0.0)
        # Home court advantage is typically 3-4 points
        self.assertGreater(spread, 2.0)
        self.assertLess(spread, 6.0)
    
    def test_confidence_capped_at_95(self):
        """Test that confidence doesn't exceed 95%"""
        # Create extreme mismatch
        super_strong = Team(
            name="Super Strong",
            offensive_rating=130.0,
            defensive_rating=95.0,
            pace=100.0,
            win_percentage=0.900,
            recent_form=1.0
        )
        
        super_weak = Team(
            name="Super Weak",
            offensive_rating=100.0,
            defensive_rating=125.0,
            pace=95.0,
            win_percentage=0.100,
            recent_form=0.0
        )
        
        game = Game(super_strong, super_weak, "2025-12-04")
        spread, spread_conf = self.analyzer.calculate_spread(game)
        total, total_conf = self.analyzer.calculate_total(game)
        
        self.assertLessEqual(spread_conf, 95.0)
        self.assertLessEqual(total_conf, 95.0)
    
    def test_prediction_string_representation(self):
        """Test that prediction has proper string representation"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04")
        prediction = self.analyzer.analyze_game(game)
        pred_str = str(prediction)
        
        # Check that key information is in the string
        self.assertIn(self.strong_team.name, pred_str)
        self.assertIn(self.weak_team.name, pred_str)
        self.assertIn("Spread:", pred_str)
        self.assertIn("Total:", pred_str)
        self.assertIn("Confidence:", pred_str)


class TestTeamAndGame(unittest.TestCase):
    """Test cases for Team and Game dataclasses"""
    
    def test_team_creation(self):
        """Test that teams can be created with all attributes"""
        team = Team(
            name="Test Team",
            offensive_rating=115.0,
            defensive_rating=110.0,
            pace=100.0,
            win_percentage=0.600,
            recent_form=0.70
        )
        
        self.assertEqual(team.name, "Test Team")
        self.assertEqual(team.offensive_rating, 115.0)
        self.assertEqual(team.defensive_rating, 110.0)
        self.assertEqual(team.pace, 100.0)
        self.assertEqual(team.win_percentage, 0.600)
        self.assertEqual(team.recent_form, 0.70)
    
    def test_game_creation(self):
        """Test that games can be created with teams"""
        team1 = Team("Team 1", 115.0, 110.0, 100.0, 0.600, 0.70)
        team2 = Team("Team 2", 112.0, 108.0, 98.0, 0.550, 0.65)
        game = Game(team1, team2, "2025-12-04")
        
        self.assertEqual(game.home_team, team1)
        self.assertEqual(game.away_team, team2)
        self.assertEqual(game.date, "2025-12-04")
    
    def test_game_with_market_spread(self):
        """Test that games can be created with market spreads"""
        team1 = Team("Team 1", 115.0, 110.0, 100.0, 0.600, 0.70)
        team2 = Team("Team 2", 112.0, 108.0, 98.0, 0.550, 0.65)
        game = Game(team1, team2, "2025-12-04", market_spread=5.5)
        
        self.assertEqual(game.market_spread, 5.5)


class TestOvervalueDetection(unittest.TestCase):
    """Test cases for overvalue detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = NBAAnalyzer(min_confidence=70.0)
        
        self.team1 = Team(
            name="Team 1",
            offensive_rating=120.0,
            defensive_rating=105.0,
            pace=100.0,
            win_percentage=0.750,
            recent_form=0.90
        )
        
        self.team2 = Team(
            name="Team 2",
            offensive_rating=108.0,
            defensive_rating=118.0,
            pace=98.0,
            win_percentage=0.300,
            recent_form=0.30
        )
    
    def test_overvalue_detection_with_no_market_spread(self):
        """Test that overvalue is not detected when no market spread is provided"""
        game = Game(self.team1, self.team2, "2025-12-04", market_spread=None)
        prediction = self.analyzer.analyze_game(game)
        
        self.assertIsNone(prediction.spread_value)
        self.assertFalse(prediction.is_overvalue)
        self.assertIsNone(prediction.value_side)
    
    def test_overvalue_detection_significant_difference(self):
        """Test that overvalue is detected with significant spread difference"""
        # Our prediction will favor team1 heavily, but market only slightly favors them
        game = Game(self.team1, self.team2, "2025-12-04", market_spread=5.0)
        prediction = self.analyzer.analyze_game(game)
        
        # Should detect overvalue if difference is >= 2.5 points
        self.assertIsNotNone(prediction.spread_value)
        if abs(prediction.spread_value) >= 2.5:
            self.assertTrue(prediction.is_overvalue)
            self.assertIsNotNone(prediction.value_side)
    
    def test_overvalue_detection_no_significant_difference(self):
        """Test that overvalue is not detected with small spread difference"""
        game = Game(self.team1, self.team2, "2025-12-04", market_spread=15.0)
        prediction = self.analyzer.analyze_game(game)
        
        # Create a prediction where market is close to our prediction
        # Manually check if difference is small
        self.assertIsNotNone(prediction.spread_value)
        if abs(prediction.spread_value) < 2.5:
            self.assertFalse(prediction.is_overvalue)
    
    def test_overvalue_home_side(self):
        """Test that home side value is correctly identified"""
        # Market undervalues home team (lower spread than our prediction)
        game = Game(self.team1, self.team2, "2025-12-04", market_spread=5.0)
        prediction = self.analyzer.analyze_game(game)
        
        if prediction.spread_value > 2.5:
            self.assertEqual(prediction.value_side, "home")
    
    def test_overvalue_away_side(self):
        """Test that away side value is correctly identified"""
        # Market overvalues home team (higher spread than our prediction)
        game = Game(self.team1, self.team2, "2025-12-04", market_spread=20.0)
        prediction = self.analyzer.analyze_game(game)
        
        if prediction.spread_value < -2.5:
            self.assertEqual(prediction.value_side, "away")
    
    def test_find_overvalue_spreads(self):
        """Test that find_overvalue_spreads returns only overvalue predictions"""
        games = [
            Game(self.team1, self.team2, "2025-12-04", market_spread=5.0),
            Game(self.team1, self.team2, "2025-12-04", market_spread=15.0),
            Game(self.team1, self.team2, "2025-12-04", market_spread=20.0),
        ]
        
        overvalue_predictions = self.analyzer.find_overvalue_spreads(games)
        
        # All returned predictions should have is_overvalue = True
        for pred in overvalue_predictions:
            self.assertTrue(pred.is_overvalue)
    
    def test_custom_value_threshold(self):
        """Test that custom value threshold works correctly"""
        game = Game(self.team1, self.team2, "2025-12-04", market_spread=12.0)
        prediction = self.analyzer.analyze_game(game)
        
        # Test with different threshold
        prediction_4pt = self.analyzer.detect_overvalue(prediction, min_value_threshold=4.0)
        
        if abs(prediction_4pt.spread_value) >= 4.0:
            self.assertTrue(prediction_4pt.is_overvalue)
        else:
            self.assertFalse(prediction_4pt.is_overvalue)


class TestExpectedValue(unittest.TestCase):
    """Test cases for Expected Value (EV) calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = NBAAnalyzer(min_confidence=70.0)
        
        self.strong_team = Team(
            name="Strong Team",
            offensive_rating=120.0,
            defensive_rating=105.0,
            pace=100.0,
            win_percentage=0.750,
            recent_form=0.90
        )
        
        self.weak_team = Team(
            name="Weak Team",
            offensive_rating=108.0,
            defensive_rating=118.0,
            pace=98.0,
            win_percentage=0.300,
            recent_form=0.30
        )
    
    def test_ev_calculation_with_overvalue(self):
        """Test that EV is calculated when overvalue is detected"""
        # Create a game where overvalue will be detected
        game = Game(self.strong_team, self.weak_team, "2025-12-04", market_spread=5.0)
        prediction = self.analyzer.analyze_game(game)
        
        if prediction.is_overvalue:
            self.assertIsNotNone(prediction.expected_value)
            self.assertIsNotNone(prediction.ev_percentage)
    
    def test_ev_not_calculated_without_overvalue(self):
        """Test that EV is not calculated when no overvalue"""
        # Create a game where market matches prediction
        game = Game(self.strong_team, self.weak_team, "2025-12-04", market_spread=15.0)
        prediction = self.analyzer.analyze_game(game)
        
        if not prediction.is_overvalue:
            self.assertIsNone(prediction.expected_value)
            self.assertIsNone(prediction.ev_percentage)
    
    def test_ev_positive_with_high_confidence(self):
        """Test that high confidence predictions yield positive EV"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04", market_spread=5.0)
        prediction = self.analyzer.analyze_game(game)
        
        # With high confidence (>70%) and overvalue, EV should be positive
        if prediction.is_overvalue and prediction.spread_confidence > 70.0:
            self.assertIsNotNone(prediction.expected_value)
            # High confidence should yield positive EV
            if prediction.expected_value is not None:
                self.assertGreater(prediction.expected_value, 0)
    
    def test_ev_percentage_matches_dollar_ev(self):
        """Test that EV percentage correctly represents dollar EV"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04", market_spread=5.0)
        prediction = self.analyzer.analyze_game(game)
        
        if prediction.expected_value is not None and prediction.ev_percentage is not None:
            # EV percentage should be (EV / stake) * 100
            # For $100 stake, ev_percentage should equal expected_value
            self.assertAlmostEqual(
                prediction.ev_percentage,
                prediction.expected_value,
                places=1
            )
    
    def test_ev_not_calculated_without_market_spread(self):
        """Test that EV is not calculated when no market spread provided"""
        game = Game(self.strong_team, self.weak_team, "2025-12-04", market_spread=None)
        prediction = self.analyzer.analyze_game(game)
        
        self.assertIsNone(prediction.expected_value)
        self.assertIsNone(prediction.ev_percentage)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
