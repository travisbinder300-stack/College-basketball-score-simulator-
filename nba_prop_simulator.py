"""
NBA Prop Betting Simulator and Analyzer
Based on PropMadness.com interfuture data structure

This module provides tools to simulate and analyze NBA prop bets,
including value analysis, probability calculations, and simulation.
"""

import random
from typing import List, Dict, Tuple
from nba_prop_data import PlayerProp, PropBetSlip, PropType, generate_sample_props
from datetime import datetime


class PropAnalyzer:
    """Analyze NBA prop bets for value and probability"""
    
    def __init__(self):
        self.variance_factor = 0.15  # 15% standard variance
    
    def calculate_hit_probability(self, prop: PlayerProp, is_over: bool = True) -> float:
        """
        Calculate the estimated probability of a prop hitting
        based on player averages and context
        """
        if prop.player_season_avg is None:
            return 0.5  # Default to 50% if no data
        
        # Weight different averages
        season_weight = 0.4
        last_5_weight = 0.4
        opponent_weight = 0.2
        
        # Calculate weighted average
        weighted_avg = 0
        total_weight = 0
        
        if prop.player_season_avg:
            weighted_avg += prop.player_season_avg * season_weight
            total_weight += season_weight
        
        if prop.player_last_5_avg:
            weighted_avg += prop.player_last_5_avg * last_5_weight
            total_weight += last_5_weight
        
        if prop.vs_opponent_avg:
            weighted_avg += prop.vs_opponent_avg * opponent_weight
            total_weight += opponent_weight
        
        if total_weight > 0:
            weighted_avg /= total_weight
        
        # Adjust for injury status
        injury_multiplier = {
            "healthy": 1.0,
            "questionable": 0.95,
            "doubtful": 0.85,
            "out": 0.0
        }
        weighted_avg *= injury_multiplier.get(prop.injury_status, 1.0)
        
        # Calculate probability using normal distribution approximation
        line = prop.prop_line.line_value
        std_dev = weighted_avg * self.variance_factor
        
        if std_dev == 0:
            return 1.0 if (is_over and weighted_avg > line) or (not is_over and weighted_avg < line) else 0.0
        
        # Z-score calculation
        z_score = (line - weighted_avg) / std_dev
        
        # Approximate probability using z-score
        # For over, we want P(X > line) = 1 - P(X <= line)
        prob_under = self._approximate_normal_cdf(z_score)
        
        return 1 - prob_under if is_over else prob_under
    
    def _approximate_normal_cdf(self, z: float) -> float:
        """Approximate the cumulative distribution function for normal distribution"""
        # Using error function approximation
        t = 1.0 / (1.0 + 0.2316419 * abs(z))
        d = 0.3989423 * pow(2.71828, -z * z / 2)
        prob = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
        
        if z > 0:
            prob = 1 - prob
        
        return prob
    
    def find_value_bets(self, props: List[PlayerProp], min_edge: float = 0.05) -> List[Tuple[PlayerProp, float]]:
        """
        Find props with positive expected value
        min_edge: minimum edge required (5% by default)
        """
        value_bets = []
        
        for prop in props:
            # Calculate our estimated probability
            estimated_prob_over = self.calculate_hit_probability(prop, is_over=True)
            estimated_prob_under = self.calculate_hit_probability(prop, is_over=False)
            
            # Get market implied probability
            market_prob_over = prop.prop_line.get_implied_probability(True)
            market_prob_under = prop.prop_line.get_implied_probability(False)
            
            # Calculate edge for over
            edge_over = estimated_prob_over - market_prob_over
            if edge_over >= min_edge:
                value_bets.append((prop, edge_over, "OVER"))
            
            # Calculate edge for under
            edge_under = estimated_prob_under - market_prob_under
            if edge_under >= min_edge:
                value_bets.append((prop, edge_under, "UNDER"))
        
        # Sort by edge (highest first)
        value_bets.sort(key=lambda x: x[1], reverse=True)
        
        return value_bets
    
    def analyze_prop(self, prop: PlayerProp) -> Dict:
        """Perform complete analysis on a single prop"""
        over_prob = self.calculate_hit_probability(prop, is_over=True)
        under_prob = self.calculate_hit_probability(prop, is_over=False)
        
        market_over_prob = prop.prop_line.get_implied_probability(True)
        market_under_prob = prop.prop_line.get_implied_probability(False)
        
        edge_over = over_prob - market_over_prob
        edge_under = under_prob - market_under_prob
        
        return {
            "prop": str(prop),
            "line": prop.prop_line.line_value,
            "estimated_over_probability": f"{over_prob:.2%}",
            "estimated_under_probability": f"{under_prob:.2%}",
            "market_over_probability": f"{market_over_prob:.2%}",
            "market_under_probability": f"{market_under_prob:.2%}",
            "edge_over": f"{edge_over:+.2%}",
            "edge_under": f"{edge_under:+.2%}",
            "recommendation": "OVER" if edge_over > edge_under else "UNDER" if edge_under > 0.02 else "PASS"
        }


class PropSimulator:
    """Simulate NBA prop bet outcomes"""
    
    def __init__(self, analyzer: PropAnalyzer):
        self.analyzer = analyzer
    
    def simulate_prop_outcome(self, prop: PlayerProp, num_simulations: int = 10000) -> Dict:
        """
        Simulate a prop outcome using Monte Carlo simulation
        """
        # Calculate expected value and standard deviation
        season_avg = prop.player_season_avg or prop.prop_line.line_value
        std_dev = season_avg * self.analyzer.variance_factor
        
        # Run simulations
        over_hits = 0
        under_hits = 0
        simulated_values = []
        
        for _ in range(num_simulations):
            # Simulate performance using normal distribution
            simulated_value = random.gauss(season_avg, std_dev)
            simulated_value = max(0, simulated_value)  # Can't be negative
            simulated_values.append(simulated_value)
            
            if simulated_value > prop.prop_line.line_value:
                over_hits += 1
            else:
                under_hits += 1
        
        # Calculate statistics
        avg_simulated = sum(simulated_values) / len(simulated_values)
        
        return {
            "prop": str(prop),
            "line": prop.prop_line.line_value,
            "simulations": num_simulations,
            "over_hit_rate": f"{over_hits / num_simulations:.2%}",
            "under_hit_rate": f"{under_hits / num_simulations:.2%}",
            "avg_simulated_value": f"{avg_simulated:.2f}",
            "expected_season_avg": f"{season_avg:.2f}"
        }
    
    def simulate_parlay(self, bet_slip: PropBetSlip, num_simulations: int = 10000) -> Dict:
        """
        Simulate a parlay bet outcome
        """
        if bet_slip.bet_type != "parlay":
            return {"error": "Only parlay bets can be simulated with this method"}
        
        parlay_hits = 0
        
        for _ in range(num_simulations):
            all_hit = True
            for prop in bet_slip.props:
                # Simulate each prop
                season_avg = prop.player_season_avg or prop.prop_line.line_value
                std_dev = season_avg * self.analyzer.variance_factor
                simulated_value = random.gauss(season_avg, std_dev)
                simulated_value = max(0, simulated_value)
                
                # Check if this prop hits (assuming all "over" for simplicity)
                if simulated_value <= prop.prop_line.line_value:
                    all_hit = False
                    break
            
            if all_hit:
                parlay_hits += 1
        
        hit_rate = parlay_hits / num_simulations
        potential_payout = bet_slip.calculate_potential_payout()
        expected_value = (hit_rate * potential_payout) - bet_slip.stake
        
        return {
            "bet_slip_id": bet_slip.slip_id,
            "num_props": len(bet_slip.props),
            "stake": f"${bet_slip.stake:.2f}",
            "potential_payout": f"${potential_payout:.2f}",
            "simulations": num_simulations,
            "hit_rate": f"{hit_rate:.2%}",
            "expected_value": f"${expected_value:.2f}",
            "roi": f"{(expected_value / bet_slip.stake):.2%}" if bet_slip.stake > 0 else "N/A"
        }


def main():
    """Main function to demonstrate the prop analyzer and simulator"""
    print("=" * 80)
    print("NBA PROP BETTING ANALYZER & SIMULATOR")
    print("Based on PropMadness.com Interfuture Data Structure")
    print("=" * 80)
    print()
    
    # Generate sample props
    props = generate_sample_props()
    
    # Initialize analyzer and simulator
    analyzer = PropAnalyzer()
    simulator = PropSimulator(analyzer)
    
    # Analyze all props
    print("\n" + "=" * 80)
    print("PROP ANALYSIS")
    print("=" * 80)
    
    for prop in props:
        analysis = analyzer.analyze_prop(prop)
        print(f"\n{analysis['prop']}")
        print("-" * 80)
        for key, value in analysis.items():
            if key != 'prop':
                print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Find value bets
    print("\n" + "=" * 80)
    print("VALUE BETS (5%+ Edge)")
    print("=" * 80)
    
    value_bets = analyzer.find_value_bets(props, min_edge=0.05)
    if value_bets:
        for prop, edge, side in value_bets:
            print(f"\n✓ {prop} - {side}")
            print(f"  Edge: {edge:+.2%}")
    else:
        print("\nNo value bets found with 5%+ edge")
    
    # Simulate individual props
    print("\n" + "=" * 80)
    print("MONTE CARLO SIMULATIONS (10,000 runs per prop)")
    print("=" * 80)
    
    for prop in props[:3]:  # Simulate first 3 props
        sim_result = simulator.simulate_prop_outcome(prop, num_simulations=10000)
        print(f"\n{sim_result['prop']}")
        print("-" * 80)
        for key, value in sim_result.items():
            if key != 'prop':
                print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Create and simulate a sample parlay
    print("\n" + "=" * 80)
    print("PARLAY SIMULATION")
    print("=" * 80)
    
    sample_parlay = PropBetSlip(
        slip_id="PARLAY_001",
        props=props[:3],  # First 3 props
        stake=50.0,
        bet_type="parlay"
    )
    
    parlay_result = simulator.simulate_parlay(sample_parlay, num_simulations=10000)
    print(f"\nParlay: {' + '.join([str(p) for p in sample_parlay.props])}")
    print("-" * 80)
    for key, value in parlay_result.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
