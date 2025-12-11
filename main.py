#!/usr/bin/env python3
"""
College Basketball Betting System - Main Application

This system uses machine learning to identify value betting opportunities
in college basketball by predicting game outcomes and comparing them to
market odds.
"""

import os
import sys
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.collector import BasketballDataCollector
from data.features import FeatureEngineer
from models.predictor import BasketballPredictor
from betting.strategy import BettingStrategy
from betting.backtest import Backtester
from utils.visualization import (plot_bankroll_over_time, plot_model_performance,
                                 plot_feature_importance, plot_bet_distribution)
from config import TRAIN_TEST_SPLIT, RANDOM_STATE, DATA_DIR, MODELS_DIR


def collect_data(args):
    """Collect and prepare data"""
    print("\n" + "="*60)
    print("STEP 1: DATA COLLECTION")
    print("="*60)
    
    collector = BasketballDataCollector()
    
    if args.data_file:
        print(f"Loading data from {args.data_file}...")
        df = collector.load_from_file(args.data_file)
    else:
        print("Generating sample data...")
        df = collector.generate_sample_data(num_teams=50, num_games=1000)
    
    print(f"Loaded {len(df)} games")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Save data if needed
    if args.save_data:
        os.makedirs(DATA_DIR, exist_ok=True)
        output_path = os.path.join(DATA_DIR, "basketball_data.csv")
        collector.save_data(df, output_path)
    
    return df


def engineer_features(df, args):
    """Create features for modeling"""
    print("\n" + "="*60)
    print("STEP 2: FEATURE ENGINEERING")
    print("="*60)
    
    engineer = FeatureEngineer()
    
    print("Creating matchup features...")
    matchup_df = engineer.create_matchup_features(df)
    print(f"Created features for {len(matchup_df)} matchups")
    
    print("\nFeature columns:")
    feature_cols = [col for col in matchup_df.columns if col not in 
                    ['game_id', 'date', 'home_team', 'away_team', 'home_won', 
                     'score_diff', 'betting_spread']]
    for col in feature_cols:
        print(f"  - {col}")
    
    return matchup_df, engineer


def train_models(matchup_df, engineer, args):
    """Train prediction models"""
    print("\n" + "="*60)
    print("STEP 3: MODEL TRAINING")
    print("="*60)
    
    # Prepare features and target
    X, y = engineer.prepare_features_and_target(matchup_df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TRAIN_TEST_SPLIT, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Home team win rate: {y.mean():.2%}")
    
    # Train models
    predictor = BasketballPredictor()
    results = predictor.train(X_train, y_train, X_test, y_test)
    
    # Show results
    print("\n" + "-"*60)
    print("Model Performance Summary:")
    print("-"*60)
    results_df = pd.DataFrame(results).T
    print(results_df.to_string())
    
    # Evaluate ensemble
    print("\n" + "-"*60)
    print("Ensemble Model Performance:")
    print("-"*60)
    ensemble_metrics = predictor.evaluate(X_test, y_test)
    print(f"Accuracy: {ensemble_metrics['accuracy']:.4f}")
    print(f"AUC: {ensemble_metrics['auc']:.4f}")
    print(f"Log Loss: {ensemble_metrics['log_loss']:.4f}")
    
    # Feature importance
    print("\n" + "-"*60)
    print("Top 10 Most Important Features:")
    print("-"*60)
    importance_df = predictor.get_feature_importance(X.columns.tolist())
    if importance_df is not None:
        print(importance_df.head(10)['mean'].to_string())
    
    # Save models if requested
    if args.save_models:
        os.makedirs(MODELS_DIR, exist_ok=True)
        predictor.save_models()
    
    # Visualizations
    if args.visualize:
        print("\nGenerating visualizations...")
        plot_model_performance(results_df, save_path='model_performance.png')
        if importance_df is not None:
            plot_feature_importance(importance_df, save_path='feature_importance.png')
    
    return predictor, X_test, y_test, matchup_df


def run_betting_strategy(predictor, matchup_df, args):
    """Run betting strategy and backtest"""
    print("\n" + "="*60)
    print("STEP 4: BETTING STRATEGY & BACKTESTING")
    print("="*60)
    
    # Generate predictions for all games
    engineer = FeatureEngineer()
    X, _ = engineer.prepare_features_and_target(matchup_df)
    
    predictions = predictor.predict_proba(X)
    
    # Create predictions dataframe
    predictions_df = matchup_df.copy()
    predictions_df['home_win_prob'] = predictions
    
    # Run backtest
    backtester = Backtester(initial_bankroll=args.bankroll)
    results = backtester.run_backtest(predictions_df, matchup_df)
    
    # Print results
    backtester.print_results(results)
    
    # Show some example value bets
    strategy = BettingStrategy(args.bankroll)
    value_bets = strategy.find_value_bets(predictions_df.head(100))
    
    if len(value_bets) > 0:
        print("\nExample Value Bets (Top 5):")
        print("-"*60)
        display_cols = ['home_team', 'away_team', 'bet_on', 'edge', 
                       'recommended_bet_pct', 'expected_value']
        print(value_bets[display_cols].head().to_string(index=False))
    
    # Visualizations
    if args.visualize and results['total_bets'] > 0:
        print("\nGenerating betting visualizations...")
        plot_bankroll_over_time(results['bankroll_history'], 
                               save_path='bankroll_progression.png')
        plot_bet_distribution(results['bet_history'], 
                            save_path='bet_distribution.png')
    
    return results


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='College Basketball Betting System - Beat the Market with ML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with sample data
  python main.py
  
  # Use custom data file
  python main.py --data-file data/my_games.csv
  
  # Run with custom bankroll and save everything
  python main.py --bankroll 5000 --save-models --save-data --visualize
  
  # Quick test without visualizations
  python main.py --no-visualize
        """
    )
    
    parser.add_argument('--data-file', type=str, default=None,
                       help='Path to CSV file with game data')
    parser.add_argument('--bankroll', type=float, default=1000.0,
                       help='Initial bankroll for betting (default: 1000)')
    parser.add_argument('--save-models', action='store_true',
                       help='Save trained models to disk')
    parser.add_argument('--save-data', action='store_true',
                       help='Save collected data to disk')
    parser.add_argument('--visualize', action='store_true', default=True,
                       help='Generate visualizations')
    parser.add_argument('--no-visualize', action='store_false', dest='visualize',
                       help='Skip visualization generation')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("COLLEGE BASKETBALL BETTING SYSTEM")
    print("Machine Learning System to Beat the Sportsbook Market")
    print("="*60)
    
    try:
        # Step 1: Collect data
        df = collect_data(args)
        
        # Step 2: Engineer features
        matchup_df, engineer = engineer_features(df, args)
        
        # Step 3: Train models
        predictor, X_test, y_test, matchup_df = train_models(matchup_df, engineer, args)
        
        # Step 4: Run betting strategy
        results = run_betting_strategy(predictor, matchup_df, args)
        
        # Final summary
        print("\n" + "="*60)
        print("EXECUTION COMPLETE")
        print("="*60)
        print("\nThe system has been successfully built and tested!")
        print("\nKey Takeaways:")
        print("1. Machine learning models have been trained to predict game outcomes")
        print("2. Betting strategy identifies value bets with positive expected value")
        print("3. Backtest results show the system's historical performance")
        print("4. Kelly Criterion is used for optimal bet sizing")
        
        if results['metrics'].get('roi', 0) > 0.05:
            print("\n✓ This system demonstrates the potential to beat the market!")
        else:
            print("\n⚠ Results suggest refinement needed for consistent market-beating performance")
        
        print("\nIMPORTANT: Past performance does not guarantee future results.")
        print("Always bet responsibly and within your means.")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
