"""
Integration: Shot Chart Defense Analysis with Prop Betting
Enhances prop analysis with defensive matchup data and similar player comparisons
"""

from typing import List, Dict, Optional, Tuple
from nba_prop_data import PlayerProp, PropType, Player, Game
from shot_chart_defense import (
    PlayerProfile, DefensiveMatchup, DefenderStats,
    TeamDefenseRanking, DefensiveMatchupAnalyzer,
    ShotZone, PlayStyle
)


class EnhancedPropAnalyzer:
    """
    Enhanced prop analyzer that incorporates shot chart and defensive matchup data
    """
    
    def __init__(self, matchup_analyzer: DefensiveMatchupAnalyzer):
        self.matchup_analyzer = matchup_analyzer
    
    def analyze_prop_with_matchup(
        self,
        prop: PlayerProp,
        player_profile: PlayerProfile,
        team_defense: TeamDefenseRanking,
        primary_defender: Optional[DefenderStats] = None
    ) -> Dict:
        """
        Analyze a prop bet with defensive matchup context
        Returns enhanced analysis with matchup-based adjustments
        """
        # Get defensive matchup analysis
        matchup = self.matchup_analyzer.analyze_matchup(
            player_profile,
            team_defense,
            primary_defender
        )
        
        # Base prop analysis (season average)
        base_value = prop.player_season_avg or prop.prop_line.line_value
        
        # Adjust based on matchup
        matchup_adjustment = matchup.expected_fg_boost
        
        # Prop-specific adjustments
        prop_multiplier = self._get_prop_multiplier(prop.prop_type, matchup)
        
        adjusted_projection = base_value * (1 + matchup_adjustment) * prop_multiplier
        
        # Calculate hit probability with matchup data
        line = prop.prop_line.line_value
        hit_probability_over = self._calculate_hit_prob(
            adjusted_projection, line, matchup.overall_matchup_rating
        )
        
        # Get market implied probability
        market_prob = prop.prop_line.get_implied_probability(True)
        
        # Calculate edge
        edge = hit_probability_over - market_prob
        
        return {
            "prop": str(prop),
            "base_projection": base_value,
            "adjusted_projection": adjusted_projection,
            "line": line,
            "matchup_rating": matchup.overall_matchup_rating,
            "expected_fg_boost": matchup.expected_fg_boost,
            "hit_probability": hit_probability_over,
            "market_probability": market_prob,
            "edge": edge,
            "recommendation": "OVER" if edge > 0.05 else "UNDER" if edge < -0.05 else "PASS",
            "favorable_zones": [z.value for z, _ in matchup.favorable_zones[:3]],
            "confidence": self._calculate_confidence(matchup, prop)
        }
    
    def _get_prop_multiplier(self, prop_type: PropType, matchup: DefensiveMatchup) -> float:
        """Get prop-specific multiplier based on matchup"""
        # Points props benefit directly from FG% boost
        if prop_type == PropType.POINTS:
            return 1.0
        
        # Rebounds - check if defense gives up rebounds
        elif prop_type == PropType.REBOUNDS:
            # Check paint defense (weak paint defense = more rebounds)
            paint_rank = matchup.team_defense.paint_defense_rank
            return 1.0 + (paint_rank - 15) * 0.01
        
        # Assists - check if defense creates turnovers
        elif prop_type == PropType.ASSISTS:
            return 0.98  # Slightly lower in tough matchups
        
        # Three pointers
        elif prop_type == PropType.THREE_POINTERS:
            three_rank = matchup.team_defense.three_pt_defense_rank
            return 1.0 + (three_rank - 15) * 0.015
        
        return 1.0
    
    def _calculate_hit_prob(
        self,
        projection: float,
        line: float,
        matchup_rating: float
    ) -> float:
        """Calculate hit probability with matchup adjustment"""
        # Base probability from projection vs line
        diff = projection - line
        std_dev = projection * 0.15  # 15% variance
        
        if std_dev == 0:
            return 1.0 if diff > 0 else 0.0
        
        # Z-score
        z = diff / std_dev
        
        # Convert to probability (simplified normal CDF)
        if z > 0:
            prob = 0.5 + min(z * 0.2, 0.45)
        else:
            prob = 0.5 - min(abs(z) * 0.2, 0.45)
        
        # Adjust for matchup rating (-1 to +1)
        prob += matchup_rating * 0.05
        
        return max(0.0, min(1.0, prob))
    
    def _calculate_confidence(
        self,
        matchup: DefensiveMatchup,
        prop: PlayerProp
    ) -> str:
        """Calculate confidence level in the projection"""
        # Factor: matchup rating strength
        rating_strength = abs(matchup.overall_matchup_rating)
        
        # Factor: sample size (how much data we have)
        has_recent_data = prop.player_last_5_avg is not None
        has_opponent_data = prop.vs_opponent_avg is not None
        
        confidence_score = rating_strength
        if has_recent_data:
            confidence_score += 0.2
        if has_opponent_data:
            confidence_score += 0.3
        
        if confidence_score >= 0.8:
            return "HIGH"
        elif confidence_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def find_best_props_vs_defense(
        self,
        props: List[PlayerProp],
        player_profiles: Dict[str, PlayerProfile],
        team_defense: TeamDefenseRanking,
        defenders: Dict[str, DefenderStats],
        min_edge: float = 0.05
    ) -> List[Tuple[PlayerProp, Dict]]:
        """
        Find best prop bets considering defensive matchups
        Returns sorted list of (prop, analysis) tuples
        """
        analyzed_props = []
        
        for prop in props:
            # Get player profile
            player_profile = player_profiles.get(prop.player.player_id)
            if not player_profile:
                continue
            
            # Get defender if playing against this team
            defender = None
            # In real implementation, would match by opponent
            
            # Analyze with matchup
            analysis = self.analyze_prop_with_matchup(
                prop, player_profile, team_defense, defender
            )
            
            # Filter by edge
            if analysis["edge"] >= min_edge:
                analyzed_props.append((prop, analysis))
        
        # Sort by edge
        analyzed_props.sort(key=lambda x: x[1]["edge"], reverse=True)
        
        return analyzed_props
    
    def compare_with_similar_players(
        self,
        player_profile: PlayerProfile,
        all_profiles: List[PlayerProfile],
        team_defense: TeamDefenseRanking
    ) -> Dict:
        """
        Compare player projection with similar players' historical performance
        """
        # Find similar players
        similar_players = self.matchup_analyzer.find_similar_players(
            player_profile, all_profiles, min_similarity=0.6
        )
        
        if not similar_players:
            return {
                "has_similar_players": False,
                "message": "No similar players found"
            }
        
        # Get historical performance
        hist_perf = self.matchup_analyzer.get_historical_performance(
            similar_players, team_defense
        )
        
        # Analyze matchup for main player
        matchup = self.matchup_analyzer.analyze_matchup(
            player_profile, team_defense
        )
        
        return {
            "has_similar_players": True,
            "num_similar_players": len(similar_players),
            "similar_players": [
                {
                    "name": p.player_name,
                    "similarity": f"{sim:.1%}",
                    "play_style": p.primary_play_style.value
                }
                for p, sim in similar_players
            ],
            "historical_avg_fg_pct": hist_perf.get("historical_fg_pct", 0),
            "player_projection": matchup.expected_fg_boost,
            "confidence": hist_perf.get("historical_confidence", 0)
        }


def create_defensive_matchup_report(
    prop: PlayerProp,
    player_profile: PlayerProfile,
    team_defense: TeamDefenseRanking,
    similar_players: List[PlayerProfile],
    defender: Optional[DefenderStats] = None
) -> str:
    """
    Create a comprehensive defensive matchup report for a prop
    """
    analyzer = DefensiveMatchupAnalyzer()
    
    # Analyze matchup
    matchup = analyzer.analyze_matchup(player_profile, team_defense, defender)
    
    # Find similar players
    similar = analyzer.find_similar_players(
        player_profile, similar_players, min_similarity=0.6, max_results=3
    )
    
    # Build report
    report = []
    report.append("=" * 80)
    report.append(f"DEFENSIVE MATCHUP REPORT: {player_profile.player_name}")
    report.append("=" * 80)
    report.append("")
    
    # Prop details
    report.append(f"Prop: {prop}")
    report.append(f"Line: {prop.prop_line.line_value}")
    report.append(f"Player Season Avg: {prop.player_season_avg}")
    report.append("")
    
    # Matchup analysis
    report.append("-" * 80)
    report.append("MATCHUP ANALYSIS")
    report.append("-" * 80)
    report.append(f"Opponent: {team_defense.team}")
    report.append(f"Defense Type: {team_defense.primary_defense_type.value}")
    report.append(f"Defensive Rating: {team_defense.defensive_rating}")
    report.append(f"Opponent FG%: {team_defense.opponent_fg_pct:.1%}")
    report.append("")
    
    # Matchup rating
    report.append(f"Overall Matchup Rating: {matchup.overall_matchup_rating:+.2f}")
    report.append(f"Expected FG% Boost: {matchup.expected_fg_boost:+.2%}")
    report.append("")
    
    # Zone analysis
    report.append("Favorable Zones:")
    for zone, advantage in matchup.favorable_zones[:3]:
        report.append(f"  • {zone.value}: +{advantage:.1%} advantage")
    
    if matchup.unfavorable_zones:
        report.append("")
        report.append("Unfavorable Zones:")
        for zone, disadvantage in matchup.unfavorable_zones[:3]:
            report.append(f"  • {zone.value}: -{disadvantage:.1%} disadvantage")
    
    # Play style matchup
    report.append("")
    vulnerable = team_defense.is_vulnerable_to(player_profile.primary_play_style)
    report.append(f"Defense Vulnerable to {player_profile.primary_play_style.value}: {'YES' if vulnerable else 'NO'}")
    
    # Defender info
    if defender:
        report.append("")
        report.append("-" * 80)
        report.append(f"PRIMARY DEFENDER: {defender.player_name}")
        report.append("-" * 80)
        report.append(f"Defensive Rating: {defender.defensive_rating}")
        report.append(f"Opponent FG% Allowed: {defender.opponent_fg_pct_allowed:.1%}")
        report.append(f"Paint FG% Allowed: {defender.paint_fg_pct_allowed:.1%}")
        report.append(f"3PT FG% Allowed: {defender.three_pt_fg_pct_allowed:.1%}")
        report.append(f"Contests per Game: {defender.contests_per_game:.1f}")
    
    # Similar players
    if similar:
        report.append("")
        report.append("-" * 80)
        report.append("SIMILAR PLAYERS")
        report.append("-" * 80)
        for player, similarity in similar:
            report.append(f"• {player.player_name} ({similarity:.1%} similar)")
            report.append(f"  Play Style: {player.primary_play_style.value}")
            report.append(f"  True Shooting: {player.true_shooting_pct:.1%}")
        
        # Historical performance
        hist = analyzer.get_historical_performance(similar, team_defense)
        report.append("")
        report.append(f"Similar Players' Avg Performance vs {team_defense.team}:")
        report.append(f"  Effective FG%: {hist.get('historical_fg_pct', 0):.1%}")
    
    # Projected hit rates
    report.append("")
    report.append("-" * 80)
    report.append("PROJECTED HIT RATES BY ZONE")
    report.append("-" * 80)
    for zone in player_profile.shot_chart.shot_zones:
        player_pct = zone.fg_percentage
        projected_pct = matchup.hit_rate_projection.get(zone.zone, player_pct)
        change = projected_pct - player_pct
        report.append(f"{zone.zone.value}: {player_pct:.1%} → {projected_pct:.1%} ({change:+.1%})")
    
    # Recommendation
    report.append("")
    report.append("=" * 80)
    
    # Calculate recommendation
    adjusted_avg = prop.player_season_avg * (1 + matchup.expected_fg_boost)
    if adjusted_avg > prop.prop_line.line_value * 1.03:
        rec = "OVER ✓"
    elif adjusted_avg < prop.prop_line.line_value * 0.97:
        rec = "UNDER ✓"
    else:
        rec = "PASS"
    
    report.append(f"RECOMMENDATION: {rec}")
    report.append(f"Adjusted Projection: {adjusted_avg:.1f}")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Demonstrate integration of shot chart defense with prop betting"""
    print("=" * 80)
    print("ENHANCED PROP ANALYSIS WITH DEFENSIVE MATCHUPS")
    print("=" * 80)
    print()
    
    # Import sample data
    from nba_prop_data import generate_sample_props
    from shot_chart_defense import (
        generate_sample_shot_charts,
        generate_sample_defenders,
        generate_sample_team_defenses
    )
    
    # Load data
    props = generate_sample_props()
    shot_charts = generate_sample_shot_charts()
    defenders = generate_sample_defenders()
    team_defenses = generate_sample_team_defenses()
    
    # Create player profiles
    from shot_chart_defense import PlayerProfile, PlayStyle, ShotZone
    
    lebron_profile = PlayerProfile(
        "2544", "LeBron James", "Los Angeles Lakers", "SF",
        primary_play_style=PlayStyle.VOLUME_SCORER,
        secondary_play_style=PlayStyle.PLAYMAKER,
        shot_chart=shot_charts[0],
        usage_rate=0.312, true_shooting_pct=0.605, effective_fg_pct=0.564,
        preferred_zones=[ShotZone.PAINT, ShotZone.THREE_POINT_TOP],
        avoids_zones=[ShotZone.MID_RANGE]
    )
    
    curry_profile = PlayerProfile(
        "201939", "Stephen Curry", "Golden State Warriors", "PG",
        primary_play_style=PlayStyle.THREE_POINT_SPECIALIST,
        secondary_play_style=PlayStyle.VOLUME_SCORER,
        shot_chart=shot_charts[1],
        usage_rate=0.298, true_shooting_pct=0.670, effective_fg_pct=0.620,
        preferred_zones=[ShotZone.THREE_POINT_TOP, ShotZone.THREE_POINT_WING],
        avoids_zones=[ShotZone.MID_RANGE]
    )
    
    tatum_profile = PlayerProfile(
        "1628369", "Jayson Tatum", "Boston Celtics", "SF",
        primary_play_style=PlayStyle.VOLUME_SCORER,
        secondary_play_style=PlayStyle.EFFICIENT_SCORER,
        shot_chart=shot_charts[2],
        usage_rate=0.325, true_shooting_pct=0.598, effective_fg_pct=0.554,
        preferred_zones=[ShotZone.PAINT, ShotZone.THREE_POINT_WING],
        avoids_zones=[ShotZone.FREE_THROW_LINE]
    )
    
    player_profiles = {
        "2544": lebron_profile,
        "201939": curry_profile,
        "1628369": tatum_profile
    }
    
    all_profiles = [lebron_profile, curry_profile, tatum_profile]
    
    # Initialize enhanced analyzer
    matchup_analyzer = DefensiveMatchupAnalyzer()
    enhanced_analyzer = EnhancedPropAnalyzer(matchup_analyzer)
    
    # Analyze LeBron's points prop vs Warriors
    lebron_prop = props[0]  # LeBron points
    warriors_defense = team_defenses[2]
    
    print("ENHANCED PROP ANALYSIS")
    print("-" * 80)
    analysis = enhanced_analyzer.analyze_prop_with_matchup(
        lebron_prop,
        lebron_profile,
        warriors_defense
    )
    
    for key, value in analysis.items():
        if isinstance(value, float):
            if "prob" in key or "edge" in key or "boost" in key:
                print(f"{key}: {value:+.2%}")
            else:
                print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Compare with similar players
    print("\n" + "=" * 80)
    print("SIMILAR PLAYER COMPARISON")
    print("-" * 80)
    
    comparison = enhanced_analyzer.compare_with_similar_players(
        lebron_profile, all_profiles, warriors_defense
    )
    
    if comparison["has_similar_players"]:
        print(f"\nFound {comparison['num_similar_players']} similar players:")
        for sim_player in comparison["similar_players"]:
            print(f"  • {sim_player['name']} ({sim_player['similarity']} similarity)")
            print(f"    Play Style: {sim_player['play_style']}")
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE MATCHUP REPORT")
    print("=" * 80)
    print()
    
    report = create_defensive_matchup_report(
        lebron_prop,
        lebron_profile,
        warriors_defense,
        all_profiles,
        None
    )
    
    print(report)
    
    print("\n✅ Enhanced prop analysis with defensive matchups complete!")


if __name__ == "__main__":
    main()
