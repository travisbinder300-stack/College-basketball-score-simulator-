#!/usr/bin/env python3
"""
Predict outcome for a specific game: Jackson State at Houston
"""

import os
import sys
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.collector import BasketballDataCollector
from src.data.features import FeatureEngineer
from src.models.predictor import BasketballPredictor
from src.betting.strategy import BettingStrategy
from sklearn.model_selection import train_test_split
from src.config import TRAIN_TEST_SPLIT, RANDOM_STATE


def create_game_prediction(home_team: str, away_team: str, betting_spread: float):
    """
    Create a prediction for a specific matchup
    
    Args:
        home_team: Home team name
        away_team: Away team name
        betting_spread: Betting spread (positive favors home team)
    """
    print("\n" + "="*60)
    print("COLLEGE BASKETBALL GAME PREDICTION")
    print("="*60)
    print(f"\nMatchup: {away_team} @ {home_team}")
    print(f"Betting Spread: {home_team} {betting_spread:+.1f}")
    print("="*60)
    
    # Step 1: Generate training data
    print("\nStep 1: Training prediction models...")
    collector = BasketballDataCollector()
    df = collector.generate_sample_data(num_teams=50, num_games=1000)
    
    # Step 2: Engineer features
    engineer = FeatureEngineer()
    matchup_df = engineer.create_matchup_features(df)
    
    # Step 3: Train models
    X, y = engineer.prepare_features_and_target(matchup_df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TRAIN_TEST_SPLIT, random_state=RANDOM_STATE, stratify=y
    )
    
    predictor = BasketballPredictor()
    predictor.train(X_train, y_train, X_test, y_test)
    
    print("\n✓ Models trained successfully")
    
    # Step 4: Create stats for the specific teams
    print("\nStep 2: Analyzing team statistics...")
    
    # For demonstration, we'll use representative stats based on the spread
    # A 15.5 spread suggests South Florida is heavily favored
    # South Florida appears to be a strong team, Charleston appears to be significantly weaker
    
    # South Florida stats (strong favorite)
    home_stats = {
        'home_ppg': 79.0,      # High scoring
        'home_fg_pct': 0.472,  # Above average shooting
        'home_3p_pct': 0.358,  # Good 3-point shooting
        'home_reb': 38.0,      # Strong rebounding
        'home_ast': 16.0,      # Good ball movement
        'home_to': 10.8,       # Low turnovers
        'home_win_pct': 0.800  # Excellent record
    }
    
    # Charleston stats (underdog)
    away_stats = {
        'away_ppg': 67.0,      # Lower scoring
        'away_fg_pct': 0.420,  # Below average shooting
        'away_3p_pct': 0.320,  # Weaker 3-point shooting
        'away_reb': 32.8,      # Weaker rebounding
        'away_ast': 12.8,      # Less assists
        'away_to': 13.8,       # More turnovers
        'away_win_pct': 0.400  # Poor record
    }
    
    # Calculate differentials
    differentials = {
        'ppg_diff': home_stats['home_ppg'] - away_stats['away_ppg'],
        'fg_pct_diff': home_stats['home_fg_pct'] - away_stats['away_fg_pct'],
        '3p_pct_diff': home_stats['home_3p_pct'] - away_stats['away_3p_pct'],
        'reb_diff': home_stats['home_reb'] - away_stats['away_reb'],
        'ast_diff': home_stats['home_ast'] - away_stats['away_ast'],
        'to_diff': away_stats['away_to'] - home_stats['home_to'],  # Lower is better
        'win_pct_diff': home_stats['home_win_pct'] - away_stats['away_win_pct']
    }
    
    # Create feature vector
    game_features = {**home_stats, **away_stats, **differentials}
    game_df = pd.DataFrame([game_features])
    
    # Display team comparison
    print(f"\n{home_team} (Home):")
    print(f"  PPG: {home_stats['home_ppg']:.1f} | FG%: {home_stats['home_fg_pct']:.1%} | 3P%: {home_stats['home_3p_pct']:.1%}")
    print(f"  REB: {home_stats['home_reb']:.1f} | AST: {home_stats['home_ast']:.1f} | TO: {home_stats['home_to']:.1f}")
    print(f"  Win %: {home_stats['home_win_pct']:.1%}")
    
    print(f"\n{away_team} (Away):")
    print(f"  PPG: {away_stats['away_ppg']:.1f} | FG%: {away_stats['away_fg_pct']:.1%} | 3P%: {away_stats['away_3p_pct']:.1%}")
    print(f"  REB: {away_stats['away_reb']:.1f} | AST: {away_stats['away_ast']:.1f} | TO: {away_stats['away_to']:.1f}")
    print(f"  Win %: {away_stats['away_win_pct']:.1%}")
    
    # Step 5: Make prediction
    print("\nStep 3: Generating prediction...")
    home_win_prob = predictor.predict_proba(game_df)[0]
    away_win_prob = 1 - home_win_prob
    
    print("\n" + "-"*60)
    print("PREDICTION RESULTS")
    print("-"*60)
    print(f"{home_team} Win Probability: {home_win_prob:.1%}")
    print(f"{away_team} Win Probability: {away_win_prob:.1%}")
    
    # Step 6: Betting analysis
    print("\n" + "-"*60)
    print("BETTING ANALYSIS")
    print("-"*60)
    
    # Convert spread to market probability
    # A spread of 38.5 means Houston is favored by 38.5 points
    # Using logistic function: p = 1 / (1 + exp(spread/4))
    # Negative spread favors home team
    if betting_spread == 0:
        market_prob = 0.5
    else:
        # For positive spread (home team favored), convert to probability
        # 38.5 point favorite has very high win probability
        market_prob = 1 / (1 + np.exp(-betting_spread / 4))
    
    print(f"Market Implied Probability: {market_prob:.1%}")
    print(f"Betting Spread: {home_team} {betting_spread:+.1f}")
    
    # Calculate edge
    edge = home_win_prob - market_prob
    print(f"\nModel Edge: {edge:+.1%}")
    
    # Create prediction dataframe for betting strategy
    pred_df = pd.DataFrame([{
        'home_team': home_team,
        'away_team': away_team,
        'home_win_prob': home_win_prob,
        'betting_spread': betting_spread
    }])
    
    # Find value bets
    strategy = BettingStrategy(initial_bankroll=1000)
    value_bets = strategy.find_value_bets(pred_df)
    
    print("\n" + "-"*60)
    print("BETTING RECOMMENDATION")
    print("-"*60)
    
    if len(value_bets) > 0:
        bet = value_bets.iloc[0]
        print(f"✓ VALUE BET IDENTIFIED")
        print(f"  Bet On: {bet['bet_on']}")
        print(f"  Edge: {bet['edge']:.1%}")
        print(f"  Recommended Bet: {bet['recommended_bet_pct']:.1%} of bankroll")
        print(f"  Bet Amount (on $1000): ${bet['recommended_bet_amount']:.2f}")
        print(f"  Expected Value: ${bet['expected_value']:.2f}")
    else:
        print("✗ NO VALUE BET")
        print(f"  The model does not find sufficient edge (≥3%) to recommend a bet.")
        print(f"  Current edge: {edge:+.1%}")
    
    # Expected score estimate
    print("\n" + "-"*60)
    print("SCORE PROJECTION")
    print("-"*60)
    
    # Use team PPG and adjust based on matchup
    expected_home_score = home_stats['home_ppg'] + (differentials['ppg_diff'] * 0.3)
    expected_away_score = away_stats['away_ppg'] - (differentials['ppg_diff'] * 0.3)
    expected_margin = expected_home_score - expected_away_score
    
    print(f"Projected Score: {home_team} {expected_home_score:.0f}, {away_team} {expected_away_score:.0f}")
    print(f"Projected Margin: {home_team} by {expected_margin:.1f}")
    
    if expected_margin > betting_spread:
        print(f"✓ Model favors {home_team} more than the spread suggests")
    elif expected_margin < betting_spread:
        print(f"⚠ Model sees {away_team} covering the spread")
    else:
        print(f"→ Model aligns closely with the betting line")
    
    print("\n" + "="*60)
    print("DISCLAIMER: This is for educational purposes only.")
    print("Always bet responsibly and within your means.")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Specific game prediction
    create_game_prediction(
        home_team="South Florida",
        away_team="Charleston", 
        betting_spread=15.5
    )
