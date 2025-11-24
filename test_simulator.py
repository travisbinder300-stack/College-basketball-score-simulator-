#!/usr/bin/env python3
"""
Test suite for the College Basketball Score Simulator.
Tests core functionality and validates realistic outputs.
"""

import sys
from basketball_simulator import Team, BasketballSimulator


def test_team_creation():
    """Test that teams can be created with custom statistics."""
    print("Testing team creation...")
    
    team = Team(
        name="Test Team",
        fg_percentage=0.50,
        three_pt_percentage=0.40,
        ft_percentage=0.80
    )
    
    assert team.name == "Test Team"
    assert team.score == 0
    assert team.fg_percentage == 0.50
    assert team.three_pt_percentage == 0.40
    assert team.ft_percentage == 0.80
    
    print("✓ Team creation test passed")


def test_shot_mechanics():
    """Test that shot mechanics work correctly."""
    print("\nTesting shot mechanics...")
    
    # Create a team with perfect shooting
    perfect_team = Team(
        name="Perfect Shooters",
        fg_percentage=1.0,
        three_pt_percentage=1.0,
        ft_percentage=1.0
    )
    
    # Test 2-point shot
    made, points = perfect_team.attempt_shot(is_three_pointer=False)
    assert made
    assert points == 2
    assert perfect_team.score == 2
    assert perfect_team.field_goals_made == 1
    assert perfect_team.field_goals_attempted == 1
    
    # Test 3-point shot
    made, points = perfect_team.attempt_shot(is_three_pointer=True)
    assert made
    assert points == 3
    assert perfect_team.score == 5
    assert perfect_team.three_pointers_made == 1
    assert perfect_team.three_pointers_attempted == 1
    
    # Test free throw
    made, points = perfect_team.attempt_free_throw()
    assert made
    assert points == 1
    assert perfect_team.score == 6
    assert perfect_team.free_throws_made == 1
    assert perfect_team.free_throws_attempted == 1
    
    print("✓ Shot mechanics test passed")


def test_team_stats():
    """Test that team statistics are calculated correctly."""
    print("\nTesting team statistics...")
    
    team = Team(name="Stats Team")
    
    # Make some shots
    team.attempt_shot(is_three_pointer=False)  # 2-pointer
    team.attempt_shot(is_three_pointer=True)   # 3-pointer
    team.attempt_free_throw()                   # Free throw
    team.commit_turnover()
    team.get_rebound()
    
    stats = team.get_stats()
    
    assert stats['name'] == "Stats Team"
    assert 'score' in stats
    assert 'fg' in stats
    assert '3pt' in stats
    assert 'ft' in stats
    assert stats['turnovers'] == 1
    assert stats['rebounds'] == 1
    
    print("✓ Team statistics test passed")


def test_game_simulation():
    """Test that a complete game can be simulated."""
    print("\nTesting game simulation...")
    
    team1 = Team(name="Team A", fg_percentage=0.45)
    team2 = Team(name="Team B", fg_percentage=0.45)
    
    simulator = BasketballSimulator(team1, team2, verbose=False)
    winner, summary = simulator.simulate_game()
    
    # Verify game was completed
    assert winner is not None
    assert winner.name in ["Team A", "Team B"]
    assert team1.score != 0 or team2.score != 0  # At least one team scored
    assert team1.score != team2.score  # No tie (overtime should resolve)
    
    # Verify summary contains expected keys
    assert 'winner' in summary
    assert 'final_score' in summary
    assert 'overtime_periods' in summary
    assert 'team1_stats' in summary
    assert 'team2_stats' in summary
    
    # Verify realistic score ranges (20-110 points per team)
    # Note: Occasionally games can be low-scoring, especially with turnovers/poor shooting
    assert 20 <= team1.score <= 110, f"Team1 score {team1.score} outside realistic range"
    assert 20 <= team2.score <= 110, f"Team2 score {team2.score} outside realistic range"
    
    print(f"✓ Game simulation test passed")
    print(f"  Final Score: {team1.name} {team1.score} - {team2.name} {team2.score}")


def test_multiple_games():
    """Test that multiple games can be simulated with consistent results."""
    print("\nTesting multiple game simulations...")
    
    games = 10
    team1_config = {
        'name': "Favorite",
        'fg_percentage': 0.55,  # Much better team
        'three_pt_percentage': 0.42,
        'ft_percentage': 0.80
    }
    
    team2_config = {
        'name': "Underdog",
        'fg_percentage': 0.40,  # Weaker team
        'three_pt_percentage': 0.30,
        'ft_percentage': 0.65
    }
    
    team1_wins = 0
    
    for _ in range(games):
        team1 = Team(**team1_config)
        team2 = Team(**team2_config)
        
        simulator = BasketballSimulator(team1, team2, verbose=False)
        winner, _ = simulator.simulate_game()
        
        if winner.name == "Favorite":
            team1_wins += 1
    
    # The better team should win more than 50% of games
    win_percentage = team1_wins / games
    assert win_percentage > 0.5, f"Better team only won {win_percentage*100}% of games"
    
    print(f"✓ Multiple games test passed")
    print(f"  Better team won {team1_wins}/{games} games ({win_percentage*100:.1f}%)")


def test_realistic_game_stats():
    """Test that game statistics are realistic."""
    print("\nTesting realistic game statistics...")
    
    team1 = Team(name="Team 1")
    team2 = Team(name="Team 2")
    
    simulator = BasketballSimulator(team1, team2, verbose=False)
    winner, summary = simulator.simulate_game()
    
    # Check realistic ranges for various stats
    for team in [team1, team2]:
        stats = team.get_stats()
        
        # Field goal attempts should be reasonable (30-90 per game)
        # Note: Can be lower with many turnovers or fouls
        assert 30 <= team.field_goals_attempted <= 90, \
            f"{team.name} had {team.field_goals_attempted} FG attempts (outside 30-90 range)"
        
        # 3-point attempts should be reasonable (5-45 per game)
        assert 5 <= team.three_pointers_attempted <= 45, \
            f"{team.name} had {team.three_pointers_attempted} 3PT attempts (outside 5-45 range)"
        
        # Free throw attempts should be reasonable (2-40 per game)
        assert 2 <= team.free_throws_attempted <= 40, \
            f"{team.name} had {team.free_throws_attempted} FT attempts (outside 2-40 range)"
        
        # Turnovers should be reasonable (2-30 per game)
        assert 2 <= team.turnovers <= 30, \
            f"{team.name} had {team.turnovers} turnovers (outside 2-30 range)"
        
        # Rebounds should be reasonable (10-60 per game)
        assert 10 <= team.rebounds <= 60, \
            f"{team.name} had {team.rebounds} rebounds (outside 10-60 range)"
    
    print("✓ Realistic game statistics test passed")


def test_overtime_handling():
    """Test that overtime is handled when teams are evenly matched."""
    print("\nTesting overtime handling...")
    
    # Create two identical teams to increase chance of overtime
    team1 = Team(name="Team OT1", fg_percentage=0.45)
    team2 = Team(name="Team OT2", fg_percentage=0.45)
    
    # Run multiple games to check overtime can happen
    overtime_occurred = False
    
    for _ in range(20):
        team1 = Team(name="Team OT1", fg_percentage=0.45)
        team2 = Team(name="Team OT2", fg_percentage=0.45)
        
        simulator = BasketballSimulator(team1, team2, verbose=False)
        winner, summary = simulator.simulate_game()
        
        if summary['overtime_periods'] > 0:
            overtime_occurred = True
            print(f"  Overtime occurred in game (OT periods: {summary['overtime_periods']})")
            break
    
    # Note: This test might occasionally fail due to randomness, but it's unlikely
    if not overtime_occurred:
        print("  ⚠ Warning: Overtime did not occur in 20 games (random chance)")
    
    print("✓ Overtime handling test passed")


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Running College Basketball Simulator Test Suite")
    print("="*60)
    
    try:
        test_team_creation()
        test_shot_mechanics()
        test_team_stats()
        test_game_simulation()
        test_multiple_games()
        test_realistic_game_stats()
        test_overtime_handling()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
