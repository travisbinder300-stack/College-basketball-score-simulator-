#!/usr/bin/env python3
"""
Milwaukee Bucks at Detroit Pistons Game Analysis
Spread: Milwaukee +12 (Detroit -12)
Total: 224.5

Simulating 10,000 games to find betting edges
"""

from nba_simulator import NBASimulator, TeamStats, KellyBetting


def main():
    print("=" * 80)
    print("NBA GAME ANALYSIS: MILWAUKEE BUCKS @ DETROIT PISTONS")
    print("=" * 80)
    print()
    print("Market Information:")
    print("  Spread: Milwaukee +12 (Detroit -12)")
    print("  Total: 224.5 points")
    print()
    print("Running 10,000 game simulations...")
    print()
    
    # Create team stats based on 2024-25 season data
    # Detroit Pistons (home team - favored by 12)
    detroit = TeamStats(
        name="Detroit Pistons",
        offensive_rating=108.5,
        defensive_rating=117.2,
        pace=97.8,
        efg_pct=0.525,
        tov_pct=15.2,
        orb_pct=22.1,
        ft_rate=0.218
    )
    
    # Milwaukee Bucks (away team - underdogs +12)
    milwaukee = TeamStats(
        name="Milwaukee Bucks",
        offensive_rating=119.8,
        defensive_rating=112.5,
        pace=99.2,
        efg_pct=0.578,
        tov_pct=12.8,
        orb_pct=25.3,
        ft_rate=0.248
    )
    
    # Initialize simulator
    simulator = NBASimulator(home_court_advantage=3.5)
    
    # Run 10,000 simulations
    results = simulator.simulate_multiple_games(detroit, milwaukee, 10000)
    
    print("-" * 80)
    print("SIMULATION RESULTS")
    print("-" * 80)
    print(f"Detroit (Home) Win %:    {results['home_win_pct']:.1%}")
    print(f"Milwaukee (Away) Win %:  {(1-results['home_win_pct']):.1%}")
    print()
    print(f"Average Detroit Score:   {results['avg_home_score']:.1f}")
    print(f"Average Milwaukee Score: {results['avg_away_score']:.1f}")
    print(f"Average Total:           {results['avg_home_score'] + results['avg_away_score']:.1f}")
    print()
    print(f"Average Margin:          Detroit {results['avg_margin']:+.1f}")
    print(f"Median Margin:           Detroit {results['median_margin']:+.1f}")
    print(f"Margin Std Dev:          {results['margin_stdev']:.1f}")
    print()
    
    # Calculate team stats
    print("-" * 80)
    print("TEAM ANALYTICS")
    print("-" * 80)
    print(f"Detroit Net Rating:      {detroit.net_rating():+.1f}")
    print(f"Milwaukee Net Rating:    {milwaukee.net_rating():+.1f}")
    print(f"Net Rating Differential: {detroit.net_rating() - milwaukee.net_rating():+.1f}")
    print()
    
    # Spread Analysis
    print("=" * 80)
    print("SPREAD BETTING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Market Spread: Milwaukee +12 / Detroit -12")
    print(f"Model Spread:  Detroit {results['avg_margin']:+.1f}")
    print()
    
    # Calculate Against The Spread (ATS) results
    spread = 12.0
    milwaukee_covers = 0  # Milwaukee covers if they lose by less than 12 or win
    detroit_covers = 0  # Detroit covers if they win by more than 12
    
    # Run detailed simulations for spread analysis
    for i in range(10000):
        game = simulator.simulate_game(detroit, milwaukee, seed=i)
        margin = game.margin  # positive = Detroit wins
        
        # Milwaukee +12 means they cover if margin < 12
        if margin < spread:
            milwaukee_covers += 1
        else:
            detroit_covers += 1
    
    milwaukee_cover_pct = milwaukee_covers / 10000
    detroit_cover_pct = detroit_covers / 10000
    
    print(f"Milwaukee +12 Covers:    {milwaukee_cover_pct:.1%} ({milwaukee_covers:,} / 10,000 games)")
    print(f"Detroit -12 Covers:      {detroit_cover_pct:.1%} ({detroit_covers:,} / 10,000 games)")
    print()
    
    # Standard spread odds are -110 on both sides (1.909 decimal)
    spread_odds = 1.909
    spread_implied = 1 / spread_odds  # ~52.4%
    
    print(f"Market Implied (each side): {spread_implied:.1%} (odds: {spread_odds:.3f})")
    print()
    
    # Kelly betting for spread
    if milwaukee_cover_pct > spread_implied:
        kelly_milwaukee = KellyBetting.calculate_kelly_fraction(milwaukee_cover_pct, spread_odds, 0.25)
        ev_milwaukee = KellyBetting.expected_value(milwaukee_cover_pct, spread_odds, 100)
        
        print("✓ MILWAUKEE +12 BET RECOMMENDED")
        print(f"  Model Probability:     {milwaukee_cover_pct:.1%}")
        print(f"  Edge:                  {(milwaukee_cover_pct - spread_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_milwaukee:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_milwaukee:+.2f} per $100")
    else:
        print("✗ No edge on Milwaukee +12")
        print(f"  Model: {milwaukee_cover_pct:.1%} vs Market: {spread_implied:.1%}")
    
    print()
    
    if detroit_cover_pct > spread_implied:
        kelly_detroit = KellyBetting.calculate_kelly_fraction(detroit_cover_pct, spread_odds, 0.25)
        ev_detroit = KellyBetting.expected_value(detroit_cover_pct, spread_odds, 100)
        
        print("✓ DETROIT -12 BET RECOMMENDED")
        print(f"  Model Probability:     {detroit_cover_pct:.1%}")
        print(f"  Edge:                  {(detroit_cover_pct - spread_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_detroit:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_detroit:+.2f} per $100")
    else:
        print("✗ No edge on Detroit -12")
        print(f"  Model: {detroit_cover_pct:.1%} vs Market: {spread_implied:.1%}")
    
    print()
    
    # Total (Over/Under) Analysis
    print("=" * 80)
    print("TOTAL (OVER/UNDER) BETTING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Market Total: 224.5 points")
    print(f"Model Total:  {results['avg_home_score'] + results['avg_away_score']:.1f} points")
    print()
    
    # Calculate Over/Under results
    total_line = 224.5
    over_count = 0
    under_count = 0
    
    for i in range(10000):
        game = simulator.simulate_game(detroit, milwaukee, seed=i+10000)
        total_points = game.home_score + game.away_score
        
        if total_points > total_line:
            over_count += 1
        elif total_points < total_line:
            under_count += 1
        # Pushes (exactly 224.5) won't happen with .5 line
    
    over_pct = over_count / 10000
    under_pct = under_count / 10000
    
    print(f"Over 224.5 hits:         {over_pct:.1%} ({over_count:,} / 10,000 games)")
    print(f"Under 224.5 hits:        {under_pct:.1%} ({under_count:,} / 10,000 games)")
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
        
        print("✓ OVER 224.5 BET RECOMMENDED")
        print(f"  Model Probability:     {over_pct:.1%}")
        print(f"  Edge:                  {(over_pct - total_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_over:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_over:+.2f} per $100")
    else:
        print("✗ No edge on Over 224.5")
        print(f"  Model: {over_pct:.1%} vs Market: {total_implied:.1%}")
    
    print()
    
    if under_pct > total_implied:
        kelly_under = KellyBetting.calculate_kelly_fraction(under_pct, total_odds, 0.25)
        ev_under = KellyBetting.expected_value(under_pct, total_odds, 100)
        
        print("✓ UNDER 224.5 BET RECOMMENDED")
        print(f"  Model Probability:     {under_pct:.1%}")
        print(f"  Edge:                  {(under_pct - total_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_under:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_under:+.2f} per $100")
    else:
        print("✗ No edge on Under 224.5")
        print(f"  Model: {under_pct:.1%} vs Market: {total_implied:.1%}")
    
    print()
    
    # Moneyline Analysis
    print("=" * 80)
    print("MONEYLINE BETTING ANALYSIS")
    print("=" * 80)
    print()
    
    # Estimate moneyline odds from spread
    # Detroit -12 suggests around -600 to -700 favorite
    # Milwaukee +12 suggests around +450 to +550 underdog
    detroit_ml_odds = 1.143  # -700 American = 1.143 decimal
    milwaukee_ml_odds = 5.50   # +450 American = 5.50 decimal
    
    print(f"Estimated Market Odds:")
    print(f"  Detroit ML:    {detroit_ml_odds:.3f} (Implied: {1/detroit_ml_odds:.1%})")
    print(f"  Milwaukee ML:  {milwaukee_ml_odds:.3f} (Implied: {1/milwaukee_ml_odds:.1%})")
    print()
    
    print(f"Model Win Probabilities:")
    print(f"  Detroit:       {results['home_win_pct']:.1%}")
    print(f"  Milwaukee:     {(1-results['home_win_pct']):.1%}")
    print()
    
    # Detroit ML
    if results['home_win_pct'] > 1/detroit_ml_odds:
        kelly_detroit_ml = KellyBetting.calculate_kelly_fraction(results['home_win_pct'], detroit_ml_odds, 0.25)
        ev_detroit_ml = KellyBetting.expected_value(results['home_win_pct'], detroit_ml_odds, 100)
        
        print("✓ DETROIT ML BET RECOMMENDED")
        print(f"  Edge:                  {(results['home_win_pct'] - 1/detroit_ml_odds):.1%}")
        print(f"  Kelly Bet Size:        {kelly_detroit_ml:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_detroit_ml:+.2f} per $100")
    else:
        print("✗ No edge on Detroit ML")
        print(f"  Model: {results['home_win_pct']:.1%} vs Market: {1/detroit_ml_odds:.1%}")
    
    print()
    
    # Milwaukee ML
    milwaukee_win_pct = 1 - results['home_win_pct']
    if milwaukee_win_pct > 1/milwaukee_ml_odds:
        kelly_milwaukee_ml = KellyBetting.calculate_kelly_fraction(milwaukee_win_pct, milwaukee_ml_odds, 0.25)
        ev_milwaukee_ml = KellyBetting.expected_value(milwaukee_win_pct, milwaukee_ml_odds, 100)
        
        print("✓ MILWAUKEE ML BET RECOMMENDED")
        print(f"  Edge:                  {(milwaukee_win_pct - 1/milwaukee_ml_odds):.1%}")
        print(f"  Kelly Bet Size:        {kelly_milwaukee_ml:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_milwaukee_ml:+.2f} per $100")
    else:
        print("✗ No edge on Milwaukee ML")
        print(f"  Model: {milwaukee_win_pct:.1%} vs Market: {1/milwaukee_ml_odds:.1%}")
    
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
