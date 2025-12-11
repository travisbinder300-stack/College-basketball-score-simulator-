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
            
            # NEW: Rest days effect (days since last game)
            all_games['rest_days'] = all_games['date'].diff().dt.days
            all_games['rest_days'] = all_games['rest_days'].fillna(7)  # First game default
            all_games['rest_days'] = all_games['rest_days'].clip(upper=10)  # Cap at 10 days
            
            # Rest advantage tracking (performance after different rest periods)
            # Performance improves with 2-4 days rest, declines with 0-1 or 5+
            all_games['optimal_rest'] = ((all_games['rest_days'] >= 2) & 
                                        (all_games['rest_days'] <= 4)).astype(int)
            all_games['tired'] = (all_games['rest_days'] <= 1).astype(int)  # Back-to-back or next day
            all_games['rusty'] = (all_games['rest_days'] >= 5).astype(int)  # Long layoff
            
            # Calculate win rate by rest category
            all_games['win_rate_optimal_rest'] = all_games[all_games['optimal_rest'] == 1]['won'].rolling(
                window=max(5, self.rolling_window), min_periods=1).mean()
            all_games['win_rate_tired'] = all_games[all_games['tired'] == 1]['won'].rolling(
                window=max(5, self.rolling_window), min_periods=1).mean()
            
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
        # Check cache first
        cache_key = (team1, team2, before_date)
        if cache_key in self.head_to_head_cache:
            return self.head_to_head_cache[cache_key]
        
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
        
        result = {
            'h2h_games': len(h2h_games),
            'team1_wins': team1_wins,
            'team1_win_pct': team1_wins / len(h2h_games),
            'avg_margin': np.mean(margins) if margins else 0
        }
        
        # Cache the result
        self.head_to_head_cache[cache_key] = result
        return result
    
    def _get_situational_performance(self, team_stats_df: pd.DataFrame, team: str, 
                                    before_date, situation: str) -> float:
        """
        Get team's performance in specific situations (coaching effect tendencies)
        
        Args:
            team_stats_df: Team statistics DataFrame
            team: Team name
            before_date: Only consider games before this date
            situation: Type of situation ('after_win', 'after_loss', 'vs_top', 'close_games')
            
        Returns:
            Win percentage in the specified situation
        """
        team_games = team_stats_df[
            (team_stats_df['team'] == team) &
            (team_stats_df['date'] < before_date)
        ].sort_values('date')
        
        if len(team_games) < 3:
            return 0.5  # Not enough data
        
        situation_games = []
        
        if situation == 'after_win':
            # Performance after winning previous game
            for i in range(1, len(team_games)):
                if team_games.iloc[i-1]['won'] == 1:
                    situation_games.append(team_games.iloc[i]['won'])
        
        elif situation == 'after_loss':
            # Performance after losing previous game (coaching adjustment/motivation)
            for i in range(1, len(team_games)):
                if team_games.iloc[i-1]['won'] == 0:
                    situation_games.append(team_games.iloc[i]['won'])
        
        elif situation == 'vs_top':
            # Performance against top 25% of opponents (big game performance)
            win_pct_threshold = team_games['win_pct'].quantile(0.75)
            for i in range(len(team_games)):
                # This is simplified - ideally would check opponent's actual win%
                if team_games.iloc[i]['win_pct'] >= win_pct_threshold:
                    situation_games.append(team_games.iloc[i]['won'])
        
        elif situation == 'close_games':
            # Performance in close games (margin ≤ 5 points) - coaching impact in clutch
            for i in range(len(team_games)):
                margin = abs(team_games.iloc[i].get('margin', 999))
                if margin <= 5:
                    situation_games.append(team_games.iloc[i]['won'])
        
        return np.mean(situation_games) if len(situation_games) >= 2 else 0.5
    
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
            
            # Calculate simplified features (optional expensive features can be added later)
            # For now, use defaults for h2h and sos to speed up processing
            h2h = {'h2h_games': 0, 'team1_win_pct': 0.5, 'avg_margin': 0}
            home_sos = 0.5
            away_sos = 0.5
            
            # Uncomment for full h2h and sos calculation (slower but more accurate):
            # h2h = self.calculate_head_to_head(df, home_team, away_team, game_date)
            # home_sos = self.calculate_strength_of_schedule(df, home_team, game_date)
            # away_sos = self.calculate_strength_of_schedule(df, away_team, game_date)
            
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
                
                # NEW: Rest days features
                'home_rest_days': home_stats.get('rest_days', 3),
                'away_rest_days': away_stats.get('rest_days', 3),
                'rest_advantage': home_stats.get('rest_days', 3) - away_stats.get('rest_days', 3),
                'home_optimal_rest': home_stats.get('optimal_rest', 0),
                'away_optimal_rest': away_stats.get('optimal_rest', 0),
                'home_tired': home_stats.get('tired', 0),
                'away_tired': away_stats.get('tired', 0),
                'home_rusty': home_stats.get('rusty', 0),
                'away_rusty': away_stats.get('rusty', 0),
                
                # NEW: Coaching effect tendencies (situational performance)
                # Teams perform differently in various situations - track this
                'home_after_win_pct': self._get_situational_performance(team_stats_df, home_team, game_date, 'after_win'),
                'away_after_win_pct': self._get_situational_performance(team_stats_df, away_team, game_date, 'after_win'),
                'home_after_loss_pct': self._get_situational_performance(team_stats_df, home_team, game_date, 'after_loss'),
                'away_after_loss_pct': self._get_situational_performance(team_stats_df, away_team, game_date, 'after_loss'),
                'home_vs_top_teams': self._get_situational_performance(team_stats_df, home_team, game_date, 'vs_top'),
                'away_vs_top_teams': self._get_situational_performance(team_stats_df, away_team, game_date, 'vs_top'),
                'home_close_game_pct': self._get_situational_performance(team_stats_df, home_team, game_date, 'close_games'),
                'away_close_game_pct': self._get_situational_performance(team_stats_df, away_team, game_date, 'close_games'),
                
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
            # Advanced features (pace, form, defense)
            'home_pace', 'away_pace', 'pace_diff',
            'home_recent_form', 'away_recent_form', 'form_diff',
            'home_margin', 'away_margin', 'margin_diff',
            'home_def_rating', 'away_def_rating', 'def_rating_diff',
            'h2h_games', 'home_h2h_win_pct', 'h2h_avg_margin',
            'home_sos', 'away_sos', 'sos_diff',
            # NEW: Rest days features
            'home_rest_days', 'away_rest_days', 'rest_advantage',
            'home_optimal_rest', 'away_optimal_rest',
            'home_tired', 'away_tired', 'home_rusty', 'away_rusty',
            # NEW: Coaching effect tendencies (situational performance)
            'home_after_win_pct', 'away_after_win_pct',
            'home_after_loss_pct', 'away_after_loss_pct',
            'home_vs_top_teams', 'away_vs_top_teams',
            'home_close_game_pct', 'away_close_game_pct'
        ]
        
        X = df[feature_cols].copy()
        y = df['home_won'].copy()
        
        return X, y
