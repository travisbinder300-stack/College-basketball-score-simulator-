"""
Import ATS records from TeamRankings.com data
Provides functionality to load team ATS records from TeamRankings.com format
"""

import csv
from typing import Dict, List, Optional
from dataclasses import dataclass
from ats_tracker import ATSTracker, ATSRecord


@dataclass
class TeamRankingsATSData:
    """
    Structure for ATS data from TeamRankings.com
    TeamRankings.com provides comprehensive ATS statistics
    """
    team: str
    ats_wins: int
    ats_losses: int
    ats_pushes: int
    ats_win_pct: float
    home_ats_record: Optional[str] = None  # Format: "W-L-P"
    away_ats_record: Optional[str] = None  # Format: "W-L-P"
    favorite_ats_record: Optional[str] = None
    underdog_ats_record: Optional[str] = None
    conference: Optional[str] = None


class TeamRankingsImporter:
    """
    Import and manage ATS data from TeamRankings.com
    """
    
    def __init__(self):
        self.teams_data: Dict[str, TeamRankingsATSData] = {}
    
    def add_team_ats_record(
        self,
        team: str,
        wins: int,
        losses: int,
        pushes: int = 0,
        home_record: Optional[str] = None,
        away_record: Optional[str] = None,
        favorite_record: Optional[str] = None,
        underdog_record: Optional[str] = None,
        conference: Optional[str] = None
    ):
        """
        Manually add a team's ATS record from TeamRankings.com
        
        Args:
            team: Team name
            wins: ATS wins
            losses: ATS losses
            pushes: ATS pushes (ties)
            home_record: Home ATS record as "W-L-P" string
            away_record: Away ATS record as "W-L-P" string
            favorite_record: As favorite ATS record as "W-L-P"
            underdog_record: As underdog ATS record as "W-L-P"
            conference: Team's conference
        """
        win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.0
        
        data = TeamRankingsATSData(
            team=team,
            ats_wins=wins,
            ats_losses=losses,
            ats_pushes=pushes,
            ats_win_pct=win_pct,
            home_ats_record=home_record,
            away_ats_record=away_record,
            favorite_ats_record=favorite_record,
            underdog_ats_record=underdog_record,
            conference=conference
        )
        
        self.teams_data[team] = data
    
    def parse_record_string(self, record_str: str) -> tuple[int, int, int]:
        """
        Parse a record string like "15-10-2" into (wins, losses, pushes)
        """
        if not record_str:
            return (0, 0, 0)
        
        parts = record_str.split('-')
        wins = int(parts[0]) if len(parts) > 0 else 0
        losses = int(parts[1]) if len(parts) > 1 else 0
        pushes = int(parts[2]) if len(parts) > 2 else 0
        
        return (wins, losses, pushes)
    
    def import_from_csv(self, filepath: str):
        """
        Import ATS data from CSV file
        
        Expected CSV format:
        Team,ATS_Wins,ATS_Losses,ATS_Pushes,Home_Record,Away_Record,Favorite_Record,Underdog_Record,Conference
        """
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_team_ats_record(
                    team=row['Team'],
                    wins=int(row['ATS_Wins']),
                    losses=int(row['ATS_Losses']),
                    pushes=int(row.get('ATS_Pushes', 0)),
                    home_record=row.get('Home_Record'),
                    away_record=row.get('Away_Record'),
                    favorite_record=row.get('Favorite_Record'),
                    underdog_record=row.get('Underdog_Record'),
                    conference=row.get('Conference')
                )
    
    def display_team_stats(self, team: str):
        """Display ATS statistics for a team from TeamRankings data"""
        if team not in self.teams_data:
            print(f"No data found for {team}")
            return
        
        data = self.teams_data[team]
        
        print(f"\n{'='*70}")
        print(f"ATS STATISTICS FOR {team.upper()} (from TeamRankings.com)")
        print(f"{'='*70}")
        
        print(f"\nOverall: {data.ats_wins}-{data.ats_losses}-{data.ats_pushes} ATS")
        print(f"  Win %: {data.ats_win_pct:.1%}")
        
        if data.home_ats_record:
            wins, losses, pushes = self.parse_record_string(data.home_ats_record)
            win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.0
            print(f"\nHome: {data.home_ats_record} ATS")
            print(f"  Win %: {win_pct:.1%}")
        
        if data.away_ats_record:
            wins, losses, pushes = self.parse_record_string(data.away_ats_record)
            win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.0
            print(f"\nAway: {data.away_ats_record} ATS")
            print(f"  Win %: {win_pct:.1%}")
        
        if data.favorite_ats_record:
            wins, losses, pushes = self.parse_record_string(data.favorite_ats_record)
            win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.0
            print(f"\nAs Favorite: {data.favorite_ats_record} ATS")
            print(f"  Win %: {win_pct:.1%}")
        
        if data.underdog_ats_record:
            wins, losses, pushes = self.parse_record_string(data.underdog_ats_record)
            win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.0
            print(f"\nAs Underdog: {data.underdog_ats_record} ATS")
            print(f"  Win %: {win_pct:.1%}")
        
        if data.conference:
            print(f"\nConference: {data.conference}")
        
        print(f"{'='*70}\n")
    
    def display_leaderboard(self, min_games: int = 10, top_n: int = 25):
        """
        Display ATS leaderboard from TeamRankings data
        """
        print(f"\n{'='*80}")
        print(f"ATS LEADERBOARD (from TeamRankings.com) - Minimum {min_games} games")
        print(f"{'='*80}")
        print(f"{'Rank':<6}{'Team':<30}{'Record':<18}{'Win %':<10}{'Conference':<16}")
        print("-" * 80)
        
        # Sort teams by win percentage
        sorted_teams = sorted(
            self.teams_data.values(),
            key=lambda x: (x.ats_win_pct, x.ats_wins),
            reverse=True
        )
        
        # Filter by minimum games
        qualified = [
            t for t in sorted_teams 
            if (t.ats_wins + t.ats_losses) >= min_games
        ]
        
        for i, team_data in enumerate(qualified[:top_n], 1):
            record_str = f"{team_data.ats_wins}-{team_data.ats_losses}-{team_data.ats_pushes}"
            conf = team_data.conference or "N/A"
            print(f"{i:<6}{team_data.team:<30}{record_str:<18}"
                  f"{team_data.ats_win_pct:<10.1%}{conf:<16}")
        
        print(f"{'='*80}\n")
    
    def get_team_data(self, team: str) -> Optional[TeamRankingsATSData]:
        """Get ATS data for a specific team"""
        return self.teams_data.get(team)
    
    def compare_teams(self, team1: str, team2: str):
        """Compare ATS records between two teams"""
        data1 = self.get_team_data(team1)
        data2 = self.get_team_data(team2)
        
        if not data1 or not data2:
            print(f"Missing data for one or both teams")
            return
        
        print(f"\n{'='*70}")
        print(f"ATS COMPARISON: {team1} vs {team2}")
        print(f"{'='*70}")
        
        print(f"\n{team1}:")
        print(f"  Overall: {data1.ats_wins}-{data1.ats_losses}-{data1.ats_pushes} ({data1.ats_win_pct:.1%})")
        if data1.home_ats_record:
            print(f"  Home: {data1.home_ats_record}")
        if data1.away_ats_record:
            print(f"  Away: {data1.away_ats_record}")
        
        print(f"\n{team2}:")
        print(f"  Overall: {data2.ats_wins}-{data2.ats_losses}-{data2.ats_pushes} ({data2.ats_win_pct:.1%})")
        if data2.home_ats_record:
            print(f"  Home: {data2.home_ats_record}")
        if data2.away_ats_record:
            print(f"  Away: {data2.away_ats_record}")
        
        print(f"\n{'='*70}\n")


def create_sample_teamrankings_data():
    """
    Create sample data in TeamRankings.com format
    This represents the type of ATS data available from TeamRankings.com
    """
    importer = TeamRankingsImporter()
    
    # Add sample teams with their ATS records from 2023-24 season
    # Data format: Team, Overall W-L-P, Home, Away, Favorite, Underdog, Conference
    
    teams_data = [
        ("Duke", 18, 12, 1, "10-5-0", "8-7-1", "12-8-1", "6-4-0", "ACC"),
        ("UNC", 16, 14, 0, "9-6-0", "7-8-0", "10-9-0", "6-5-0", "ACC"),
        ("Kentucky", 17, 13, 0, "11-4-0", "6-9-0", "13-7-0", "4-6-0", "SEC"),
        ("Kansas", 19, 11, 0, "12-3-0", "7-8-0", "14-6-0", "5-5-0", "Big 12"),
        ("Gonzaga", 20, 10, 0, "13-2-0", "7-8-0", "16-4-0", "4-6-0", "WCC"),
        ("Villanova", 15, 15, 0, "8-7-0", "7-8-0", "11-9-0", "4-6-0", "Big East"),
        ("Michigan State", 16, 13, 1, "10-5-1", "6-8-0", "12-8-0", "4-5-1", "Big Ten"),
        ("Texas", 17, 12, 1, "11-4-0", "6-8-1", "13-7-1", "4-5-0", "Big 12"),
        ("UCLA", 18, 11, 1, "10-5-0", "8-6-1", "14-6-1", "4-5-0", "Pac-12"),
        ("Arizona", 19, 10, 1, "12-3-1", "7-7-0", "15-5-0", "4-5-1", "Pac-12"),
        ("Purdue", 20, 9, 1, "13-2-0", "7-7-1", "17-3-1", "3-6-0", "Big Ten"),
        ("Baylor", 17, 12, 1, "10-5-0", "7-7-1", "13-7-0", "4-5-1", "Big 12"),
        ("Houston", 21, 8, 1, "14-1-0", "7-7-1", "18-2-1", "3-6-0", "Big 12"),
        ("Alabama", 16, 13, 1, "9-6-1", "7-7-0", "12-8-0", "4-5-1", "SEC"),
        ("Tennessee", 18, 11, 1, "11-4-0", "7-7-1", "14-6-1", "4-5-0", "SEC"),
    ]
    
    for team_data in teams_data:
        importer.add_team_ats_record(*team_data)
    
    return importer


def example_teamrankings_usage():
    """
    Example of using TeamRankings.com ATS data
    """
    print("=" * 80)
    print("IMPORTING ATS RECORDS FROM TEAMRANKINGS.COM")
    print("=" * 80)
    print()
    
    # Create sample data
    importer = create_sample_teamrankings_data()
    
    # Display leaderboard
    importer.display_leaderboard(min_games=10, top_n=15)
    
    # Display individual team stats
    importer.display_team_stats("Duke")
    importer.display_team_stats("Houston")
    
    # Compare teams
    importer.compare_teams("Duke", "UNC")
    importer.compare_teams("Houston", "Purdue")
    
    print("\nNote: To import from actual TeamRankings.com data:")
    print("1. Export data to CSV with columns: Team, ATS_Wins, ATS_Losses, etc.")
    print("2. Use: importer.import_from_csv('teamrankings_data.csv')")
    print()


if __name__ == "__main__":
    example_teamrankings_usage()
