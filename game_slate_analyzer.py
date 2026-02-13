"""
Practical Example: Using Billy Walters Framework for Real Analysis
Shows how to analyze a full slate of games
"""

from billy_walters_predictor import (
    PowerRatings, TeamStats, PredictionEngine, 
    BankrollManagement, GameFactors
)
from advanced_analysis import MonteCarloSimulator, ValueFinder


def analyze_game_slate():
    """
    Example: Analyze multiple games to find best betting opportunities
    Following Walters' approach of finding value across entire slate
    """
    print("=" * 80)
    print("BILLY WALTERS FRAMEWORK - GAME SLATE ANALYSIS")
    print("Finding Value Across Multiple Games")
    print("=" * 80)
    print()
    
    # Initialize systems
    pr = PowerRatings()
    simulator = MonteCarloSimulator(n_simulations=5000)
    bankroll = BankrollManagement(total_bankroll=10000)
    
    # Define teams for today's slate
    teams = {
        'Duke': TeamStats(
            name='Duke',
            offensive_efficiency=115.5,
            defensive_efficiency=95.2,
            tempo=70.5,
            recent_form=['W', 'W', 'L', 'W', 'W'],
            strength_of_schedule=2.5,
            injuries=[]
        ),
        'UNC': TeamStats(
            name='UNC',
            offensive_efficiency=112.3,
            defensive_efficiency=98.1,
            tempo=72.8,
            recent_form=['W', 'L', 'W', 'W', 'L'],
            strength_of_schedule=2.2,
            injuries=['Starting PG']
        ),
        'Kentucky': TeamStats(
            name='Kentucky',
            offensive_efficiency=118.2,
            defensive_efficiency=93.5,
            tempo=68.2,
            recent_form=['W', 'W', 'W', 'W', 'L'],
            strength_of_schedule=3.1,
            injuries=[]
        ),
        'Kansas': TeamStats(
            name='Kansas',
            offensive_efficiency=116.8,
            defensive_efficiency=94.8,
            tempo=69.5,
            recent_form=['W', 'W', 'W', 'L', 'W'],
            strength_of_schedule=2.8,
            injuries=[]
        ),
        'Gonzaga': TeamStats(
            name='Gonzaga',
            offensive_efficiency=120.5,
            defensive_efficiency=92.1,
            tempo=73.5,
            recent_form=['W', 'W', 'W', 'W', 'W'],
            strength_of_schedule=1.8,
            injuries=[]
        ),
        'Saint Marys': TeamStats(
            name='Saint Marys',
            offensive_efficiency=108.5,
            defensive_efficiency=99.2,
            tempo=65.8,
            recent_form=['W', 'L', 'L', 'W', 'W'],
            strength_of_schedule=1.2,
            injuries=['Top Scorer']
        )
    }
    
    # Calculate power ratings
    for team_name, stats in teams.items():
        pr.update_rating(team_name, stats)
    
    # Define today's games with market lines
    games = [
        {
            'home': 'Duke',
            'away': 'UNC',
            'market_spread': 5.5,
            'market_favorite': 'Duke',
            'market_total': 155.0,
            'neutral_site': False,
            'rivalry': True,
            'conference': True
        },
        {
            'home': 'Kentucky',
            'away': 'Kansas',
            'market_spread': 3.0,
            'market_favorite': 'Kentucky',
            'market_total': 145.5,
            'neutral_site': False,
            'rivalry': False,
            'conference': False
        },
        {
            'home': 'Gonzaga',
            'away': 'Saint Marys',
            'market_spread': 14.5,
            'market_favorite': 'Gonzaga',
            'market_total': 142.0,
            'neutral_site': False,
            'rivalry': True,
            'conference': True
        }
    ]
    
    # Analyze each game
    engine = PredictionEngine(pr)
    opportunities = []
    
    print("GAME-BY-GAME ANALYSIS")
    print("=" * 80)
    
    for i, game in enumerate(games, 1):
        print(f"\nGame {i}: {game['away']} @ {game['home']}")
        print("-" * 80)
        
        # Get our prediction
        predicted_spread, predicted_favorite = engine.predict_spread(
            home_team=game['home'],
            away_team=game['away'],
            is_neutral_site=game['neutral_site'],
            is_rivalry=game['rivalry'],
            is_conference_game=game['conference']
        )
        
        # Predict total
        predicted_total = engine.predict_total(
            game['home'], 
            game['away'],
            teams[game['home']], 
            teams[game['away']]
        )
        
        print(f"Market Line: {game['market_favorite']} -{game['market_spread']}")
        print(f"Our Line:    {predicted_favorite} -{predicted_spread}")
        print(f"Market Total: {game['market_total']}")
        print(f"Our Total:    {predicted_total}")
        
        # Calculate edges
        spread_edge = engine.calculate_edge(predicted_spread, game['market_spread'])
        total_edge = engine.calculate_edge(predicted_total, game['market_total'])
        
        print(f"\nSpread Edge: {spread_edge:.1%}")
        print(f"Total Edge:  {total_edge:.1%}")
        
        # Check if worth betting
        if spread_edge >= 0.03:  # 3% minimum edge
            opportunities.append({
                'game': f"{game['away']} @ {game['home']}",
                'bet_type': 'spread',
                'side': predicted_favorite if predicted_spread > game['market_spread'] else 'underdog',
                'edge': spread_edge,
                'line': game['market_spread'],
                'confidence': 0.7
            })
            print(f"✓ SPREAD VALUE DETECTED")
        
        if total_edge >= 0.03:
            bet_side = 'OVER' if predicted_total > game['market_total'] else 'UNDER'
            opportunities.append({
                'game': f"{game['away']} @ {game['home']}",
                'bet_type': 'total',
                'side': bet_side,
                'edge': total_edge,
                'line': game['market_total'],
                'confidence': 0.65
            })
            print(f"✓ TOTAL VALUE DETECTED")
        
        # Run Monte Carlo for best opportunities
        if spread_edge >= 0.05 or total_edge >= 0.05:
            print("\nRunning Monte Carlo simulation...")
            sim_result = simulator.simulate_game(
                home_offensive_eff=teams[game['home']].offensive_efficiency,
                home_defensive_eff=teams[game['home']].defensive_efficiency,
                away_offensive_eff=teams[game['away']].offensive_efficiency,
                away_defensive_eff=teams[game['away']].defensive_efficiency,
                avg_tempo=(teams[game['home']].tempo + teams[game['away']].tempo) / 2
            )
            print(f"Simulated Home Win Probability: {sim_result.home_win_probability:.1%}")
    
    # Summary of opportunities
    print("\n" + "=" * 80)
    print("BETTING OPPORTUNITIES SUMMARY")
    print("=" * 80)
    
    if not opportunities:
        print("\nNo value bets found today.")
        print("Walters principle: Don't force action. Wait for clear edge.")
    else:
        # Sort by edge
        opportunities.sort(key=lambda x: x['edge'], reverse=True)
        
        print(f"\nFound {len(opportunities)} value opportunities:\n")
        
        total_bet_amount = 0
        
        for i, opp in enumerate(opportunities, 1):
            bet_size = bankroll.calculate_bet_size(opp['edge'], opp['confidence'])
            total_bet_amount += bet_size
            
            print(f"{i}. {opp['game']}")
            print(f"   Type: {opp['bet_type'].upper()}")
            print(f"   Bet:  {opp['side']} {opp['line']}")
            print(f"   Edge: {opp['edge']:.1%}")
            print(f"   Recommended Bet: ${bet_size:.2f} "
                  f"({(bet_size/bankroll.current_bankroll)*100:.1f}% of bankroll)")
            print()
        
        print(f"Total Action Today: ${total_bet_amount:.2f} "
              f"({(total_bet_amount/bankroll.current_bankroll)*100:.1f}% of bankroll)")
        
        print("\n" + "-" * 80)
        print("Risk Management Check:")
        total_risk_pct = (total_bet_amount / bankroll.current_bankroll) * 100
        
        if total_risk_pct <= 10:
            print(f"✓ Total risk ({total_risk_pct:.1f}%) is within safe limits")
        else:
            print(f"⚠ WARNING: Total risk ({total_risk_pct:.1f}%) exceeds 10% of bankroll")
            print("  Consider reducing bet sizes or being more selective")
    
    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS:")
    print("=" * 80)
    print("• Only bet games where model shows clear edge (>3%)")
    print("• Size bets proportional to edge and confidence")
    print("• Never risk more than 1-3% per individual bet")
    print("• Total daily action should stay under 10% of bankroll")
    print("• Be patient - not every day will have value opportunities")
    print("• Track results to validate model accuracy over time")
    print("=" * 80)


if __name__ == "__main__":
    analyze_game_slate()
