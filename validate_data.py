#!/usr/bin/env python3
"""
Data Validation Script

Validates user-provided NBA prop betting data.
Run this before using your custom data to ensure it's properly formatted.

Usage:
    python validate_data.py
    python validate_data.py --verbose
    python validate_data.py --fix-common-issues
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple

class DataValidator:
    def __init__(self, data_dir: str = "user_data", verbose: bool = False):
        self.data_dir = data_dir
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = f"[{level}]"
            print(f"{prefix} {message}")
    
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        self.log(message, "ERROR")
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
        self.log(message, "WARNING")
    
    def load_json(self, filename: str) -> Tuple[bool, Any]:
        """Load and parse JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            self.add_error(f"Required file not found: {filename}")
            return False, None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.log(f"Successfully loaded {filename}")
            return True, data
        except json.JSONDecodeError as e:
            self.add_error(f"Invalid JSON in {filename}: {e}")
            return False, None
        except Exception as e:
            self.add_error(f"Error loading {filename}: {e}")
            return False, None
    
    def validate_players(self, data: Dict) -> bool:
        """Validate players data"""
        self.log("Validating players data...")
        
        if "players" not in data:
            self.add_error("players.json missing 'players' array")
            return False
        
        players = data["players"]
        if not isinstance(players, list):
            self.add_error("'players' must be an array")
            return False
        
        if len(players) == 0:
            self.add_warning("No players found in players.json")
        
        player_ids = set()
        required_fields = ["player_id", "name", "team", "position", "active"]
        
        for i, player in enumerate(players):
            # Check required fields
            for field in required_fields:
                if field not in player:
                    self.add_error(f"Player {i}: Missing required field '{field}'")
            
            # Check for duplicate IDs
            player_id = player.get("player_id")
            if player_id:
                if player_id in player_ids:
                    self.add_error(f"Duplicate player_id: {player_id}")
                player_ids.add(player_id)
            
            # Check if using template data
            if player_id and "example" in player_id.lower():
                self.add_warning(f"Player {i}: Still using template/example data")
            
            # Validate position
            valid_positions = ["PG", "SG", "SF", "PF", "C", "G", "F"]
            position = player.get("position", "")
            if position and position not in valid_positions:
                self.add_warning(f"Player {player_id}: Invalid position '{position}'")
        
        self.log(f"Found {len(players)} players")
        return len(self.errors) == 0
    
    def validate_props(self, data: Dict, player_ids: set) -> bool:
        """Validate props data"""
        self.log("Validating props data...")
        
        if "props" not in data:
            self.add_error("props.json missing 'props' array")
            return False
        
        props = data["props"]
        if not isinstance(props, list):
            self.add_error("'props' must be an array")
            return False
        
        if len(props) == 0:
            self.add_warning("No props found in props.json")
        
        required_fields = ["prop_id", "player_id", "game_date", "opponent", "prop_type", "line"]
        valid_prop_types = ["points", "rebounds", "assists", "threes", "blocks", "steals", "turnovers"]
        
        for i, prop in enumerate(props):
            # Check required fields
            for field in required_fields:
                if field not in prop:
                    self.add_error(f"Prop {i}: Missing required field '{field}'")
            
            # Validate player_id exists
            player_id = prop.get("player_id")
            if player_id and player_ids and player_id not in player_ids:
                self.add_error(f"Prop {i}: player_id '{player_id}' not found in players.json")
            
            # Validate date format
            game_date = prop.get("game_date")
            if game_date:
                try:
                    datetime.strptime(game_date, "%Y-%m-%d")
                except ValueError:
                    self.add_error(f"Prop {i}: Invalid date format '{game_date}' (use YYYY-MM-DD)")
            
            # Validate prop type
            prop_type = prop.get("prop_type")
            if prop_type and prop_type not in valid_prop_types:
                self.add_warning(f"Prop {i}: Uncommon prop_type '{prop_type}'")
            
            # Validate line is numeric
            line = prop.get("line")
            if line is not None and not isinstance(line, (int, float)):
                self.add_error(f"Prop {i}: 'line' must be a number")
            
            # Check template data
            if prop.get("prop_id") and "example" in str(prop.get("prop_id")).lower():
                self.add_warning(f"Prop {i}: Still using template/example data")
        
        self.log(f"Found {len(props)} props")
        return len(self.errors) == 0
    
    def validate_lineups(self, data: Dict, player_ids: set) -> bool:
        """Validate lineups data"""
        self.log("Validating lineups data...")
        
        if "lineups" not in data:
            self.add_error("lineups.json missing 'lineups' array")
            return False
        
        lineups = data["lineups"]
        if not isinstance(lineups, list):
            self.add_error("'lineups' must be an array")
            return False
        
        required_fields = ["team", "player_id"]
        
        for i, lineup in enumerate(lineups):
            # Check required fields
            for field in required_fields:
                if field not in lineup:
                    self.add_error(f"Lineup {i}: Missing required field '{field}'")
            
            # Validate player_id exists
            player_id = lineup.get("player_id")
            if player_id and player_ids and player_id not in player_ids:
                self.add_error(f"Lineup {i}: player_id '{player_id}' not found in players.json")
            
            # Validate with_players and without_players
            for field in ["with_players", "without_players"]:
                if field in lineup:
                    player_list = lineup[field]
                    if not isinstance(player_list, list):
                        self.add_error(f"Lineup {i}: '{field}' must be an array")
                    elif player_ids:
                        for pid in player_list:
                            if pid not in player_ids:
                                self.add_error(f"Lineup {i}: {field} contains unknown player_id '{pid}'")
        
        self.log(f"Found {len(lineups)} lineup configurations")
        return len(self.errors) == 0
    
    def validate_shot_charts(self, data: Dict, player_ids: set) -> bool:
        """Validate shot charts data"""
        self.log("Validating shot charts data...")
        
        if "shot_charts" not in data:
            self.add_warning("shot_charts.json missing 'shot_charts' array")
        else:
            shot_charts = data["shot_charts"]
            if not isinstance(shot_charts, list):
                self.add_error("'shot_charts' must be an array")
            else:
                for i, chart in enumerate(shot_charts):
                    player_id = chart.get("player_id")
                    if player_id and player_ids and player_id not in player_ids:
                        self.add_error(f"Shot chart {i}: player_id '{player_id}' not found")
                    
                    if "zones" not in chart:
                        self.add_warning(f"Shot chart {i}: Missing 'zones' data")
        
        if "defenders" not in data:
            self.add_warning("shot_charts.json missing 'defenders' array")
        else:
            defenders = data["defenders"]
            if not isinstance(defenders, list):
                self.add_error("'defenders' must be an array")
        
        return len(self.errors) == 0
    
    def validate_all(self) -> bool:
        """Run all validations"""
        print(f"\nValidating data in '{self.data_dir}'...\n")
        
        # Check if directory exists
        if not os.path.exists(self.data_dir):
            self.add_error(f"Data directory '{self.data_dir}' does not exist")
            self.add_error("Please create it and add your data files")
            return False
        
        # Load all data files
        players_ok, players_data = self.load_json("players.json")
        props_ok, props_data = self.load_json("props.json")
        lineups_ok, lineups_data = self.load_json("lineups.json")
        shot_charts_ok, shot_charts_data = self.load_json("shot_charts.json")
        
        # Extract player IDs for cross-validation
        player_ids = set()
        if players_ok and players_data:
            player_ids = {p.get("player_id") for p in players_data.get("players", []) if p.get("player_id")}
        
        # Run validations
        if players_ok:
            self.validate_players(players_data)
        
        if props_ok:
            self.validate_props(props_data, player_ids)
        
        if lineups_ok:
            self.validate_lineups(lineups_data, player_ids)
        
        if shot_charts_ok:
            self.validate_shot_charts(shot_charts_data, player_ids)
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
            print("Your data is ready to use.")
        elif not self.errors:
            print("\n✅ No critical errors found.")
            print("Review warnings and fix if needed.")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s).")
            print("Please fix the errors and run validation again.")
        
        print("="*60 + "\n")
        
        return len(self.errors) == 0

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate NBA prop betting data")
    parser.add_argument("--data-dir", default="user_data", help="Data directory path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    validator = DataValidator(data_dir=args.data_dir, verbose=args.verbose)
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
