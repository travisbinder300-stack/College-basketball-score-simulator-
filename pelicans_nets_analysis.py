#!/usr/bin/env python3
"""
Pelicans vs Nets Game Analysis
Spread: Pelicans +3.5 (Brooklyn -3.5)
Total: 227

Simulating 10,000 games to find betting edges
"""

from nba_simulator import NBASimulator, TeamStats, KellyBetting


def main():
    print("=" * 80)
    print("NBA GAME ANALYSIS: NEW ORLEANS PELICANS vs BROOKLYN NETS")
    print("=" * 80)
    print()
    print("Market Information:")
    print("  Spread: Pelicans +3.5 (Brooklyn -3.5)")
    print("  Total: 227 points")
    print()
    print("Running 10,000 game simulations...")
    print()
    
    # Create team stats based on 2024-25 season data
    # Brooklyn Nets (home team - since they're favored by 3.5)
    brooklyn = TeamStats(
        name="Brooklyn Nets",
        offensive_rating=114.2,
        defensive_rating=115.8,
        pace=98.5,
        efg_pct=0.548,
        tov_pct=13.8,
        orb_pct=23.5,
        ft_rate=0.228
    )
    
    # New Orleans Pelicans (away team - underdogs +3.5)
    pelicans = TeamStats(
        name="New Orleans Pelicans",
        offensive_rating=112.8,
        defensive_rating=114.5,
        pace=100.2,
        efg_pct=0.542,
        tov_pct=14.2,
        orb_pct=24.8,
        ft_rate=0.235
    )
    
    # Initialize simulator
    simulator = NBASimulator(home_court_advantage=3.5)
    
    # Run 10,000 simulations
    results = simulator.simulate_multiple_games(brooklyn, pelicans, 10000)
    
    print("-" * 80)
    print("SIMULATION RESULTS")
    print("-" * 80)
    print(f"Brooklyn (Home) Win %:   {results['home_win_pct']:.1%}")
    print(f"Pelicans (Away) Win %:   {(1-results['home_win_pct']):.1%}")
    print()
    print(f"Average Brooklyn Score:  {results['avg_home_score']:.1f}")
    print(f"Average Pelicans Score:  {results['avg_away_score']:.1f}")
    print(f"Average Total:           {results['avg_home_score'] + results['avg_away_score']:.1f}")
    print()
    print(f"Average Margin:          Brooklyn {results['avg_margin']:+.1f}")
    print(f"Median Margin:           Brooklyn {results['median_margin']:+.1f}")
    print(f"Margin Std Dev:          {results['margin_stdev']:.1f}")
    print()
    
    # Calculate team stats
    print("-" * 80)
    print("TEAM ANALYTICS")
    print("-" * 80)
    print(f"Brooklyn Net Rating:     {brooklyn.net_rating():+.1f}")
    print(f"Pelicans Net Rating:     {pelicans.net_rating():+.1f}")
    print(f"Net Rating Differential: {brooklyn.net_rating() - pelicans.net_rating():+.1f}")
    print()
    
    # Spread Analysis
    print("=" * 80)
    print("SPREAD BETTING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Market Spread: Pelicans +3.5 / Brooklyn -3.5")
    print(f"Model Spread:  Brooklyn {results['avg_margin']:+.1f}")
    print()
    
    # Calculate Against The Spread (ATS) results
    spread = 3.5
    pelicans_covers = 0  # Pelicans cover if they lose by less than 3.5 or win
    brooklyn_covers = 0  # Brooklyn covers if they win by more than 3.5
    
    # Run detailed simulations for spread analysis
    for i in range(10000):
        game = simulator.simulate_game(brooklyn, pelicans, seed=i)
        margin = game.margin  # positive = Brooklyn wins
        
        # Pelicans +3.5 means they cover if margin < 3.5
        if margin < spread:
            pelicans_covers += 1
        else:
            brooklyn_covers += 1
    
    pelicans_cover_pct = pelicans_covers / 10000
    brooklyn_cover_pct = brooklyn_covers / 10000
    
    print(f"Pelicans +3.5 Covers:    {pelicans_cover_pct:.1%} ({pelicans_covers:,} / 10,000 games)")
    print(f"Brooklyn -3.5 Covers:    {brooklyn_cover_pct:.1%} ({brooklyn_covers:,} / 10,000 games)")
    print()
    
    # Standard spread odds are -110 on both sides (1.909 decimal)
    spread_odds = 1.909
    spread_implied = 1 / spread_odds  # ~52.4%
    
    print(f"Market Implied (each side): {spread_implied:.1%} (odds: {spread_odds:.3f})")
    print()
    
    # Kelly betting for spread
    if pelicans_cover_pct > spread_implied:
        kelly_pelicans = KellyBetting.calculate_kelly_fraction(pelicans_cover_pct, spread_odds, 0.25)
        ev_pelicans = KellyBetting.expected_value(pelicans_cover_pct, spread_odds, 100)
        
        print("✓ PELICANS +3.5 BET RECOMMENDED")
        print(f"  Model Probability:     {pelicans_cover_pct:.1%}")
        print(f"  Edge:                  {(pelicans_cover_pct - spread_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_pelicans:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_pelicans:+.2f} per $100")
    else:
        print("✗ No edge on Pelicans +3.5")
        print(f"  Model: {pelicans_cover_pct:.1%} vs Market: {spread_implied:.1%}")
    
    print()
    
    if brooklyn_cover_pct > spread_implied:
        kelly_brooklyn = KellyBetting.calculate_kelly_fraction(brooklyn_cover_pct, spread_odds, 0.25)
        ev_brooklyn = KellyBetting.expected_value(brooklyn_cover_pct, spread_odds, 100)
        
        print("✓ BROOKLYN -3.5 BET RECOMMENDED")
        print(f"  Model Probability:     {brooklyn_cover_pct:.1%}")
        print(f"  Edge:                  {(brooklyn_cover_pct - spread_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_brooklyn:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_brooklyn:+.2f} per $100")
    else:
        print("✗ No edge on Brooklyn -3.5")
        print(f"  Model: {brooklyn_cover_pct:.1%} vs Market: {spread_implied:.1%}")
    
    print()
    
    # Total (Over/Under) Analysis
    print("=" * 80)
    print("TOTAL (OVER/UNDER) BETTING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Market Total: 227 points")
    print(f"Model Total:  {results['avg_home_score'] + results['avg_away_score']:.1f} points")
    print()
    
    # Calculate Over/Under results
    total_line = 227
    over_count = 0
    under_count = 0
    
    for i in range(10000):
        game = simulator.simulate_game(brooklyn, pelicans, seed=i+10000)
        total_points = game.home_score + game.away_score
        
        if total_points > total_line:
            over_count += 1
        elif total_points < total_line:
            under_count += 1
        # Pushes (exactly 227) don't count
    
    over_pct = over_count / 10000
    under_pct = under_count / 10000
    push_pct = 1 - over_pct - under_pct
    
    print(f"Over 227 hits:           {over_pct:.1%} ({over_count:,} / 10,000 games)")
    print(f"Under 227 hits:          {under_pct:.1%} ({under_count:,} / 10,000 games)")
    print(f"Push (exactly 227):      {push_pct:.1%}")
    print()
    
    # Standard total odds are -110 on both sides
    total_odds = 1.909
    total_implied = 1 / total_odds  # ~52.4%
    
    print(f"Market Implied (each side): {total_implied:.1%} (odds: {total_odds:.3f})")
    print()
    
    # Kelly betting for total
    if over_pct > total_implied:
        kelly_over = KellyBetting.calculate_kelly_fraction(over_pct, total_odds, 0.25)
        ev_over = KellyBetting.expected_value(over_pct, total_odds, 100)
        
        print("✓ OVER 227 BET RECOMMENDED")
        print(f"  Model Probability:     {over_pct:.1%}")
        print(f"  Edge:                  {(over_pct - total_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_over:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_over:+.2f} per $100")
    else:
        print("✗ No edge on Over 227")
        print(f"  Model: {over_pct:.1%} vs Market: {total_implied:.1%}")
    
    print()
    
    if under_pct > total_implied:
        kelly_under = KellyBetting.calculate_kelly_fraction(under_pct, total_odds, 0.25)
        ev_under = KellyBetting.expected_value(under_pct, total_odds, 100)
        
        print("✓ UNDER 227 BET RECOMMENDED")
        print(f"  Model Probability:     {under_pct:.1%}")
        print(f"  Edge:                  {(under_pct - total_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_under:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_under:+.2f} per $100")
    else:
        print("✗ No edge on Under 227")
        print(f"  Model: {under_pct:.1%} vs Market: {total_implied:.1%}")
    
    print()
    
    # Moneyline Analysis
    print("=" * 80)
    print("MONEYLINE BETTING ANALYSIS")
    print("=" * 80)
    print()
    
    # Estimate moneyline odds from spread
    # Brooklyn -3.5 suggests around -160 to -180 favorite
    # Pelicans +3.5 suggests around +140 to +160 underdog
    brooklyn_ml_odds = 1.556  # -180 American = 1.556 decimal
    pelicans_ml_odds = 2.60   # +160 American = 2.60 decimal
    
    print(f"Estimated Market Odds:")
    print(f"  Brooklyn ML: {brooklyn_ml_odds:.3f} (Implied: {1/brooklyn_ml_odds:.1%})")
    print(f"  Pelicans ML: {pelicans_ml_odds:.3f} (Implied: {1/pelicans_ml_odds:.1%})")
    print()
    
    print(f"Model Win Probabilities:")
    print(f"  Brooklyn:    {results['home_win_pct']:.1%}")
    print(f"  Pelicans:    {(1-results['home_win_pct']):.1%}")
    print()
    
    # Brooklyn ML
    if results['home_win_pct'] > 1/brooklyn_ml_odds:
        kelly_brooklyn_ml = KellyBetting.calculate_kelly_fraction(results['home_win_pct'], brooklyn_ml_odds, 0.25)
        ev_brooklyn_ml = KellyBetting.expected_value(results['home_win_pct'], brooklyn_ml_odds, 100)
        
        print("✓ BROOKLYN ML BET RECOMMENDED")
        print(f"  Edge:                  {(results['home_win_pct'] - 1/brooklyn_ml_odds):.1%}")
        print(f"  Kelly Bet Size:        {kelly_brooklyn_ml:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_brooklyn_ml:+.2f} per $100")
    else:
        print("✗ No edge on Brooklyn ML")
        print(f"  Model: {results['home_win_pct']:.1%} vs Market: {1/brooklyn_ml_odds:.1%}")
    
    print()
    
    # Pelicans ML
    pelicans_win_pct = 1 - results['home_win_pct']
    if pelicans_win_pct > 1/pelicans_ml_odds:
        kelly_pelicans_ml = KellyBetting.calculate_kelly_fraction(pelicans_win_pct, pelicans_ml_odds, 0.25)
        ev_pelicans_ml = KellyBetting.expected_value(pelicans_win_pct, pelicans_ml_odds, 100)
        
        print("✓ PELICANS ML BET RECOMMENDED")
        print(f"  Edge:                  {(pelicans_win_pct - 1/pelicans_ml_odds):.1%}")
        print(f"  Kelly Bet Size:        {kelly_pelicans_ml:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_pelicans_ml:+.2f} per $100")
    else:
        print("✗ No edge on Pelicans ML")
        print(f"  Model: {pelicans_win_pct:.1%} vs Market: {1/pelicans_ml_odds:.1%}")
    
    print()
    print("=" * 80)
    print("BETTING SUMMARY")
    print("=" * 80)
    print()
    print("Based on 10,000 game simulations using advanced analytics,")
    print("the model identifies betting opportunities where the edge")
    print("exceeds the market's implied probability.")
    print()
    print("Remember:")
    print("- These are model estimates based on season statistics")
    print("- Injuries, rest, and other factors may affect actual game")
    print("- Always bet responsibly and within your means")
    print("- Use fractional Kelly (quarter-Kelly shown) to reduce variance")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
