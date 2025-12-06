#!/usr/bin/env python3
"""
Atlanta Hawks vs Washington Wizards Game Analysis
Spread: Atlanta -9 (Washington +9)
Total: 235.5

Simulating 10,000 games to find betting edges
"""

from nba_simulator import NBASimulator, TeamStats, KellyBetting


def main():
    print("=" * 80)
    print("NBA GAME ANALYSIS: ATLANTA HAWKS vs WASHINGTON WIZARDS")
    print("=" * 80)
    print()
    print("Market Information:")
    print("  Spread: Atlanta -9 (Washington +9)")
    print("  Total: 235.5 points")
    print()
    print("Running 10,000 game simulations...")
    print()
    
    # Create team stats based on 2024-25 season data
    # Atlanta Hawks (home team - favored by 9)
    atlanta = TeamStats(
        name="Atlanta Hawks",
        offensive_rating=117.8,
        defensive_rating=118.2,
        pace=100.8,
        efg_pct=0.556,
        tov_pct=13.2,
        orb_pct=25.8,
        ft_rate=0.238
    )
    
    # Washington Wizards (away team - underdogs +9)
    washington = TeamStats(
        name="Washington Wizards",
        offensive_rating=109.2,
        defensive_rating=120.5,
        pace=99.8,
        efg_pct=0.528,
        tov_pct=15.8,
        orb_pct=22.5,
        ft_rate=0.225
    )
    
    # Initialize simulator
    simulator = NBASimulator(home_court_advantage=3.5)
    
    # Run 10,000 simulations
    results = simulator.simulate_multiple_games(atlanta, washington, 10000)
    
    print("-" * 80)
    print("SIMULATION RESULTS")
    print("-" * 80)
    print(f"Atlanta (Home) Win %:    {results['home_win_pct']:.1%}")
    print(f"Washington (Away) Win %: {(1-results['home_win_pct']):.1%}")
    print()
    print(f"Average Atlanta Score:   {results['avg_home_score']:.1f}")
    print(f"Average Washington Score:{results['avg_away_score']:.1f}")
    print(f"Average Total:           {results['avg_home_score'] + results['avg_away_score']:.1f}")
    print()
    print(f"Average Margin:          Atlanta {results['avg_margin']:+.1f}")
    print(f"Median Margin:           Atlanta {results['median_margin']:+.1f}")
    print(f"Margin Std Dev:          {results['margin_stdev']:.1f}")
    print()
    
    # Calculate team stats
    print("-" * 80)
    print("TEAM ANALYTICS")
    print("-" * 80)
    print(f"Atlanta Net Rating:      {atlanta.net_rating():+.1f}")
    print(f"Washington Net Rating:   {washington.net_rating():+.1f}")
    print(f"Net Rating Differential: {atlanta.net_rating() - washington.net_rating():+.1f}")
    print()
    
    # Spread Analysis
    print("=" * 80)
    print("SPREAD BETTING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Market Spread: Washington +9 / Atlanta -9")
    print(f"Model Spread:  Atlanta {results['avg_margin']:+.1f}")
    print()
    
    # Calculate Against The Spread (ATS) results
    spread = 9.0
    washington_covers = 0  # Washington covers if they lose by less than 9 or win
    atlanta_covers = 0  # Atlanta covers if they win by more than 9
    
    # Run detailed simulations for spread analysis
    for i in range(10000):
        game = simulator.simulate_game(atlanta, washington, seed=i)
        margin = game.margin  # positive = Atlanta wins
        
        # Washington +9 means they cover if margin < 9
        if margin < spread:
            washington_covers += 1
        else:
            atlanta_covers += 1
    
    washington_cover_pct = washington_covers / 10000
    atlanta_cover_pct = atlanta_covers / 10000
    
    print(f"Washington +9 Covers:    {washington_cover_pct:.1%} ({washington_covers:,} / 10,000 games)")
    print(f"Atlanta -9 Covers:       {atlanta_cover_pct:.1%} ({atlanta_covers:,} / 10,000 games)")
    print()
    
    # Standard spread odds are -110 on both sides (1.909 decimal)
    spread_odds = 1.909
    spread_implied = 1 / spread_odds  # ~52.4%
    
    print(f"Market Implied (each side): {spread_implied:.1%} (odds: {spread_odds:.3f})")
    print()
    
    # Kelly betting for spread
    if washington_cover_pct > spread_implied:
        kelly_washington = KellyBetting.calculate_kelly_fraction(washington_cover_pct, spread_odds, 0.25)
        ev_washington = KellyBetting.expected_value(washington_cover_pct, spread_odds, 100)
        
        print("✓ WASHINGTON +9 BET RECOMMENDED")
        print(f"  Model Probability:     {washington_cover_pct:.1%}")
        print(f"  Edge:                  {(washington_cover_pct - spread_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_washington:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_washington:+.2f} per $100")
    else:
        print("✗ No edge on Washington +9")
        print(f"  Model: {washington_cover_pct:.1%} vs Market: {spread_implied:.1%}")
    
    print()
    
    if atlanta_cover_pct > spread_implied:
        kelly_atlanta = KellyBetting.calculate_kelly_fraction(atlanta_cover_pct, spread_odds, 0.25)
        ev_atlanta = KellyBetting.expected_value(atlanta_cover_pct, spread_odds, 100)
        
        print("✓ ATLANTA -9 BET RECOMMENDED")
        print(f"  Model Probability:     {atlanta_cover_pct:.1%}")
        print(f"  Edge:                  {(atlanta_cover_pct - spread_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_atlanta:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_atlanta:+.2f} per $100")
    else:
        print("✗ No edge on Atlanta -9")
        print(f"  Model: {atlanta_cover_pct:.1%} vs Market: {spread_implied:.1%}")
    
    print()
    
    # Total (Over/Under) Analysis
    print("=" * 80)
    print("TOTAL (OVER/UNDER) BETTING ANALYSIS")
    print("=" * 80)
    print()
    print(f"Market Total: 235.5 points")
    print(f"Model Total:  {results['avg_home_score'] + results['avg_away_score']:.1f} points")
    print()
    
    # Calculate Over/Under results
    total_line = 235.5
    over_count = 0
    under_count = 0
    
    for i in range(10000):
        game = simulator.simulate_game(atlanta, washington, seed=i+10000)
        total_points = game.home_score + game.away_score
        
        if total_points > total_line:
            over_count += 1
        elif total_points < total_line:
            under_count += 1
        # Pushes (exactly 235.5) won't happen with .5 line
    
    over_pct = over_count / 10000
    under_pct = under_count / 10000
    
    print(f"Over 235.5 hits:         {over_pct:.1%} ({over_count:,} / 10,000 games)")
    print(f"Under 235.5 hits:        {under_pct:.1%} ({under_count:,} / 10,000 games)")
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
        
        print("✓ OVER 235.5 BET RECOMMENDED")
        print(f"  Model Probability:     {over_pct:.1%}")
        print(f"  Edge:                  {(over_pct - total_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_over:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_over:+.2f} per $100")
    else:
        print("✗ No edge on Over 235.5")
        print(f"  Model: {over_pct:.1%} vs Market: {total_implied:.1%}")
    
    print()
    
    if under_pct > total_implied:
        kelly_under = KellyBetting.calculate_kelly_fraction(under_pct, total_odds, 0.25)
        ev_under = KellyBetting.expected_value(under_pct, total_odds, 100)
        
        print("✓ UNDER 235.5 BET RECOMMENDED")
        print(f"  Model Probability:     {under_pct:.1%}")
        print(f"  Edge:                  {(under_pct - total_implied):.1%}")
        print(f"  Kelly Bet Size:        {kelly_under:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_under:+.2f} per $100")
    else:
        print("✗ No edge on Under 235.5")
        print(f"  Model: {under_pct:.1%} vs Market: {total_implied:.1%}")
    
    print()
    
    # Moneyline Analysis
    print("=" * 80)
    print("MONEYLINE BETTING ANALYSIS")
    print("=" * 80)
    print()
    
    # Estimate moneyline odds from spread
    # Atlanta -9 suggests around -400 to -450 favorite
    # Washington +9 suggests around +300 to +350 underdog
    atlanta_ml_odds = 1.222  # -450 American = 1.222 decimal
    washington_ml_odds = 4.00   # +300 American = 4.00 decimal
    
    print(f"Estimated Market Odds:")
    print(f"  Atlanta ML:    {atlanta_ml_odds:.3f} (Implied: {1/atlanta_ml_odds:.1%})")
    print(f"  Washington ML: {washington_ml_odds:.3f} (Implied: {1/washington_ml_odds:.1%})")
    print()
    
    print(f"Model Win Probabilities:")
    print(f"  Atlanta:       {results['home_win_pct']:.1%}")
    print(f"  Washington:    {(1-results['home_win_pct']):.1%}")
    print()
    
    # Atlanta ML
    if results['home_win_pct'] > 1/atlanta_ml_odds:
        kelly_atlanta_ml = KellyBetting.calculate_kelly_fraction(results['home_win_pct'], atlanta_ml_odds, 0.25)
        ev_atlanta_ml = KellyBetting.expected_value(results['home_win_pct'], atlanta_ml_odds, 100)
        
        print("✓ ATLANTA ML BET RECOMMENDED")
        print(f"  Edge:                  {(results['home_win_pct'] - 1/atlanta_ml_odds):.1%}")
        print(f"  Kelly Bet Size:        {kelly_atlanta_ml:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_atlanta_ml:+.2f} per $100")
    else:
        print("✗ No edge on Atlanta ML")
        print(f"  Model: {results['home_win_pct']:.1%} vs Market: {1/atlanta_ml_odds:.1%}")
    
    print()
    
    # Washington ML
    washington_win_pct = 1 - results['home_win_pct']
    if washington_win_pct > 1/washington_ml_odds:
        kelly_washington_ml = KellyBetting.calculate_kelly_fraction(washington_win_pct, washington_ml_odds, 0.25)
        ev_washington_ml = KellyBetting.expected_value(washington_win_pct, washington_ml_odds, 100)
        
        print("✓ WASHINGTON ML BET RECOMMENDED")
        print(f"  Edge:                  {(washington_win_pct - 1/washington_ml_odds):.1%}")
        print(f"  Kelly Bet Size:        {kelly_washington_ml:.2%} of bankroll")
        print(f"  Expected Value:        ${ev_washington_ml:+.2f} per $100")
    else:
        print("✗ No edge on Washington ML")
        print(f"  Model: {washington_win_pct:.1%} vs Market: {1/washington_ml_odds:.1%}")
    
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
