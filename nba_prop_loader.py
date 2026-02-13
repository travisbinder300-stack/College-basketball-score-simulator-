"""
NBA Prop Data Loader
Loads interfuture NBA prop data from JSON files and converts to Python objects
"""

import json
from datetime import datetime
from typing import List, Dict, Tuple
from nba_prop_data import (
    Player, Game, PropLine, PlayerProp, PropType,
    OddsFormat
)


class PropDataLoader:
    """Load and parse NBA prop data from interfuture JSON format"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.data = None
        self.players_dict = {}
        self.games_dict = {}
    
    def load_data(self) -> Dict:
        """Load JSON data from file"""
        with open(self.json_file_path, 'r') as f:
            self.data = json.load(f)
        return self.data
    
    def parse_players(self) -> List[Player]:
        """Parse player data from JSON"""
        if not self.data:
            self.load_data()
        
        players = []
        for player_data in self.data.get('players', []):
            player = Player(
                player_id=player_data['player_id'],
                name=player_data['name'],
                team=player_data['team'],
                position=player_data['position'],
                jersey_number=player_data.get('jersey_number')
            )
            players.append(player)
            self.players_dict[player.player_id] = player
        
        return players
    
    def parse_games(self) -> List[Game]:
        """Parse game data from JSON"""
        if not self.data:
            self.load_data()
        
        games = []
        for game_data in self.data.get('games', []):
            game = Game(
                game_id=game_data['game_id'],
                home_team=game_data['home_team'],
                away_team=game_data['away_team'],
                scheduled_time=datetime.fromisoformat(game_data['scheduled_time'].replace('Z', '+00:00')),
                venue=game_data['venue'],
                season=self.data['metadata']['season'],
                status=game_data.get('status', 'scheduled')
            )
            games.append(game)
            self.games_dict[game.game_id] = game
        
        return games
    
    def parse_props(self) -> List[PlayerProp]:
        """Parse prop data from JSON"""
        if not self.data:
            self.load_data()
        
        # Ensure players and games are loaded
        if not self.players_dict:
            self.parse_players()
        if not self.games_dict:
            self.parse_games()
        
        props = []
        for prop_data in self.data.get('props', []):
            # Get player and game objects
            player = self.players_dict.get(prop_data['player_id'])
            game = self.games_dict.get(prop_data['game_id'])
            
            if not player or not game:
                continue
            
            # Parse prop line
            line_data = prop_data['line']
            prop_line = PropLine(
                line_value=line_data['value'],
                over_odds=line_data['over_odds'],
                under_odds=line_data['under_odds'],
                bookmaker=line_data['bookmaker'],
                last_updated=datetime.fromisoformat(line_data['last_updated'].replace('Z', '+00:00'))
            )
            
            # Parse prop type
            prop_type_str = prop_data['prop_type']
            prop_type = PropType(prop_type_str)
            
            # Parse player stats
            stats = prop_data.get('player_stats', {})
            context = prop_data.get('context', {})
            
            # Create prop object
            prop = PlayerProp(
                prop_id=prop_data['prop_id'],
                player=player,
                game=game,
                prop_type=prop_type,
                prop_line=prop_line,
                player_season_avg=stats.get('season_avg'),
                player_last_5_avg=stats.get('last_5_avg'),
                vs_opponent_avg=stats.get('vs_opponent_avg'),
                injury_status=context.get('injury_status', 'healthy'),
                minutes_projection=context.get('minutes_projection')
            )
            
            props.append(prop)
        
        return props
    
    def load_all(self) -> Tuple[List[Player], List[Game], List[PlayerProp]]:
        """Load all data (players, games, props)"""
        self.load_data()
        players = self.parse_players()
        games = self.parse_games()
        props = self.parse_props()
        return players, games, props
    
    def get_metadata(self) -> Dict:
        """Get metadata from JSON file"""
        if not self.data:
            self.load_data()
        return self.data.get('metadata', {})
    
    def filter_props_by_game(self, game_id: str) -> List[PlayerProp]:
        """Get all props for a specific game"""
        if not self.data:
            self.load_data()
        
        all_props = self.parse_props()
        return [prop for prop in all_props if prop.game.game_id == game_id]
    
    def filter_props_by_player(self, player_id: str) -> List[PlayerProp]:
        """Get all props for a specific player"""
        if not self.data:
            self.load_data()
        
        all_props = self.parse_props()
        return [prop for prop in all_props if prop.player.player_id == player_id]
    
    def filter_props_by_type(self, prop_type: PropType) -> List[PlayerProp]:
        """Get all props of a specific type"""
        if not self.data:
            self.load_data()
        
        all_props = self.parse_props()
        return [prop for prop in all_props if prop.prop_type == prop_type]


def main():
    """Example usage of PropDataLoader"""
    import os
    
    print("=" * 80)
    print("NBA PROP DATA LOADER")
    print("Loading Interfuture Data from JSON")
    print("=" * 80)
    print()
    
    # Get the JSON file path
    json_file = os.path.join(
        os.path.dirname(__file__),
        'interfuture_nba_props.json'
    )
    
    # Load data
    loader = PropDataLoader(json_file)
    
    # Get metadata
    metadata = loader.get_metadata()
    print("METADATA:")
    print("-" * 80)
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Load all data
    players, games, props = loader.load_all()
    
    print(f"\n\nDATA SUMMARY:")
    print("-" * 80)
    print(f"  Total Players: {len(players)}")
    print(f"  Total Games: {len(games)}")
    print(f"  Total Props: {len(props)}")
    
    # Display players
    print("\n\nPLAYERS:")
    print("-" * 80)
    for player in players:
        print(f"  {player}")
    
    # Display games
    print("\n\nGAMES:")
    print("-" * 80)
    for game in games:
        print(f"  {game}")
    
    # Display props
    print("\n\nPROPS:")
    print("-" * 80)
    for prop in props:
        print(f"\n  {prop}")
        print(f"    Season Avg: {prop.player_season_avg}")
        print(f"    Last 5 Avg: {prop.player_last_5_avg}")
        print(f"    Over Odds: {prop.prop_line.over_odds}")
        print(f"    Under Odds: {prop.prop_line.under_odds}")
    
    # Example: Filter by game
    print("\n\nFILTERED: Props for LAL @ GSW:")
    print("-" * 80)
    lal_gsw_props = loader.filter_props_by_game("NBA_2024_LAL_GSW_001")
    for prop in lal_gsw_props:
        print(f"  {prop}")
    
    # Example: Filter by player
    print("\n\nFILTERED: Props for LeBron James:")
    print("-" * 80)
    lebron_props = loader.filter_props_by_player("2544")
    for prop in lebron_props:
        print(f"  {prop}")
    
    # Example: Filter by prop type
    print("\n\nFILTERED: All Points props:")
    print("-" * 80)
    points_props = loader.filter_props_by_type(PropType.POINTS)
    for prop in points_props:
        print(f"  {prop}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
