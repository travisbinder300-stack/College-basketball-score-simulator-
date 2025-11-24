#!/usr/bin/env python3
"""
Test suite for the College Basketball Score Simulator
"""

import unittest
from simulator import (
    Team, BasketballSimulator,
    MIN_TURNOVER_RATE, MAX_TURNOVER_RATE,
    MIN_TWO_PT_SUCCESS, MAX_TWO_PT_SUCCESS
)


class TestTeam(unittest.TestCase):
    """Test the Team class."""
    
    def test_team_creation(self):
        """Test creating a team with default values."""
        team = Team("Test Team")
        self.assertEqual(team.name, "Test Team")
        self.assertEqual(team.offense_rating, 50.0)
        self.assertEqual(team.defense_rating, 50.0)
        self.assertEqual(team.three_point_pct, 0.35)
        self.assertEqual(team.free_throw_pct, 0.75)
    
    def test_team_with_custom_stats(self):
        """Test creating a team with custom statistics."""
        team = Team("Custom Team", offense_rating=80, defense_rating=70,
                   three_point_pct=0.40, free_throw_pct=0.80)
        self.assertEqual(team.offense_rating, 80.0)
        self.assertEqual(team.defense_rating, 70.0)
        self.assertEqual(team.three_point_pct, 0.40)
        self.assertEqual(team.free_throw_pct, 0.80)
    
    def test_team_rating_bounds(self):
        """Test that team ratings are bounded correctly."""
        # Test upper bounds
        team1 = Team("Team1", offense_rating=150, defense_rating=150)
        self.assertEqual(team1.offense_rating, 100.0)
        self.assertEqual(team1.defense_rating, 100.0)
        
        # Test lower bounds
        team2 = Team("Team2", offense_rating=-10, defense_rating=-10)
        self.assertEqual(team2.offense_rating, 0.0)
        self.assertEqual(team2.defense_rating, 0.0)
    
    def test_team_percentage_bounds(self):
        """Test that shooting percentages are bounded correctly."""
        # Test upper bounds
        team1 = Team("Team1", three_point_pct=1.5, free_throw_pct=1.5)
        self.assertEqual(team1.three_point_pct, 1.0)
        self.assertEqual(team1.free_throw_pct, 1.0)
        
        # Test lower bounds
        team2 = Team("Team2", three_point_pct=-0.5, free_throw_pct=-0.5)
        self.assertEqual(team2.three_point_pct, 0.0)
        self.assertEqual(team2.free_throw_pct, 0.0)
    
    def test_team_str(self):
        """Test string representation of team."""
        team = Team("Test Team", offense_rating=75, defense_rating=80)
        expected = "Test Team (OFF: 75.0, DEF: 80.0)"
        self.assertEqual(str(team), expected)


class TestBasketballSimulator(unittest.TestCase):
    """Test the BasketballSimulator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.team1 = Team("Team A", offense_rating=80, defense_rating=75)
        self.team2 = Team("Team B", offense_rating=70, defense_rating=80)
        self.simulator = BasketballSimulator(self.team1, self.team2)
    
    def test_simulator_creation(self):
        """Test creating a simulator."""
        self.assertEqual(self.simulator.home_team, self.team1)
        self.assertEqual(self.simulator.away_team, self.team2)
        self.assertEqual(self.simulator.home_score, 0)
        self.assertEqual(self.simulator.away_score, 0)
        self.assertFalse(self.simulator.verbose)
    
    def test_simulate_possession_returns_valid_points(self):
        """Test that possession simulation returns valid point values."""
        for _ in range(100):
            points = self.simulator.simulate_possession(self.team1, self.team2, is_home=True)
            self.assertIn(points, [0, 1, 2, 3], 
                         "Possession should return 0, 1, 2, or 3 points")
    
    def test_simulate_game_returns_scores(self):
        """Test that game simulation returns valid scores."""
        home_score, away_score = self.simulator.simulate_game(total_possessions=100)
        
        # Check that scores are non-negative
        self.assertGreaterEqual(home_score, 0)
        self.assertGreaterEqual(away_score, 0)
        
        # Check that scores are stored in simulator
        self.assertEqual(home_score, self.simulator.home_score)
        self.assertEqual(away_score, self.simulator.away_score)
        
        # Check that scores are reasonable (typically 40-120 for college basketball)
        self.assertLess(home_score, 200)
        self.assertLess(away_score, 200)
    
    def test_multiple_games_produce_different_results(self):
        """Test that multiple games produce varying results."""
        results = []
        for _ in range(10):
            sim = BasketballSimulator(self.team1, self.team2)
            home_score, away_score = sim.simulate_game(total_possessions=100)
            results.append((home_score, away_score))
        
        # Check that not all games have identical results
        unique_results = set(results)
        self.assertGreater(len(unique_results), 1, 
                          "Multiple games should produce varying results")
    
    def test_better_offense_tends_to_score_more(self):
        """Test that teams with better offense tend to score more over multiple games."""
        strong_team = Team("Strong", offense_rating=90, defense_rating=60)
        weak_team = Team("Weak", offense_rating=50, defense_rating=60)
        
        strong_total = 0
        weak_total = 0
        games = 100
        
        for _ in range(games):
            sim = BasketballSimulator(strong_team, weak_team)
            strong_score, weak_score = sim.simulate_game(total_possessions=100)
            strong_total += strong_score
            weak_total += weak_score
        
        # Strong offensive team should score more on average (with similar defense)
        self.assertGreater(strong_total / games, weak_total / games,
                          "Team with better offense should average more points")


class TestGameRealism(unittest.TestCase):
    """Test that simulated games produce realistic results."""
    
    def test_average_game_scores_realistic(self):
        """Test that average scores are realistic for college basketball."""
        team1 = Team("Team 1", offense_rating=75, defense_rating=75)
        team2 = Team("Team 2", offense_rating=75, defense_rating=75)
        
        total_points = 0
        games = 100
        
        for _ in range(games):
            sim = BasketballSimulator(team1, team2)
            score1, score2 = sim.simulate_game()
            total_points += score1 + score2
        
        avg_total = total_points / games
        
        # Average total points in college basketball is typically 130-150
        self.assertGreater(avg_total, 100, "Average game total too low")
        self.assertLess(avg_total, 200, "Average game total too high")
    
    def test_score_distribution_reasonable(self):
        """Test that scores have reasonable distribution."""
        team1 = Team("Team 1", offense_rating=70, defense_rating=70)
        team2 = Team("Team 2", offense_rating=70, defense_rating=70)
        
        scores = []
        games = 100
        
        for _ in range(games):
            sim = BasketballSimulator(team1, team2)
            score1, score2 = sim.simulate_game()
            scores.extend([score1, score2])
        
        avg_score = sum(scores) / len(scores)
        
        # Average team score in college basketball is typically 65-75
        self.assertGreater(avg_score, 40, "Average score too low")
        self.assertLess(avg_score, 100, "Average score too high")


class TestPerformance(unittest.TestCase):
    """Test performance optimizations."""
    
    def test_cached_matchup_stats(self):
        """Test that matchup statistics are cached on simulator creation."""
        team1 = Team("Team 1", offense_rating=80, defense_rating=75)
        team2 = Team("Team 2", offense_rating=70, defense_rating=80)
        
        sim = BasketballSimulator(team1, team2)
        
        # Verify cached attributes exist
        self.assertTrue(hasattr(sim, 'home_turnover_rate'))
        self.assertTrue(hasattr(sim, 'away_turnover_rate'))
        self.assertTrue(hasattr(sim, 'home_two_pt_rate'))
        self.assertTrue(hasattr(sim, 'away_two_pt_rate'))
        
        # Verify cached values are in valid ranges (using constants from simulator)
        self.assertGreaterEqual(sim.home_turnover_rate, MIN_TURNOVER_RATE)
        self.assertLessEqual(sim.home_turnover_rate, MAX_TURNOVER_RATE)
        self.assertGreaterEqual(sim.home_two_pt_rate, MIN_TWO_PT_SUCCESS)
        self.assertLessEqual(sim.home_two_pt_rate, MAX_TWO_PT_SUCCESS)
    
    def test_simulator_reuse(self):
        """Test that simulator can be reused for multiple games."""
        team1 = Team("Team 1", offense_rating=75, defense_rating=75)
        team2 = Team("Team 2", offense_rating=75, defense_rating=75)
        
        sim = BasketballSimulator(team1, team2)
        
        # Simulate multiple games with same simulator
        results = []
        for _ in range(10):
            score1, score2 = sim.simulate_game()
            results.append((score1, score2))
        
        # Verify all games produced valid results
        for score1, score2 in results:
            self.assertGreaterEqual(score1, 0)
            self.assertGreaterEqual(score2, 0)
            self.assertLess(score1, 200)
            self.assertLess(score2, 200)
        
        # Verify different results (not all same)
        unique_results = set(results)
        self.assertGreater(len(unique_results), 1, 
                          "Multiple games should produce varying results")


if __name__ == '__main__':
    unittest.main()
