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
        self.head_to_head_cache = {}  # Cache for head-to-head records
        
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
            
            # NEW: Additional advanced features
            # Pace of play (possessions per game)
            all_games['pace'] = (all_games['team_score'] + all_games['opp_score']) / 2
            all_games['rolling_pace'] = all_games['pace'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            
            # Home/Away performance splits
            all_games['rolling_home_win_pct'] = all_games[all_games['is_home'] == 1]['won'].rolling(
                window=max(3, self.rolling_window // 2), min_periods=1).mean()
            all_games['rolling_away_win_pct'] = all_games[all_games['is_home'] == 0]['won'].rolling(
                window=max(3, self.rolling_window // 2), min_periods=1).mean()
            
            # Recent form (last 3 games momentum)
            all_games['recent_form'] = all_games['won'].rolling(
                window=3, min_periods=1).mean()
            
            # Scoring margin
            all_games['margin'] = all_games['team_score'] - all_games['opp_score']
            all_games['rolling_margin'] = all_games['margin'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            
            # Defensive rating (opponent points per game)
            all_games['opp_ppg'] = all_games['opp_score']
            all_games['rolling_opp_ppg'] = all_games['opp_ppg'].rolling(
                window=self.rolling_window, min_periods=1).mean()
            
            team_stats.append(all_games)
        
        return pd.concat(team_stats, ignore_index=True)
    
    def calculate_head_to_head(self, df: pd.DataFrame, team1: str, team2: str, before_date) -> dict:
        """
        Calculate head-to-head record between two teams
        
        Args:
            df: Historical game data
            team1: First team
            team2: Second team
            before_date: Only consider games before this date
            
        Returns:
            Dict with head-to-head statistics
        """
        # Filter games between these two teams before the given date
        h2h_games = df[
            (((df['home_team'] == team1) & (df['away_team'] == team2)) |
             ((df['home_team'] == team2) & (df['away_team'] == team1))) &
            (df['date'] < before_date)
        ]
        
        if len(h2h_games) == 0:
            return {'h2h_games': 0, 'team1_wins': 0, 'team1_win_pct': 0.5, 'avg_margin': 0}
        
        team1_wins = 0
        margins = []
        
        for _, game in h2h_games.iterrows():
            if game['home_team'] == team1:
                won = game['home_won']
                margin = game['score_diff']
            else:
                won = 1 - game['home_won']
                margin = -game['score_diff']
            
            team1_wins += won
            margins.append(margin)
        
        return {
            'h2h_games': len(h2h_games),
            'team1_wins': team1_wins,
            'team1_win_pct': team1_wins / len(h2h_games),
            'avg_margin': np.mean(margins) if margins else 0
        }
    
    def calculate_strength_of_schedule(self, df: pd.DataFrame, team: str, before_date) -> float:
        """
        Calculate strength of schedule for a team
        
        Args:
            df: Historical game data
            team: Team name
            before_date: Only consider games before this date
            
        Returns:
            Average win percentage of opponents
        """
        # Get games for this team
        team_games = df[
            ((df['home_team'] == team) | (df['away_team'] == team)) &
            (df['date'] < before_date)
        ]
        
        if len(team_games) == 0:
            return 0.5
        
        opponent_win_pcts = []
        
        for _, game in team_games.iterrows():
            opponent = game['away_team'] if game['home_team'] == team else game['home_team']
            
            # Calculate opponent's win percentage before this game
            opp_games = df[
                ((df['home_team'] == opponent) | (df['away_team'] == opponent)) &
                (df['date'] < game['date'])
            ]
            
            if len(opp_games) > 0:
                opp_wins = 0
                for _, opp_game in opp_games.iterrows():
                    if opp_game['home_team'] == opponent:
                        opp_wins += opp_game['home_won']
                    else:
                        opp_wins += (1 - opp_game['home_won'])
                
                opponent_win_pcts.append(opp_wins / len(opp_games))
        
        return np.mean(opponent_win_pcts) if opponent_win_pcts else 0.5
    
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
            
            # Calculate head-to-head and strength of schedule
            h2h = self.calculate_head_to_head(df, home_team, away_team, game_date)
            home_sos = self.calculate_strength_of_schedule(df, home_team, game_date)
            away_sos = self.calculate_strength_of_schedule(df, away_team, game_date)
            
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
                
                # NEW: Advanced features
                'home_pace': home_stats.get('rolling_pace', 70),
                'away_pace': away_stats.get('rolling_pace', 70),
                'pace_diff': home_stats.get('rolling_pace', 70) - away_stats.get('rolling_pace', 70),
                
                'home_recent_form': home_stats.get('recent_form', 0.5),
                'away_recent_form': away_stats.get('recent_form', 0.5),
                'form_diff': home_stats.get('recent_form', 0.5) - away_stats.get('recent_form', 0.5),
                
                'home_margin': home_stats.get('rolling_margin', 0),
                'away_margin': away_stats.get('rolling_margin', 0),
                'margin_diff': home_stats.get('rolling_margin', 0) - away_stats.get('rolling_margin', 0),
                
                'home_def_rating': home_stats.get('rolling_opp_ppg', 70),
                'away_def_rating': away_stats.get('rolling_opp_ppg', 70),
                'def_rating_diff': away_stats.get('rolling_opp_ppg', 70) - home_stats.get('rolling_opp_ppg', 70),
                
                # Head-to-head features
                'h2h_games': h2h['h2h_games'],
                'home_h2h_win_pct': h2h['team1_win_pct'],
                'h2h_avg_margin': h2h['avg_margin'],
                
                # Strength of schedule
                'home_sos': home_sos,
                'away_sos': away_sos,
                'sos_diff': home_sos - away_sos,
                
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
            # Basic team stats
            'home_ppg', 'home_fg_pct', 'home_3p_pct', 'home_reb', 'home_ast', 'home_to', 'home_win_pct',
            'away_ppg', 'away_fg_pct', 'away_3p_pct', 'away_reb', 'away_ast', 'away_to', 'away_win_pct',
            # Basic differentials
            'ppg_diff', 'fg_pct_diff', '3p_pct_diff', 'reb_diff', 'ast_diff', 'to_diff', 'win_pct_diff',
            # NEW: Advanced features
            'home_pace', 'away_pace', 'pace_diff',
            'home_recent_form', 'away_recent_form', 'form_diff',
            'home_margin', 'away_margin', 'margin_diff',
            'home_def_rating', 'away_def_rating', 'def_rating_diff',
            'h2h_games', 'home_h2h_win_pct', 'h2h_avg_margin',
            'home_sos', 'away_sos', 'sos_diff'
        ]
        
        X = df[feature_cols].copy()
        y = df['home_won'].copy()
        
        return X, y
