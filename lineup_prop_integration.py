"""
Integration: Lineup Impact with Prop Betting Analysis
Enhances prop analysis with lineup-dependent statistics
"""

from typing import List, Dict, Optional
from nba_prop_data import PlayerProp, PropType
from lineup_impact import (
    LineupImpactAnalyzer, LineupConfiguration, LineupImpactStats,
    KeyPlayerImpact, generate_sample_lineup_data
)


class LineupAwarePropAnalyzer:
    """
    Enhanced prop analyzer that considers lineup configurations
    """
    
    def __init__(self, lineup_analyzer: LineupImpactAnalyzer):
        self.lineup_analyzer = lineup_analyzer
    
    def analyze_prop_with_lineup(
        self,
        prop: PlayerProp,
        lineup_config: LineupConfiguration,
        key_players_status: Optional[Dict[str, bool]] = None
    ) -> Dict:
        """
        Analyze prop bet with lineup context
        
        Args:
            prop: The prop bet to analyze
            lineup_config: Current lineup configuration
            key_players_status: Dict of key_player_id -> is_playing
        
        Returns:
            Enhanced analysis with lineup adjustments
        """
        # Get base prop info
        base_value = prop.player_season_avg or prop.prop_line.line_value
        line = prop.prop_line.line_value
        
        # Map prop type to stat type
        stat_type_map = {
            PropType.POINTS: 'points',
            PropType.REBOUNDS: 'rebounds',
            PropType.ASSISTS: 'assists',
            PropType.THREE_POINTERS: 'points',  # Approximate
            PropType.PRA: 'points'  # Use points as proxy
        }
        
        stat_type = stat_type_map.get(prop.prop_type, 'points')
        
        # Get lineup adjustment
        adjustment = self.lineup_analyzer.calculate_prop_adjustment(
            prop.player.player_id,
            lineup_config,
            stat_type,
            line
        )
        
        # Calculate edge with lineup data
        if adjustment.get('hit_rate'):
            hit_prob = adjustment['hit_rate']
        else:
            # Fallback to projection-based probability
            adjusted_value = adjustment['adjusted_value']
            if adjusted_value > line:
                hit_prob = 0.55 + (adjusted_value - line) / line * 0.2
            else:
                hit_prob = 0.45 - (line - adjusted_value) / line * 0.2
            hit_prob = max(0.2, min(0.8, hit_prob))
        
        # Market probability
        market_prob = prop.prop_line.get_implied_probability(True)
        
        # Calculate edge
        edge = hit_prob - market_prob
        
        # Determine recommendation
        if edge > 0.05 and adjustment['confidence'] > 0.5:
            recommendation = "STRONG OVER"
        elif edge > 0.02:
            recommendation = "OVER"
        elif edge < -0.05 and adjustment['confidence'] > 0.5:
            recommendation = "STRONG UNDER"
        elif edge < -0.02:
            recommendation = "UNDER"
        else:
            recommendation = "PASS"
        
        return {
            "prop": str(prop),
            "line": line,
            "base_value": base_value,
            "adjusted_value": adjustment['adjusted_value'],
            "adjustment_factor": adjustment['adjustment_factor'],
            "hit_probability": hit_prob,
            "market_probability": market_prob,
            "edge": edge,
            "recommendation": recommendation,
            "confidence": adjustment['confidence'],
            "lineup_context": {
                "minutes_per_game": adjustment.get('minutes_per_game', 0),
                "usage_rate": adjustment.get('usage_rate', 0),
                "pace": adjustment.get('pace', 0),
                "games_played": adjustment.get('games_played', 0)
            }
        }
    
    def compare_lineup_scenarios(
        self,
        prop: PlayerProp,
        lineup_with_key_player: LineupConfiguration,
        lineup_without_key_player: LineupConfiguration,
        key_player_name: str
    ) -> Dict:
        """
        Compare prop in two lineup scenarios (with/without key player)
        """
        # Analyze with key player
        analysis_with = self.analyze_prop_with_lineup(prop, lineup_with_key_player)
        
        # Analyze without key player
        analysis_without = self.analyze_prop_with_lineup(prop, lineup_without_key_player)
        
        # Calculate differences
        value_diff = analysis_without['adjusted_value'] - analysis_with['adjusted_value']
        hit_prob_diff = analysis_without['hit_probability'] - analysis_with['hit_probability']
        edge_diff = analysis_without['edge'] - analysis_with['edge']
        
        return {
            "prop": str(prop),
            "key_player": key_player_name,
            "with_key_player": {
                "adjusted_value": analysis_with['adjusted_value'],
                "hit_probability": analysis_with['hit_probability'],
                "edge": analysis_with['edge'],
                "recommendation": analysis_with['recommendation'],
                "usage_rate": analysis_with['lineup_context']['usage_rate'],
                "pace": analysis_with['lineup_context']['pace']
            },
            "without_key_player": {
                "adjusted_value": analysis_without['adjusted_value'],
                "hit_probability": analysis_without['hit_probability'],
                "edge": analysis_without['edge'],
                "recommendation": analysis_without['recommendation'],
                "usage_rate": analysis_without['lineup_context']['usage_rate'],
                "pace": analysis_without['lineup_context']['pace']
            },
            "differentials": {
                "value_diff": value_diff,
                "hit_prob_diff": hit_prob_diff,
                "edge_diff": edge_diff,
                "usage_diff": analysis_without['lineup_context']['usage_rate'] - analysis_with['lineup_context']['usage_rate'],
                "pace_diff": analysis_without['lineup_context']['pace'] - analysis_with['lineup_context']['pace']
            },
            "recommendation": self._get_scenario_recommendation(
                analysis_with, analysis_without, value_diff, edge_diff
            )
        }
    
    def _get_scenario_recommendation(
        self,
        with_analysis: Dict,
        without_analysis: Dict,
        value_diff: float,
        edge_diff: float
    ) -> str:
        """Generate recommendation based on lineup scenario comparison"""
        if abs(value_diff) < 1.0:
            return "Lineup has minimal impact on this prop"
        
        if value_diff > 2.0 and edge_diff > 0.05:
            return "Strong OVER opportunity when key player is OUT"
        elif value_diff > 1.0 and edge_diff > 0.02:
            return "Consider OVER when key player is OUT"
        elif value_diff < -2.0 and edge_diff < -0.05:
            return "Strong UNDER opportunity when key player is OUT"
        elif value_diff < -1.0 and edge_diff < -0.02:
            return "Consider UNDER when key player is OUT"
        else:
            return "Lineup impact exists but edge is marginal"
    
    def generate_lineup_report(
        self,
        prop: PlayerProp,
        lineup_config: LineupConfiguration,
        key_player_impacts: Optional[List[KeyPlayerImpact]] = None
    ) -> str:
        """
        Generate comprehensive lineup impact report for a prop
        """
        analysis = self.analyze_prop_with_lineup(prop, lineup_config)
        
        report = []
        report.append("=" * 80)
        report.append(f"LINEUP-AWARE PROP ANALYSIS: {prop.player.name}")
        report.append("=" * 80)
        report.append("")
        
        # Prop details
        report.append(f"Prop: {prop}")
        report.append(f"Line: {analysis['line']}")
        report.append("")
        
        # Lineup context
        report.append("-" * 80)
        report.append("LINEUP CONTEXT")
        report.append("-" * 80)
        lineup_ctx = analysis['lineup_context']
        report.append(f"Minutes per Game: {lineup_ctx['minutes_per_game']:.1f}")
        report.append(f"Usage Rate: {lineup_ctx['usage_rate']:.1%}")
        report.append(f"Pace: {lineup_ctx['pace']:.1f}")
        report.append(f"Games Played: {lineup_ctx['games_played']}")
        report.append("")
        
        # Analysis
        report.append("-" * 80)
        report.append("PROP ANALYSIS")
        report.append("-" * 80)
        report.append(f"Base Value: {analysis['base_value']:.1f}")
        report.append(f"Lineup-Adjusted Value: {analysis['adjusted_value']:.1f}")
        report.append(f"Adjustment Factor: {analysis['adjustment_factor']:.3f}")
        report.append("")
        report.append(f"Hit Probability: {analysis['hit_probability']:.1%}")
        report.append(f"Market Probability: {analysis['market_probability']:.1%}")
        report.append(f"Edge: {analysis['edge']:+.2%}")
        report.append("")
        report.append(f"Confidence: {analysis['confidence']:.1%}")
        report.append(f"Recommendation: {analysis['recommendation']}")
        
        # Key player impacts
        if key_player_impacts:
            report.append("")
            report.append("-" * 80)
            report.append("KEY PLAYER IMPACTS")
            report.append("-" * 80)
            for impact in key_player_impacts:
                if impact.affected_player_id == prop.player.player_id:
                    report.append(f"\nWith/Without {impact.key_player_name}:")
                    diff = impact.get_impact_differential()
                    if diff:
                        report.append(f"  Usage Diff: {diff.get('usage_diff', 0):+.1%}")
                        report.append(f"  Pace Diff: {diff.get('pace_diff', 0):+.1f}")
                        report.append(f"  Points Diff: {diff.get('points_diff', 0):+.1f}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Demonstrate lineup-aware prop analysis"""
    print("=" * 80)
    print("LINEUP-AWARE PROP ANALYSIS")
    print("=" * 80)
    print()
    
    # Import existing prop data
    from nba_prop_data import generate_sample_props, Player, Game, PropLine, PropType
    from datetime import datetime
    
    # Generate lineup data
    lineup_stats = generate_sample_lineup_data()
    
    # Initialize lineup analyzer
    lineup_analyzer = LineupImpactAnalyzer()
    for stats in lineup_stats:
        lineup_analyzer.add_lineup_stats(stats)
    
    # Initialize lineup-aware prop analyzer
    prop_analyzer = LineupAwarePropAnalyzer(lineup_analyzer)
    
    # Create sample props
    props = generate_sample_props()
    lebron_prop = props[0]  # LeBron points prop
    
    # Get lineup configurations
    lebron_with_reaves = lineup_stats[0].lineup_config
    lebron_without_reaves = lineup_stats[1].lineup_config
    
    # Analyze with Reaves in lineup
    print("SCENARIO 1: Austin Reaves PLAYING")
    print("-" * 80)
    analysis_with_reaves = prop_analyzer.analyze_prop_with_lineup(
        lebron_prop,
        lebron_with_reaves
    )
    
    for key, value in analysis_with_reaves.items():
        if key == 'lineup_context':
            print(f"\n{key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    print(f"    {k}: {v:.2f}")
                else:
                    print(f"    {k}: {v}")
        elif isinstance(value, float):
            if 'prob' in key or 'edge' in key or 'factor' in key or 'confidence' in key:
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    # Analyze without Reaves
    print("\n\n" + "=" * 80)
    print("SCENARIO 2: Austin Reaves OUT")
    print("-" * 80)
    analysis_without_reaves = prop_analyzer.analyze_prop_with_lineup(
        lebron_prop,
        lebron_without_reaves
    )
    
    for key, value in analysis_without_reaves.items():
        if key == 'lineup_context':
            print(f"\n{key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    print(f"    {k}: {v:.2f}")
                else:
                    print(f"    {k}: {v}")
        elif isinstance(value, float):
            if 'prob' in key or 'edge' in key or 'factor' in key or 'confidence' in key:
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    # Compare scenarios
    print("\n\n" + "=" * 80)
    print("LINEUP SCENARIO COMPARISON")
    print("=" * 80)
    
    comparison = prop_analyzer.compare_lineup_scenarios(
        lebron_prop,
        lebron_with_reaves,
        lebron_without_reaves,
        "Austin Reaves"
    )
    
    print(f"\nProp: {comparison['prop']}")
    print(f"Key Player: {comparison['key_player']}")
    print()
    
    print("WITH Austin Reaves:")
    for key, value in comparison['with_key_player'].items():
        if isinstance(value, float):
            if 'rate' in key or 'prob' in key or 'edge' in key:
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    print("\nWITHOUT Austin Reaves:")
    for key, value in comparison['without_key_player'].items():
        if isinstance(value, float):
            if 'rate' in key or 'prob' in key or 'edge' in key:
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    print("\nDIFFERENTIALS:")
    for key, value in comparison['differentials'].items():
        print(f"  {key}: {value:+.3f}")
    
    print(f"\nRECOMMENDATION: {comparison['recommendation']}")
    
    # Generate full report
    print("\n\n" + "=" * 80)
    print("COMPREHENSIVE LINEUP REPORT")
    print("=" * 80)
    print()
    
    report = prop_analyzer.generate_lineup_report(
        lebron_prop,
        lebron_without_reaves,
        None
    )
    
    print(report)
    
    print("\n✅ Lineup-aware prop analysis complete!")


if __name__ == "__main__":
    main()
