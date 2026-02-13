#!/usr/bin/env python3
"""
ATS Away Team Performance Analysis - 2025-26 Season

Analyzes team performance Against The Spread (ATS) specifically for away games.
Identifies road warriors (teams that cover well on the road) vs home-dependent teams.

Data source: https://www.teamrankings.com/ncb/trends/ats_trends/?sc=is_away

⚠️  WARNING: Use ONLY current 2025-26 season data!
"""

import csv
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class AwayATSRecord:
    """Away team ATS performance data"""
    team: str
    ats_record: str  # Format: "W-L-P"
    wins: int
    losses: int
    pushes: int
    cover_pct: float
    mov: float  # Margin of Victory
    ats_plus_minus: float  # How much they beat/miss spread by
    
    @property
    def total_games(self) -> int:
        return self.wins + self.losses + self.pushes
    
    @property
    def games_decided(self) -> int:
        return self.wins + self.losses


class ATSAwayAnalyzer:
    """Analyzer for ATS performance on the road"""
    
    def __init__(self):
        self.teams: Dict[str, AwayATSRecord] = {}
    
    def load_from_csv(self, filename: str):
        """Load away team ATS data from CSV file"""
        print(f"\n⚠️  Loading away team ATS data from {filename}")
        print("⚠️  WARNING: Verify this file contains ONLY 2025-26 season data!")
        print("⚠️  Do NOT use data from previous seasons!")
        
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Skip comment lines and header
                if not row or row[0].startswith('#') or row[0] == 'Team':
                    continue
                
                team = row[0]
                record = AwayATSRecord(
                    team=team,
                    ats_record=row[1],
                    wins=int(row[2]),
                    losses=int(row[3]),
                    pushes=int(row[4]),
                    cover_pct=float(row[5]),
                    mov=float(row[6]),
                    ats_plus_minus=float(row[7])
                )
                self.teams[team] = record
        
        print(f"Loaded {len(self.teams)} teams with away ATS data")
        print("⚠️  WARNING: Verify data is from current 2025-26 season only!\n")
    
    def get_best_away_teams(self, min_games: int = 5, top_n: int = 10) -> List[Tuple[str, AwayATSRecord]]:
        """Get teams with best ATS record on the road"""
        qualified = [(name, rec) for name, rec in self.teams.items() 
                    if rec.games_decided >= min_games]
        return sorted(qualified, key=lambda x: x[1].cover_pct, reverse=True)[:top_n]
    
    def get_worst_away_teams(self, min_games: int = 5, top_n: int = 10) -> List[Tuple[str, AwayATSRecord]]:
        """Get teams with worst ATS record on the road"""
        qualified = [(name, rec) for name, rec in self.teams.items() 
                    if rec.games_decided >= min_games]
        return sorted(qualified, key=lambda x: x[1].cover_pct)[:top_n]
    
    def get_road_warriors(self, min_cover_pct: float = 75.0, min_games: int = 5) -> List[Tuple[str, AwayATSRecord]]:
        """Get teams that excel on the road (75%+ cover rate)"""
        warriors = [(name, rec) for name, rec in self.teams.items()
                   if rec.games_decided >= min_games and rec.cover_pct >= min_cover_pct]
        return sorted(warriors, key=lambda x: x[1].cover_pct, reverse=True)
    
    def get_home_dependent_teams(self, max_cover_pct: float = 35.0, min_games: int = 5) -> List[Tuple[str, AwayATSRecord]]:
        """Get teams that struggle on the road (<35% cover rate)"""
        strugglers = [(name, rec) for name, rec in self.teams.items()
                     if rec.games_decided >= min_games and rec.cover_pct <= max_cover_pct]
        return sorted(strugglers, key=lambda x: x[1].cover_pct)
    
    def get_team_analysis(self, team_name: str) -> Optional[AwayATSRecord]:
        """Get away ATS analysis for a specific team"""
        return self.teams.get(team_name)
    
    def display_team_analysis(self, team_name: str):
        """Display detailed away ATS analysis for a team"""
        record = self.get_team_analysis(team_name)
        if not record:
            print(f"\n❌ No away ATS data found for {team_name}")
            return
        
        print(f"\n{'='*70}")
        print(f"AWAY TEAM ATS ANALYSIS: {team_name}")
        print(f"{'='*70}")
        print(f"ATS Record (Away):     {record.ats_record} ({record.cover_pct:.1f}%)")
        print(f"Total Away Games:      {record.total_games}")
        print(f"Margin of Victory:     {record.mov:+.1f} points")
        print(f"ATS +/-:               {record.ats_plus_minus:+.1f} points")
        
        # Performance rating
        if record.cover_pct >= 75.0:
            rating = "🏆 ROAD WARRIOR - Excellent away performer"
        elif record.cover_pct >= 60.0:
            rating = "✓ SOLID - Good away performer"
        elif record.cover_pct >= 50.0:
            rating = "○ AVERAGE - Neutral away performance"
        elif record.cover_pct >= 40.0:
            rating = "⚠ BELOW AVERAGE - Struggles on road"
        else:
            rating = "❌ POOR - Home-dependent team"
        
        print(f"\nPerformance Rating:    {rating}")
        print(f"{'='*70}\n")
    
    def display_comprehensive_report(self, top_n: int = 10):
        """Display comprehensive away team ATS analysis"""
        print("\n" + "="*80)
        print("NCAA BASKETBALL - AWAY TEAM ATS PERFORMANCE ANALYSIS")
        print("2025-26 Season")
        print("="*80)
        
        # Best road performers
        print(f"\n🏆 TOP {top_n} ROAD WARRIORS (Best ATS Away)")
        print("-" * 80)
        print(f"{'Rank':<6}{'Team':<25}{'ATS Record':<15}{'Cover %':<12}{'ATS +/-':<10}")
        print("-" * 80)
        
        best = self.get_best_away_teams(min_games=5, top_n=top_n)
        for i, (team, rec) in enumerate(best, 1):
            print(f"{i:<6}{team:<25}{rec.ats_record:<15}{rec.cover_pct:>6.1f}%{rec.ats_plus_minus:>10.1f}")
        
        # Worst road performers
        print(f"\n❌ WORST {top_n} ROAD PERFORMERS (Worst ATS Away)")
        print("-" * 80)
        print(f"{'Rank':<6}{'Team':<25}{'ATS Record':<15}{'Cover %':<12}{'ATS +/-':<10}")
        print("-" * 80)
        
        worst = self.get_worst_away_teams(min_games=5, top_n=top_n)
        for i, (team, rec) in enumerate(worst, 1):
            print(f"{i:<6}{team:<25}{rec.ats_record:<15}{rec.cover_pct:>6.1f}%{rec.ats_plus_minus:>10.1f}")
        
        # Road warriors (75%+)
        warriors = self.get_road_warriors(min_cover_pct=75.0, min_games=5)
        print(f"\n🔥 ROAD WARRIORS ({len(warriors)} teams with 75%+ cover rate away)")
        print("-" * 80)
        for team, rec in warriors[:15]:  # Top 15
            print(f"  {team:<25}{rec.ats_record:<15}{rec.cover_pct:>6.1f}%")
        
        # Home-dependent teams
        strugglers = self.get_home_dependent_teams(max_cover_pct=35.0, min_games=5)
        if strugglers:
            print(f"\n⚠️  HOME-DEPENDENT TEAMS ({len(strugglers)} teams with <35% cover rate away)")
            print("-" * 80)
            for team, rec in strugglers:
                print(f"  {team:<25}{rec.ats_record:<15}{rec.cover_pct:>6.1f}%")
        
        # Betting insights
        print("\n" + "="*80)
        print("BETTING INSIGHTS FOR AWAY GAMES")
        print("="*80)
        print("\n✓ BACK ON THE ROAD:")
        print("  • Road warriors with 75%+ away ATS (Portland St, Georgia Tech, Clemson, etc.)")
        print("  • Teams with positive ATS +/- on road")
        print("  • Proven away performers in hostile environments")
        
        print("\n⚠️  FADE ON THE ROAD:")
        print("  • Home-dependent teams with <35% away ATS")
        print("  • Teams with large negative ATS +/- on road")
        print("  • Teams that struggle in away environments")
        
        print("\n💡 KEY PRINCIPLES:")
        print("  • Road success is harder to achieve - value road warriors")
        print("  • Public often overvalues popular teams on the road")
        print("  • Look for teams that have proven road toughness")
        print("  • Fade home-dependent teams in away spots")
        
        print("\n" + "="*80 + "\n")


def main():
    """Main analysis function"""
    analyzer = ATSAwayAnalyzer()
    
    # Load data
    analyzer.load_from_csv('ats_away_team_2025_26_sample.csv')
    
    # Display comprehensive report
    analyzer.display_comprehensive_report(top_n=10)
    
    # Example: Analyze specific teams
    print("\nSPECIFIC TEAM EXAMPLES:")
    print("="*80)
    
    # Best away team
    analyzer.display_team_analysis("Portland St")
    
    # Compare Manhattan and Niagara
    analyzer.display_team_analysis("Manhattan")
    analyzer.display_team_analysis("Niagara")


if __name__ == "__main__":
    main()
