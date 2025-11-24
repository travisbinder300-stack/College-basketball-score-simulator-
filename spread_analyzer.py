#!/usr/bin/env python3
"""
Spread Analyzer for College Basketball Score Simulator
Analyzes which team can cover a point spread based on simulation results.
"""

import sys
from typing import Dict, List, Tuple
from basketball_simulator import Team, BasketballSimulator


class SpreadAnalyzer:
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
            team1 = Team(**self.team1_config)
            team2 = Team(**self.team2_config)
            
            # Run simulation
            simulator = BasketballSimulator(team1, team2, verbose=False)
            winner, summary = simulator.simulate_game()
            
            # Calculate point differential (team1 score - team2 score)
            point_diff = team1.score - team2.score
            
            self.results.append({
                'game_num': i + 1,
                'team1_score': team1.score,
                'team2_score': team2.score,
                'point_diff': point_diff,
                'winner': winner.name
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
                   Example: spread = 5.0 means team1 is favored by 5 points
        
        Returns:
            Dictionary with spread coverage analysis
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        # Count how many times each team covers the spread
        team1_covers = 0
        team2_covers = 0
        pushes = 0  # Exactly ties the spread
        
        for result in self.results:
            point_diff = result['point_diff']
            
            # Team1 is favored (positive spread)
            # Team1 covers if they win by more than the spread
            # Team2 covers if they lose by less than the spread (or win)
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
    
    def find_optimal_spread(self) -> float:
        """Find the spread where the line is most even (closest to 50/50)."""
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        # Calculate average point differential
        total_diff = sum(r['point_diff'] for r in self.results)
        avg_diff = total_diff / self.num_simulations
        
        return avg_diff
    
    def find_overvalued_spreads(self, min_points: float = 5.0, max_points: float = 20.0) -> List[Dict]:
        """
        Find spreads where the underdog is getting too many points (overvalued).
        
        An overvalued spread means the underdog is getting more points than they need,
        making them a good bet to cover. This happens when the actual average margin
        is much less than the spread being offered.
        
        Args:
            min_points: Minimum spread to check (default 5.0)
            max_points: Maximum spread to check (default 20.0)
        
        Returns:
            List of dictionaries with overvalued spread information
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        optimal = self.find_optimal_spread()
        overvalued = []
        
        # Check spreads from min_points to max_points
        for spread in range(int(min_points), int(max_points) + 1):
            spread_float = float(spread)
            
            # Skip spreads close to the optimal (within 2 points)
            if abs(spread_float - abs(optimal)) < 2:
                continue
            
            # If the spread is much higher than the optimal, it's overvalued
            # (underdog getting too many points)
            if spread_float > abs(optimal):
                analysis = self.analyze_spread(spread_float)
                
                # Check if underdog (team2) covers with high confidence
                # When spread > optimal, team2 is getting extra points
                if analysis['team2_cover_pct'] >= 65:  # 65%+ is valuable
                    value = spread_float - abs(optimal)  # Extra points being given
                    overvalued.append({
                        'spread': spread_float,
                        'underdog': self.team2_config['name'],
                        'favorite': self.team1_config['name'],
                        'underdog_covers_pct': analysis['team2_cover_pct'],
                        'extra_points': value,
                        'optimal_spread': abs(optimal),
                        'confidence': analysis['confidence'] if analysis['team2_cover_pct'] >= 70 else 'MEDIUM',
                        'value_rating': 'EXCELLENT' if value >= 5 else 'GOOD' if value >= 3 else 'FAIR'
                    })
            
            # Also check negative spreads (team2 favored)
            negative_spread = -spread_float
            if abs(negative_spread) > abs(optimal):
                analysis = self.analyze_spread(negative_spread)
                
                # When negative spread, team1 is the underdog getting points
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
                        'value_rating': 'EXCELLENT' if value >= 5 else 'GOOD' if value >= 3 else 'FAIR'
                    })
        
        # Sort by underdog cover percentage (best bets first)
        overvalued.sort(key=lambda x: x['underdog_covers_pct'], reverse=True)
        
        return overvalued
    
    def find_undervalued_spreads(self, min_points: float = 5.0, max_points: float = 20.0) -> List[Dict]:
        """
        Find spreads where the favorite is giving too many points (undervalued).
        
        An undervalued spread means the favorite has to cover more points than they
        statistically should, making them a bad bet. The underdog is not getting enough
        points, making the favorite overpriced.
        
        Args:
            min_points: Minimum spread to check (default 5.0)
            max_points: Maximum spread to check (default 20.0)
        
        Returns:
            List of dictionaries with undervalued spread information
        """
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        optimal = self.find_optimal_spread()
        undervalued = []
        
        # Check spreads from min_points to max_points
        for spread in range(int(min_points), int(max_points) + 1):
            spread_float = float(spread)
            
            # Skip spreads close to the optimal (within 2 points)
            if abs(spread_float - abs(optimal)) < 2:
                continue
            
            # If the spread is much lower than the optimal, it's undervalued
            # (favorite giving too few points / having to cover too much)
            if spread_float < abs(optimal):
                analysis = self.analyze_spread(spread_float)
                
                # Check if favorite (team1) fails to cover frequently
                # When spread < optimal, favorite is giving too few points to underdog
                if analysis['team1_cover_pct'] <= 40:  # 40% or less means bad bet
                    shortage = abs(optimal) - spread_float  # Points short of optimal
                    undervalued.append({
                        'spread': spread_float,
                        'favorite': self.team1_config['name'],
                        'underdog': self.team2_config['name'],
                        'favorite_covers_pct': analysis['team1_cover_pct'],
                        'points_short': shortage,
                        'optimal_spread': abs(optimal),
                        'risk_rating': 'HIGH_RISK' if shortage >= 5 else 'MODERATE_RISK' if shortage >= 3 else 'LOW_RISK',
                        'advice': f'AVOID betting {self.team1_config["name"]} at -{spread_float}'
                    })
            
            # Also check negative spreads (team2 as favorite giving too many points)
            negative_spread = -spread_float
            if abs(negative_spread) < abs(optimal):
                analysis = self.analyze_spread(negative_spread)
                
                # When negative spread, team2 is favorite - check if they fail to cover
                if analysis['team2_cover_pct'] <= 40:
                    shortage = abs(optimal) - abs(negative_spread)
                    undervalued.append({
                        'spread': negative_spread,
                        'favorite': self.team2_config['name'],
                        'underdog': self.team1_config['name'],
                        'favorite_covers_pct': analysis['team2_cover_pct'],
                        'points_short': shortage,
                        'optimal_spread': abs(optimal),
                        'risk_rating': 'HIGH_RISK' if shortage >= 5 else 'MODERATE_RISK' if shortage >= 3 else 'LOW_RISK',
                        'advice': f'AVOID betting {self.team2_config["name"]} at -{abs(negative_spread)}'
                    })
        
        # Sort by favorite cover percentage (worst bets first - lowest coverage)
        undervalued.sort(key=lambda x: x['favorite_covers_pct'])
        
        return undervalued
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics from all simulations."""
        if not self.results:
            raise ValueError("No simulation results available. Run run_simulations() first.")
        
        team1_scores = [r['team1_score'] for r in self.results]
        team2_scores = [r['team2_score'] for r in self.results]
        point_diffs = [r['point_diff'] for r in self.results]
        
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
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'team1_win_pct': (team1_wins / self.num_simulations) * 100,
            'team2_win_pct': (team2_wins / self.num_simulations) * 100
        }
    
    def print_report(self, spread: float = None):
        """Print a comprehensive report of the spread analysis."""
        if not self.results:
            print("No simulation results available. Run run_simulations() first.")
            return
        
        stats = self.get_statistics()
        optimal_spread = self.find_optimal_spread()
        
        print("="*70)
        print(" "*20 + "SPREAD ANALYSIS REPORT")
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
                print(f"\n⚠ MEDIUM CONFIDENCE - {analysis['best_bet']} has slight edge at {analysis['cover_rate']:.1f}%")
            else:
                print(f"\n✗ LOW CONFIDENCE - Too close to call ({analysis['cover_rate']:.1f}%)")
    
    def print_overvalued_spreads(self):
        """Print report of overvalued spreads (underdog getting too many points)."""
        if not self.results:
            print("No simulation results available. Run run_simulations() first.")
            return
        
        overvalued = self.find_overvalued_spreads()
        
        print("\n" + "="*70)
        print(" "*15 + "⭐ OVERVALUED SPREADS REPORT ⭐")
        print("="*70)
        print("\nIdentifying spreads where the underdog is getting TOO MANY points")
        print("(These are VALUE BETS - bet on the underdog)")
        print("-"*70)
        
        if not overvalued:
            print("\nNo significantly overvalued spreads found in the 5-20 point range.")
            print("The lines appear to be fairly priced based on simulation results.")
        else:
            print(f"\nFound {len(overvalued)} overvalued spread(s):\n")
            
            for i, bet in enumerate(overvalued, 1):
                spread_display = f"+{abs(bet['spread']):.1f}" if bet['spread'] < 0 else f"+{bet['spread']:.1f}"
                
                print(f"{i}. {bet['underdog']} {spread_display}")
                print(f"   Underdog covers: {bet['underdog_covers_pct']:.1f}% of the time")
                print(f"   Extra points given: {bet['extra_points']:.1f} (Optimal: {bet['optimal_spread']:.1f})")
                print(f"   Value Rating: {bet['value_rating']}")
                print(f"   Confidence: {bet['confidence']}")
                
                if bet['value_rating'] == 'EXCELLENT':
                    print(f"   🎯 EXCELLENT VALUE - Underdog getting {bet['extra_points']:.1f} extra points!")
                elif bet['value_rating'] == 'GOOD':
                    print(f"   ✓ GOOD VALUE - Underdog has clear advantage")
                
                print()
            
            # Highlight the best value bet
            best = overvalued[0]
            print("="*70)
            print("🏆 BEST VALUE BET (Underdog Getting Most Extra Points)")
            print("="*70)
            print(f"Bet on: {best['underdog']} +{abs(best['spread']):.1f}")
            print(f"Coverage Rate: {best['underdog_covers_pct']:.1f}%")
            print(f"Extra Points: {best['extra_points']:.1f} points above optimal")
            print(f"Value Rating: {best['value_rating']}")
            print("="*70)
    
    def print_undervalued_spreads(self):
        """Print report of undervalued spreads (favorite giving too many points)."""
        if not self.results:
            print("No simulation results available. Run run_simulations() first.")
            return
        
        undervalued = self.find_undervalued_spreads()
        
        print("\n" + "="*70)
        print(" "*15 + "⚠️  UNDERVALUED SPREADS REPORT ⚠️")
        print("="*70)
        print("\nIdentifying spreads where the favorite is giving TOO MANY points")
        print("(These are TRAPS - AVOID betting the favorite at these lines)")
        print("-"*70)
        
        if not undervalued:
            print("\nNo significantly undervalued spreads found in the 5-20 point range.")
            print("Favorites appear capable of covering the spreads offered.")
        else:
            print(f"\nFound {len(undervalued)} undervalued spread(s) - AVOID THESE BETS:\n")
            
            for i, bet in enumerate(undervalued, 1):
                print(f"{i}. {bet['favorite']} -{abs(bet['spread']):.1f}")
                print(f"   Favorite only covers: {bet['favorite_covers_pct']:.1f}% of the time")
                print(f"   Points short of optimal: {bet['points_short']:.1f} (Optimal: {bet['optimal_spread']:.1f})")
                print(f"   Risk Rating: {bet['risk_rating']}")
                print(f"   ⚠️  {bet['advice']}")
                
                if bet['risk_rating'] == 'HIGH_RISK':
                    print(f"   🚫 HIGH RISK - Favorite unlikely to cover this spread!")
                elif bet['risk_rating'] == 'MODERATE_RISK':
                    print(f"   ⚠ MODERATE RISK - Favorite struggling to cover")
                
                print()
            
            # Highlight the worst bet (favorite least likely to cover)
            worst = undervalued[0]
            print("="*70)
            print("🚫 WORST BET (Favorite Least Likely to Cover)")
            print("="*70)
            print(f"AVOID: {worst['favorite']} -{abs(worst['spread']):.1f}")
            print(f"Coverage Rate: Only {worst['favorite_covers_pct']:.1f}%")
            print(f"Favorite is {worst['points_short']:.1f} points short of what they should give")
            print(f"Risk Rating: {worst['risk_rating']}")
            print(f"\n💡 Better Option: Bet on {worst['underdog']} +{abs(worst['spread']):.1f} instead")
            print("="*70)


def main():
    """Main function for command-line spread analysis."""
    print("\n" + "="*70)
    print(" "*15 + "COLLEGE BASKETBALL SPREAD ANALYZER")
    print("="*70)
    
    # Example: Duke vs UNC
    team1_config = {
        'name': 'Duke Blue Devils',
        'fg_percentage': 0.48,
        'three_pt_percentage': 0.38,
        'ft_percentage': 0.75,
        'turnover_rate': 0.12,
        'offensive_rebound_rate': 0.32,
        'defensive_rebound_rate': 0.72
    }
    
    team2_config = {
        'name': 'UNC Tar Heels',
        'fg_percentage': 0.45,
        'three_pt_percentage': 0.35,
        'ft_percentage': 0.70,
        'turnover_rate': 0.14,
        'offensive_rebound_rate': 0.28,
        'defensive_rebound_rate': 0.68
    }
    
    # Create analyzer and run simulations
    analyzer = SpreadAnalyzer(team1_config, team2_config, num_simulations=1000)
    analyzer.run_simulations()
    
    # Test different spreads
    spreads_to_test = [3.0, 5.0, 7.0]
    
    for spread in spreads_to_test:
        print("\n" + "="*70)
        analyzer.print_report(spread=spread)
    
    # Find the optimal spread
    print("\n" + "="*70)
    print("FINDING OPTIMAL SPREAD (Most Even Line)")
    print("="*70)
    optimal = analyzer.find_optimal_spread()
    print(f"\nOptimal spread for 50/50 split: {optimal:.1f} points")
    analyzer.print_report(spread=optimal)
    
    # NEW: Find overvalued spreads
    print("\n" + "="*70)
    analyzer.print_overvalued_spreads()
    
    # NEW: Find undervalued spreads (favorites giving too many points)
    print("\n" + "="*70)
    analyzer.print_undervalued_spreads()


if __name__ == "__main__":
    main()
