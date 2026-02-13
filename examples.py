"""
NBA Prop Betting - Complete Examples
Demonstrates all features of the NBA prop betting system
"""

import os
from nba_prop_data import generate_sample_props, PropBetSlip, PropType
from nba_prop_simulator import PropAnalyzer, PropSimulator
from nba_prop_loader import PropDataLoader


def example_1_basic_prop_analysis():
    """Example 1: Analyze individual props"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Prop Analysis")
    print("=" * 80)
    print()
    
    # Generate sample props
    props = generate_sample_props()
    analyzer = PropAnalyzer()
    
    # Analyze the first prop (LeBron James points)
    lebron_prop = props[0]
    analysis = analyzer.analyze_prop(lebron_prop)
    
    print(f"Analyzing: {analysis['prop']}")
    print(f"Line: {analysis['line']}")
    print(f"Estimated Over Probability: {analysis['estimated_over_probability']}")
    print(f"Market Over Probability: {analysis['market_over_probability']}")
    print(f"Edge: {analysis['edge_over']}")
    print(f"Recommendation: {analysis['recommendation']}")
    print()


def example_2_find_value_bets():
    """Example 2: Find value bets across all props"""
    print("=" * 80)
    print("EXAMPLE 2: Finding Value Bets")
    print("=" * 80)
    print()
    
    props = generate_sample_props()
    analyzer = PropAnalyzer()
    
    # Find all props with 5%+ edge
    value_bets = analyzer.find_value_bets(props, min_edge=0.05)
    
    print(f"Found {len(value_bets)} value bets with 5%+ edge:\n")
    
    for prop, edge, side in value_bets:
        print(f"✓ {prop.player.name} - {prop.prop_type.value.upper()}")
        print(f"  Line: {prop.prop_line.line_value}")
        print(f"  Recommendation: {side}")
        print(f"  Edge: {edge:+.2%}")
        print(f"  Season Avg: {prop.player_season_avg}")
        print()


def example_3_simulate_single_prop():
    """Example 3: Monte Carlo simulation of a single prop"""
    print("=" * 80)
    print("EXAMPLE 3: Monte Carlo Simulation - Single Prop")
    print("=" * 80)
    print()
    
    props = generate_sample_props()
    analyzer = PropAnalyzer()
    simulator = PropSimulator(analyzer)
    
    # Simulate Stephen Curry's 3-pointers prop
    curry_prop = props[1]
    print(f"Simulating: {curry_prop}")
    print(f"Running 10,000 simulations...\n")
    
    result = simulator.simulate_prop_outcome(curry_prop, num_simulations=10000)
    
    print(f"Results:")
    print(f"  Line: {result['line']}")
    print(f"  Over Hit Rate: {result['over_hit_rate']}")
    print(f"  Under Hit Rate: {result['under_hit_rate']}")
    print(f"  Average Simulated Value: {result['avg_simulated_value']}")
    print(f"  Player Season Average: {result['expected_season_avg']}")
    print()


def example_4_create_and_simulate_parlay():
    """Example 4: Create and simulate a parlay bet"""
    print("=" * 80)
    print("EXAMPLE 4: Parlay Simulation")
    print("=" * 80)
    print()
    
    props = generate_sample_props()
    analyzer = PropAnalyzer()
    simulator = PropSimulator(analyzer)
    
    # Create a 3-leg parlay
    parlay_props = props[:3]
    parlay = PropBetSlip(
        slip_id="EXAMPLE_PARLAY_001",
        props=parlay_props,
        stake=50.0,
        bet_type="parlay"
    )
    
    print("Creating parlay with:")
    for i, prop in enumerate(parlay_props, 1):
        print(f"  {i}. {prop.player.name} {prop.prop_type.value} OVER {prop.prop_line.line_value}")
    
    print(f"\nStake: ${parlay.stake:.2f}")
    print(f"Potential Payout: ${parlay.calculate_potential_payout():.2f}")
    print(f"\nRunning 10,000 simulations...\n")
    
    result = simulator.simulate_parlay(parlay, num_simulations=10000)
    
    print("Results:")
    print(f"  Hit Rate: {result['hit_rate']}")
    print(f"  Expected Value: {result['expected_value']}")
    print(f"  Return on Investment (ROI): {result['roi']}")
    print()


def example_5_load_from_json():
    """Example 5: Load data from interfuture JSON file"""
    print("=" * 80)
    print("EXAMPLE 5: Loading Data from Interfuture JSON")
    print("=" * 80)
    print()
    
    json_file = os.path.join(os.path.dirname(__file__), 'interfuture_nba_props.json')
    loader = PropDataLoader(json_file)
    
    # Load metadata
    metadata = loader.get_metadata()
    print("Data Source:")
    print(f"  {metadata['source']}")
    print(f"  Season: {metadata['season']}")
    print(f"  Data Type: {metadata['data_type']}")
    print()
    
    # Load all data
    players, games, props = loader.load_all()
    
    print(f"Loaded Data:")
    print(f"  {len(players)} players")
    print(f"  {len(games)} games")
    print(f"  {len(props)} props")
    print()
    
    # Filter by specific game
    print("Props for Lakers @ Warriors:")
    lal_gsw_props = loader.filter_props_by_game("NBA_2024_LAL_GSW_001")
    for prop in lal_gsw_props:
        print(f"  • {prop.player.name}: {prop.prop_type.value} O/U {prop.prop_line.line_value}")
    print()


def example_6_comprehensive_analysis():
    """Example 6: Comprehensive analysis workflow"""
    print("=" * 80)
    print("EXAMPLE 6: Comprehensive Analysis Workflow")
    print("=" * 80)
    print()
    
    # Load data
    json_file = os.path.join(os.path.dirname(__file__), 'interfuture_nba_props.json')
    loader = PropDataLoader(json_file)
    players, games, props = loader.load_all()
    
    # Initialize analyzer and simulator
    analyzer = PropAnalyzer()
    simulator = PropSimulator(analyzer)
    
    # Step 1: Find best value bets
    print("Step 1: Finding Best Value Bets")
    print("-" * 80)
    value_bets = analyzer.find_value_bets(props, min_edge=0.10)
    
    if value_bets:
        print(f"Found {len(value_bets)} props with 10%+ edge:\n")
        best_prop, best_edge, best_side = value_bets[0]
        
        print(f"Best Value Bet:")
        print(f"  {best_prop.player.name} - {best_prop.prop_type.value.upper()}")
        print(f"  Line: {best_prop.prop_line.line_value} ({best_side})")
        print(f"  Edge: {best_edge:+.2%}")
        print(f"  Bookmaker: {best_prop.prop_line.bookmaker}")
        print()
        
        # Step 2: Simulate the best value bet
        print("Step 2: Simulating Best Value Bet")
        print("-" * 80)
        sim_result = simulator.simulate_prop_outcome(best_prop, num_simulations=10000)
        print(f"Over Hit Rate: {sim_result['over_hit_rate']}")
        print(f"Expected Value: {sim_result['avg_simulated_value']}")
        print()
        
        # Step 3: Build optimal parlay
        print("Step 3: Building Optimal Parlay")
        print("-" * 80)
        
        # Take top 3 value bets
        top_3_props = [vb[0] for vb in value_bets[:3]]
        
        parlay = PropBetSlip(
            slip_id="OPTIMAL_PARLAY",
            props=top_3_props,
            stake=100.0,
            bet_type="parlay"
        )
        
        print("Parlay legs:")
        for i, prop in enumerate(top_3_props, 1):
            edge = value_bets[i-1][1]
            print(f"  {i}. {prop.player.name} {prop.prop_type.value} (Edge: {edge:+.2%})")
        
        print(f"\nStake: ${parlay.stake:.2f}")
        print(f"Potential Payout: ${parlay.calculate_potential_payout():.2f}")
        
        # Simulate parlay
        parlay_result = simulator.simulate_parlay(parlay, num_simulations=10000)
        print(f"Expected Hit Rate: {parlay_result['hit_rate']}")
        print(f"Expected Value: {parlay_result['expected_value']}")
        print(f"ROI: {parlay_result['roi']}")
    else:
        print("No props found with 10%+ edge in this dataset.")
    
    print()


def example_7_filter_and_analyze():
    """Example 7: Filter props by type and analyze"""
    print("=" * 80)
    print("EXAMPLE 7: Filter by Prop Type and Analyze")
    print("=" * 80)
    print()
    
    json_file = os.path.join(os.path.dirname(__file__), 'interfuture_nba_props.json')
    loader = PropDataLoader(json_file)
    analyzer = PropAnalyzer()
    
    # Filter only points props
    points_props = loader.filter_props_by_type(PropType.POINTS)
    
    print(f"Analyzing {len(points_props)} POINTS props:\n")
    
    for prop in points_props:
        analysis = analyzer.analyze_prop(prop)
        
        print(f"{prop.player.name} - {prop.game.away_team} @ {prop.game.home_team}")
        print(f"  Line: {prop.prop_line.line_value}")
        print(f"  Season Avg: {prop.player_season_avg}")
        print(f"  Recommendation: {analysis['recommendation']}")
        print(f"  Edge (OVER): {analysis['edge_over']}")
        print()


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("NBA PROP BETTING SYSTEM - COMPLETE EXAMPLES")
    print("=" * 80)
    print("\n")
    
    examples = [
        example_1_basic_prop_analysis,
        example_2_find_value_bets,
        example_3_simulate_single_prop,
        example_4_create_and_simulate_parlay,
        example_5_load_from_json,
        example_6_comprehensive_analysis,
        example_7_filter_and_analyze
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            if i < len(examples):
                input("Press Enter to continue to next example...")
                print("\n" * 2)
        except Exception as e:
            print(f"Error in example {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
