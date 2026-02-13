"""
ATS Performance as Favorite Analysis - 2025-26 Season
Analyzes team ATS performance when they are betting favorites

Based on TeamRankings.com data:
https://www.teamrankings.com/ncb/trends/ats_trends/?sc=is_fav

IMPORTANT: Use ONLY current 2025-26 season data
"""

import csv
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TeamATSasFavorite:
    """Team's ATS performance as a favorite"""
    team: str
    conference: str
    overall_wins: int
    overall_losses: int
    overall_pushes: int
    favorite_wins: int
    favorite_losses: int
    favorite_pushes: int
    
    @property
    def overall_ats_pct(self) -> float:
        """Overall ATS win percentage"""
        total = self.overall_wins + self.overall_losses
        return (self.overall_wins / total * 100) if total > 0 else 0.0
    
    @property
    def favorite_ats_pct(self) -> float:
        """ATS win percentage as favorite"""
        total = self.favorite_wins + self.favorite_losses
        return (self.favorite_wins / total * 100) if total > 0 else 0.0
    
    @property
    def favorite_games(self) -> int:
        """Total games as favorite"""
        return self.favorite_wins + self.favorite_losses + self.favorite_pushes
    
    @property
    def performance_gap(self) -> float:
        """Difference between as favorite and overall performance"""
        return self.favorite_ats_pct - self.overall_ats_pct


class ATSasFavoriteAnalyzer:
    """
    Analyze ATS performance when teams are favorites
    
    Key insights:
    - Which teams cover consistently when favored?
    - Which favorites fail to cover?
    - Performance gaps (better/worse as favorite)
    """
    
    def __init__(self):
        self.teams: Dict[str, TeamATSasFavorite] = {}
    
    def load_from_csv(self, filename: str) -> None:
        """
        Load ATS data from TeamRankings.com CSV format
        
        Expected columns:
        Team, ATS_Wins, ATS_Losses, ATS_Pushes, Favorite_Record, Conference
        
        Favorite_Record format: "W-L-P" (e.g., "18-2-1")
        """
        print(f"⚠️  Loading ATS as favorite data from {filename}")
        print(f"⚠️  WARNING: Verify this file contains ONLY 2025-26 season data!")
        print(f"⚠️  Do NOT use data from previous seasons")
        
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip comment lines
                if row.get('Team', '').startswith('#'):
                    continue
                
                team = row['Team']
                overall_wins = int(row['ATS_Wins'])
                overall_losses = int(row['ATS_Losses'])
                overall_pushes = int(row['ATS_Pushes'])
                
                # Parse favorite record (format: "W-L-P")
                fav_record = row.get('Favorite_Record', '0-0-0')
                fav_parts = fav_record.split('-')
                fav_wins = int(fav_parts[0])
                fav_losses = int(fav_parts[1])
                fav_pushes = int(fav_parts[2]) if len(fav_parts) > 2 else 0
                
                conference = row.get('Conference', 'Unknown')
                
                self.teams[team] = TeamATSasFavorite(
                    team=team,
                    conference=conference,
                    overall_wins=overall_wins,
                    overall_losses=overall_losses,
                    overall_pushes=overall_pushes,
                    favorite_wins=fav_wins,
                    favorite_losses=fav_losses,
                    favorite_pushes=fav_pushes
                )
        
        print(f"Loaded {len(self.teams)} teams with ATS as favorite data")
        print(f"⚠️  WARNING: Verify data is from current 2025-26 season only!\n")
    
    def get_best_as_favorite(self, min_games: int = 10) -> List[TeamATSasFavorite]:
        """Get teams with best ATS record as favorites"""
        qualifying = [t for t in self.teams.values() if t.favorite_games >= min_games]
        return sorted(qualifying, key=lambda x: x.favorite_ats_pct, reverse=True)
    
    def get_worst_as_favorite(self, min_games: int = 10) -> List[TeamATSasFavorite]:
        """Get teams with worst ATS record as favorites"""
        qualifying = [t for t in self.teams.values() if t.favorite_games >= min_games]
        return sorted(qualifying, key=lambda x: x.favorite_ats_pct)
    
    def get_teams_better_as_favorite(self, min_gap: float = 10.0, min_games: int = 10) -> List[TeamATSasFavorite]:
        """Get teams that perform better as favorites (positive gap)"""
        qualifying = [t for t in self.teams.values() 
                     if t.favorite_games >= min_games and t.performance_gap >= min_gap]
        return sorted(qualifying, key=lambda x: x.performance_gap, reverse=True)
    
    def get_teams_worse_as_favorite(self, min_gap: float = -10.0, min_games: int = 10) -> List[TeamATSasFavorite]:
        """Get teams that perform worse as favorites (negative gap)"""
        qualifying = [t for t in self.teams.values() 
                     if t.favorite_games >= min_games and t.performance_gap <= min_gap]
        return sorted(qualifying, key=lambda x: x.performance_gap)
    
    def get_team_analysis(self, team: str) -> Optional[TeamATSasFavorite]:
        """Get detailed analysis for a specific team"""
        return self.teams.get(team)
    
    def display_team_analysis(self, team: str) -> None:
        """Display detailed analysis for a specific team"""
        data = self.get_team_analysis(team)
        if not data:
            print(f"No data found for {team}")
            return
        
        print(f"\n{'='*70}")
        print(f"ATS ANALYSIS: {data.team} ({data.conference})")
        print(f"{'='*70}")
        
        print(f"\n📊 OVERALL ATS PERFORMANCE:")
        print(f"  Record: {data.overall_wins}-{data.overall_losses}-{data.overall_pushes}")
        print(f"  Win %: {data.overall_ats_pct:.1f}%")
        
        print(f"\n🎯 AS FAVORITE ATS PERFORMANCE:")
        print(f"  Record: {data.favorite_wins}-{data.favorite_losses}-{data.favorite_pushes}")
        print(f"  Win %: {data.favorite_ats_pct:.1f}%")
        print(f"  Games as Favorite: {data.favorite_games}")
        
        print(f"\n📈 PERFORMANCE GAP:")
        gap = data.performance_gap
        if gap > 10:
            print(f"  Gap: +{gap:.1f}% (BETTER as favorite)")
            print(f"  ✓ Performs well when favored")
        elif gap < -10:
            print(f"  Gap: {gap:.1f}% (WORSE as favorite)")
            print(f"  ⚠️ Struggles to cover when favored")
        else:
            print(f"  Gap: {gap:+.1f}% (Similar performance)")
            print(f"  → Consistent across situations")
        
        print(f"\n💡 BETTING RECOMMENDATION:")
        if data.favorite_ats_pct >= 85.0:
            print(f"  ✓ BACK AS FAVORITE - Elite performer ({data.favorite_ats_pct:.1f}%)")
        elif data.favorite_ats_pct >= 70.0:
            print(f"  ✓ BACK AS FAVORITE - Strong performer ({data.favorite_ats_pct:.1f}%)")
        elif data.favorite_ats_pct >= 60.0:
            print(f"  → NEUTRAL - Average favorite ({data.favorite_ats_pct:.1f}%)")
        else:
            print(f"  ⚠️ FADE AS FAVORITE - Poor performer ({data.favorite_ats_pct:.1f}%)")
    
    def display_comprehensive_report(self, top_n: int = 10) -> None:
        """Display comprehensive ATS as favorite report"""
        print("\n" + "="*80)
        print("COLLEGE BASKETBALL - ATS PERFORMANCE AS FAVORITES")
        print("Which Teams Cover When Favored?")
        print("="*80)
        
        # Best performers as favorites
        print(f"\n🏆 TOP {top_n} TEAMS - ATS as FAVORITES")
        print("-" * 80)
        best = self.get_best_as_favorite(min_games=10)[:top_n]
        for i, team in enumerate(best, 1):
            status = "🔥" if team.favorite_ats_pct >= 85.0 else "✓" if team.favorite_ats_pct >= 70.0 else ""
            print(f"{i:2d}. {team.team:20s} {team.favorite_wins:2d}-{team.favorite_losses:2d}-{team.favorite_pushes} "
                  f"({team.favorite_ats_pct:5.1f}%) - {team.conference:15s} {status}")
        
        # Worst performers as favorites
        print(f"\n⚠️  WORST PERFORMERS - ATS as FAVORITES")
        print("-" * 80)
        worst = self.get_worst_as_favorite(min_games=10)[:5]
        for i, team in enumerate(worst, 1):
            print(f"{i}. {team.team:20s} {team.favorite_wins:2d}-{team.favorite_losses:2d}-{team.favorite_pushes} "
                  f"({team.favorite_ats_pct:5.1f}%) - {team.conference}")
        
        # Teams better as favorites
        print(f"\n📈 TEAMS PERFORMING BETTER AS FAVORITES")
        print("-" * 80)
        better = self.get_teams_better_as_favorite(min_gap=10.0)
        if better:
            for team in better[:5]:
                print(f"{team.team:20s} Gap: +{team.performance_gap:5.1f}% "
                      f"(as fav: {team.favorite_ats_pct:5.1f}%, overall: {team.overall_ats_pct:5.1f}%)")
        else:
            print("No teams with significant positive gap")
        
        # Teams worse as favorites
        print(f"\n⚠️  TEAMS PERFORMING WORSE AS FAVORITES")
        print("-" * 80)
        worse = self.get_teams_worse_as_favorite(min_gap=-10.0)
        if worse:
            for team in worse[:5]:
                print(f"{team.team:20s} Gap: {team.performance_gap:6.1f}% "
                      f"(as fav: {team.favorite_ats_pct:5.1f}%, overall: {team.overall_ats_pct:5.1f}%)")
        else:
            print("No teams with significant negative gap")
        
        # Betting insights
        print(f"\n💡 BETTING INSIGHTS")
        print("-" * 80)
        print("✓ BACK AS FAVORITES:")
        print("  - Teams with 85%+ ATS as favorites (elite performers)")
        print("  - Teams with +10% positive gap (rise when favored)")
        print("  - Consistent favorites that deliver")
        print("")
        print("⚠️ FADE AS FAVORITES:")
        print("  - Teams with <55% ATS as favorites (poor performers)")
        print("  - Popular teams that fail to cover (public bias)")
        print("  - Teams with negative gap (worse when favored)")
        print("")
        print("📊 KEY METRIC:")
        print("  - 85%+ = Elite favorite")
        print("  - 70-85% = Strong favorite")
        print("  - 60-70% = Average favorite")
        print("  - <60% = Weak favorite (consider fading)")


def main():
    """Run comprehensive ATS as favorite analysis"""
    analyzer = ATSasFavoriteAnalyzer()
    analyzer.load_from_csv('sample_teamrankings_data.csv')
    
    # Display comprehensive report
    analyzer.display_comprehensive_report()
    
    # Example: Analyze specific team
    print("\n" + "="*80)
    print("EXAMPLE: Detailed Team Analysis")
    print("="*80)
    analyzer.display_team_analysis("Houston")
    analyzer.display_team_analysis("UNC")


if __name__ == "__main__":
    main()
