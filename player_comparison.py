"""
Player Comparison Module
Compare player prop performance - Luka Doncic vs LeBron James
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ComparisonMetric(Enum):
    """Metrics for comparing players"""
    POINTS = "points"
    REBOUNDS = "rebounds"
    ASSISTS = "assists"
    USAGE_RATE = "usage_rate"
    PACE = "pace"
    EFFICIENCY = "efficiency"
    PROP_HIT_RATE = "prop_hit_rate"


@dataclass
class PlayerProfile:
    """Complete player profile for comparison"""
    player_id: str
    player_name: str
    team: str
    position: str
    season: str
    
    # Basic stats
    points_per_game: float
    rebounds_per_game: float
    assists_per_game: float
    
    # Advanced stats
    usage_rate: float
    pace: float
    true_shooting_percentage: float
    field_goal_percentage: float
    three_point_percentage: float
    
    # Prop performance
    prop_hit_rates: Dict[str, Dict[float, float]]  # stat_type -> line -> hit_rate
    
    # Minutes and workload
    minutes_per_game: float
    games_played: int
    
    def __str__(self):
        return f"{self.player_name} ({self.team}) - {self.season}"


@dataclass
class ComparisonResult:
    """Result of comparing two players"""
    player1: PlayerProfile
    player2: PlayerProfile
    
    similarities: Dict[str, float]  # metric -> similarity score (0-1)
    differences: Dict[str, float]  # metric -> difference
    
    overall_similarity: float
    
    strengths_player1: List[str]
    strengths_player2: List[str]
    
    prop_recommendations: Dict[str, str]  # prop_type -> recommendation
    
    def get_summary(self) -> str:
        """Get human-readable comparison summary"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"PLAYER COMPARISON: {self.player1.player_name} vs {self.player2.player_name}")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"Overall Similarity: {self.overall_similarity:.1%}")
        lines.append("")
        
        lines.append("-" * 80)
        lines.append("STATISTICAL COMPARISON")
        lines.append("-" * 80)
        
        lines.append(f"\nPoints per Game:")
        lines.append(f"  {self.player1.player_name}: {self.player1.points_per_game:.1f}")
        lines.append(f"  {self.player2.player_name}: {self.player2.points_per_game:.1f}")
        lines.append(f"  Difference: {abs(self.player1.points_per_game - self.player2.points_per_game):.1f}")
        
        lines.append(f"\nAssists per Game:")
        lines.append(f"  {self.player1.player_name}: {self.player1.assists_per_game:.1f}")
        lines.append(f"  {self.player2.player_name}: {self.player2.assists_per_game:.1f}")
        lines.append(f"  Difference: {abs(self.player1.assists_per_game - self.player2.assists_per_game):.1f}")
        
        lines.append(f"\nUsage Rate:")
        lines.append(f"  {self.player1.player_name}: {self.player1.usage_rate:.1%}")
        lines.append(f"  {self.player2.player_name}: {self.player2.usage_rate:.1%}")
        lines.append(f"  Difference: {abs(self.player1.usage_rate - self.player2.usage_rate):.1%}")
        
        lines.append("")
        lines.append("-" * 80)
        lines.append("STRENGTHS")
        lines.append("-" * 80)
        
        lines.append(f"\n{self.player1.player_name}:")
        for strength in self.strengths_player1:
            lines.append(f"  • {strength}")
        
        lines.append(f"\n{self.player2.player_name}:")
        for strength in self.strengths_player2:
            lines.append(f"  • {strength}")
        
        if self.prop_recommendations:
            lines.append("")
            lines.append("-" * 80)
            lines.append("PROP BETTING RECOMMENDATIONS")
            lines.append("-" * 80)
            for prop_type, recommendation in self.prop_recommendations.items():
                lines.append(f"\n{prop_type.upper()}: {recommendation}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


class PlayerComparator:
    """Compare two players across multiple metrics"""
    
    def __init__(self):
        self.comparison_weights = {
            ComparisonMetric.POINTS: 0.25,
            ComparisonMetric.ASSISTS: 0.20,
            ComparisonMetric.REBOUNDS: 0.15,
            ComparisonMetric.USAGE_RATE: 0.15,
            ComparisonMetric.EFFICIENCY: 0.15,
            ComparisonMetric.PACE: 0.10
        }
    
    def calculate_similarity(self, value1: float, value2: float, max_diff: float) -> float:
        """
        Calculate similarity score between two values
        Returns 1.0 for identical, approaching 0 as difference increases
        """
        diff = abs(value1 - value2)
        if diff >= max_diff:
            return 0.0
        return 1.0 - (diff / max_diff)
    
    def compare_players(
        self,
        player1: PlayerProfile,
        player2: PlayerProfile
    ) -> ComparisonResult:
        """
        Comprehensive comparison between two players
        """
        similarities = {}
        differences = {}
        
        # Points comparison
        similarities[ComparisonMetric.POINTS.value] = self.calculate_similarity(
            player1.points_per_game,
            player2.points_per_game,
            max_diff=15.0
        )
        differences[ComparisonMetric.POINTS.value] = player1.points_per_game - player2.points_per_game
        
        # Assists comparison
        similarities[ComparisonMetric.ASSISTS.value] = self.calculate_similarity(
            player1.assists_per_game,
            player2.assists_per_game,
            max_diff=8.0
        )
        differences[ComparisonMetric.ASSISTS.value] = player1.assists_per_game - player2.assists_per_game
        
        # Rebounds comparison
        similarities[ComparisonMetric.REBOUNDS.value] = self.calculate_similarity(
            player1.rebounds_per_game,
            player2.rebounds_per_game,
            max_diff=6.0
        )
        differences[ComparisonMetric.REBOUNDS.value] = player1.rebounds_per_game - player2.rebounds_per_game
        
        # Usage rate comparison
        similarities[ComparisonMetric.USAGE_RATE.value] = self.calculate_similarity(
            player1.usage_rate,
            player2.usage_rate,
            max_diff=0.15
        )
        differences[ComparisonMetric.USAGE_RATE.value] = player1.usage_rate - player2.usage_rate
        
        # Efficiency comparison
        similarities[ComparisonMetric.EFFICIENCY.value] = self.calculate_similarity(
            player1.true_shooting_percentage,
            player2.true_shooting_percentage,
            max_diff=0.10
        )
        differences[ComparisonMetric.EFFICIENCY.value] = player1.true_shooting_percentage - player2.true_shooting_percentage
        
        # Pace comparison
        similarities[ComparisonMetric.PACE.value] = self.calculate_similarity(
            player1.pace,
            player2.pace,
            max_diff=10.0
        )
        differences[ComparisonMetric.PACE.value] = player1.pace - player2.pace
        
        # Calculate overall similarity
        overall_similarity = sum(
            similarities[metric.value] * self.comparison_weights[metric]
            for metric in self.comparison_weights.keys()
        )
        
        # Identify strengths
        strengths_player1 = []
        strengths_player2 = []
        
        if player1.points_per_game > player2.points_per_game:
            strengths_player1.append(f"Higher scoring: {player1.points_per_game:.1f} vs {player2.points_per_game:.1f} PPG")
        else:
            strengths_player2.append(f"Higher scoring: {player2.points_per_game:.1f} vs {player1.points_per_game:.1f} PPG")
        
        if player1.assists_per_game > player2.assists_per_game:
            strengths_player1.append(f"Better playmaker: {player1.assists_per_game:.1f} vs {player2.assists_per_game:.1f} APG")
        else:
            strengths_player2.append(f"Better playmaker: {player2.assists_per_game:.1f} vs {player1.assists_per_game:.1f} APG")
        
        if player1.true_shooting_percentage > player2.true_shooting_percentage:
            strengths_player1.append(f"More efficient: {player1.true_shooting_percentage:.1%} vs {player2.true_shooting_percentage:.1%} TS%")
        else:
            strengths_player2.append(f"More efficient: {player2.true_shooting_percentage:.1%} vs {player1.true_shooting_percentage:.1%} TS%")
        
        if player1.usage_rate > player2.usage_rate:
            strengths_player1.append(f"Higher usage: {player1.usage_rate:.1%} vs {player2.usage_rate:.1%}")
        else:
            strengths_player2.append(f"Higher usage: {player2.usage_rate:.1%} vs {player1.usage_rate:.1%}")
        
        # Generate prop recommendations
        prop_recommendations = self._generate_prop_recommendations(player1, player2, differences)
        
        return ComparisonResult(
            player1=player1,
            player2=player2,
            similarities=similarities,
            differences=differences,
            overall_similarity=overall_similarity,
            strengths_player1=strengths_player1,
            strengths_player2=strengths_player2,
            prop_recommendations=prop_recommendations
        )
    
    def _generate_prop_recommendations(
        self,
        player1: PlayerProfile,
        player2: PlayerProfile,
        differences: Dict[str, float]
    ) -> Dict[str, str]:
        """Generate prop betting recommendations based on comparison"""
        recommendations = {}
        
        # Points recommendations
        if abs(differences[ComparisonMetric.POINTS.value]) > 3.0:
            if differences[ComparisonMetric.POINTS.value] > 0:
                recommendations["points"] = f"{player1.player_name} averages {abs(differences[ComparisonMetric.POINTS.value]):.1f} more PPG - favor OVER for {player1.player_name}"
            else:
                recommendations["points"] = f"{player2.player_name} averages {abs(differences[ComparisonMetric.POINTS.value]):.1f} more PPG - favor OVER for {player2.player_name}"
        else:
            recommendations["points"] = f"Similar scoring output ({abs(differences[ComparisonMetric.POINTS.value]):.1f} PPG diff) - use matchup data to decide"
        
        # Assists recommendations
        if abs(differences[ComparisonMetric.ASSISTS.value]) > 2.0:
            if differences[ComparisonMetric.ASSISTS.value] > 0:
                recommendations["assists"] = f"{player1.player_name} averages {abs(differences[ComparisonMetric.ASSISTS.value]):.1f} more APG - favor OVER for {player1.player_name}"
            else:
                recommendations["assists"] = f"{player2.player_name} averages {abs(differences[ComparisonMetric.ASSISTS.value]):.1f} more APG - favor OVER for {player2.player_name}"
        else:
            recommendations["assists"] = f"Similar playmaking ({abs(differences[ComparisonMetric.ASSISTS.value]):.1f} APG diff)"
        
        # Usage/efficiency trade-off
        if differences[ComparisonMetric.USAGE_RATE.value] > 0.05:
            if differences[ComparisonMetric.EFFICIENCY.value] > 0:
                recommendations["efficiency"] = f"{player1.player_name} has higher usage AND efficiency - excellent prop value"
            else:
                recommendations["efficiency"] = f"{player1.player_name} has higher usage but lower efficiency - volume scorer profile"
        elif differences[ComparisonMetric.USAGE_RATE.value] < -0.05:
            if differences[ComparisonMetric.EFFICIENCY.value] < 0:
                recommendations["efficiency"] = f"{player2.player_name} has higher usage AND efficiency - excellent prop value"
            else:
                recommendations["efficiency"] = f"{player2.player_name} has higher usage but lower efficiency - volume scorer profile"
        
        return recommendations
    
    def compare_prop_hit_rates(
        self,
        player1: PlayerProfile,
        player2: PlayerProfile,
        prop_type: str,
        line: float
    ) -> Dict[str, any]:
        """Compare prop hit rates for a specific prop"""
        hit_rate1 = None
        hit_rate2 = None
        
        if prop_type in player1.prop_hit_rates:
            if line in player1.prop_hit_rates[prop_type]:
                hit_rate1 = player1.prop_hit_rates[prop_type][line]
        
        if prop_type in player2.prop_hit_rates:
            if line in player2.prop_hit_rates[prop_type]:
                hit_rate2 = player2.prop_hit_rates[prop_type][line]
        
        result = {
            "prop_type": prop_type,
            "line": line,
            f"{player1.player_name}_hit_rate": hit_rate1,
            f"{player2.player_name}_hit_rate": hit_rate2
        }
        
        if hit_rate1 is not None and hit_rate2 is not None:
            result["difference"] = hit_rate1 - hit_rate2
            result["better_value"] = player1.player_name if hit_rate1 > hit_rate2 else player2.player_name
        
        return result


def create_luka_doncic_profile() -> PlayerProfile:
    """Create Luka Doncic player profile for 2025-26 season (Updated February 2026)"""
    return PlayerProfile(
        player_id="1629029",
        player_name="Luka Doncic",
        team="Dallas Mavericks",
        position="PG/SG",
        season="2025-26 (Feb 2026)",
        points_per_game=34.5,
        rebounds_per_game=9.4,
        assists_per_game=9.8,
        usage_rate=0.370,
        pace=99.8,
        true_shooting_percentage=0.625,
        field_goal_percentage=0.493,
        three_point_percentage=0.387,
        prop_hit_rates={
            "points": {
                30.5: 0.73,
                32.5: 0.64,
                34.5: 0.54,
                36.5: 0.43
            },
            "rebounds": {
                8.5: 0.67,
                9.5: 0.58,
                10.5: 0.45
            },
            "assists": {
                8.5: 0.76,
                9.5: 0.68,
                10.5: 0.57,
                11.5: 0.44
            }
        },
        minutes_per_game=37.5,
        games_played=67
    )


def create_lebron_james_profile() -> PlayerProfile:
    """Create LeBron James player profile for 2025-26 season (Updated February 2026)"""
    return PlayerProfile(
        player_id="2544",
        player_name="LeBron James",
        team="Los Angeles Lakers",
        position="SF/PF",
        season="2025-26 (Feb 2026)",
        points_per_game=24.8,
        rebounds_per_game=7.8,
        assists_per_game=9.2,
        usage_rate=0.298,
        pace=99.5,
        true_shooting_percentage=0.585,
        field_goal_percentage=0.498,
        three_point_percentage=0.358,
        prop_hit_rates={
            "points": {
                23.5: 0.58,
                25.5: 0.48,
                27.5: 0.38,
                29.5: 0.28
            },
            "rebounds": {
                7.5: 0.55,
                8.5: 0.45,
                9.5: 0.32
            },
            "assists": {
                8.5: 0.64,
                9.5: 0.52,
                10.5: 0.39,
                11.5: 0.26
            }
        },
        minutes_per_game=33.5,
        games_played=62
    )


def main():
    """Demonstrate Luka Doncic vs LeBron James comparison"""
    print("=" * 80)
    print("LUKA DONCIC vs LEBRON JAMES PROP COMPARISON")
    print("2025-26 NBA Season")
    print("=" * 80)
    print()
    
    # Create player profiles
    luka = create_luka_doncic_profile()
    lebron = create_lebron_james_profile()
    
    print(f"Player 1: {luka}")
    print(f"Player 2: {lebron}")
    print()
    
    # Compare players
    comparator = PlayerComparator()
    comparison = comparator.compare_players(luka, lebron)
    
    # Display results
    print(comparison.get_summary())
    
    # Compare specific prop hit rates
    print("\n" + "=" * 80)
    print("PROP HIT RATE COMPARISON")
    print("=" * 80)
    print()
    
    # Points prop comparison
    points_lines = [30.5, 32.5]
    for line in points_lines:
        result = comparator.compare_prop_hit_rates(luka, lebron, "points", line)
        print(f"\nPoints O/U {line}:")
        print(f"  Luka: {result.get(f'{luka.player_name}_hit_rate', 'N/A'):.1%}" if result.get(f"{luka.player_name}_hit_rate") else f"  Luka: N/A")
        print(f"  LeBron: {result.get(f'{lebron.player_name}_hit_rate', 'N/A'):.1%}" if result.get(f"{lebron.player_name}_hit_rate") else f"  LeBron: N/A")
        if 'better_value' in result:
            print(f"  Better Value: {result['better_value']}")
    
    # Assists prop comparison
    assists_lines = [9.5, 10.5]
    for line in assists_lines:
        result = comparator.compare_prop_hit_rates(luka, lebron, "assists", line)
        print(f"\nAssists O/U {line}:")
        print(f"  Luka: {result.get(f'{luka.player_name}_hit_rate', 'N/A'):.1%}" if result.get(f"{luka.player_name}_hit_rate") else f"  Luka: N/A")
        print(f"  LeBron: {result.get(f'{lebron.player_name}_hit_rate', 'N/A'):.1%}" if result.get(f"{lebron.player_name}_hit_rate") else f"  LeBron: N/A")
        if 'better_value' in result:
            print(f"  Better Value: {result['better_value']}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print()
    print("• Luka Doncic is a higher volume scorer with elite usage rate")
    print("• LeBron James remains efficient despite lower usage in 2025-26")
    print("• Both are elite playmakers with similar assists numbers")
    print("• Luka's prop lines are higher, reflecting his scoring dominance")
    print("• LeBron provides value on lower lines with consistent performance")
    print()
    print("✅ Comparison complete!")


if __name__ == "__main__":
    main()
