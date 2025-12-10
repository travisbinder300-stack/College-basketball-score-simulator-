"""
Feature engineering for basketball prediction models
"""

import pandas as pd
import numpy as np
from typing import List, Tuple
try:
    from ..config import ROLLING_WINDOW, MIN_GAMES_THRESHOLD
except ImportError:
    # Fallback for running as script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import ROLLING_WINDOW, MIN_GAMES_THRESHOLD


class FeatureEngineer:
    """Creates features for machine learning models"""
    
    def __init__(self, rolling_window: int = ROLLING_WINDOW):
        self.rolling_window = rolling_window
        
    def create_team_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling team statistics
        
        Args:
            df: Historical game data
            
        Returns:
            DataFrame with team statistics
        """
        df = df.sort_values('date').reset_index(drop=True)
        
        team_stats = []
        teams = set(df['home_team'].unique()).union(set(df['away_team'].unique()))
        
        for team in teams:
            # Home games
            home_games = df[df['home_team'] == team].copy()
            home_games['is_home'] = 1
            home_games['team_score'] = home_games['home_score']
            home_games['opp_score'] = home_games['away_score']
            home_games['team_fg_pct'] = home_games['home_fg_pct']
            home_games['team_3p_pct'] = home_games['home_3p_pct']
            home_games['team_reb'] = home_games['home_reb']
            home_games['team_ast'] = home_games['home_ast']
            home_games['team_to'] = home_games['home_to']
            home_games['won'] = home_games['home_won']
            
            # Away games
            away_games = df[df['away_team'] == team].copy()
            away_games['is_home'] = 0
            away_games['team_score'] = away_games['away_score']
            away_games['opp_score'] = away_games['home_score']
            away_games['team_fg_pct'] = away_games['away_fg_pct']
            away_games['team_3p_pct'] = away_games['away_3p_pct']
            away_games['team_reb'] = away_games['away_reb']
            away_games['team_ast'] = away_games['away_ast']
            away_games['team_to'] = away_games['away_to']
            away_games['won'] = 1 - away_games['home_won']
            
            # Combine
            all_games = pd.concat([home_games, away_games]).sort_values('date')
            all_games['team'] = team
            
            # Calculate rolling stats
            all_games['rolling_ppg'] = all_games['team_score'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['rolling_fg_pct'] = all_games['team_fg_pct'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['rolling_3p_pct'] = all_games['team_3p_pct'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['rolling_reb'] = all_games['team_reb'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['rolling_ast'] = all_games['team_ast'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['rolling_to'] = all_games['team_to'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['win_pct'] = all_games['won'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            all_games['games_played'] = range(1, len(all_games) + 1)
            
            team_stats.append(all_games)
        
        return pd.concat(team_stats, ignore_index=True)
    
    def create_matchup_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for each matchup combining both team statistics
        
        Args:
            df: Historical game data with team stats
            
        Returns:
            DataFrame with matchup features
        """
        # First create team stats
        team_stats_df = self.create_team_stats(df)
        
        # Create lookup dictionary for team stats by date
        team_stats_dict = {}
        for _, row in team_stats_df.iterrows():
            key = (row['team'], row['date'])
            team_stats_dict[key] = row
        
        matchup_features = []
        
        for _, game in df.iterrows():
            home_team = game['home_team']
            away_team = game['away_team']
            game_date = game['date']
            
            # Get most recent stats for each team before this game
            home_stats = None
            away_stats = None
            
            # Look for stats on game date
            if (home_team, game_date) in team_stats_dict:
                home_stats = team_stats_dict[(home_team, game_date)]
            if (away_team, game_date) in team_stats_dict:
                away_stats = team_stats_dict[(away_team, game_date)]
            
            # Skip if we don't have enough data
            if home_stats is None or away_stats is None:
                continue
            if home_stats['games_played'] < MIN_GAMES_THRESHOLD or away_stats['games_played'] < MIN_GAMES_THRESHOLD:
                continue
            
            # Create feature set
            features = {
                'game_id': game['game_id'],
                'date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                
                # Home team features
                'home_ppg': home_stats['rolling_ppg'],
                'home_fg_pct': home_stats['rolling_fg_pct'],
                'home_3p_pct': home_stats['rolling_3p_pct'],
                'home_reb': home_stats['rolling_reb'],
                'home_ast': home_stats['rolling_ast'],
                'home_to': home_stats['rolling_to'],
                'home_win_pct': home_stats['win_pct'],
                
                # Away team features
                'away_ppg': away_stats['rolling_ppg'],
                'away_fg_pct': away_stats['rolling_fg_pct'],
                'away_3p_pct': away_stats['rolling_3p_pct'],
                'away_reb': away_stats['rolling_reb'],
                'away_ast': away_stats['rolling_ast'],
                'away_to': away_stats['rolling_to'],
                'away_win_pct': away_stats['win_pct'],
                
                # Differential features (key predictors)
                'ppg_diff': home_stats['rolling_ppg'] - away_stats['rolling_ppg'],
                'fg_pct_diff': home_stats['rolling_fg_pct'] - away_stats['rolling_fg_pct'],
                '3p_pct_diff': home_stats['rolling_3p_pct'] - away_stats['rolling_3p_pct'],
                'reb_diff': home_stats['rolling_reb'] - away_stats['rolling_reb'],
                'ast_diff': home_stats['rolling_ast'] - away_stats['rolling_ast'],
                'to_diff': away_stats['rolling_to'] - home_stats['rolling_to'],  # Lower is better
                'win_pct_diff': home_stats['win_pct'] - away_stats['win_pct'],
                
                # Target variables
                'home_won': game['home_won'],
                'score_diff': game['score_diff'],
                'betting_spread': game['betting_spread']
            }
            
            matchup_features.append(features)
        
        return pd.DataFrame(matchup_features)
    
    def prepare_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare feature matrix and target variable
        
        Args:
            df: DataFrame with matchup features
            
        Returns:
            Tuple of (features DataFrame, target Series)
        """
        feature_cols = [
            'home_ppg', 'home_fg_pct', 'home_3p_pct', 'home_reb', 'home_ast', 'home_to', 'home_win_pct',
            'away_ppg', 'away_fg_pct', 'away_3p_pct', 'away_reb', 'away_ast', 'away_to', 'away_win_pct',
            'ppg_diff', 'fg_pct_diff', '3p_pct_diff', 'reb_diff', 'ast_diff', 'to_diff', 'win_pct_diff'
        ]
        
        X = df[feature_cols].copy()
        y = df['home_won'].copy()
        
        return X, y
