"""
Data collector for college basketball statistics
This module provides functionality to collect and structure basketball data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class BasketballDataCollector:
    """Collects and processes college basketball data"""
    
    def __init__(self):
        self.teams_data = {}
        self.games_data = []
        
    def generate_sample_data(self, num_teams: int = 50, num_games: int = 2000, 
                           seasons: int = 3) -> pd.DataFrame:
        """
        Generate sample historical data for demonstration and testing with multiple seasons
        In production, this would fetch real data from APIs or web scraping
        
        Args:
            num_teams: Number of teams to generate data for
            num_games: Number of games to simulate per season
            seasons: Number of seasons to generate
            
        Returns:
            DataFrame with historical game data
        """
        np.random.seed(42)
        
        # Generate team ratings (strength)
        teams = [f"Team_{i}" for i in range(num_teams)]
        team_ratings = {team: np.random.normal(100, 15) for team in teams}
        
        # Generate team locations (for travel distance calculation)
        # Simulate geographic distribution across US (longitude -125 to -70, latitude 25 to 50)
        team_locations = {
            team: {
                'latitude': np.random.uniform(25, 50),
                'longitude': np.random.uniform(-125, -70)
            } for team in teams
        }
        
        games = []
        game_id_counter = 0
        
        # Generate data for multiple seasons
        for season in range(seasons):
            print(f"Generating season {season + 1}/{seasons}...")
            
            # Slightly adjust team ratings between seasons (team improvement/decline)
            if season > 0:
                for team in teams:
                    team_ratings[team] += np.random.normal(0, 3)
        
            for game_num in range(num_games):
                game_id = game_id_counter
                game_id_counter += 1
                
                # Select two random teams
                home_team, away_team = np.random.choice(teams, 2, replace=False)
                
                # Calculate expected performance with home court advantage
                home_rating = team_ratings[home_team] + 3  # Home court advantage
                away_rating = team_ratings[away_team]
                
                # Generate stats with some randomness
                home_ppg = np.random.normal(home_rating * 0.7, 10)
                away_ppg = np.random.normal(away_rating * 0.7, 10)
                
                home_fg_pct = np.random.normal(0.44 + (home_rating - 100) * 0.001, 0.05)
                away_fg_pct = np.random.normal(0.44 + (away_rating - 100) * 0.001, 0.05)
                
                home_3p_pct = np.random.normal(0.34 + (home_rating - 100) * 0.001, 0.05)
                away_3p_pct = np.random.normal(0.34 + (away_rating - 100) * 0.001, 0.05)
                
                home_reb = np.random.normal(35 + (home_rating - 100) * 0.1, 5)
                away_reb = np.random.normal(35 + (away_rating - 100) * 0.1, 5)
                
                home_ast = np.random.normal(15 + (home_rating - 100) * 0.05, 3)
                away_ast = np.random.normal(15 + (away_rating - 100) * 0.05, 3)
                
                home_to = np.random.normal(12 - (home_rating - 100) * 0.02, 3)
                away_to = np.random.normal(12 - (away_rating - 100) * 0.02, 3)
                
                # Calculate actual score with randomness
                rating_diff = home_rating - away_rating
                win_prob = 1 / (1 + np.exp(-rating_diff / 15))
                home_won = np.random.random() < win_prob
                
                if home_won:
                    home_score = np.random.normal(home_ppg + 2, 8)
                    away_score = np.random.normal(away_ppg - 2, 8)
                else:
                    home_score = np.random.normal(home_ppg - 2, 8)
                    away_score = np.random.normal(away_ppg + 2, 8)
                
                # Generate betting line (spread)
                true_spread = rating_diff * 0.5
                betting_spread = true_spread + np.random.normal(0, 2)  # Add noise to create opportunities
                
                # Date calculation: spread games across season
                days_back = (seasons * num_games) - game_id
                game_date = datetime.now() - timedelta(days=days_back)
                
                # Calculate travel distance for away team (haversine formula approximation)
                home_loc = team_locations[home_team]
                away_loc = team_locations[away_team]
                
                # Simplified distance calculation (rough miles estimate)
                lat_diff = abs(home_loc['latitude'] - away_loc['latitude'])
                lon_diff = abs(home_loc['longitude'] - away_loc['longitude'])
                distance_miles = np.sqrt(lat_diff**2 * 69**2 + lon_diff**2 * 54.6**2)  # Approximate
                
                # Estimate travel time (hours): short flight ~2-3hrs, long flight ~5-6hrs, driving varies
                if distance_miles < 200:
                    travel_time = distance_miles / 60  # Bus travel at 60mph average
                elif distance_miles < 500:
                    travel_time = 3 + (distance_miles - 200) / 300  # Short flight + logistics
                else:
                    travel_time = 5 + (distance_miles - 500) / 500  # Long flight + logistics
                
                # Cap at reasonable max (cross-country is ~6 hours flight + 4 hours logistics = 10)
                travel_time = min(travel_time, 10)
                
                games.append({
                    'game_id': game_id,
                    'date': game_date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': max(40, home_score),
                    'away_score': max(40, away_score),
                    'home_ppg': home_ppg,
                    'away_ppg': away_ppg,
                    'home_fg_pct': np.clip(home_fg_pct, 0.3, 0.6),
                    'away_fg_pct': np.clip(away_fg_pct, 0.3, 0.6),
                    'home_3p_pct': np.clip(home_3p_pct, 0.2, 0.5),
                    'away_3p_pct': np.clip(away_3p_pct, 0.2, 0.5),
                    'home_reb': max(20, home_reb),
                    'away_reb': max(20, away_reb),
                    'home_ast': max(5, home_ast),
                    'away_ast': max(5, away_ast),
                    'home_to': max(5, home_to),
                    'away_to': max(5, away_to),
                    'betting_spread': betting_spread,
                    'home_won': int(home_won),
                    'travel_distance': distance_miles,
                    'travel_time': travel_time
                })
        
        df = pd.DataFrame(games)
        df['score_diff'] = df['home_score'] - df['away_score']
        df['total_score'] = df['home_score'] + df['away_score']
        
        return df
    
    def load_from_file(self, filepath: str) -> pd.DataFrame:
        """
        Load basketball data from a CSV file
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with game data
        """
        try:
            df = pd.read_csv(filepath)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            print(f"File {filepath} not found. Generating sample data instead.")
            return self.generate_sample_data()
    
    def save_data(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Save data to CSV file
        
        Args:
            df: DataFrame to save
            filepath: Path to save to
        """
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
