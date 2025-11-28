#!/usr/bin/env python3
"""
Football Picks Finder
Quickly finds high-confidence betting picks for college football games.
"""

from typing import Dict, List
try:
    from football_simulator import FootballTeam, FootballSimulator
    from football_spread_analyzer import FootballSpreadAnalyzer
except ImportError:
    from .football_simulator import FootballTeam, FootballSimulator
    from .football_spread_analyzer import FootballSpreadAnalyzer


def analyze_matchup(team1_config: Dict, team2_config: Dict, spread: float, 
                   total: float = None, num_sims: int = 1000) -> Dict:
    """
    Analyze a specific matchup and return pick recommendation.
    
    Args:
        team1_config: Team 1 configuration (the favorite if spread > 0)
        team2_config: Team 2 configuration
        spread: Point spread (positive = team1 favored)
        total: Over/under total (optional)
        num_sims: Number of simulations to run
    
    Returns:
        Dictionary with pick recommendation
    """
    analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=num_sims)
    analyzer.run_simulations()
    
    spread_analysis = analyzer.analyze_spread(spread)
    stats = analyzer.get_statistics()
    optimal = analyzer.find_optimal_spread()
    
    result = {
        'matchup': f"{team1_config['name']} vs {team2_config['name']}",
        'spread': spread,
        'optimal_spread': optimal,
        'team1_win_pct': stats['team1_win_pct'],
        'team2_win_pct': stats['team2_win_pct'],
        'avg_scores': f"{stats['team1_avg_score']:.1f} - {stats['team2_avg_score']:.1f}",
        'team1_covers_pct': spread_analysis['team1_cover_pct'],
        'team2_covers_pct': spread_analysis['team2_cover_pct'],
        'best_bet': spread_analysis['best_bet'],
        'coverage': spread_analysis['cover_rate'],
        'confidence': spread_analysis['confidence']
    }
    
    # Determine recommendation
    if spread_analysis['team1_cover_pct'] > spread_analysis['team2_cover_pct']:
        if spread > 0:
            result['recommendation'] = f"{team1_config['name']} -{abs(spread)}"
        else:
            result['recommendation'] = f"{team1_config['name']} +{abs(spread)}"
    else:
        if spread > 0:
            result['recommendation'] = f"{team2_config['name']} +{abs(spread)}"
        else:
            result['recommendation'] = f"{team2_config['name']} -{abs(spread)}"
    
    # Add total analysis if provided
    if total is not None:
        total_analysis = analyzer.analyze_total(total)
        result['total'] = total
        result['avg_total'] = stats['avg_total']
        result['over_pct'] = total_analysis['over_pct']
        result['under_pct'] = total_analysis['under_pct']
        result['total_recommendation'] = total_analysis['best_bet']
        result['total_confidence'] = total_analysis['confidence']
    
    return result


def find_value_picks(team1_config: Dict, team2_config: Dict, num_sims: int = 1000) -> List[Dict]:
    """
    Find all value picks (spreads where underdog is getting too many points).
    
    Returns list of valuable betting opportunities sorted by confidence.
    """
    analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=num_sims)
    analyzer.run_simulations()
    
    picks = []
    optimal = analyzer.find_optimal_spread()
    
    # Check various spreads
    for spread in range(3, 36):
        spread_float = float(spread)
        analysis = analyzer.analyze_spread(spread_float)
        
        # Check if team2 (underdog at positive spread) has value
        if analysis['team2_cover_pct'] >= 60:
            value = spread_float - abs(optimal) if spread_float > abs(optimal) else 0
            picks.append({
                'spread': f"+{spread_float}",
                'team': team2_config['name'],
                'covers_pct': analysis['team2_cover_pct'],
                'confidence': analysis['confidence'],
                'value_points': value,
                'type': 'underdog'
            })
        
        # Check if team1 (favorite at positive spread) has value
        if analysis['team1_cover_pct'] >= 60:
            value = abs(optimal) - spread_float if spread_float < abs(optimal) else 0
            picks.append({
                'spread': f"-{spread_float}",
                'team': team1_config['name'],
                'covers_pct': analysis['team1_cover_pct'],
                'confidence': analysis['confidence'],
                'value_points': value,
                'type': 'favorite'
            })
    
    # Sort by coverage percentage
    picks.sort(key=lambda x: x['covers_pct'], reverse=True)
    
    return picks


def print_quick_analysis(team1_config: Dict, team2_config: Dict, spread: float, 
                        total: float = None, num_sims: int = 500):
    """Print a quick analysis with pick recommendation."""
    print(f"\n{'='*60}")
    print(f"QUICK ANALYSIS: {team1_config['name']} vs {team2_config['name']}")
    print(f"{'='*60}")
    
    result = analyze_matchup(team1_config, team2_config, spread, total, num_sims)
    
    print(f"\nSpread: {team1_config['name']} {'-' if spread > 0 else '+'}{abs(spread)}")
    print(f"Win Probability: {result['team1_win_pct']:.1f}% - {result['team2_win_pct']:.1f}%")
    print(f"Average Scores: {result['avg_scores']}")
    print(f"Optimal Spread: {result['optimal_spread']:.1f}")
    
    print(f"\n{'='*60}")
    print(f"SPREAD PICK: {result['recommendation']}")
    print(f"Coverage: {result['coverage']:.1f}%")
    print(f"Confidence: {result['confidence']}")
    print(f"{'='*60}")
    
    if result['confidence'] == 'HIGH':
        print(f"✅ HIGH CONFIDENCE - Take {result['recommendation']}")
    elif result['confidence'] == 'MEDIUM':
        print(f"⚠️  MEDIUM CONFIDENCE - Consider {result['recommendation']}")
    else:
        print(f"❌ LOW CONFIDENCE - Avoid this spread")
    
    if total is not None:
        print(f"\n{'='*60}")
        print(f"TOTAL: {total}")
        print(f"Average Total: {result['avg_total']:.1f}")
        print(f"Over: {result['over_pct']:.1f}% | Under: {result['under_pct']:.1f}%")
        print(f"Pick: {result['total_recommendation']} {total}")
        print(f"Confidence: {result['total_confidence']}")
        print(f"{'='*60}")


def main():
    """Run example football picks analysis."""
    print("\n" + "="*70)
    print(" "*15 + "🏈 COLLEGE FOOTBALL PICKS FINDER 🏈")
    print("="*70)
    
    # Example matchups
    
    # Matchup 1: Top 10 vs Mid-tier team
    print("\n" + "="*70)
    print("MATCHUP 1: Power Program vs Mid-Tier")
    print("="*70)
    
    team1 = {
        'name': 'Ohio State',
        'pass_completion_pct': 0.66,
        'yards_per_completion': 14.0,
        'rush_yards_per_carry': 5.5,
        'turnover_rate': 0.02,
        'red_zone_td_pct': 0.72,
        'field_goal_pct': 0.85,
        'home_field': True
    }
    
    team2 = {
        'name': 'Purdue',
        'pass_completion_pct': 0.58,
        'yards_per_completion': 11.0,
        'rush_yards_per_carry': 3.8,
        'turnover_rate': 0.035,
        'red_zone_td_pct': 0.55,
        'field_goal_pct': 0.72
    }
    
    print_quick_analysis(team1, team2, spread=17.5, total=55.5, num_sims=500)
    
    # Matchup 2: Rivalry game
    print("\n" + "="*70)
    print("MATCHUP 2: Rivalry Game")
    print("="*70)
    
    team3 = {
        'name': 'Michigan',
        'pass_completion_pct': 0.62,
        'yards_per_completion': 12.5,
        'rush_yards_per_carry': 5.0,
        'turnover_rate': 0.025,
        'red_zone_td_pct': 0.65,
        'field_goal_pct': 0.78
    }
    
    team4 = {
        'name': 'Michigan State',
        'pass_completion_pct': 0.58,
        'yards_per_completion': 11.5,
        'rush_yards_per_carry': 4.2,
        'turnover_rate': 0.03,
        'red_zone_td_pct': 0.58,
        'field_goal_pct': 0.75,
        'home_field': True
    }
    
    print_quick_analysis(team3, team4, spread=7.0, total=48.5, num_sims=500)
    
    # Find all value picks for a matchup
    print("\n" + "="*70)
    print("VALUE PICKS: Finding spreads with edge")
    print("="*70)
    
    analyzer = FootballSpreadAnalyzer(team1, team2, num_simulations=500)
    analyzer.run_simulations()
    
    picks = find_value_picks(team1, team2, num_sims=500)
    
    print("\nTop Value Picks (60%+ coverage):")
    print("-" * 50)
    
    for i, pick in enumerate(picks[:10], 1):
        emoji = "✅" if pick['confidence'] == 'HIGH' else "⚠️" if pick['confidence'] == 'MEDIUM' else "❌"
        print(f"{i}. {emoji} {pick['team']} {pick['spread']}: {pick['covers_pct']:.1f}% ({pick['confidence']})")
    
    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)


if __name__ == "__main__":
    main()
