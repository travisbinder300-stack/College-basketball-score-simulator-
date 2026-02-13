"""
Lineup Impact Analysis
Track player performance based on lineup configurations (who's in/out)
Includes minutes, pace, usage, and hit rates with specific lineup combinations
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Set
from enum import Enum


class LineupStatus(Enum):
    """Status of a player in lineup"""
    IN_LINEUP = "in_lineup"
    OUT_OF_LINEUP = "out_of_lineup"
    BENCH = "bench"


@dataclass
class LineupConfiguration:
    """
    Configuration tracking which players are in/out of the lineup
    """
    game_id: str
    team: str
    players_in: List[str]  # Player IDs in the lineup
    players_out: List[str]  # Player IDs out of the lineup
    season: str
    
    def __str__(self):
        return f"{self.team} - In: {len(self.players_in)}, Out: {len(self.players_out)}"
    
    def has_player(self, player_id: str) -> bool:
        """Check if player is in the lineup"""
        return player_id in self.players_in
    
    def is_player_out(self, player_id: str) -> bool:
        """Check if player is out of the lineup"""
        return player_id in self.players_out
    
    def get_lineup_key(self) -> str:
        """Get unique key for this lineup configuration"""
        in_sorted = sorted(self.players_in)
        out_sorted = sorted(self.players_out)
        return f"IN:{','.join(in_sorted)}|OUT:{','.join(out_sorted)}"


@dataclass
class LineupImpactStats:
    """
    Performance statistics for a specific lineup configuration
    """
    player_id: str
    player_name: str
    lineup_config: LineupConfiguration
    
    # Playing time
    minutes_per_game: float
    games_played: int
    
    # Pace and usage
    pace: float  # Possessions per 48 minutes
    usage_rate: float  # % of team possessions used
    
    # Performance stats
    points_per_game: float
    rebounds_per_game: float
    assists_per_game: float
    
    # Efficiency
    field_goal_percentage: float
    three_point_percentage: float
    true_shooting_percentage: float
    
    # Hit rates (for prop betting)
    points_hit_rate: Dict[float, float]  # Line -> hit rate
    rebounds_hit_rate: Dict[float, float]
    assists_hit_rate: Dict[float, float]
    
    def get_hit_rate(self, stat_type: str, line: float) -> Optional[float]:
        """Get hit rate for a specific stat and line"""
        hit_rates = {
            'points': self.points_hit_rate,
            'rebounds': self.rebounds_hit_rate,
            'assists': self.assists_hit_rate
        }
        
        stat_dict = hit_rates.get(stat_type)
        if stat_dict:
            # Find closest line
            if line in stat_dict:
                return stat_dict[line]
            # Interpolate if exact line not available
            lines = sorted(stat_dict.keys())
            if lines:
                closest = min(lines, key=lambda x: abs(x - line))
                return stat_dict[closest]
        return None
    
    def __str__(self):
        return f"{self.player_name}: {self.minutes_per_game:.1f} MPG, {self.points_per_game:.1f} PPG (Pace: {self.pace:.1f})"


@dataclass
class KeyPlayerImpact:
    """
    Impact of a specific key player being in or out of the lineup
    Tracks how another player performs with/without this key player
    """
    affected_player_id: str
    affected_player_name: str
    key_player_id: str
    key_player_name: str
    
    # Stats with key player IN lineup
    with_key_player: Optional[LineupImpactStats]
    
    # Stats with key player OUT of lineup
    without_key_player: Optional[LineupImpactStats]
    
    def get_impact_differential(self) -> Dict[str, float]:
        """
        Calculate the differential in performance with/without key player
        Positive value means better with key player
        """
        if not self.with_key_player or not self.without_key_player:
            return {}
        
        return {
            "minutes_diff": self.with_key_player.minutes_per_game - self.without_key_player.minutes_per_game,
            "pace_diff": self.with_key_player.pace - self.without_key_player.pace,
            "usage_diff": self.with_key_player.usage_rate - self.without_key_player.usage_rate,
            "points_diff": self.with_key_player.points_per_game - self.without_key_player.points_per_game,
            "rebounds_diff": self.with_key_player.rebounds_per_game - self.without_key_player.rebounds_per_game,
            "assists_diff": self.with_key_player.assists_per_game - self.without_key_player.assists_per_game,
            "fg_pct_diff": self.with_key_player.field_goal_percentage - self.without_key_player.field_goal_percentage,
            "ts_pct_diff": self.with_key_player.true_shooting_percentage - self.without_key_player.true_shooting_percentage
        }
    
    def get_impact_summary(self) -> str:
        """Get human-readable summary of impact"""
        if not self.with_key_player or not self.without_key_player:
            return "Insufficient data"
        
        diff = self.get_impact_differential()
        
        summary = []
        summary.append(f"{self.affected_player_name} with/without {self.key_player_name}:")
        summary.append(f"  Minutes: {self.with_key_player.minutes_per_game:.1f} vs {self.without_key_player.minutes_per_game:.1f} ({diff['minutes_diff']:+.1f})")
        summary.append(f"  Pace: {self.with_key_player.pace:.1f} vs {self.without_key_player.pace:.1f} ({diff['pace_diff']:+.1f})")
        summary.append(f"  Usage: {self.with_key_player.usage_rate:.1%} vs {self.without_key_player.usage_rate:.1%} ({diff['usage_diff']:+.1%})")
        summary.append(f"  PPG: {self.with_key_player.points_per_game:.1f} vs {self.without_key_player.points_per_game:.1f} ({diff['points_diff']:+.1f})")
        summary.append(f"  FG%: {self.with_key_player.field_goal_percentage:.1%} vs {self.without_key_player.field_goal_percentage:.1%} ({diff['fg_pct_diff']:+.1%})")
        
        return "\n".join(summary)


@dataclass
class TeamPaceMetrics:
    """Team-level pace metrics"""
    team: str
    season: str
    
    overall_pace: float  # Overall team pace
    home_pace: float
    away_pace: float
    
    # Pace by lineup configuration
    pace_by_lineup: Dict[str, float]  # lineup_key -> pace
    
    def get_pace_for_lineup(self, lineup_config: LineupConfiguration) -> float:
        """Get pace for specific lineup"""
        key = lineup_config.get_lineup_key()
        return self.pace_by_lineup.get(key, self.overall_pace)


class LineupImpactAnalyzer:
    """Analyze player performance based on lineup configurations"""
    
    def __init__(self):
        self.lineup_stats_cache: Dict[str, LineupImpactStats] = {}
        self.key_player_impacts: Dict[str, List[KeyPlayerImpact]] = {}
    
    def add_lineup_stats(self, stats: LineupImpactStats):
        """Add lineup statistics to cache"""
        key = f"{stats.player_id}_{stats.lineup_config.get_lineup_key()}"
        self.lineup_stats_cache[key] = stats
    
    def get_lineup_stats(
        self,
        player_id: str,
        lineup_config: LineupConfiguration
    ) -> Optional[LineupImpactStats]:
        """Get stats for player in specific lineup"""
        key = f"{player_id}_{lineup_config.get_lineup_key()}"
        return self.lineup_stats_cache.get(key)
    
    def analyze_key_player_impact(
        self,
        affected_player_id: str,
        key_player_id: str,
        all_lineup_stats: List[LineupImpactStats]
    ) -> Optional[KeyPlayerImpact]:
        """
        Analyze how a player performs with/without a key teammate
        """
        # Find stats with key player in lineup
        with_key_stats = None
        without_key_stats = None
        
        for stats in all_lineup_stats:
            if stats.player_id != affected_player_id:
                continue
            
            if stats.lineup_config.has_player(key_player_id):
                # Key player is in lineup
                if not with_key_stats or stats.games_played > with_key_stats.games_played:
                    with_key_stats = stats
            elif not stats.lineup_config.is_player_out(key_player_id):
                # Key player is on team but not specifically tracked
                continue
            else:
                # Key player is out of lineup
                if not without_key_stats or stats.games_played > without_key_stats.games_played:
                    without_key_stats = stats
        
        if with_key_stats or without_key_stats:
            # Get player names
            affected_name = with_key_stats.player_name if with_key_stats else without_key_stats.player_name
            key_name = "Key Player"  # Would need lookup
            
            return KeyPlayerImpact(
                affected_player_id=affected_player_id,
                affected_player_name=affected_name,
                key_player_id=key_player_id,
                key_player_name=key_name,
                with_key_player=with_key_stats,
                without_key_player=without_key_stats
            )
        
        return None
    
    def calculate_prop_adjustment(
        self,
        player_id: str,
        lineup_config: LineupConfiguration,
        prop_type: str,
        base_line: float
    ) -> Dict[str, float]:
        """
        Calculate prop adjustment based on lineup
        Returns adjustment factors and projected values
        """
        stats = self.get_lineup_stats(player_id, lineup_config)
        
        if not stats:
            return {
                "adjustment_factor": 1.0,
                "adjusted_value": base_line,
                "confidence": 0.0
            }
        
        # Get expected value based on lineup
        prop_value_map = {
            'points': stats.points_per_game,
            'rebounds': stats.rebounds_per_game,
            'assists': stats.assists_per_game
        }
        
        lineup_value = prop_value_map.get(prop_type, base_line)
        
        # Calculate adjustment factor
        adjustment_factor = lineup_value / base_line if base_line > 0 else 1.0
        
        # Calculate confidence based on games played
        confidence = min(stats.games_played / 20.0, 1.0)  # Full confidence at 20+ games
        
        # Get hit rate for this line
        hit_rate = stats.get_hit_rate(prop_type, base_line)
        
        return {
            "adjustment_factor": adjustment_factor,
            "adjusted_value": lineup_value,
            "confidence": confidence,
            "hit_rate": hit_rate,
            "games_played": stats.games_played,
            "minutes_per_game": stats.minutes_per_game,
            "usage_rate": stats.usage_rate,
            "pace": stats.pace
        }
    
    def compare_lineups(
        self,
        player_id: str,
        lineup1: LineupConfiguration,
        lineup2: LineupConfiguration
    ) -> Dict[str, float]:
        """Compare player's performance in two different lineups"""
        stats1 = self.get_lineup_stats(player_id, lineup1)
        stats2 = self.get_lineup_stats(player_id, lineup2)
        
        if not stats1 or not stats2:
            return {}
        
        return {
            "minutes_diff": stats1.minutes_per_game - stats2.minutes_per_game,
            "pace_diff": stats1.pace - stats2.pace,
            "usage_diff": stats1.usage_rate - stats2.usage_rate,
            "points_diff": stats1.points_per_game - stats2.points_per_game,
            "rebounds_diff": stats1.rebounds_per_game - stats2.rebounds_per_game,
            "assists_diff": stats1.assists_per_game - stats2.assists_per_game,
            "fg_pct_diff": stats1.field_goal_percentage - stats2.field_goal_percentage
        }


def generate_sample_lineup_data() -> List[LineupImpactStats]:
    """Generate sample lineup impact data for 2025-26 season"""
    
    # LeBron James with Austin Reaves in lineup (2025-26)
    lebron_with_reaves = LineupConfiguration(
        game_id="sample_1",
        team="Los Angeles Lakers",
        players_in=["2544", "1630559"],  # LeBron, Austin Reaves
        players_out=[],
        season="2025-26"
    )
    
    lebron_with_reaves_stats = LineupImpactStats(
        player_id="2544",
        player_name="LeBron James",
        lineup_config=lebron_with_reaves,
        minutes_per_game=32.8,
        games_played=42,
        pace=101.2,
        usage_rate=0.285,
        points_per_game=24.2,
        rebounds_per_game=7.5,
        assists_per_game=8.8,
        field_goal_percentage=0.515,
        three_point_percentage=0.368,
        true_shooting_percentage=0.598,
        points_hit_rate={23.5: 0.55, 25.5: 0.45, 27.5: 0.35},
        rebounds_hit_rate={7.5: 0.52, 8.5: 0.40},
        assists_hit_rate={8.5: 0.54, 9.5: 0.42}
    )
    
    # LeBron James without Austin Reaves (2025-26)
    lebron_without_reaves = LineupConfiguration(
        game_id="sample_2",
        team="Los Angeles Lakers",
        players_in=["2544"],  # Just LeBron
        players_out=["1630559"],  # Reaves out
        season="2025-26"
    )
    
    lebron_without_reaves_stats = LineupImpactStats(
        player_id="2544",
        player_name="LeBron James",
        lineup_config=lebron_without_reaves,
        minutes_per_game=35.5,
        games_played=12,
        pace=97.5,
        usage_rate=0.325,
        points_per_game=27.2,
        rebounds_per_game=8.8,
        assists_per_game=10.5,
        field_goal_percentage=0.488,
        three_point_percentage=0.355,
        true_shooting_percentage=0.578,
        points_hit_rate={23.5: 0.75, 25.5: 0.67, 27.5: 0.50},
        rebounds_hit_rate={7.5: 0.75, 8.5: 0.58},
        assists_hit_rate={8.5: 0.83, 9.5: 0.67}
    )
    
    # Stephen Curry with Draymond Green (2025-26)
    curry_with_draymond = LineupConfiguration(
        game_id="sample_3",
        team="Golden State Warriors",
        players_in=["201939", "203110"],  # Curry, Draymond
        players_out=[],
        season="2025-26"
    )
    
    curry_with_draymond_stats = LineupImpactStats(
        player_id="201939",
        player_name="Stephen Curry",
        lineup_config=curry_with_draymond,
        minutes_per_game=31.2,
        games_played=48,
        pace=103.5,
        usage_rate=0.305,
        points_per_game=25.8,
        rebounds_per_game=4.2,
        assists_per_game=6.2,
        field_goal_percentage=0.448,
        three_point_percentage=0.412,
        true_shooting_percentage=0.652,
        points_hit_rate={25.5: 0.52, 27.5: 0.42, 29.5: 0.32},
        rebounds_hit_rate={4.5: 0.48, 5.5: 0.32},
        assists_hit_rate={6.5: 0.48, 7.5: 0.35}
    )
    
    # Stephen Curry without Draymond Green (2025-26)
    curry_without_draymond = LineupConfiguration(
        game_id="sample_4",
        team="Golden State Warriors",
        players_in=["201939"],  # Just Curry
        players_out=["203110"],  # Draymond out
        season="2025-26"
    )
    
    curry_without_draymond_stats = LineupImpactStats(
        player_id="201939",
        player_name="Stephen Curry",
        lineup_config=curry_without_draymond,
        minutes_per_game=33.5,
        games_played=16,
        pace=98.8,
        usage_rate=0.338,
        points_per_game=28.8,
        rebounds_per_game=4.8,
        assists_per_game=7.2,
        field_goal_percentage=0.438,
        three_point_percentage=0.405,
        true_shooting_percentage=0.645,
        points_hit_rate={25.5: 0.69, 27.5: 0.56, 29.5: 0.44},
        rebounds_hit_rate={4.5: 0.62, 5.5: 0.44},
        assists_hit_rate={6.5: 0.69, 7.5: 0.56}
    )
    
    return [
        lebron_with_reaves_stats,
        lebron_without_reaves_stats,
        curry_with_draymond_stats,
        curry_without_draymond_stats
    ]


def main():
    """Demonstrate lineup impact analysis"""
    print("=" * 80)
    print("LINEUP IMPACT ANALYSIS")
    print("=" * 80)
    print()
    
    # Generate sample data
    lineup_stats = generate_sample_lineup_data()
    
    # Initialize analyzer
    analyzer = LineupImpactAnalyzer()
    
    # Add stats to analyzer
    for stats in lineup_stats:
        analyzer.add_lineup_stats(stats)
    
    # Analyze LeBron with/without Austin Reaves
    print("KEY PLAYER IMPACT ANALYSIS")
    print("-" * 80)
    
    lebron_reaves_impact = analyzer.analyze_key_player_impact(
        "2544",  # LeBron
        "1630559",  # Austin Reaves
        lineup_stats
    )
    
    if lebron_reaves_impact:
        print(lebron_reaves_impact.get_impact_summary())
        print()
        
        diff = lebron_reaves_impact.get_impact_differential()
        print("Impact Differential:")
        for key, value in diff.items():
            print(f"  {key}: {value:+.3f}")
    
    print("\n" + "=" * 80)
    print("PROP ADJUSTMENT BASED ON LINEUP")
    print("-" * 80)
    
    # LeBron points prop with Reaves in lineup
    lebron_with_reaves_config = lineup_stats[0].lineup_config
    adjustment = analyzer.calculate_prop_adjustment(
        "2544",  # LeBron
        lebron_with_reaves_config,
        "points",
        25.5  # Base line
    )
    
    print("\nLeBron James Points (O/U 25.5) WITH Austin Reaves:")
    for key, value in adjustment.items():
        if isinstance(value, float):
            if 'rate' in key or 'factor' in key or 'confidence' in key:
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    # LeBron points prop without Reaves
    lebron_without_reaves_config = lineup_stats[1].lineup_config
    adjustment_no_reaves = analyzer.calculate_prop_adjustment(
        "2544",
        lebron_without_reaves_config,
        "points",
        25.5
    )
    
    print("\nLeBron James Points (O/U 25.5) WITHOUT Austin Reaves:")
    for key, value in adjustment_no_reaves.items():
        if isinstance(value, float):
            if 'rate' in key or 'factor' in key or 'confidence' in key:
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    # Compare the two scenarios
    print("\n" + "-" * 80)
    print("COMPARISON: With Reaves vs Without Reaves")
    print("-" * 80)
    
    print(f"Adjusted Value: {adjustment['adjusted_value']:.1f} vs {adjustment_no_reaves['adjusted_value']:.1f}")
    print(f"Hit Rate: {adjustment.get('hit_rate', 0):.1%} vs {adjustment_no_reaves.get('hit_rate', 0):.1%}")
    print(f"Usage Rate: {adjustment['usage_rate']:.1%} vs {adjustment_no_reaves['usage_rate']:.1%}")
    print(f"Pace: {adjustment['pace']:.1f} vs {adjustment_no_reaves['pace']:.1f}")
    
    print("\n✅ Lineup impact analysis complete!")


if __name__ == "__main__":
    main()
