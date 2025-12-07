#!/usr/bin/env python3
"""
Gonzaga vs Baylor - High-Scoring Offensive Showdown
Two elite offensive teams with fast pace
"""

from basketball_simulator import GameSimulator, TeamStats

# Gonzaga Bulldogs - Elite offense, fast pace
gonzaga = TeamStats(
    name="Gonzaga Bulldogs",
    offensive_efficiency=125.8,  # Elite offense
    defensive_efficiency=96.5,
    pace=75.2,  # Fast pace
    three_point_rate=0.44,
    three_point_percentage=0.402,
    two_point_percentage=0.598,
    free_throw_rate=0.32,
    free_throw_percentage=0.782,
    offensive_rebound_rate=0.32,
    turnover_rate=0.14,
    and_one_rate=0.08
)

# Baylor Bears - Elite offense, fast pace
baylor = TeamStats(
    name="Baylor Bears",
    offensive_efficiency=123.4,  # Elite offense
    defensive_efficiency=97.8,
    pace=74.8,  # Fast pace
    three_point_rate=0.42,
    three_point_percentage=0.388,
    two_point_percentage=0.585,
    free_throw_rate=0.34,
    free_throw_percentage=0.765,
    offensive_rebound_rate=0.35,
    turnover_rate=0.15,
    and_one_rate=0.075
)

# Run simulation
simulator = GameSimulator(gonzaga, baylor)
results = simulator.run_simulation(num_simulations=10000)

# Print results
simulator.print_results(results)

# Betting line analysis
print("\n" + "="*80)
print("BETTING LINE ANALYSIS")
print("="*80)

# Spread: Gonzaga -3.5
spread = 3.5
gonzaga_covers = sum(1 for m in results['margins'] if m > spread)
baylor_covers = sum(1 for m in results['margins'] if m < -spread)
gonzaga_cover_pct = (gonzaga_covers / len(results['margins'])) * 100
baylor_cover_pct = (baylor_covers / len(results['margins'])) * 100

print(f"\n📊 SPREAD ANALYSIS (Gonzaga -{spread} / Baylor +{spread}):")
print(f"   Gonzaga covers -{spread}: {gonzaga_cover_pct:.1f}% of simulations")
print(f"   Baylor covers +{spread}: {baylor_cover_pct:.1f}% of simulations")

# Analyze Gonzaga -3.5
from basketball_simulator import KellyCriterion
spread_prob_gonzaga = gonzaga_cover_pct / 100
spread_prob_baylor = baylor_cover_pct / 100

print(f"\n   Gonzaga -{spread} (-110 odds):")
kelly_gonzaga = KellyCriterion.calculate_kelly(spread_prob_gonzaga, american_odds=-110)
if kelly_gonzaga > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_gonzaga)
    edge = ((1.909 * spread_prob_gonzaga) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_gonzaga*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_gonzaga*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

print(f"\n   Baylor +{spread} (-110 odds):")
kelly_baylor = KellyCriterion.calculate_kelly(spread_prob_baylor, american_odds=-110)
if kelly_baylor > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_baylor)
    edge = ((1.909 * spread_prob_baylor) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_baylor*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_baylor*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

# Total: 162.5
total_line = 162.5
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
