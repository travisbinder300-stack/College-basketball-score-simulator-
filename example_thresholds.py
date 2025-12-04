#!/usr/bin/env python3
"""
Example demonstrating different confidence thresholds for NBA analysis
"""

from nba_analysis import NBAAnalyzer, create_sample_teams, create_sample_games


def main():
    """Demonstrate analysis with different confidence thresholds"""
    print("=" * 80)
    print("NBA ANALYSIS - CONFIDENCE THRESHOLD COMPARISON")
    print("=" * 80)
    print()
    
    # Create sample data
    teams = create_sample_teams()
    games = create_sample_games(teams)
    
    # Test different confidence thresholds
    thresholds = [60.0, 70.0, 80.0, 90.0]
    
    for threshold in thresholds:
        analyzer = NBAAnalyzer(min_confidence=threshold)
        predictions = analyzer.analyze_games(games)
        
        print(f"\n{'='*80}")
        print(f"Confidence Threshold: {threshold:.0f}%")
        print(f"{'='*80}")
        print(f"Predictions found: {len(predictions)} out of {len(games)} games analyzed")
        
        if predictions:
            avg_spread_conf = sum(p.spread_confidence for p in predictions) / len(predictions)
            avg_total_conf = sum(p.total_confidence for p in predictions) / len(predictions)
            
            print(f"Average spread confidence: {avg_spread_conf:.1f}%")
            print(f"Average total confidence: {avg_total_conf:.1f}%")
            
            # Show first prediction as example
            print(f"\nExample prediction:")
            print(f"  {predictions[0].game.away_team.name} @ {predictions[0].game.home_team.name}")
            print(f"  Spread: {predictions[0].game.home_team.name} {predictions[0].spread:+.1f} ({predictions[0].spread_confidence:.1f}%)")
            print(f"  Total: {predictions[0].total:.1f} pts ({predictions[0].total_confidence:.1f}%)")
        else:
            print("No predictions meet this confidence threshold.")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Insights:")
    print("- Higher confidence thresholds result in fewer predictions")
    print("- 70% threshold provides a good balance of confidence and coverage")
    print("- Strong mismatches produce higher confidence predictions")
    print("- Similar teams or close matchups may not meet high thresholds")


if __name__ == "__main__":
    main()
