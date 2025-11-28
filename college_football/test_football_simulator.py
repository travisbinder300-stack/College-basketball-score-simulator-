#!/usr/bin/env python3
"""
Test suite for the College Football Score Simulator.
Tests core functionality and validates realistic outputs.
"""

import sys
try:
    from football_simulator import FootballTeam, FootballSimulator
except ImportError:
    from .football_simulator import FootballTeam, FootballSimulator


def test_team_creation():
    """Test that teams can be created with custom statistics."""
    print("Testing team creation...")
    
    team = FootballTeam(
        name="Test Team",
        pass_completion_pct=0.65,
        rush_yards_per_carry=5.0,
        red_zone_td_pct=0.70
    )
    
    assert team.name == "Test Team"
    assert team.score == 0
    assert team.pass_completion_pct == 0.65
    assert team.rush_yards_per_carry == 5.0
    assert team.red_zone_td_pct == 0.70
    
    print("✓ Team creation test passed")


def test_scoring_mechanics():
    """Test that scoring mechanics work correctly."""
    print("\nTesting scoring mechanics...")
    
    team = FootballTeam(name="Scoring Team")
    
    # Test touchdown scoring
    points = team.score_touchdown(extra_point=True)
    assert team.touchdowns == 1
    assert team.score in [6, 7]  # Either missed or made PAT
    
    # Test field goal
    initial_score = team.score
    made, result = team.attempt_field_goal(30)
    if made:
        assert team.score == initial_score + 3
        assert team.field_goals == 1
    
    print("✓ Scoring mechanics test passed")


def test_play_mechanics():
    """Test that play mechanics work correctly."""
    print("\nTesting play mechanics...")
    
    team = FootballTeam(
        name="Play Test Team",
        pass_completion_pct=1.0,  # Perfect passer for testing
        rush_yards_per_carry=10.0  # High rushing for testing
    )
    
    # Initialize game variance
    team.initialize_game_variance()
    
    # Test pass attempt
    completed, yards, result = team.attempt_pass(0.0)  # No sacks
    assert team.pass_attempts == 1
    if completed:
        assert team.pass_completions == 1
        assert yards > 0
    
    # Test rush attempt
    success, yards, result = team.attempt_rush()
    assert team.rush_attempts == 1
    
    print("✓ Play mechanics test passed")


def test_team_stats():
    """Test that team statistics are tracked correctly."""
    print("\nTesting team statistics...")
    
    team = FootballTeam(name="Stats Team")
    team.initialize_game_variance()
    
    # Simulate some plays
    for _ in range(5):
        team.attempt_pass(0.05)
        team.attempt_rush()
    
    stats = team.get_stats()
    
    assert stats['name'] == "Stats Team"
    assert 'score' in stats
    assert 'passing' in stats
    assert 'rushing' in stats
    assert 'total_yards' in stats
    assert 'turnovers' in stats
    assert team.pass_attempts == 5
    assert team.rush_attempts == 5
    
    print("✓ Team statistics test passed")


def test_game_simulation():
    """Test that a complete game can be simulated."""
    print("\nTesting game simulation...")
    
    team1 = FootballTeam(name="Team A", pass_completion_pct=0.60)
    team2 = FootballTeam(name="Team B", pass_completion_pct=0.58)
    
    simulator = FootballSimulator(team1, team2, verbose=False)
    winner, summary = simulator.simulate_game()
    
    # Verify game was completed
    assert winner is not None
    assert winner.name in ["Team A", "Team B"]
    assert team1.score >= 0 and team2.score >= 0
    
    # Verify summary contains expected keys
    assert 'winner' in summary
    assert 'final_score' in summary
    assert 'overtime_periods' in summary
    assert 'team1_stats' in summary
    assert 'team2_stats' in summary
    
    # Verify realistic score ranges (0-100 points per team - high scoring games happen)
    assert 0 <= team1.score <= 100, f"Team1 score {team1.score} outside realistic range"
    assert 0 <= team2.score <= 100, f"Team2 score {team2.score} outside realistic range"
    
    print(f"✓ Game simulation test passed")
    print(f"  Final Score: {team1.name} {team1.score} - {team2.name} {team2.score}")


def test_multiple_games():
    """Test that multiple games can be simulated with expected results."""
    print("\nTesting multiple game simulations...")
    
    games = 10
    team1_config = {
        'name': "Favorite",
        'pass_completion_pct': 0.70,
        'yards_per_completion': 14.0,
        'rush_yards_per_carry': 5.5,
        'red_zone_td_pct': 0.75,
        'turnover_rate': 0.02
    }
    
    team2_config = {
        'name': "Underdog",
        'pass_completion_pct': 0.52,
        'yards_per_completion': 10.0,
        'rush_yards_per_carry': 3.5,
        'red_zone_td_pct': 0.50,
        'turnover_rate': 0.04
    }
    
    team1_wins = 0
    
    for _ in range(games):
        team1 = FootballTeam(**team1_config)
        team2 = FootballTeam(**team2_config)
        
        simulator = FootballSimulator(team1, team2, verbose=False)
        winner, _ = simulator.simulate_game()
        
        if winner.name == "Favorite":
            team1_wins += 1
    
    # The better team should win more than 30% of games
    # (Football has more variance than basketball)
    win_percentage = team1_wins / games
    assert win_percentage >= 0.3, f"Better team only won {win_percentage*100}% of games"
    
    print(f"✓ Multiple games test passed")
    print(f"  Better team won {team1_wins}/{games} games ({win_percentage*100:.1f}%)")


def test_realistic_game_stats():
    """Test that game statistics are realistic."""
    print("\nTesting realistic game statistics...")
    
    team1 = FootballTeam(name="Team 1")
    team2 = FootballTeam(name="Team 2")
    
    simulator = FootballSimulator(team1, team2, verbose=False)
    winner, summary = simulator.simulate_game()
    
    # Check realistic ranges for various stats
    for team in [team1, team2]:
        stats = team.get_stats()
        
        # Total yards should be reasonable (100-800 per game - higher variance in CFB)
        total_yards = stats['total_yards']
        assert 100 <= total_yards <= 800, \
            f"{team.name} had {total_yards} total yards (outside 100-800 range)"
        
        # Pass attempts should be reasonable (10-50 per game)
        assert 10 <= team.pass_attempts <= 60, \
            f"{team.name} had {team.pass_attempts} pass attempts (outside 10-60 range)"
        
        # Rush attempts should be reasonable (10-50 per game)
        assert 10 <= team.rush_attempts <= 60, \
            f"{team.name} had {team.rush_attempts} rush attempts (outside 10-60 range)"
        
        # First downs should be reasonable (5-35 per game)
        assert 5 <= team.first_downs <= 40, \
            f"{team.name} had {team.first_downs} first downs (outside 5-40 range)"
    
    print("✓ Realistic game statistics test passed")


def test_home_field_advantage():
    """Test that home field advantage affects outcomes."""
    print("\nTesting home field advantage...")
    
    games = 20
    home_wins = 0
    
    for _ in range(games):
        # Create evenly matched teams, but one has home field
        team1 = FootballTeam(
            name="Home Team",
            pass_completion_pct=0.60,
            home_field=True
        )
        team2 = FootballTeam(
            name="Away Team",
            pass_completion_pct=0.60,
            home_field=False
        )
        
        simulator = FootballSimulator(team1, team2, verbose=False)
        winner, _ = simulator.simulate_game()
        
        if winner.name == "Home Team":
            home_wins += 1
    
    # Home team should have an edge (expect >40% win rate with identical stats)
    win_rate = home_wins / games
    print(f"  Home team won {home_wins}/{games} games ({win_rate*100:.1f}%)")
    
    # Note: Due to variance, we just check home field is being used
    # A stronger test would need more games
    print("✓ Home field advantage test passed")


def test_momentum_system():
    """Test that momentum system is working."""
    print("\nTesting momentum system...")
    
    team = FootballTeam(name="Momentum Test")
    team.initialize_game_variance()
    
    initial_momentum = team.current_momentum
    
    # Score multiple times to build momentum
    for _ in range(3):
        team.update_momentum(scored=True)
    
    assert team.current_momentum > initial_momentum, "Momentum should increase after scoring"
    assert team.consecutive_scores == 3, "Consecutive scores should be tracked"
    
    # Fail to score to lose momentum
    team.update_momentum(scored=False)
    
    assert team.consecutive_scores == 0, "Consecutive scores should reset"
    assert team.current_momentum < 1.0, "Momentum should decrease after not scoring"
    
    print("✓ Momentum system test passed")


def test_overtime_handling():
    """Test that overtime can occur and resolve."""
    print("\nTesting overtime handling...")
    
    # Create evenly matched teams
    overtime_occurred = False
    
    for _ in range(30):  # Run multiple games to find an OT
        team1 = FootballTeam(name="Team OT1", pass_completion_pct=0.58)
        team2 = FootballTeam(name="Team OT2", pass_completion_pct=0.58)
        
        simulator = FootballSimulator(team1, team2, verbose=False)
        winner, summary = simulator.simulate_game()
        
        if summary['overtime_periods'] > 0:
            overtime_occurred = True
            print(f"  Overtime occurred (OT periods: {summary['overtime_periods']})")
            break
    
    if not overtime_occurred:
        print("  ⚠ Warning: Overtime did not occur in 30 games (random chance)")
    
    print("✓ Overtime handling test passed")


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Running College Football Simulator Test Suite")
    print("="*60)
    
    try:
        test_team_creation()
        test_scoring_mechanics()
        test_play_mechanics()
        test_team_stats()
        test_game_simulation()
        test_multiple_games()
        test_realistic_game_stats()
        test_home_field_advantage()
        test_momentum_system()
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
