"""
Weber State vs St. Thomas MN Simulation
Betting Lines: Weber State +7.5, St. Thomas MN -7.5, Total 154
 
This simulation analyzes the Weber State vs St. Thomas MN matchup with real betting lines.
"""

from basketball_simulator import GameSimulator, TeamStats, KellyCriterion


def create_weber_state_vs_st_thomas_mn():
    """
    Create Weber State and St. Thomas MN teams with realistic 2024-25 statistics
    """
    
    # St. Thomas MN Tommies - Strong mid-major transitioning to D1
    st_thomas_mn = TeamStats(
        name="St. Thomas MN Tommies",
        offensive_efficiency=108.5,    # Good offense for mid-major
        defensive_efficiency=100.8,    # Solid defense
        pace=70.5,                     # Moderate pace
        three_point_rate=0.38,         # 38% of shots are 3PT
        three_point_percentage=0.35,   # 35% from three
        two_point_percentage=0.52,     # 52% from two
        free_throw_rate=0.35,          # Good free throw rate
        free_throw_percentage=0.73,    # 73% FT shooting
        turnover_rate=0.15,            # 15% turnover rate
        offensive_rebound_rate=0.30,   # 30% offensive rebound rate
        performance_variance=0.06      # 6% variance
    )
    
    # Weber State Wildcats - Competitive Big Sky team
    weber_state = TeamStats(
        name="Weber State Wildcats",
        offensive_efficiency=106.2,    # Solid mid-major offense
        defensive_efficiency=103.5,    # Average defense
        pace=69.8,                     # Moderate pace
        three_point_rate=0.40,         # 40% of shots are 3PT
        three_point_percentage=0.34,   # 34% from three
        two_point_percentage=0.50,     # 50% from two
        free_throw_rate=0.33,          # Average free throw rate
        free_throw_percentage=0.72,    # 72% FT shooting
        turnover_rate=0.16,            # 16% turnover rate
        offensive_rebound_rate=0.28,   # 28% offensive rebound rate
        performance_variance=0.07      # 7% variance
    )
    
    return st_thomas_mn, weber_state


def main():
    print("=" * 80)
    print("WEBER STATE WILDCATS vs ST. THOMAS MN TOMMIES")
    print("College Basketball Simulation - 10,000 Monte Carlo Iterations")
    print("=" * 80)
    print()
    
    # Create teams
    st_thomas_mn, weber_state = create_weber_state_vs_st_thomas_mn()
    
    # Run simulation
    simulator = GameSimulator(st_thomas_mn, weber_state)
    results = simulator.run_simulation(num_simulations=10000)
    
    # Display results
    print(f"\n{results['team1_name']} vs {results['team2_name']}")
    print(f"Expected Score: {results['team1_name']} {results['team1_avg_score']:.1f} - "
          f"{results['team2_name']} {results['team2_avg_score']:.1f}")
    print(f"Expected Margin: {results['team1_name']} by {results['avg_margin']:.1f} points")
    print()
    print(f"Win Probabilities:")
    print(f"  {results['team1_name']}: {results['team1_win_pct']:.1f}%")
    print(f"  {results['team2_name']}: {results['team2_win_pct']:.1f}%")
    print()
    
    print("=" * 80)
    print("BETTING LINE ANALYSIS")
    print("=" * 80)
    
    # Spread: St. Thomas MN -7.5, Weber State +7.5
    spread = 7.5
    margins = [s1 - s2 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores'])]
    st_thomas_covers = sum(1 for m in margins if m > spread) / len(margins) * 100
    weber_covers = sum(1 for m in margins if m <= spread) / len(margins) * 100
    
    print(f"\n--- SPREAD ANALYSIS (St. Thomas MN -{spread} / Weber State +{spread}) ---")
    print(f"St. Thomas MN covers -{spread}: {st_thomas_covers:.1f}% of simulations")
    print(f"Weber State covers +{spread}: {weber_covers:.1f}% of simulations")
    print(f"Expected Margin: St. Thomas MN by {results['avg_margin']:.1f} points")
    print()
    
    # Determine if we should suppress favorite recommendation
    suppress_favorite = weber_covers >= 70.0 and st_thomas_covers < 60.0
    
    # Kelly Criterion for St. Thomas MN -7.5 (favorite)
    if not suppress_favorite:
        st_thomas_spread_prob = st_thomas_covers / 100
        st_thomas_spread_odds = -110  # Standard spread odds
        print(f"St. Thomas MN -{spread} ({st_thomas_spread_odds}):")
        spread_results_fav = {
            'team1_name': f'St. Thomas MN -{spread}',
            'team2_name': f'Weber State +{spread}',
            'team1_win_pct': st_thomas_covers,
            'team2_win_pct': weber_covers,
            'num_simulations': results['num_simulations']
        }
        KellyCriterion.analyze_betting_opportunity(
            spread_results_fav,
            team=1,
            american_odds=st_thomas_spread_odds
        )
    
    # Kelly Criterion for Weber State +7.5 (underdog)
    weber_spread_prob = weber_covers / 100
    weber_spread_odds = -110  # Standard spread odds
    print(f"Weber State +{spread} ({weber_spread_odds}):")
    spread_results_dog = {
        'team1_name': f'Weber State +{spread}',
        'team2_name': f'St. Thomas MN -{spread}',
        'team1_win_pct': weber_covers,
        'team2_win_pct': st_thomas_covers,
        'num_simulations': results['num_simulations']
    }
    KellyCriterion.analyze_betting_opportunity(
        spread_results_dog,
        team=1,
        american_odds=weber_spread_odds
    )
    
    if suppress_favorite:
        print("\n*** STRONG UNDERDOG VALUE - Favorite recommendation suppressed ***")
    
    # Total: 154
    total_line = 154.0
    total_scores = [s1 + s2 for s1, s2 in zip(results['all_team1_scores'], results['all_team2_scores'])]
    over_pct = sum(1 for total in total_scores if total > total_line) / len(total_scores) * 100
    under_pct = sum(1 for total in total_scores if total <= total_line) / len(total_scores) * 100
    avg_total = sum(total_scores) / len(total_scores)
    
    print(f"\n--- TOTAL ANALYSIS (O/U {total_line}) ---")
    print(f"Over {total_line}: {over_pct:.1f}% of simulations")
    print(f"Under {total_line}: {under_pct:.1f}% of simulations")
    print(f"Expected Total: {avg_total:.1f} points ({avg_total - total_line:+.1f} vs line)")
    print()
    
    # Kelly Criterion for Over
    over_prob = over_pct / 100
    over_odds = -110
    print(f"Over {total_line} ({over_odds}):")
    total_results_over = {
        'team1_name': f'Over {total_line}',
        'team2_name': f'Under {total_line}',
        'team1_win_pct': over_pct,
        'team2_win_pct': under_pct,
        'num_simulations': results['num_simulations']
    }
    KellyCriterion.analyze_betting_opportunity(
        total_results_over,
        team=1,
        american_odds=over_odds
    )
    
    # Kelly Criterion for Under
    under_prob = under_pct / 100
    under_odds = -110
    print(f"Under {total_line} ({under_odds}):")
    total_results_under = {
        'team1_name': f'Under {total_line}',
        'team2_name': f'Over {total_line}',
        'team1_win_pct': under_pct,
        'team2_win_pct': over_pct,
        'num_simulations': results['num_simulations']
    }
    KellyCriterion.analyze_betting_opportunity(
        total_results_under,
        team=1,
        american_odds=under_odds
    )
    
    # Moneyline Analysis
    print(f"\n--- MONEYLINE ANALYSIS ---")
    print(f"St. Thomas MN: {results['team1_win_pct']:.1f}% win probability")
    
    # Estimate moneyline odds based on win probability
    st_thomas_ml_odds = -350  # Strong favorite
    weber_ml_odds = +275      # Underdog
    
    print(f"Weber State: {results['team2_win_pct']:.1f}% win probability")
    print()
    
    print(f"St. Thomas MN (Estimated: {st_thomas_ml_odds}):")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=1,
        american_odds=st_thomas_ml_odds
    )
    
    print(f"Weber State (Estimated: {weber_ml_odds}):")
    KellyCriterion.analyze_betting_opportunity(
        results,
        team=2,
        american_odds=weber_ml_odds
    )
    
    print("\n" + "=" * 80)
    print("SUMMARY OF BEST BETTING OPPORTUNITIES")
    print("=" * 80)
    
    # Collect all opportunities with positive edge
    opportunities = []
    
    # Check each betting option
    if weber_spread_prob * 1.9091 > 1:  # -110 odds = 1.9091 decimal
        edge = (weber_spread_prob * 1.9091 - 1) * 100
        opportunities.append((f"Weber State +{spread}", edge, weber_spread_prob * 100))
    
    if not suppress_favorite and st_thomas_spread_prob * 1.9091 > 1:
        edge = (st_thomas_spread_prob * 1.9091 - 1) * 100
        opportunities.append((f"St. Thomas MN -{spread}", edge, st_thomas_spread_prob * 100))
    
    if over_prob * 1.9091 > 1:
        edge = (over_prob * 1.9091 - 1) * 100
        opportunities.append((f"Over {total_line}", edge, over_prob * 100))
    
    if under_prob * 1.9091 > 1:
        edge = (under_prob * 1.9091 - 1) * 100
        opportunities.append((f"Under {total_line}", edge, under_prob * 100))
    
    # Check moneyline
    weber_ml_prob = results['team2_win_pct'] / 100
    weber_ml_decimal = KellyCriterion.american_to_decimal(weber_ml_odds)
    if weber_ml_prob * weber_ml_decimal > 1:
        edge = (weber_ml_prob * weber_ml_decimal - 1) * 100
        opportunities.append((f"Weber State ML {weber_ml_odds}", edge, results['team2_win_pct']))
    
    st_thomas_ml_prob = results['team1_win_pct'] / 100
    st_thomas_ml_decimal = KellyCriterion.american_to_decimal(st_thomas_ml_odds)
    if st_thomas_ml_prob * st_thomas_ml_decimal > 1:
        edge = (st_thomas_ml_prob * st_thomas_ml_decimal - 1) * 100
        opportunities.append((f"St. Thomas MN ML {st_thomas_ml_odds}", edge, results['team1_win_pct']))
    
    if opportunities:
        opportunities.sort(key=lambda x: x[1], reverse=True)
        print()
        for i, (bet, edge, prob) in enumerate(opportunities, 1):
            print(f"{i}. {bet} - Edge: {edge:+.2f}% (Simulation: {prob:.1f}%)")
    else:
        print("\nNo betting opportunities with positive expected value found.")
    
    print("\n" + "=" * 80)
    print("Responsible Gambling Reminder:")
    print("These are simulations for educational purposes.")
    print("Past performance and simulations do not guarantee future results.")
    print("=" * 80)


if __name__ == "__main__":
    main()
