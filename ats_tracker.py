"""
ATS (Against The Spread) Record Tracking System
Track how teams perform against betting spreads for college basketball
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


@dataclass
class GameResult:
    """
    Stores the actual result of a college basketball game
    """
    date: str  # Format: YYYY-MM-DD
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    spread: float  # Negative means home team favored, positive means away team favored
    closing_line: Optional[float] = None  # Optional: track line movement
    location: str = "home"  # "home", "away", or "neutral"
    
    def __post_init__(self):
        """Validate game result data"""
        if self.home_score < 0 or self.away_score < 0:
            raise ValueError("Scores cannot be negative")
        if self.location not in ["home", "away", "neutral"]:
            raise ValueError("Location must be 'home', 'away', or 'neutral'")


@dataclass
class ATSRecord:
    """
    Tracks ATS (Against The Spread) performance for a team
    """
    team_name: str
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    
    @property
    def total_games(self) -> int:
        """Total games with ATS results"""
        return self.wins + self.losses + self.pushes
    
    @property
    def win_percentage(self) -> float:
        """ATS win percentage (excluding pushes)"""
        decided_games = self.wins + self.losses
        if decided_games == 0:
            return 0.0
        return self.wins / decided_games
    
    @property
    def cover_percentage(self) -> float:
        """Cover percentage (including pushes as half win)"""
        if self.total_games == 0:
            return 0.0
        return (self.wins + self.pushes * 0.5) / self.total_games
    
    def add_result(self, result: str):
        """
        Add an ATS result
        
        Args:
            result: 'W' for win, 'L' for loss, 'P' for push
        """
        result = result.upper()
        if result == 'W':
            self.wins += 1
        elif result == 'L':
            self.losses += 1
        elif result == 'P':
            self.pushes += 1
        else:
            raise ValueError(f"Invalid result: {result}. Use 'W', 'L', or 'P'")
    
    def __str__(self) -> str:
        """String representation of ATS record"""
        return f"{self.team_name}: {self.wins}-{self.losses}-{self.pushes} ATS ({self.win_percentage:.1%})"


class ATSTracker:
    """
    Main class for tracking ATS records across multiple teams and games
    """
    
    def __init__(self):
        self.games: List[GameResult] = []
        self.team_records: Dict[str, ATSRecord] = {}
        # Track records by situation
        self.home_records: Dict[str, ATSRecord] = {}
        self.away_records: Dict[str, ATSRecord] = {}
        self.favorite_records: Dict[str, ATSRecord] = {}
        self.underdog_records: Dict[str, ATSRecord] = {}
    
    def _get_or_create_record(self, records_dict: Dict[str, ATSRecord], team: str) -> ATSRecord:
        """Get existing record or create new one"""
        if team not in records_dict:
            records_dict[team] = ATSRecord(team_name=team)
        return records_dict[team]
    
    def calculate_ats_result(self, game: GameResult) -> tuple[str, str]:
        """
        Calculate ATS result for both teams
        
        Returns:
            (home_result, away_result) where each is 'W', 'L', or 'P'
        """
        # Calculate actual margin (positive = home team won)
        actual_margin = game.home_score - game.away_score
        
        # Calculate margin against spread
        # If spread is -7 for home team, they need to win by 8+ to cover
        # Spread is from home team perspective
        spread_margin = actual_margin + game.spread
        
        # Determine results
        if abs(spread_margin) < 0.5:  # Push (within 0.5 to handle rounding)
            home_result = 'P'
            away_result = 'P'
        elif spread_margin > 0:  # Home team covered
            home_result = 'W'
            away_result = 'L'
        else:  # Away team covered
            home_result = 'L'
            away_result = 'W'
        
        return home_result, away_result
    
    def add_game(
        self,
        date: str,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        spread: float,
        location: str = "home",
        closing_line: Optional[float] = None
    ) -> Dict[str, str]:
        """
        Manually add a game result and calculate ATS outcomes
        
        Args:
            date: Game date (YYYY-MM-DD)
            home_team: Home team name
            away_team: Away team name
            home_score: Final score for home team
            away_score: Final score for away team
            spread: Point spread (negative = home favored, positive = away favored)
            location: "home", "away", or "neutral"
            closing_line: Optional closing line for tracking
        
        Returns:
            Dictionary with ATS results for both teams
        """
        # Create game result
        game = GameResult(
            date=date,
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            spread=spread,
            location=location,
            closing_line=closing_line
        )
        
        # Calculate ATS results
        home_result, away_result = self.calculate_ats_result(game)
        
        # Update overall records
        home_record = self._get_or_create_record(self.team_records, home_team)
        away_record = self._get_or_create_record(self.team_records, away_team)
        home_record.add_result(home_result)
        away_record.add_result(away_result)
        
        # Update home/away records
        home_home_record = self._get_or_create_record(self.home_records, home_team)
        away_away_record = self._get_or_create_record(self.away_records, away_team)
        home_home_record.add_result(home_result)
        away_away_record.add_result(away_result)
        
        # Update favorite/underdog records
        if spread < 0:  # Home team favored
            home_fav_record = self._get_or_create_record(self.favorite_records, home_team)
            away_dog_record = self._get_or_create_record(self.underdog_records, away_team)
            home_fav_record.add_result(home_result)
            away_dog_record.add_result(away_result)
        elif spread > 0:  # Away team favored
            away_fav_record = self._get_or_create_record(self.favorite_records, away_team)
            home_dog_record = self._get_or_create_record(self.underdog_records, home_team)
            away_fav_record.add_result(away_result)
            home_dog_record.add_result(home_result)
        # If spread == 0, don't track as favorite/underdog
        
        # Store the game
        self.games.append(game)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_result': home_result,
            'away_result': away_result,
            'home_score': home_score,
            'away_score': away_score,
            'spread': spread
        }
    
    def get_team_record(self, team: str, record_type: str = "overall") -> Optional[ATSRecord]:
        """
        Get ATS record for a team
        
        Args:
            team: Team name
            record_type: "overall", "home", "away", "favorite", or "underdog"
        
        Returns:
            ATSRecord or None if team not found
        """
        record_type = record_type.lower()
        
        if record_type == "overall":
            return self.team_records.get(team)
        elif record_type == "home":
            return self.home_records.get(team)
        elif record_type == "away":
            return self.away_records.get(team)
        elif record_type == "favorite":
            return self.favorite_records.get(team)
        elif record_type == "underdog":
            return self.underdog_records.get(team)
        else:
            raise ValueError(f"Invalid record_type: {record_type}")
    
    def get_all_records(self) -> List[ATSRecord]:
        """Get all team records sorted by win percentage"""
        records = list(self.team_records.values())
        # Sort by win percentage (descending), then by total games
        records.sort(key=lambda r: (r.win_percentage, r.total_games), reverse=True)
        return records
    
    def display_team_stats(self, team: str):
        """
        Display comprehensive ATS statistics for a team
        """
        print(f"\n{'='*70}")
        print(f"ATS STATISTICS FOR {team.upper()}")
        print(f"{'='*70}")
        
        # Overall record
        overall = self.get_team_record(team, "overall")
        if overall is None:
            print(f"No ATS records found for {team}")
            return
        
        print(f"\nOverall: {overall.wins}-{overall.losses}-{overall.pushes} ATS")
        print(f"  Win %: {overall.win_percentage:.1%}")
        print(f"  Cover %: {overall.cover_percentage:.1%}")
        
        # Home record
        home = self.get_team_record(team, "home")
        if home and home.total_games > 0:
            print(f"\nHome: {home.wins}-{home.losses}-{home.pushes} ATS")
            print(f"  Win %: {home.win_percentage:.1%}")
        
        # Away record
        away = self.get_team_record(team, "away")
        if away and away.total_games > 0:
            print(f"\nAway: {away.wins}-{away.losses}-{away.pushes} ATS")
            print(f"  Win %: {away.win_percentage:.1%}")
        
        # As favorite
        favorite = self.get_team_record(team, "favorite")
        if favorite and favorite.total_games > 0:
            print(f"\nAs Favorite: {favorite.wins}-{favorite.losses}-{favorite.pushes} ATS")
            print(f"  Win %: {favorite.win_percentage:.1%}")
        
        # As underdog
        underdog = self.get_team_record(team, "underdog")
        if underdog and underdog.total_games > 0:
            print(f"\nAs Underdog: {underdog.wins}-{underdog.losses}-{underdog.pushes} ATS")
            print(f"  Win %: {underdog.win_percentage:.1%}")
        
        print(f"{'='*70}\n")
    
    def display_leaderboard(self, min_games: int = 5, top_n: int = 10):
        """
        Display ATS leaderboard
        
        Args:
            min_games: Minimum games to qualify
            top_n: Number of teams to display
        """
        print(f"\n{'='*70}")
        print(f"ATS LEADERBOARD (Minimum {min_games} games)")
        print(f"{'='*70}")
        print(f"{'Rank':<6}{'Team':<25}{'Record':<20}{'Win %':<10}{'Cover %':<10}")
        print("-" * 70)
        
        # Filter teams with minimum games
        qualified = [r for r in self.get_all_records() if r.total_games >= min_games]
        
        for i, record in enumerate(qualified[:top_n], 1):
            record_str = f"{record.wins}-{record.losses}-{record.pushes}"
            print(f"{i:<6}{record.team_name:<25}{record_str:<20}"
                  f"{record.win_percentage:<10.1%}{record.cover_percentage:<10.1%}")
        
        print(f"{'='*70}\n")
    
    def get_head_to_head(self, team1: str, team2: str) -> Dict:
        """
        Get head-to-head ATS record between two teams
        """
        team1_results = []
        team2_results = []
        
        for game in self.games:
            if (game.home_team == team1 and game.away_team == team2) or \
               (game.home_team == team2 and game.away_team == team1):
                home_result, away_result = self.calculate_ats_result(game)
                
                if game.home_team == team1:
                    team1_results.append(home_result)
                    team2_results.append(away_result)
                else:
                    team1_results.append(away_result)
                    team2_results.append(home_result)
        
        return {
            'team1': team1,
            'team2': team2,
            'team1_wins': team1_results.count('W'),
            'team1_losses': team1_results.count('L'),
            'team1_pushes': team1_results.count('P'),
            'team2_wins': team2_results.count('W'),
            'team2_losses': team2_results.count('L'),
            'team2_pushes': team2_results.count('P'),
            'total_games': len(team1_results)
        }
    
    def export_records(self) -> Dict:
        """
        Export all records to a dictionary format
        """
        return {
            'overall': {team: {
                'wins': record.wins,
                'losses': record.losses,
                'pushes': record.pushes,
                'win_pct': record.win_percentage
            } for team, record in self.team_records.items()},
            'total_games': len(self.games)
        }


def example_ats_tracking():
    """
    Example of using the ATS tracking system
    """
    print("=" * 70)
    print("ATS (AGAINST THE SPREAD) TRACKING SYSTEM")
    print("=" * 70)
    print()
    
    # Initialize tracker
    tracker = ATSTracker()
    
    print("Adding game results...")
    print()
    
    # Add some example games
    games = [
        # Date, Home, Away, Home Score, Away Score, Spread
        ("2026-01-15", "Duke", "UNC", 85, 78, -7.5),
        ("2026-01-18", "Duke", "Virginia", 72, 68, -8.0),
        ("2026-01-22", "Kentucky", "Duke", 88, 84, -3.5),
        ("2026-01-25", "UNC", "Kentucky", 76, 81, -2.5),
        ("2026-01-29", "UNC", "Virginia", 69, 65, -5.5),
        ("2026-02-01", "Kansas", "Duke", 77, 75, -1.0),
        ("2026-02-05", "Duke", "Kansas", 82, 79, -4.5),
        ("2026-02-08", "Virginia", "UNC", 71, 74, 3.0),
        ("2026-02-12", "Kentucky", "Kansas", 90, 87, -6.5),
        ("2026-02-13", "Duke", "Kentucky", 79, 76, -2.5),
    ]
    
    for game_data in games:
        date = game_data[0]
        result = tracker.add_game(*game_data)
        print(f"{date}: {result['home_team']} {result['home_score']} vs "
              f"{result['away_team']} {result['away_score']} (Spread: {result['spread']})")
        print(f"  ATS Result: {result['home_team']} ({result['home_result']}), "
              f"{result['away_team']} ({result['away_result']})")
        print()
    
    # Display individual team stats
    tracker.display_team_stats("Duke")
    tracker.display_team_stats("UNC")
    
    # Display leaderboard
    tracker.display_leaderboard(min_games=3, top_n=5)
    
    # Head to head
    h2h = tracker.get_head_to_head("Duke", "UNC")
    print(f"HEAD-TO-HEAD: Duke vs UNC")
    print(f"Duke ATS: {h2h['team1_wins']}-{h2h['team1_losses']}-{h2h['team1_pushes']}")
    print(f"UNC ATS: {h2h['team2_wins']}-{h2h['team2_losses']}-{h2h['team2_pushes']}")
    print()


if __name__ == "__main__":
    example_ats_tracking()
