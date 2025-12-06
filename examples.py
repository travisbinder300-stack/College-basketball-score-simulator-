#!/usr/bin/env python3
"""
Example usage of the Basketball Predictor
Demonstrates various prediction scenarios
"""

from basketball_predictor import BasketballPredictor, TeamStats, load_team_data


def example_1_team_stats_prediction():
    """Example: Predict game using team statistics"""
    print("=" * 60)
    print("Example 1: Prediction Using Team Statistics")
    print("=" * 60)
    
    # Load team data from JSON file
    teams = load_team_data('example_teams.json')
    
    # Create predictor
    predictor = BasketballPredictor()
    
    # Predict Duke vs North Carolina at Cameron Indoor Stadium
    prediction = predictor.predict_game(
        home_team=teams['Duke'],
        away_team=teams['North Carolina']
    )
    
    print(prediction)


def example_2_spread_total_prediction():
    """Example: Predict game using betting lines"""
    print("=" * 60)
    print("Example 2: Prediction Using Point Spread and Total")
    print("=" * 60)
    
    predictor = BasketballPredictor()
    
    # Betting line: Kansas -6.5, Total 145.5
    prediction = predictor.predict_from_spread_and_total(
        home_team_name="Kansas",
        away_team_name="Kentucky",
        point_spread=6.5,
        total_points=145.5
    )
    
    print(prediction)


def example_3_neutral_site():
    """Example: Predict neutral site game"""
    print("=" * 60)
    print("Example 3: Neutral Site Game (NCAA Tournament)")
    print("=" * 60)
    
    teams = load_team_data('example_teams.json')
    predictor = BasketballPredictor()
    
    # Gonzaga vs Kansas at neutral site
    prediction = predictor.predict_game(
        home_team=teams['Gonzaga'],
        away_team=teams['Kansas'],
        neutral_site=True
    )
    
    print(prediction)


def example_4_monte_carlo_simulation():
    """Example: Run Monte Carlo simulation"""
    print("=" * 60)
    print("Example 4: Monte Carlo Simulation")
    print("=" * 60)
    
    predictor = BasketballPredictor()
    
    # Create prediction
    prediction = predictor.predict_from_spread_and_total(
        home_team_name="Villanova",
        away_team_name="Purdue",
        point_spread=2.5,
        total_points=138.0
    )
    
    print(prediction)
    
    # Run simulation
    print("\nRunning 10,000 game simulations...")
    results = predictor.simulate_game(prediction, num_simulations=10000)
    
    print(f"\nSimulation Results:")
    print(f"  Home Win Probability: {results['home_win_pct']:.1%}")
    print(f"  Away Win Probability: {results['away_win_pct']:.1%}")
    print(f"  Average Home Score: {results['avg_home_score']:.1f}")
    print(f"  Average Away Score: {results['avg_away_score']:.1f}")
    print(f"  Home Score 90% CI: [{results['home_score_range'][0]:.1f}, "
          f"{results['home_score_range'][1]:.1f}]")
    print(f"  Away Score 90% CI: [{results['away_score_range'][0]:.1f}, "
          f"{results['away_score_range'][1]:.1f}]")


def example_5_custom_home_advantage():
    """Example: Custom home court advantage"""
    print("=" * 60)
    print("Example 5: Custom Home Court Advantage")
    print("=" * 60)
    
    teams = load_team_data('example_teams.json')
    
    # Virginia has strong home court advantage (5 points)
    predictor_strong_hca = BasketballPredictor(home_court_advantage=5.0)
    
    prediction = predictor_strong_hca.predict_game(
        home_team=teams['Virginia'],
        away_team=teams['Duke']
    )
    
    print(prediction)


def example_6_multiple_games():
    """Example: Predict multiple games at once"""
    print("=" * 60)
    print("Example 6: Multiple Game Predictions")
    print("=" * 60)
    
    teams = load_team_data('example_teams.json')
    predictor = BasketballPredictor()
    
    # List of matchups
    matchups = [
        ('Duke', 'North Carolina'),
        ('Kansas', 'Kentucky'),
        ('Gonzaga', 'Villanova'),
        ('UCLA', 'Arizona')
    ]
    
    for home, away in matchups:
        prediction = predictor.predict_game(teams[home], teams[away])
        print(f"{away} @ {home}: {prediction.point_spread:+.1f} "
              f"(Total: {prediction.total_points:.1f})")
    print()


def example_7_programmatic_usage():
    """Example: Create teams programmatically"""
    print("=" * 60)
    print("Example 7: Programmatic Team Creation")
    print("=" * 60)
    
    # Create custom team stats (e.g., from web scraping KenPom)
    team_a = TeamStats(
        name="Hypothetical Elite Team",
        offensive_efficiency=120.0,  # Elite offense
        defensive_efficiency=88.0,   # Elite defense
        tempo=70.0
    )
    
    team_b = TeamStats(
        name="Hypothetical Good Team",
        offensive_efficiency=110.0,
        defensive_efficiency=98.0,
        tempo=72.0
    )
    
    predictor = BasketballPredictor()
    prediction = predictor.predict_game(team_a, team_b)
    
    print(prediction)


if __name__ == '__main__':
    # Run all examples
    example_1_team_stats_prediction()
    example_2_spread_total_prediction()
    example_3_neutral_site()
    example_4_monte_carlo_simulation()
    example_5_custom_home_advantage()
    example_6_multiple_games()
    example_7_programmatic_usage()
