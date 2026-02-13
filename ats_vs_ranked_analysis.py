"""
ATS Performance vs Ranked Opponents Analysis - 2025-26 Season
Analyze how teams perform Against The Spread when facing ranked opponents

IMPORTANT: Use ONLY current 2025-26 season data
Data Source: https://www.teamrankings.com/ncb/trends/ats_trends/?sc=vs_ranked

This tool helps identify:
- Teams that perform better vs ranked opponents
- Teams that struggle vs ranked teams  
- Situational betting edges
- Value opportunities in matchups
"""

import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class TeamATSvsRanked:
    """
    Track team's ATS performance overall and vs ranked opponents
    """
    team: str
    conference: str
    
    # Overall ATS record
    overall_wins: int
    overall_losses: int
    overall_pushes: int
    
    # ATS record vs ranked opponents
    vs_ranked_wins: int
    vs_ranked_losses: int
    vs_ranked_pushes: int
    
    # ATS record vs unranked opponents (calculated)
    @property
    def vs_unranked_wins(self) -> int:
        return self.overall_wins - self.vs_ranked_wins
    
    @property
    def vs_unranked_losses(self) -> int:
        return self.overall_losses - self.vs_ranked_losses
    
    @property
    def vs_unranked_pushes(self) -> int:
        return self.overall_pushes - self.vs_ranked_pushes
    
    # Overall ATS percentage
    @property
    def overall_ats_pct(self) -> float:
        decided = self.overall_wins + self.overall_losses
        return (self.overall_wins / decided * 100) if decided > 0 else 0.0
    
    # ATS percentage vs ranked
    @property
    def vs_ranked_ats_pct(self) -> float:
        decided = self.vs_ranked_wins + self.vs_ranked_losses
        return (self.vs_ranked_wins / decided * 100) if decided > 0 else 0.0
    
    # ATS percentage vs unranked
    @property
    def vs_unranked_ats_pct(self) -> float:
        decided = self.vs_unranked_wins + self.vs_unranked_losses
        return (self.vs_unranked_wins / decided * 100) if decided > 0 else 0.0
    
    # Performance gap (vs ranked - vs unranked)
    @property
    def ranked_performance_gap(self) -> float:
        """Positive means better vs ranked, negative means worse vs ranked"""
        return self.vs_ranked_ats_pct - self.vs_unranked_ats_pct
    
    @property
    def vs_ranked_games(self) -> int:
        return self.vs_ranked_wins + self.vs_ranked_losses + self.vs_ranked_pushes
    
    @property
    def vs_unranked_games(self) -> int:
        return self.vs_unranked_wins + self.vs_unranked_losses + self.vs_unranked_pushes


class ATSvsRankedAnalyzer:
    """
    Analyze ATS performance vs ranked opponents
    """
    
    def __init__(self):
        self.teams: Dict[str, TeamATSvsRanked] = {}
    
    def add_team(
        self,
        team: str,
        conference: str,
        overall_wins: int,
        overall_losses: int,
        overall_pushes: int,
        vs_ranked_wins: int,
        vs_ranked_losses: int,
        vs_ranked_pushes: int
    ):
        """Add a team's ATS data"""
        team_data = TeamATSvsRanked(
            team=team,
            conference=conference,
            overall_wins=overall_wins,
            overall_losses=overall_losses,
            overall_pushes=overall_pushes,
            vs_ranked_wins=vs_ranked_wins,
            vs_ranked_losses=vs_ranked_losses,
            vs_ranked_pushes=vs_ranked_pushes
        )
        self.teams[team] = team_data
    
    def load_from_csv(self, filepath: str):
        """
        Load ATS vs ranked data from CSV file
        
        CSV Format:
        Team,Conference,Overall_W,Overall_L,Overall_P,VsRanked_W,VsRanked_L,VsRanked_P
        """
        print(f"\n⚠️  Importing ATS vs Ranked data from {filepath}")
        print(f"⚠️  WARNING: Verify this file contains ONLY 2025-26 season data!")
        print(f"⚠️  Data source: https://www.teamrankings.com/ncb/trends/ats_trends/?sc=vs_ranked\n")
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
            # Filter out comment lines
            data_lines = [line for line in lines if not line.strip().startswith('#')]
            
            reader = csv.DictReader(data_lines)
            for row in reader:
                self.add_team(
                    team=row['Team'],
                    conference=row['Conference'],
                    overall_wins=int(row['Overall_W']),
                    overall_losses=int(row['Overall_L']),
                    overall_pushes=int(row.get('Overall_P', 0)),
                    vs_ranked_wins=int(row['VsRanked_W']),
                    vs_ranked_losses=int(row['VsRanked_L']),
                    vs_ranked_pushes=int(row.get('VsRanked_P', 0))
                )
        
        print(f"✓ Loaded {len(self.teams)} teams with ATS vs ranked data")
    
    def get_best_vs_ranked(self, min_games: int = 5) -> List[TeamATSvsRanked]:
        """Get teams with best ATS record vs ranked opponents"""
        qualified = [
            team for team in self.teams.values()
            if team.vs_ranked_games >= min_games
        ]
        return sorted(qualified, key=lambda t: t.vs_ranked_ats_pct, reverse=True)
    
    def get_teams_that_rise_vs_ranked(self, min_gap: float = 10.0, min_games: int = 5) -> List[TeamATSvsRanked]:
        """Get teams that perform significantly better vs ranked opponents"""
        qualified = [
            team for team in self.teams.values()
            if team.vs_ranked_games >= min_games and team.ranked_performance_gap >= min_gap
        ]
        return sorted(qualified, key=lambda t: t.ranked_performance_gap, reverse=True)
    
    def get_teams_that_struggle_vs_ranked(self, min_gap: float = -10.0, min_games: int = 5) -> List[TeamATSvsRanked]:
        """Get teams that perform significantly worse vs ranked opponents"""
        qualified = [
            team for team in self.teams.values()
            if team.vs_ranked_games >= min_games and team.ranked_performance_gap <= min_gap
        ]
        return sorted(qualified, key=lambda t: t.ranked_performance_gap)
    
    def get_team_analysis(self, team_name: str) -> Optional[TeamATSvsRanked]:
        """Get specific team's analysis"""
        return self.teams.get(team_name)
    
    def display_team_analysis(self, team_name: str):
        """Display detailed analysis for a specific team"""
        team = self.get_team_analysis(team_name)
        if not team:
            print(f"Team '{team_name}' not found")
            return
        
        print(f"\n{'='*80}")
        print(f"ATS ANALYSIS: {team.team} ({team.conference})")
        print(f"{'='*80}")
        
        print(f"\n📊 OVERALL ATS RECORD:")
        print(f"   {team.overall_wins}-{team.overall_losses}-{team.overall_pushes} ({team.overall_ats_pct:.1f}%)")
        
        print(f"\n🏆 ATS vs RANKED OPPONENTS:")
        print(f"   {team.vs_ranked_wins}-{team.vs_ranked_losses}-{team.vs_ranked_pushes} ({team.vs_ranked_ats_pct:.1f}%)")
        print(f"   Games vs ranked: {team.vs_ranked_games}")
        
        print(f"\n📈 ATS vs UNRANKED OPPONENTS:")
        print(f"   {team.vs_unranked_wins}-{team.vs_unranked_losses}-{team.vs_unranked_pushes} ({team.vs_unranked_ats_pct:.1f}%)")
        print(f"   Games vs unranked: {team.vs_unranked_games}")
        
        print(f"\n💡 PERFORMANCE GAP:")
        gap = team.ranked_performance_gap
        if gap > 10:
            print(f"   +{gap:.1f}% BETTER vs ranked opponents ✓")
            print(f"   This team RISES to the competition")
        elif gap < -10:
            print(f"   {gap:.1f}% WORSE vs ranked opponents ⚠")
            print(f"   This team STRUGGLES vs top competition")
        else:
            print(f"   {gap:+.1f}% (similar performance)")
            print(f"   Consistent performer regardless of opponent")
    
    def display_comprehensive_report(self, top_n: int = 10):
        """Display comprehensive analysis report"""
        print("\n" + "="*80)
        print("ATS PERFORMANCE vs RANKED OPPONENTS ANALYSIS")
        print("2025-26 Season | Data from TeamRankings.com")
        print("="*80)
        
        # Best overall vs ranked
        print(f"\n🏆 TOP {top_n} TEAMS - ATS vs RANKED OPPONENTS")
        print("-" * 80)
        best_vs_ranked = self.get_best_vs_ranked(min_games=5)[:top_n]
        
        for i, team in enumerate(best_vs_ranked, 1):
            print(f"{i:2d}. {team.team:20s} {team.vs_ranked_wins}-{team.vs_ranked_losses}-{team.vs_ranked_pushes} "
                  f"({team.vs_ranked_ats_pct:5.1f}%) - {team.conference}")
        
        # Teams that rise to competition
        print(f"\n📈 TEAMS THAT RISE vs RANKED OPPONENTS (Better vs Ranked)")
        print("-" * 80)
        risers = self.get_teams_that_rise_vs_ranked(min_gap=10.0, min_games=5)[:10]
        
        if risers:
            for team in risers:
                print(f"   {team.team:20s} Gap: +{team.ranked_performance_gap:5.1f}% "
                      f"(vs ranked: {team.vs_ranked_ats_pct:.1f}%, vs unranked: {team.vs_unranked_ats_pct:.1f}%)")
        else:
            print("   No teams meet the criteria (min +10% gap, 5+ games vs ranked)")
        
        # Teams that struggle
        print(f"\n⚠️  TEAMS THAT STRUGGLE vs RANKED OPPONENTS (Worse vs Ranked)")
        print("-" * 80)
        strugglers = self.get_teams_that_struggle_vs_ranked(min_gap=-10.0, min_games=5)[:10]
        
        if strugglers:
            for team in strugglers:
                print(f"   {team.team:20s} Gap: {team.ranked_performance_gap:5.1f}% "
                      f"(vs ranked: {team.vs_ranked_ats_pct:.1f}%, vs unranked: {team.vs_unranked_ats_pct:.1f}%)")
        else:
            print("   No teams meet the criteria (min -10% gap, 5+ games vs ranked)")
        
        # Betting insights
        print(f"\n💰 BETTING INSIGHTS")
        print("-" * 80)
        print("✓ BACK teams with 70%+ ATS vs ranked when they face ranked opponents")
        print("✓ BACK underdogs that rise to competition (+15% gap vs ranked)")
        print("⚠ FADE teams with <40% ATS vs ranked when they face ranked opponents")
        print("⚠ AVOID betting on teams that struggle vs ranked (-15% gap)")
        print("\n📊 Best situation: Underdog with strong vs ranked record facing a ranked opponent")
        print("📊 Avoid: Favorite with poor vs ranked record facing ranked opponent")


def main():
    """Example usage"""
    analyzer = ATSvsRankedAnalyzer()
    
    # Load data from CSV
    analyzer.load_from_csv('sample_ats_vs_ranked_data.csv')
    
    # Display comprehensive report
    analyzer.display_comprehensive_report(top_n=10)
    
    # Example: Analyze specific teams
    print("\n" + "="*80)
    print("DETAILED TEAM EXAMPLES")
    print("="*80)
    
    if "Duke" in analyzer.teams:
        analyzer.display_team_analysis("Duke")
    
    if "Marquette" in analyzer.teams:
        analyzer.display_team_analysis("Marquette")


if __name__ == "__main__":
    main()
