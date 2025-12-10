#!/usr/bin/env python3
"""
Villanova vs UConn - Big East Offensive Battle
High-scoring conference matchup
"""

from basketball_simulator import GameSimulator, TeamStats

# Villanova Wildcats - Strong offense, uptempo
villanova = TeamStats(
    name="Villanova Wildcats",
    offensive_efficiency=121.5,
    defensive_efficiency=99.2,
    pace=73.8,  # Uptempo
    three_point_rate=0.46,  # Love the three
    three_point_percentage=0.395,
    two_point_percentage=0.572,
    free_throw_rate=0.30,
    free_throw_percentage=0.802,
    offensive_rebound_rate=0.28,
    turnover_rate=0.13,
    and_one_rate=0.07
)

# UConn Huskies - Balanced, strong offense
uconn = TeamStats(
    name="UConn Huskies",
    offensive_efficiency=120.2,
    defensive_efficiency=98.8,
    pace=73.2,  # Uptempo
    three_point_rate=0.40,
    three_point_percentage=0.378,
    two_point_percentage=0.580,
    free_throw_rate=0.33,
    free_throw_percentage=0.758,
    offensive_rebound_rate=0.31,
    turnover_rate=0.14,
    and_one_rate=0.08
)

# Run simulation
simulator = GameSimulator(villanova, uconn)
results = simulator.run_simulation(num_simulations=10000)

# Print results
simulator.print_results(results)

# Betting line analysis
print("\n" + "="*80)
print("BETTING LINE ANALYSIS")
print("="*80)

# Spread: Villanova -2.5
spread = 2.5
villanova_covers = sum(1 for m in results['margins'] if m > spread)
uconn_covers = sum(1 for m in results['margins'] if m < -spread)
villanova_cover_pct = (villanova_covers / len(results['margins'])) * 100
uconn_cover_pct = (uconn_covers / len(results['margins'])) * 100

print(f"\n📊 SPREAD ANALYSIS (Villanova -{spread} / UConn +{spread}):")
print(f"   Villanova covers -{spread}: {villanova_cover_pct:.1f}% of simulations")
print(f"   UConn covers +{spread}: {uconn_cover_pct:.1f}% of simulations")

# Analyze Villanova -2.5
from basketball_simulator import KellyCriterion
spread_prob_villanova = villanova_cover_pct / 100
spread_prob_uconn = uconn_cover_pct / 100

print(f"\n   Villanova -{spread} (-110 odds):")
kelly_villanova = KellyCriterion.calculate_kelly(spread_prob_villanova, american_odds=-110)
if kelly_villanova > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_villanova)
    edge = ((1.909 * spread_prob_villanova) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_villanova*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_villanova*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

print(f"\n   UConn +{spread} (-110 odds):")
kelly_uconn = KellyCriterion.calculate_kelly(spread_prob_uconn, american_odds=-110)
if kelly_uconn > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_uconn)
    edge = ((1.909 * spread_prob_uconn) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_uconn*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_uconn*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

# Total: 155.5
total_line = 155.5
over_count = sum(1 for t in results['total_scores'] if t > total_line)
under_count = sum(1 for t in results['total_scores'] if t < total_line)
over_pct = (over_count / len(results['total_scores'])) * 100
under_pct = (under_count / len(results['total_scores'])) * 100

print(f"\n📊 TOTAL ANALYSIS (O/U {total_line}):")
print(f"   Over {total_line}: {over_pct:.1f}% of simulations")
print(f"   Under {total_line}: {under_pct:.1f}% of simulations")
print(f"   Expected total: {results['avg_total']:.1f} points")

# Analyze Over
over_prob = over_pct / 100
print(f"\n   Over {total_line} (-110 odds):")
kelly_over = KellyCriterion.calculate_kelly(over_prob, american_odds=-110)
if kelly_over > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_over)
    edge = ((1.909 * over_prob) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_over*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_over*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

# Analyze Under
under_prob = under_pct / 100
print(f"\n   Under {total_line} (-110 odds):")
kelly_under = KellyCriterion.calculate_kelly(under_prob, american_odds=-110)
if kelly_under > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_under)
    edge = ((1.909 * under_prob) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_under*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_under*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

print("\n" + "="*80)
print("⚠️  RESPONSIBLE GAMBLING REMINDER")
print("="*80)
print("This is a simulation for educational purposes. Past performance does not")
print("guarantee future results. Only bet what you can afford to lose.")
print("="*80)
