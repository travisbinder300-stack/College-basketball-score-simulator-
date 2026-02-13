#!/usr/bin/env python3
"""
Custom Data Loader

Loads user-provided NBA prop betting data from the user_data directory.
This replaces all example/template data with your actual data.

Usage:
    from custom_data_loader import CustomDataLoader
    
    loader = CustomDataLoader()
    players = loader.get_players()
    props = loader.get_props()
    lineups = loader.get_lineups()
    shot_charts = loader.get_shot_charts()
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class CustomDataLoader:
    """Loads and provides access to custom user data"""
    
    def __init__(self, data_dir: str = "user_data"):
        """
        Initialize the data loader
        
        Args:
            data_dir: Directory containing user data files
        """
        self.data_dir = data_dir
        self._players = None
        self._props = None
        self._lineups = None
        self._shot_charts = None
        self._loaded = False
        
    def _load_json(self, filename: str) -> Optional[Dict]:
        """Load JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: {filename} not found in {self.data_dir}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filename}: {e}")
            return None
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def load_all(self) -> bool:
        """
        Load all data files
        
        Returns:
            True if all files loaded successfully, False otherwise
        """
        print(f"Loading data from {self.data_dir}...")
        
        if not os.path.exists(self.data_dir):
            print(f"Error: Directory {self.data_dir} does not exist")
            print("Please create the directory and add your data files")
            print("See data_templates/ for file format examples")
            return False
        
        # Load each file
        players_data = self._load_json("players.json")
        props_data = self._load_json("props.json")
        lineups_data = self._load_json("lineups.json")
        shot_charts_data = self._load_json("shot_charts.json")
        
        # Store data
        self._players = players_data.get("players", []) if players_data else []
        self._props = props_data.get("props", []) if props_data else []
        self._lineups = lineups_data.get("lineups", []) if lineups_data else []
        
        if shot_charts_data:
            self._shot_charts = {
                "shot_charts": shot_charts_data.get("shot_charts", []),
                "defenders": shot_charts_data.get("defenders", []),
                "team_defenses": shot_charts_data.get("team_defenses", [])
            }
        else:
            self._shot_charts = {"shot_charts": [], "defenders": [], "team_defenses": []}
        
        self._loaded = True
        
        # Print summary
        print(f"✓ Loaded {len(self._players)} players")
        print(f"✓ Loaded {len(self._props)} props")
        print(f"✓ Loaded {len(self._lineups)} lineup configurations")
        print(f"✓ Loaded {len(self._shot_charts['shot_charts'])} shot charts")
        print(f"✓ Loaded {len(self._shot_charts['defenders'])} defenders")
        print(f"✓ Loaded {len(self._shot_charts['team_defenses'])} team defenses")
        
        return True
    
    def get_players(self, team: Optional[str] = None, active_only: bool = True) -> List[Dict]:
        """
        Get players
        
        Args:
            team: Filter by team abbreviation (optional)
            active_only: Only return active players
            
        Returns:
            List of player dictionaries
        """
        if not self._loaded:
            self.load_all()
        
        players = self._players
        
        if active_only:
            players = [p for p in players if p.get("active", True)]
        
        if team:
            players = [p for p in players if p.get("team") == team]
        
        return players
    
    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        """Get a specific player by ID"""
        if not self._loaded:
            self.load_all()
        
        for player in self._players:
            if player.get("player_id") == player_id:
                return player
        
        return None
    
    def get_props(self, player_id: Optional[str] = None, 
                  prop_type: Optional[str] = None,
                  date: Optional[str] = None) -> List[Dict]:
        """
        Get props
        
        Args:
            player_id: Filter by player ID (optional)
            prop_type: Filter by prop type (optional)
            date: Filter by game date (optional)
            
        Returns:
            List of prop dictionaries
        """
        if not self._loaded:
            self.load_all()
        
        props = self._props
        
        if player_id:
            props = [p for p in props if p.get("player_id") == player_id]
        
        if prop_type:
            props = [p for p in props if p.get("prop_type") == prop_type]
        
        if date:
            props = [p for p in props if p.get("game_date") == date]
        
        return props
    
    def get_lineups(self, player_id: Optional[str] = None,
                    team: Optional[str] = None) -> List[Dict]:
        """
        Get lineup configurations
        
        Args:
            player_id: Filter by player ID (optional)
            team: Filter by team (optional)
            
        Returns:
            List of lineup configuration dictionaries
        """
        if not self._loaded:
            self.load_all()
        
        lineups = self._lineups
        
        if player_id:
            lineups = [l for l in lineups if l.get("player_id") == player_id]
        
        if team:
            lineups = [l for l in lineups if l.get("team") == team]
        
        return lineups
    
    def get_shot_chart(self, player_id: str) -> Optional[Dict]:
        """Get shot chart for a specific player"""
        if not self._loaded:
            self.load_all()
        
        for chart in self._shot_charts["shot_charts"]:
            if chart.get("player_id") == player_id:
                return chart
        
        return None
    
    def get_defender(self, defender_id: str) -> Optional[Dict]:
        """Get defender stats for a specific player"""
        if not self._loaded:
            self.load_all()
        
        for defender in self._shot_charts["defenders"]:
            if defender.get("defender_id") == defender_id:
                return defender
        
        return None
    
    def get_team_defense(self, team: str) -> Optional[Dict]:
        """Get team defense stats"""
        if not self._loaded:
            self.load_all()
        
        for defense in self._shot_charts["team_defenses"]:
            if defense.get("team") == team:
                return defense
        
        return None
    
    def get_teams(self) -> List[str]:
        """Get list of all teams in the dataset"""
        if not self._loaded:
            self.load_all()
        
        teams = set()
        for player in self._players:
            if player.get("team"):
                teams.add(player["team"])
        
        return sorted(list(teams))
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of loaded data"""
        if not self._loaded:
            self.load_all()
        
        return {
            "total_players": len(self._players),
            "active_players": len([p for p in self._players if p.get("active", True)]),
            "total_props": len(self._props),
            "total_lineups": len(self._lineups),
            "total_shot_charts": len(self._shot_charts["shot_charts"]),
            "total_defenders": len(self._shot_charts["defenders"]),
            "total_team_defenses": len(self._shot_charts["team_defenses"]),
            "teams": self.get_teams(),
            "data_directory": self.data_dir
        }


# Example usage
if __name__ == "__main__":
    print("Custom Data Loader - Example Usage\n")
    print("="*60)
    
    # Initialize loader
    loader = CustomDataLoader()
    
    # Load all data
    if not loader.load_all():
        print("\nError: Could not load data")
        print("\nTo use this loader:")
        print("1. Copy templates from data_templates/ to user_data/")
        print("2. Fill in your actual data")
        print("3. Run: python validate_data.py")
        print("4. Use this loader in your code")
        exit(1)
    
    # Get summary
    print("\n" + "="*60)
    print("DATA SUMMARY")
    print("="*60)
    summary = loader.get_data_summary()
    for key, value in summary.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(value) if value else 'None'}")
        else:
            print(f"{key}: {value}")
    
    # Example queries
    print("\n" + "="*60)
    print("EXAMPLE QUERIES")
    print("="*60)
    
    players = loader.get_players()
    if players:
        print(f"\nFirst player: {players[0].get('name')} ({players[0].get('team')})")
    
    props = loader.get_props()
    if props:
        print(f"First prop: {props[0].get('prop_type')} - Line: {props[0].get('line')}")
    
    lineups = loader.get_lineups()
    if lineups:
        print(f"First lineup: {lineups[0].get('player_id')} - Minutes: {lineups[0].get('minutes_per_game')}")
    
    print("\n" + "="*60)
    print("\nData loaded successfully! You can now use this in your analysis.")
