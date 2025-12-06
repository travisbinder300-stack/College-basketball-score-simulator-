#!/usr/bin/env python3
"""
Example usage of NBA Simulator for betting analysis
Demonstrates finding betting edges and optimal Kelly sizing
"""

from nba_simulator import NBASimulator, TeamStats, KellyBetting


def main():
    """Run example betting analysis scenarios"""
    
    print("=" * 80)
    print("NBA BETTING ANALYSIS EXAMPLES")
    print("Using Kelly Criterion with 10,000 Game Simulations")
    print("=" * 80)
    print()
    
    # Create realistic NBA teams (based on 2024 season stats)
    bucks = TeamStats(
        name="Milwaukee Bucks",
        offensive_rating=119.8,
        defensive_rating=112.5,
        pace=99.2,
        efg_pct=0.578,
        tov_pct=12.8,
        orb_pct=25.3,
        ft_rate=0.248
    )
    
    celtics = TeamStats(
        name="Boston Celtics",
        offensive_rating=120.6,
        defensive_rating=110.6,
        pace=98.5,
        efg_pct=0.591,
        tov_pct=11.9,
        orb_pct=27.1,
        ft_rate=0.242
    )
    
    warriors = TeamStats(
        name="Golden State Warriors",
        offensive_rating=116.2,
        defensive_rating=113.8,
        pace=99.8,
        efg_pct=0.570,
        tov_pct=13.5,
        orb_pct=24.8,
        ft_rate=0.235
    )
    
    pistons = TeamStats(
        name="Detroit Pistons",
        offensive_rating=108.5,
        defensive_rating=117.2,
        pace=97.8,
        efg_pct=0.525,
        tov_pct=15.2,
        orb_pct=22.1,
        ft_rate=0.218
    )
    
    # Initialize simulator
    simulator = NBASimulator(home_court_advantage=3.5)
    
    # Scenario 1: Championship matchup
    print("SCENARIO 1: Championship Contender Matchup")
    print("-" * 80)
    print(f"Home: {celtics.name} (Net Rating: {celtics.net_rating():+.1f})")
    print(f"Away: {bucks.name} (Net Rating: {bucks.net_rating():+.1f})")
    print()
    
    results1 = simulator.simulate_multiple_games(celtics, bucks, 10000)
    
    print(f"Model Win Probability (Home): {results1['home_win_pct']:.1%}")
    print(f"Expected Score: {results1['avg_home_score']:.1f} - {results1['avg_away_score']:.1f}")
    print(f"Expected Margin: {results1['avg_margin']:+.1f} ± {results1['margin_stdev']:.1f}")
    print()
    
    # Example market odds
    market_odds_home = 1.80  # -125 American odds
    market_odds_away = 2.10  # +110 American odds
    
    print("Market Analysis:")
    print(f"  Home Odds: {market_odds_home:.2f} (Implied: {1/market_odds_home:.1%})")
    print(f"  Away Odds: {market_odds_away:.2f} (Implied: {1/market_odds_away:.1%})")
    print()
    
    # Calculate Kelly bets
    kelly_home = KellyBetting.calculate_kelly_fraction(results1['home_win_pct'], market_odds_home, 0.25)
    ev_home = KellyBetting.expected_value(results1['home_win_pct'], market_odds_home, 100)
    
    kelly_away = KellyBetting.calculate_kelly_fraction(1 - results1['home_win_pct'], market_odds_away, 0.25)
    ev_away = KellyBetting.expected_value(1 - results1['home_win_pct'], market_odds_away, 100)
    
    if kelly_home > 0:
        print(f"✓ HOME BET RECOMMENDED:")
        print(f"  Kelly Bet Size: {kelly_home:.2%} of bankroll")
        print(f"  Expected Value: ${ev_home:+.2f} per $100")
        print(f"  Edge: {(results1['home_win_pct'] - 1/market_odds_home):.1%}")
    else:
        print(f"✗ No home bet (Model: {results1['home_win_pct']:.1%} vs Market: {1/market_odds_home:.1%})")
    
    print()
    
    if kelly_away > 0:
        print(f"✓ AWAY BET RECOMMENDED:")
        print(f"  Kelly Bet Size: {kelly_away:.2%} of bankroll")
        print(f"  Expected Value: ${ev_away:+.2f} per $100")
        print(f"  Edge: {((1-results1['home_win_pct']) - 1/market_odds_away):.1%}")
    else:
        print(f"✗ No away bet (Model: {1-results1['home_win_pct']:.1%} vs Market: {1/market_odds_away:.1%})")
    
    print()
    print()
    
    # Scenario 2: Mismatch game
    print("SCENARIO 2: Mismatched Game (Potential Value)")
    print("-" * 80)
    print(f"Home: {pistons.name} (Net Rating: {pistons.net_rating():+.1f})")
    print(f"Away: {warriors.name} (Net Rating: {warriors.net_rating():+.1f})")
    print()
    
    results2 = simulator.simulate_multiple_games(pistons, warriors, 10000)
    
    print(f"Model Win Probability (Home): {results2['home_win_pct']:.1%}")
    print(f"Expected Score: {results2['avg_home_score']:.1f} - {results2['avg_away_score']:.1f}")
    print(f"Expected Margin: {results2['avg_margin']:+.1f} ± {results2['margin_stdev']:.1f}")
    print()
    
    # Market might overvalue Warriors on the road
    market_odds_home2 = 3.50  # +250 American odds (underdog)
    market_odds_away2 = 1.33  # -300 American odds (heavy favorite)
    
    print("Market Analysis:")
    print(f"  Home Odds: {market_odds_home2:.2f} (Implied: {1/market_odds_home2:.1%})")
    print(f"  Away Odds: {market_odds_away2:.2f} (Implied: {1/market_odds_away2:.1%})")
    print()
    
    kelly_home2 = KellyBetting.calculate_kelly_fraction(results2['home_win_pct'], market_odds_home2, 0.25)
    ev_home2 = KellyBetting.expected_value(results2['home_win_pct'], market_odds_home2, 100)
    
    kelly_away2 = KellyBetting.calculate_kelly_fraction(1 - results2['home_win_pct'], market_odds_away2, 0.25)
    ev_away2 = KellyBetting.expected_value(1 - results2['home_win_pct'], market_odds_away2, 100)
    
    if kelly_home2 > 0:
        print(f"✓ HOME BET RECOMMENDED:")
        print(f"  Kelly Bet Size: {kelly_home2:.2%} of bankroll")
        print(f"  Expected Value: ${ev_home2:+.2f} per $100")
        print(f"  Edge: {(results2['home_win_pct'] - 1/market_odds_home2):.1%}")
    else:
        print(f"✗ No home bet (Model: {results2['home_win_pct']:.1%} vs Market: {1/market_odds_home2:.1%})")
    
    print()
    
    if kelly_away2 > 0:
        print(f"✓ AWAY BET RECOMMENDED:")
        print(f"  Kelly Bet Size: {kelly_away2:.2%} of bankroll")
        print(f"  Expected Value: ${ev_away2:+.2f} per $100")
        print(f"  Edge: {((1-results2['home_win_pct']) - 1/market_odds_away2):.1%}")
    else:
        print(f"✗ No away bet (Model: {1-results2['home_win_pct']:.1%} vs Market: {1/market_odds_away2:.1%})")
    
    print()
    print()
    
    # Scenario 3: Bankroll simulation
    print("SCENARIO 3: Bankroll Growth Simulation")
    print("-" * 80)
    print("Simulating 100 bets using Kelly strategy vs flat betting")
    print()
    
    starting_bankroll = 10000
    num_bets = 100
    
    # Kelly strategy
    kelly_bankroll = starting_bankroll
    
    # Flat betting (always 2%)
    flat_bankroll = starting_bankroll
    flat_bet_pct = 0.02
    
    wins_kelly = 0
    wins_flat = 0
    
    for i in range(num_bets):
        # Use Celtics vs Bucks matchup
        result = simulator.simulate_game(celtics, bucks)
        home_won = result.home_win
        
        # Kelly bet
        kelly_bet_size = kelly_bankroll * kelly_home if kelly_home > 0 else 0
        if kelly_bet_size > 0:
            if home_won:
                kelly_bankroll += kelly_bet_size * (market_odds_home - 1)
                wins_kelly += 1
            else:
                kelly_bankroll -= kelly_bet_size
        
        # Flat bet
        flat_bet_size = flat_bankroll * flat_bet_pct
        if home_won:
            flat_bankroll += flat_bet_size * (market_odds_home - 1)
            wins_flat += 1
        else:
            flat_bankroll -= flat_bet_size
    
    print(f"Results after {num_bets} bets:")
    print(f"  Kelly Strategy:")
    print(f"    Final Bankroll: ${kelly_bankroll:,.2f}")
    print(f"    ROI: {(kelly_bankroll/starting_bankroll - 1):.1%}")
    print(f"    Wins: {wins_kelly}/{num_bets} ({wins_kelly/num_bets:.1%})")
    print()
    print(f"  Flat Betting (2%):")
    print(f"    Final Bankroll: ${flat_bankroll:,.2f}")
    print(f"    ROI: {(flat_bankroll/starting_bankroll - 1):.1%}")
    print(f"    Wins: {wins_flat}/{num_bets} ({wins_flat/num_bets:.1%})")
    print()
    
    if kelly_bankroll > flat_bankroll:
        print(f"Kelly outperformed by ${kelly_bankroll - flat_bankroll:,.2f}")
    else:
        print(f"Flat betting outperformed by ${flat_bankroll - kelly_bankroll:,.2f}")
    
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("1. Kelly Criterion maximizes long-term growth when you have an edge")
    print("2. Quarter-Kelly (25%) reduces variance while maintaining good returns")
    print("3. Only bet when model probability > market implied probability")
    print("4. Larger edges justify larger bet sizes (up to maximum)")
    print("5. Variance is high in small samples - Kelly shines over many bets")


if __name__ == "__main__":
    main()
