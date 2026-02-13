"""
Best ATS Performers Analysis
Identifies which Division I teams cover the spread most frequently
"""

from teamrankings_importer import TeamRankingsImporter, TeamRankingsATSData
from typing import List, Tuple, Dict
import csv


class ATSPerformanceAnalyzer:
    """
    Analyzes ATS (Against The Spread) performance to identify
    which teams cover the spread most frequently
    """
    
    def __init__(self):
        self.importer = TeamRankingsImporter()
        
    def load_data(self, filepath: str = 'sample_teamrankings_data.csv'):
        """Load ATS data from CSV file"""
        self.importer.import_from_csv(filepath)
        print(f"Loaded {len(self.importer.teams_data)} teams with ATS data")
    
    def get_best_overall_ats(self, min_games: int = 10) -> List[Tuple[str, float, int, int, int]]:
        """
        Get teams with best overall ATS record
        
        Args:
            min_games: Minimum number of games to qualify
        
        Returns:
            List of (team, win_pct, wins, losses, pushes) sorted by win percentage
        """
        results = []
        
        for team_name, data in self.importer.teams_data.items():
            total_games = data.ats_wins + data.ats_losses
            if total_games >= min_games:
                results.append((
                    team_name,
                    data.ats_win_pct,
                    data.ats_wins,
                    data.ats_losses,
                    data.ats_pushes,
                    data.conference
                ))
        
        # Sort by win percentage (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_best_home_ats(self, min_games: int = 5) -> List[Tuple[str, float, str]]:
        """Get teams with best home ATS record"""
        results = []
        
        for team_name, data in self.importer.teams_data.items():
            if data.home_ats_record:
                wins, losses, pushes = self.importer.parse_record_string(data.home_ats_record)
                total_games = wins + losses
                if total_games >= min_games:
                    win_pct = wins / total_games if total_games > 0 else 0
                    results.append((team_name, win_pct, data.home_ats_record))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_best_away_ats(self, min_games: int = 5) -> List[Tuple[str, float, str]]:
        """Get teams with best away ATS record"""
        results = []
        
        for team_name, data in self.importer.teams_data.items():
            if data.away_ats_record:
                wins, losses, pushes = self.importer.parse_record_string(data.away_ats_record)
                total_games = wins + losses
                if total_games >= min_games:
                    win_pct = wins / total_games if total_games > 0 else 0
                    results.append((team_name, win_pct, data.away_ats_record))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_best_as_favorite(self, min_games: int = 5) -> List[Tuple[str, float, str]]:
        """Get teams with best ATS record as favorites"""
        results = []
        
        for team_name, data in self.importer.teams_data.items():
            if data.favorite_ats_record:
                wins, losses, pushes = self.importer.parse_record_string(data.favorite_ats_record)
                total_games = wins + losses
                if total_games >= min_games:
                    win_pct = wins / total_games if total_games > 0 else 0
                    results.append((team_name, win_pct, data.favorite_ats_record))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_best_as_underdog(self, min_games: int = 5) -> List[Tuple[str, float, str]]:
        """Get teams with best ATS record as underdogs"""
        results = []
        
        for team_name, data in self.importer.teams_data.items():
            if data.underdog_ats_record:
                wins, losses, pushes = self.importer.parse_record_string(data.underdog_ats_record)
                total_games = wins + losses
                if total_games >= min_games:
                    win_pct = wins / total_games if total_games > 0 else 0
                    results.append((team_name, win_pct, data.underdog_ats_record))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_conference_leaders(self) -> Dict[str, Tuple[str, float]]:
        """Get best ATS team from each conference"""
        conference_leaders = {}
        
        for team_name, data in self.importer.teams_data.items():
            if data.conference:
                conf = data.conference
                if conf not in conference_leaders or data.ats_win_pct > conference_leaders[conf][1]:
                    conference_leaders[conf] = (team_name, data.ats_win_pct)
        
        return conference_leaders
    
    def display_comprehensive_report(self, top_n: int = 25):
        """
        Display comprehensive ATS performance report
        Shows which teams cover the spread most frequently
        """
        print("\n" + "=" * 90)
        print("TEAMS THAT COVER THE SPREAD MOST - COMPREHENSIVE ATS ANALYSIS")
        print("=" * 90)
        print()
        
        # Overall best performers
        print(f"TOP {top_n} TEAMS - OVERALL ATS PERFORMANCE")
        print("-" * 90)
        print(f"{'Rank':<6}{'Team':<25}{'Win %':<10}{'Record (W-L-P)':<20}{'Conference':<20}")
        print("-" * 90)
        
        overall = self.get_best_overall_ats(min_games=10)
        for i, (team, win_pct, wins, losses, pushes, conf) in enumerate(overall[:top_n], 1):
            record = f"{wins}-{losses}-{pushes}"
            print(f"{i:<6}{team:<25}{win_pct:<10.1%}{record:<20}{conf:<20}")
        
        print()
        print("=" * 90)
        
        # Key insight
        if overall:
            best_team = overall[0]
            print(f"\n🏆 BEST OVERALL ATS PERFORMER: {best_team[0]}")
            print(f"   Record: {best_team[2]}-{best_team[3]}-{best_team[4]} ({best_team[1]:.1%})")
            print(f"   Conference: {best_team[5]}")
            print()
        
        # Best by situation
        print("=" * 90)
        print("BEST ATS PERFORMERS BY SITUATION")
        print("=" * 90)
        
        # Home
        print("\nTOP 10 AT HOME:")
        print(f"{'Rank':<6}{'Team':<25}{'Win %':<10}{'Record':<15}")
        print("-" * 56)
        home_leaders = self.get_best_home_ats(min_games=5)
        for i, (team, win_pct, record) in enumerate(home_leaders[:10], 1):
            print(f"{i:<6}{team:<25}{win_pct:<10.1%}{record:<15}")
        
        # Away
        print("\nTOP 10 ON THE ROAD:")
        print(f"{'Rank':<6}{'Team':<25}{'Win %':<10}{'Record':<15}")
        print("-" * 56)
        away_leaders = self.get_best_away_ats(min_games=5)
        for i, (team, win_pct, record) in enumerate(away_leaders[:10], 1):
            print(f"{i:<6}{team:<25}{win_pct:<10.1%}{record:<15}")
        
        # As favorite
        print("\nTOP 10 AS FAVORITES:")
        print(f"{'Rank':<6}{'Team':<25}{'Win %':<10}{'Record':<15}")
        print("-" * 56)
        fav_leaders = self.get_best_as_favorite(min_games=5)
        for i, (team, win_pct, record) in enumerate(fav_leaders[:10], 1):
            print(f"{i:<6}{team:<25}{win_pct:<10.1%}{record:<15}")
        
        # As underdog
        print("\nTOP 10 AS UNDERDOGS:")
        print(f"{'Rank':<6}{'Team':<25}{'Win %':<10}{'Record':<15}")
        print("-" * 56)
        dog_leaders = self.get_best_as_underdog(min_games=5)
        for i, (team, win_pct, record) in enumerate(dog_leaders[:10], 1):
            print(f"{i:<6}{team:<25}{win_pct:<10.1%}{record:<15}")
        
        # Conference leaders
        print("\n" + "=" * 90)
        print("BEST ATS TEAM BY CONFERENCE")
        print("-" * 90)
        print(f"{'Conference':<25}{'Team':<30}{'ATS Win %':<15}")
        print("-" * 90)
        
        conf_leaders = self.get_conference_leaders()
        for conf in sorted(conf_leaders.keys()):
            team, win_pct = conf_leaders[conf]
            print(f"{conf:<25}{team:<30}{win_pct:<15.1%}")
        
        print("\n" + "=" * 90)
        print("KEY INSIGHTS")
        print("=" * 90)
        print()
        print("✓ Teams above 55% ATS are profitable long-term")
        print("✓ Teams above 60% ATS are exceptional performers")
        print("✓ Consider situational factors (home/away, favorite/underdog)")
        print("✓ Conference leaders may have schedule advantages")
        print()
        print("Data Source: TeamRankings.com")
        print("=" * 90)
    
    def display_team_details(self, team_name: str):
        """Display detailed ATS breakdown for a specific team"""
        data = self.importer.teams_data.get(team_name)
        if not data:
            print(f"Team '{team_name}' not found in data")
            return
        
        print("\n" + "=" * 70)
        print(f"DETAILED ATS ANALYSIS: {team_name.upper()}")
        print("=" * 70)
        
        print(f"\nConference: {data.conference}")
        print(f"\nOverall ATS Record: {data.ats_wins}-{data.ats_losses}-{data.ats_pushes}")
        print(f"ATS Win Percentage: {data.ats_win_pct:.1%}")
        
        if data.ats_win_pct >= 0.60:
            print("⭐ EXCEPTIONAL PERFORMER (60%+ ATS)")
        elif data.ats_win_pct >= 0.55:
            print("✓ PROFITABLE (55%+ ATS)")
        elif data.ats_win_pct >= 0.50:
            print("• ABOVE AVERAGE")
        else:
            print("• BELOW AVERAGE")
        
        if data.home_ats_record:
            wins, losses, pushes = self.importer.parse_record_string(data.home_ats_record)
            total = wins + losses
            pct = wins / total if total > 0 else 0
            print(f"\nHome ATS: {data.home_ats_record} ({pct:.1%})")
        
        if data.away_ats_record:
            wins, losses, pushes = self.importer.parse_record_string(data.away_ats_record)
            total = wins + losses
            pct = wins / total if total > 0 else 0
            print(f"Away ATS: {data.away_ats_record} ({pct:.1%})")
        
        if data.favorite_ats_record:
            wins, losses, pushes = self.importer.parse_record_string(data.favorite_ats_record)
            total = wins + losses
            pct = wins / total if total > 0 else 0
            print(f"As Favorite: {data.favorite_ats_record} ({pct:.1%})")
        
        if data.underdog_ats_record:
            wins, losses, pushes = self.importer.parse_record_string(data.underdog_ats_record)
            total = wins + losses
            pct = wins / total if total > 0 else 0
            print(f"As Underdog: {data.underdog_ats_record} ({pct:.1%})")
        
        print("=" * 70)
    
    def export_best_performers(self, filepath: str = 'best_ats_performers.csv', top_n: int = 50):
        """Export top ATS performers to CSV"""
        overall = self.get_best_overall_ats(min_games=10)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Rank', 'Team', 'ATS_Win_Pct', 'Wins', 'Losses', 'Pushes', 
                           'Total_Games', 'Conference'])
            
            for i, (team, win_pct, wins, losses, pushes, conf) in enumerate(overall[:top_n], 1):
                total_games = wins + losses + pushes
                writer.writerow([i, team, f"{win_pct:.3f}", wins, losses, pushes, 
                               total_games, conf])
        
        print(f"Exported top {len(overall[:top_n])} ATS performers to {filepath}")


def main():
    """
    Main function to analyze and display which teams cover the spread most
    """
    print("=" * 90)
    print("DIVISION I BASKETBALL - ATS PERFORMANCE ANALYSIS")
    print("Which Teams Cover The Spread Most?")
    print("=" * 90)
    print()
    
    # Create analyzer
    analyzer = ATSPerformanceAnalyzer()
    
    # Load data
    print("Loading ATS data from TeamRankings.com...")
    analyzer.load_data('sample_teamrankings_data.csv')
    print()
    
    # Display comprehensive report
    analyzer.display_comprehensive_report(top_n=25)
    
    # Show detailed analysis for top performer
    print("\n")
    best_overall = analyzer.get_best_overall_ats(min_games=10)
    if best_overall:
        analyzer.display_team_details(best_overall[0][0])
    
    # Export results
    print("\n")
    analyzer.export_best_performers('best_ats_performers.csv', top_n=50)
    
    print("\n" + "=" * 90)
    print("ANALYSIS COMPLETE")
    print("=" * 90)
    print("\nFor more details, see:")
    print("  - best_ats_performers.csv (exported rankings)")
    print("  - ATS_GUIDE.md (comprehensive guide)")
    print()


if __name__ == "__main__":
    main()
