"""
Betting strategy and bankroll management
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
try:
    from ..config import (MIN_EDGE_THRESHOLD, MAX_EDGE_THRESHOLD, KELLY_FRACTION,
                        MAX_BET_SIZE, MIN_BET_SIZE, JUICE_ADJUSTMENT)
except ImportError:
    # Fallback for running as script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import (MIN_EDGE_THRESHOLD, MAX_EDGE_THRESHOLD, KELLY_FRACTION,
                        MAX_BET_SIZE, MIN_BET_SIZE, JUICE_ADJUSTMENT)


class BettingStrategy:
    """Implements betting strategies and bankroll management"""
    
    def __init__(self, initial_bankroll: float = 1000.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.bet_history = []
        
    def american_to_probability(self, odds: float) -> float:
        """
        Convert American odds to implied probability
        
        Args:
            odds: American odds (e.g., -110, +150)
            
        Returns:
            Implied probability
        """
        if odds < 0:
            return (-odds) / (-odds + 100)
        else:
            return 100 / (odds + 100)
    
    def probability_to_american(self, prob: float) -> float:
        """
        Convert probability to American odds
        
        Args:
            prob: Probability
            
        Returns:
            American odds
        """
        # Clamp probability to valid range to prevent division by zero
        prob = max(0.01, min(0.99, prob))
        
        if prob >= 0.5:
            return -(prob * 100) / (1 - prob)
        else:
            return ((1 - prob) * 100) / prob
    
    def calculate_edge(self, model_prob: float, market_prob: float) -> float:
        """
        Calculate betting edge
        
        Args:
            model_prob: Model's predicted probability
            market_prob: Market implied probability
            
        Returns:
            Edge (positive means value)
        """
        return model_prob - market_prob
    
    def kelly_criterion(self, win_prob: float, odds: float, fraction: float = KELLY_FRACTION) -> float:
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            win_prob: Probability of winning
            odds: Decimal odds (e.g., 2.0 for even money)
            fraction: Fraction of Kelly to use (for conservative betting)
            
        Returns:
            Bet size as fraction of bankroll
        """
        # Kelly formula: f = (bp - q) / b
        # where b = odds - 1, p = win probability, q = 1 - p
        b = odds - 1
        q = 1 - win_prob
        
        kelly = (b * win_prob - q) / b
        
        # Apply fraction for conservative betting
        kelly = kelly * fraction
        
        # Ensure within bounds
        kelly = max(0, min(kelly, MAX_BET_SIZE))
        
        return kelly if kelly >= MIN_BET_SIZE else 0
    
    def find_value_bets(self, predictions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify value betting opportunities
        
        Args:
            predictions_df: DataFrame with predictions and betting lines
            
        Returns:
            DataFrame with value bets and recommended sizes
        """
        value_bets = []
        
        for _, row in predictions_df.iterrows():
            model_prob = row['home_win_prob']
            betting_spread = row['betting_spread']
            
            # Convert spread to approximate moneyline probability
            # Using logistic function: spread ≈ -4 * log(p/(1-p))
            # The coefficient 4 represents the typical point spread where the 
            # probability is ~75% (roughly 8-point favorite)
            # This is derived from historical sports betting markets
            if betting_spread == 0:
                market_prob = 0.5
            else:
                # Approximate market probability from spread using inverse logistic
                market_prob = 1 / (1 + np.exp(betting_spread / 4))
            
            # Adjust for juice
            market_prob_adjusted = market_prob + JUICE_ADJUSTMENT
            
            # Calculate edge for home team
            home_edge = self.calculate_edge(model_prob, market_prob_adjusted)
            away_edge = self.calculate_edge(1 - model_prob, 1 - market_prob_adjusted)
            
            # Check for value bets
            if home_edge >= MIN_EDGE_THRESHOLD and home_edge <= MAX_EDGE_THRESHOLD:
                # Convert to decimal odds for Kelly
                market_odds = 1 / market_prob
                bet_size = self.kelly_criterion(model_prob, market_odds)
                
                if bet_size > 0:
                    value_bets.append({
                        'game_id': row.get('game_id', None),
                        'home_team': row['home_team'],
                        'away_team': row['away_team'],
                        'bet_on': row['home_team'],
                        'model_prob': model_prob,
                        'market_prob': market_prob,
                        'edge': home_edge,
                        'recommended_bet_pct': bet_size,
                        'recommended_bet_amount': bet_size * self.current_bankroll,
                        'expected_value': home_edge * bet_size * self.current_bankroll,
                        'betting_spread': betting_spread,
                        'side': 'home'
                    })
            
            if away_edge >= MIN_EDGE_THRESHOLD and away_edge <= MAX_EDGE_THRESHOLD:
                market_odds = 1 / (1 - market_prob)
                bet_size = self.kelly_criterion(1 - model_prob, market_odds)
                
                if bet_size > 0:
                    value_bets.append({
                        'game_id': row.get('game_id', None),
                        'home_team': row['home_team'],
                        'away_team': row['away_team'],
                        'bet_on': row['away_team'],
                        'model_prob': 1 - model_prob,
                        'market_prob': 1 - market_prob,
                        'edge': away_edge,
                        'recommended_bet_pct': bet_size,
                        'recommended_bet_amount': bet_size * self.current_bankroll,
                        'expected_value': away_edge * bet_size * self.current_bankroll,
                        'betting_spread': betting_spread,
                        'side': 'away'
                    })
        
        if not value_bets:
            return pd.DataFrame()
        
        df = pd.DataFrame(value_bets)
        df = df.sort_values('expected_value', ascending=False)
        
        return df
    
    def record_bet(self, bet_info: dict, result: str, profit: float) -> None:
        """
        Record a bet result
        
        Args:
            bet_info: Dictionary with bet information
            result: 'win' or 'loss'
            profit: Profit/loss amount
        """
        self.current_bankroll += profit
        
        bet_record = {
            **bet_info,
            'result': result,
            'profit': profit,
            'bankroll_after': self.current_bankroll
        }
        
        self.bet_history.append(bet_record)
    
    def get_performance_metrics(self) -> dict:
        """
        Calculate performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.bet_history:
            return {}
        
        df = pd.DataFrame(self.bet_history)
        
        total_bets = len(df)
        wins = len(df[df['result'] == 'win'])
        win_rate = wins / total_bets if total_bets > 0 else 0
        
        total_profit = self.current_bankroll - self.initial_bankroll
        roi = total_profit / self.initial_bankroll
        
        avg_bet = df['recommended_bet_amount'].mean()
        avg_profit_per_bet = df['profit'].mean()
        
        metrics = {
            'total_bets': total_bets,
            'wins': wins,
            'losses': total_bets - wins,
            'win_rate': win_rate,
            'initial_bankroll': self.initial_bankroll,
            'current_bankroll': self.current_bankroll,
            'total_profit': total_profit,
            'roi': roi,
            'avg_bet_size': avg_bet,
            'avg_profit_per_bet': avg_profit_per_bet
        }
        
        return metrics
