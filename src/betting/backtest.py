"""
Backtesting framework for evaluating betting strategy
"""

import pandas as pd
import numpy as np
from typing import Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from betting.strategy import BettingStrategy


class Backtester:
    """Backtests betting strategies on historical data"""
    
    def __init__(self, initial_bankroll: float = 1000.0):
        self.initial_bankroll = initial_bankroll
        self.strategy = BettingStrategy(initial_bankroll)
        
    def run_backtest(self, predictions_df: pd.DataFrame, 
                     actual_results_df: pd.DataFrame) -> Dict:
        """
        Run backtest on historical predictions
        
        Args:
            predictions_df: DataFrame with model predictions
            actual_results_df: DataFrame with actual game results
            
        Returns:
            Dictionary with backtest results
        """
        # Find value bets
        value_bets = self.strategy.find_value_bets(predictions_df)
        
        if len(value_bets) == 0:
            print("No value bets found in the dataset")
            return {
                'total_bets': 0,
                'bankroll_history': [self.initial_bankroll],
                'metrics': {}
            }
        
        print(f"\nFound {len(value_bets)} value betting opportunities")
        
        # Track bankroll over time
        bankroll_history = [self.initial_bankroll]
        
        # Simulate each bet
        for _, bet in value_bets.iterrows():
            game_id = bet.get('game_id')
            
            # Find actual result
            if game_id is not None:
                actual_game = actual_results_df[actual_results_df['game_id'] == game_id]
            else:
                # Match by teams if game_id not available
                actual_game = actual_results_df[
                    (actual_results_df['home_team'] == bet['home_team']) &
                    (actual_results_df['away_team'] == bet['away_team'])
                ]
            
            if len(actual_game) == 0:
                continue
            
            actual_game = actual_game.iloc[0]
            bet_amount = bet['recommended_bet_amount']
            
            # Determine if bet won
            if bet['side'] == 'home':
                bet_won = actual_game['home_won'] == 1
            else:
                bet_won = actual_game['home_won'] == 0
            
            # Calculate profit/loss (assuming -110 odds, typical for spreads)
            if bet_won:
                profit = bet_amount * 0.909  # Win at -110 odds
                result = 'win'
            else:
                profit = -bet_amount
                result = 'loss'
            
            # Record bet
            self.strategy.record_bet(bet.to_dict(), result, profit)
            bankroll_history.append(self.strategy.current_bankroll)
        
        # Calculate performance metrics
        metrics = self.strategy.get_performance_metrics()
        
        return {
            'total_bets': len(value_bets),
            'bankroll_history': bankroll_history,
            'metrics': metrics,
            'bet_history': self.strategy.bet_history
        }
    
    def print_results(self, results: Dict) -> None:
        """
        Print backtest results
        
        Args:
            results: Results dictionary from run_backtest
        """
        metrics = results['metrics']
        
        if not metrics:
            print("\nNo bets were placed")
            return
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        
        print(f"\nBetting Performance:")
        print(f"  Total Bets: {metrics['total_bets']}")
        print(f"  Wins: {metrics['wins']}")
        print(f"  Losses: {metrics['losses']}")
        print(f"  Win Rate: {metrics['win_rate']:.2%}")
        
        print(f"\nBankroll Performance:")
        print(f"  Initial Bankroll: ${metrics['initial_bankroll']:.2f}")
        print(f"  Final Bankroll: ${metrics['current_bankroll']:.2f}")
        print(f"  Total Profit: ${metrics['total_profit']:.2f}")
        print(f"  ROI: {metrics['roi']:.2%}")
        
        print(f"\nBet Sizing:")
        print(f"  Average Bet Size: ${metrics['avg_bet_size']:.2f}")
        print(f"  Average Profit per Bet: ${metrics['avg_profit_per_bet']:.2f}")
        
        print("\n" + "="*60)
        
        # Determine if system beats the market
        if metrics['roi'] > 0.05 and metrics['win_rate'] > 0.54:
            print("✓ SYSTEM BEATS THE MARKET!")
            print("  This system shows positive expected value and")
            print("  outperforms typical sportsbook requirements.")
        elif metrics['roi'] > 0:
            print("⚠ SYSTEM SHOWS POSITIVE ROI")
            print("  But may need more data or refinement to consistently")
            print("  beat the market after accounting for variance.")
        else:
            print("✗ SYSTEM NEEDS IMPROVEMENT")
            print("  Current performance does not beat the market.")
            print("  Consider refining features, models, or bet selection criteria.")
        
        print("="*60 + "\n")
