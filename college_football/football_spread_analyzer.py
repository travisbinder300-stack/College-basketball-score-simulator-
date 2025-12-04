#!/usr/bin/env python3
"""
Spread Analyzer for College Football Score Simulator
Analyzes which team can cover a point spread based on simulation results.
"""

import sys
from typing import Dict, List, Tuple
try:
    from football_simulator import FootballTeam, FootballSimulator
except ImportError:
    from .football_simulator import FootballTeam, FootballSimulator


class FootballSpreadAnalyzer:
    """Analyzes teams and spreads using multiple game simulations."""
    
    def __init__(self, team1_config: Dict, team2_config: Dict, num_simulations: int = 1000):
        """
        Initialize spread analyzer.
        
        Args:
            team1_config: Configuration for team 1 (name and stats)
            team2_config: Configuration for team 2 (name and stats)
            num_simulations: Number of games to simulate (default 1000)
        """
        self.team1_config = team1_config
        self.team2_config = team2_config
        self.num_simulations = num_simulations
        self.results = []
    
    def run_simulations(self) -> List[Dict]:
        """Run multiple game simulations and collect results."""
        print(f"\nRunning {self.num_simulations} simulations...")
        print(f"{self.team1_config['name']} vs {self.team2_config['name']}\n")
        
        self.results = []
        
        for i in range(self.num_simulations):
            # Create fresh team instances for each simulation
            team1 = FootballTeam(**self.team1_config)
            team2 = FootballTeam(**self.team2_config)
            
            # Run simulation
            simulator = FootballSimulator(team1, team2, verbose=False)
            winner, summary = simulator.simulate_game()
            
            # Calculate point differential (team1 score - team2 score)
            point_diff = team1.score - team2.score
            
            self.results.append({
                'game_num': i + 1,
                'team1_score': team1.score,
                'team2_score': team2.score,
                'point_diff': point_diff,
                'winner': winner.name,
                'total_points': team1.score + team2.score
            })
            
            # Show progress every 100 games
            if (i + 1) % 100 == 0:
                print(f"  Completed {i + 1}/{self.num_simulations} simulations...")
        
        print(f"\nSimulations complete!\n")
        return self.results
    
    def analyze_spread(self, spread: float) -> Dict:
        """
        Analyze if a team can cover the spread.
        
        Args:
            spread: Point spread (positive means team1 is favored, negative means team2 is favored)
                   Example: spread = 7.0 means team1 is favored by 7 points
        
        Returns:
            Dictionary with spread coverage analysis
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        # Count how many times each team covers the spread
        team1_covers = 0
        team2_covers = 0
        pushes = 0
        
        for result in self.results:
            point_diff = result['point_diff']
            
            if point_diff > spread:
                team1_covers += 1
            elif point_diff < spread:
                team2_covers += 1
            else:
                pushes += 1
        
        team1_cover_pct = (team1_covers / self.num_simulations) * 100
        team2_cover_pct = (team2_covers / self.num_simulations) * 100
        push_pct = (pushes / self.num_simulations) * 100
        
        # Determine which team covers more reliably
        if team1_cover_pct > team2_cover_pct:
            best_bet = self.team1_config['name']
            cover_rate = team1_cover_pct
        elif team2_cover_pct > team1_cover_pct:
            best_bet = self.team2_config['name']
            cover_rate = team2_cover_pct
        else:
            best_bet = "Even"
            cover_rate = team1_cover_pct
        
        return {
            'spread': spread,
            'team1_covers': team1_covers,
            'team1_cover_pct': team1_cover_pct,
            'team2_covers': team2_covers,
            'team2_cover_pct': team2_cover_pct,
            'pushes': pushes,
            'push_pct': push_pct,
            'best_bet': best_bet,
            'cover_rate': cover_rate,
            'confidence': 'HIGH' if cover_rate >= 70 else 'MEDIUM' if cover_rate >= 60 else 'LOW'
        }
    
    def analyze_total(self, total: float) -> Dict:
        """
        Analyze over/under total.
        
        Args:
            total: Total points line
        
        Returns:
            Dictionary with over/under analysis
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        overs = 0
        unders = 0
        pushes = 0
        
        for result in self.results:
            game_total = result['total_points']
            
            if game_total > total:
                overs += 1
            elif game_total < total:
                unders += 1
            else:
                pushes += 1
        
        over_pct = (overs / self.num_simulations) * 100
        under_pct = (unders / self.num_simulations) * 100
        push_pct = (pushes / self.num_simulations) * 100
        
        avg_total = sum(r['total_points'] for r in self.results) / len(self.results)
        
        return {
            'total': total,
            'overs': overs,
            'over_pct': over_pct,
            'unders': unders,
            'under_pct': under_pct,
            'pushes': pushes,
            'push_pct': push_pct,
            'avg_total': avg_total,
            'best_bet': 'Over' if over_pct > under_pct else 'Under',
            'cover_rate': max(over_pct, under_pct),
            'confidence': 'HIGH' if max(over_pct, under_pct) >= 70 else 'MEDIUM' if max(over_pct, under_pct) >= 60 else 'LOW'
        }
    
    def find_optimal_spread(self) -> float:
        """Find the spread where the line is most even (closest to 50/50)."""
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        # Calculate average point differential
        total_diff = sum(r['point_diff'] for r in self.results)
        avg_diff = total_diff / self.num_simulations
        
        return avg_diff
    
    def find_overvalued_spreads(self, min_points: float = 7.0, max_points: float = 35.0) -> List[Dict]:
        """
        Find spreads where the underdog is getting too many points (overvalued).
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        optimal = self.find_optimal_spread()
        overvalued = []
        
        for spread in range(int(min_points), int(max_points) + 1):
            spread_float = float(spread)
            
            if abs(spread_float - abs(optimal)) < 3:
                continue
            
            if spread_float > abs(optimal):
                analysis = self.analyze_spread(spread_float)
                
                if analysis['team2_cover_pct'] >= 65:
                    value = spread_float - abs(optimal)
                    overvalued.append({
                        'spread': spread_float,
                        'underdog': self.team2_config['name'],
                        'favorite': self.team1_config['name'],
                        'underdog_covers_pct': analysis['team2_cover_pct'],
                        'extra_points': value,
                        'optimal_spread': abs(optimal),
                        'confidence': analysis['confidence'] if analysis['team2_cover_pct'] >= 70 else 'MEDIUM',
                        'value_rating': 'EXCELLENT' if value >= 7 else 'GOOD' if value >= 4 else 'FAIR'
                    })
            
            negative_spread = -spread_float
            if abs(negative_spread) > abs(optimal):
                analysis = self.analyze_spread(negative_spread)
                
                if analysis['team1_cover_pct'] >= 65:
                    value = abs(negative_spread) - abs(optimal)
                    overvalued.append({
                        'spread': negative_spread,
                        'underdog': self.team1_config['name'],
                        'favorite': self.team2_config['name'],
                        'underdog_covers_pct': analysis['team1_cover_pct'],
                        'extra_points': value,
                        'optimal_spread': abs(optimal),
                        'confidence': analysis['confidence'] if analysis['team1_cover_pct'] >= 70 else 'MEDIUM',
                        'value_rating': 'EXCELLENT' if value >= 7 else 'GOOD' if value >= 4 else 'FAIR'
                    })
        
        overvalued.sort(key=lambda x: x['underdog_covers_pct'], reverse=True)
        
        return overvalued
    
    def find_undervalued_spreads(self, min_points: float = 7.0, max_points: float = 35.0) -> List[Dict]:
        """
        Find spreads where the favorite is giving too many points (trap bets).
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        optimal = self.find_optimal_spread()
        undervalued = []
        
        for spread in range(int(min_points), int(max_points) + 1):
            spread_float = float(spread)
            
            if abs(spread_float - abs(optimal)) < 3:
                continue
            
            if spread_float < abs(optimal):
                analysis = self.analyze_spread(spread_float)
                
                if analysis['team1_cover_pct'] <= 40:
                    shortage = abs(optimal) - spread_float
                    undervalued.append({
                        'spread': spread_float,
                        'favorite': self.team1_config['name'],
                        'underdog': self.team2_config['name'],
                        'favorite_covers_pct': analysis['team1_cover_pct'],
                        'points_short': shortage,
                        'optimal_spread': abs(optimal),
                        'risk_rating': 'HIGH_RISK' if shortage >= 7 else 'MODERATE_RISK' if shortage >= 4 else 'LOW_RISK',
                        'advice': f'AVOID betting {self.team1_config["name"]} at -{spread_float}'
                    })
        
        undervalued.sort(key=lambda x: x['favorite_covers_pct'])
        
        return undervalued
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics from all simulations."""
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        team1_scores = [r['team1_score'] for r in self.results]
        team2_scores = [r['team2_score'] for r in self.results]
        point_diffs = [r['point_diff'] for r in self.results]
        totals = [r['total_points'] for r in self.results]
        
        team1_wins = sum(1 for r in self.results if r['winner'] == self.team1_config['name'])
        team2_wins = self.num_simulations - team1_wins
        
        return {
            'team1_avg_score': sum(team1_scores) / len(team1_scores),
            'team2_avg_score': sum(team2_scores) / len(team2_scores),
            'team1_min_score': min(team1_scores),
            'team1_max_score': max(team1_scores),
            'team2_min_score': min(team2_scores),
            'team2_max_score': max(team2_scores),
            'avg_point_diff': sum(point_diffs) / len(point_diffs),
            'avg_total': sum(totals) / len(totals),
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'team1_win_pct': (team1_wins / self.num_simulations) * 100,
            'team2_win_pct': (team2_wins / self.num_simulations) * 100
        }
    
    def print_report(self, spread: float = None, total: float = None):
        """Print a comprehensive report of the spread analysis."""
        if not self.results:
            print("No simulation results available. Run run_simulations() first.")
            return
        
        stats = self.get_statistics()
        optimal_spread = self.find_optimal_spread()
        
        print("="*70)
        print(" "*15 + "COLLEGE FOOTBALL SPREAD ANALYSIS REPORT")
        print("="*70)
        
        print(f"\nMatchup: {self.team1_config['name']} vs {self.team2_config['name']}")
        print(f"Simulations: {self.num_simulations}")
        
        print("\n" + "-"*70)
        print("OVERALL STATISTICS")
        print("-"*70)
        
        print(f"\n{self.team1_config['name']}:")
        print(f"  Wins: {stats['team1_wins']} ({stats['team1_win_pct']:.1f}%)")
        print(f"  Avg Score: {stats['team1_avg_score']:.1f}")
        print(f"  Score Range: {stats['team1_min_score']} - {stats['team1_max_score']}")
        
        print(f"\n{self.team2_config['name']}:")
        print(f"  Wins: {stats['team2_wins']} ({stats['team2_win_pct']:.1f}%)")
        print(f"  Avg Score: {stats['team2_avg_score']:.1f}")
        print(f"  Score Range: {stats['team2_min_score']} - {stats['team2_max_score']}")
        
        print(f"\nAverage Point Differential: {stats['avg_point_diff']:.1f}")
        print(f"Average Total Points: {stats['avg_total']:.1f}")
        print(f"Optimal Spread (50/50 line): {optimal_spread:.1f}")
        
        if spread is not None:
            print("\n" + "-"*70)
            print(f"SPREAD ANALYSIS: {abs(spread):.1f} points")
            if spread > 0:
                print(f"({self.team1_config['name']} favored by {spread:.1f})")
            else:
                print(f"({self.team2_config['name']} favored by {abs(spread):.1f})")
            print("-"*70)
            
            analysis = self.analyze_spread(spread)
            
            print(f"\n{self.team1_config['name']} covers: {analysis['team1_covers']} times ({analysis['team1_cover_pct']:.1f}%)")
            print(f"{self.team2_config['name']} covers: {analysis['team2_covers']} times ({analysis['team2_cover_pct']:.1f}%)")
            print(f"Pushes (exact tie): {analysis['pushes']} times ({analysis['push_pct']:.1f}%)")
            
            print(f"\n{'='*70}")
            print(f"RECOMMENDATION: Bet on {analysis['best_bet']}")
            print(f"Cover Rate: {analysis['cover_rate']:.1f}%")
            print(f"Confidence Level: {analysis['confidence']}")
            print(f"{'='*70}")
            
            if analysis['cover_rate'] >= 70:
                print(f"\n✓ HIGH CONFIDENCE BET - {analysis['best_bet']} covers {analysis['cover_rate']:.1f}% of the time")
            elif analysis['cover_rate'] >= 60:
                print(f"\n⚠ MEDIUM CONFIDENCE - {analysis['best_bet']} has edge at {analysis['cover_rate']:.1f}%")
            else:
                print(f"\n✗ LOW CONFIDENCE - Too close to call ({analysis['cover_rate']:.1f}%)")
        
        if total is not None:
            print("\n" + "-"*70)
            print(f"TOTAL ANALYSIS: {total:.1f} points")
            print("-"*70)
            
            total_analysis = self.analyze_total(total)
            
            print(f"\nOver {total}: {total_analysis['overs']} times ({total_analysis['over_pct']:.1f}%)")
            print(f"Under {total}: {total_analysis['unders']} times ({total_analysis['under_pct']:.1f}%)")
            print(f"Average Total: {total_analysis['avg_total']:.1f}")
            
            print(f"\n{'='*70}")
            print(f"RECOMMENDATION: {total_analysis['best_bet']} {total}")
            print(f"Confidence Level: {total_analysis['confidence']}")
            print(f"{'='*70}")


def main():
    """Main function for command-line spread analysis."""
    print("\n" + "="*70)
    print(" "*15 + "COLLEGE FOOTBALL SPREAD ANALYZER")
    print("="*70)
    
    # Example: Alabama vs Auburn
    team1_config = {
        'name': 'Alabama Crimson Tide',
        'pass_completion_pct': 0.65,
        'yards_per_completion': 13.5,
        'rush_yards_per_carry': 5.2,
        'turnover_rate': 0.02,
        'red_zone_td_pct': 0.70,
        'field_goal_pct': 0.82,
        'home_field': True
    }
    
    team2_config = {
        'name': 'Auburn Tigers',
        'pass_completion_pct': 0.58,
        'yards_per_completion': 11.5,
        'rush_yards_per_carry': 4.5,
        'turnover_rate': 0.03,
        'red_zone_td_pct': 0.58,
        'field_goal_pct': 0.75
    }
    
    # Create analyzer and run simulations
    analyzer = FootballSpreadAnalyzer(team1_config, team2_config, num_simulations=1000)
    analyzer.run_simulations()
    
    # Test different spreads
    spreads_to_test = [7.0, 10.0, 14.0]
    
    for spread in spreads_to_test:
        print("\n" + "="*70)
        analyzer.print_report(spread=spread, total=52.5)


if __name__ == "__main__":
    main()
