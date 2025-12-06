#!/usr/bin/env python3
"""
Example: Advanced Monte Carlo Simulation (Haralabos Voulgaris Style)

Demonstrates the enhanced simulation features:
- 100,000+ simulations for precision
- Overtime/shootout probabilities
- Score margin distributions
- Betting edge analysis
- Batch processing multiple games
"""

from nhl_analytics import NHLAnalytics

def main():
    # Initialize with all enhancements
    analytics = NHLAnalytics(use_moneypuck=True, use_recent_form=True)
    
    print("=" * 80)
    print("ADVANCED MONTE CARLO SIMULATION - HARALABOS VOULGARIS STYLE")
    print("=" * 80)
    print()
    
    # Example 1: Single game with 100,000 simulations and betting edge analysis
    print("Example 1: Buffalo @ Winnipeg Jets (100,000 simulations)")
    print("-" * 80)
    
    result = analytics.simulate_score_advanced(
        home_team="WPG",
        away_team="BUF",
        num_simulations=100000,
        market_spread=-1.5,  # WPG -1.5
        market_total=6.0
    )
    
    print(f"Matchup: {result['matchup']}")
    print(f"Predicted Final Score: {result['predicted_final_score']}")
    print(f"Probability: {result['most_likely_score']['probability']}")
    print()
    
    print("Win Probabilities (including OT/SO):")
    for key, value in result['win_probabilities']['including_ot_so'].items():
        print(f"  {key}: {value}")
    print()
    
    print("Overtime/Shootout Probabilities:")
    for key, value in result['win_probabilities']['overtime_shootout'].items():
        print(f"  {key}: {value}")
    print()
    
    print("Score Margin Distribution (Top 10):")
    for margin, prob in list(result['score_margin_distribution'].items())[:10]:
        print(f"  {margin}: {prob}")
    print()
    
    if 'betting_edge_analysis' in result:
        print("Betting Edge Analysis:")
        if 'spread' in result['betting_edge_analysis']:
            spread_edge = result['betting_edge_analysis']['spread']
            print(f"  Spread ({spread_edge['market_line']})")
            print(f"    Cover Probability: {spread_edge['cover_probability']}")
            print(f"    Edge: {spread_edge['edge']}")
            print(f"    Recommendation: {spread_edge['recommendation']} ({spread_edge['confidence']} confidence)")
        
        if 'total' in result['betting_edge_analysis']:
            total_edge = result['betting_edge_analysis']['total']
            print(f"  Total ({total_edge['market_line']})")
            print(f"    Over Probability: {total_edge['over_probability']}")
            print(f"    Edge: {total_edge['edge']}")
            print(f"    Recommendation: {total_edge['recommendation']} ({total_edge['confidence']} confidence)")
    print()
    
    print("Top 10 Most Likely Scores:")
    for i, score in enumerate(result['top_10_likely_scores'], 1):
        print(f"  {i}. {score['score']:25} - {score['probability']}")
    print()
    
    print("Simulation Statistics:")
    stats = result['simulation_stats']
    print(f"  Simulations Run: {stats['simulations_run']:,}")
    print(f"  Average Score: {stats['average_home_score']} - {stats['average_away_score']}")
    print(f"  Median Score: {stats['median_home_score']} - {stats['median_away_score']}")
    print(f"  Std Dev: ±{stats['std_dev_home']}, ±{stats['std_dev_away']}")
    print()
    
    # Example 2: Batch analysis of multiple games
    print("=" * 80)
    print("Example 2: Batch Analysis - Multiple Games (50,000 simulations each)")
    print("-" * 80)
    print()
    
    games_to_analyze = [
        ("LAK", "CHI"),  # LA Kings vs Chicago
        ("COL", "NYI"),  # Colorado vs NY Islanders
        ("TOR", "MTL"),  # Toronto vs Montreal
    ]
    
    batch_results = analytics.batch_analyze_games(
        games=games_to_analyze,
        num_simulations=50000,
        include_score_sim=True
    )
    
    print(f"Analyzed {batch_results['summary']['total_games_analyzed']} games")
    print(f"Total simulations: {batch_results['summary']['total_simulations_run']:,}")
    print()
    
    for game in batch_results['games']:
        print(f"Game {game['game_number']}: {game['matchup']}")
        spread = game['spread_analysis']
        print(f"  Predicted Spread: {spread['predicted_spread']}")
        
        if 'score_simulation' in game:
            sim = game['score_simulation']
            print(f"  Most Likely Score: {sim['predicted_final_score']}")
            print(f"  Probability: {sim['most_likely_score']['probability']}")
            
            # Win probabilities
            win_probs = sim['win_probabilities']['including_ot_so']
            home_team = game['matchup'].split('@')[1].strip()
            away_team = game['matchup'].split('@')[0].strip()
            print(f"  Win Probability: {win_probs[f'{home_team}_win']} (home) vs {win_probs[f'{away_team}_win']} (away)")
        print()
    
    print("=" * 80)
    print("Analysis complete! All simulations use Poisson distribution.")
    print("Advanced features: OT/SO probabilities, margin distributions, edge analysis")
    print("=" * 80)

if __name__ == "__main__":
    main()
