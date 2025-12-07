#!/usr/bin/env python3
"""
TCU vs Kansas State - High-Pace Big 12 Shootout
Fast-paced offensive game
"""

from basketball_simulator import GameSimulator, TeamStats

# TCU Horned Frogs - Fast pace, efficient offense
tcu = TeamStats(
    name="TCU Horned Frogs",
    offensive_efficiency=118.5,
    defensive_efficiency=102.5,
    pace=76.5,  # Very fast pace
    three_point_rate=0.41,
    three_point_percentage=0.368,
    two_point_percentage=0.555,
    free_throw_rate=0.35,
    free_throw_percentage=0.745,
    offensive_rebound_rate=0.33,
    turnover_rate=0.16,
    and_one_rate=0.08
)

# Kansas State Wildcats - Fast pace, balanced
kansas_state = TeamStats(
    name="Kansas State Wildcats",
    offensive_efficiency=117.8,
    defensive_efficiency=103.2,
    pace=76.2,  # Very fast pace
    three_point_rate=0.38,
    three_point_percentage=0.355,
    two_point_percentage=0.548,
    free_throw_rate=0.36,
    free_throw_percentage=0.732,
    offensive_rebound_rate=0.34,
    turnover_rate=0.17,
    and_one_rate=0.075
)

# Run simulation
simulator = GameSimulator(tcu, kansas_state)
results = simulator.run_simulation(num_simulations=10000)

# Print results
simulator.print_results(results)

# Betting line analysis
print("\n" + "="*80)
print("BETTING LINE ANALYSIS")
print("="*80)

# Spread: TCU -1.5
spread = 1.5
tcu_covers = sum(1 for m in results['margins'] if m > spread)
kstate_covers = sum(1 for m in results['margins'] if m < -spread)
tcu_cover_pct = (tcu_covers / len(results['margins'])) * 100
kstate_cover_pct = (kstate_covers / len(results['margins'])) * 100

print(f"\n📊 SPREAD ANALYSIS (TCU -{spread} / Kansas State +{spread}):")
print(f"   TCU covers -{spread}: {tcu_cover_pct:.1f}% of simulations")
print(f"   Kansas State covers +{spread}: {kstate_cover_pct:.1f}% of simulations")

# Analyze TCU -1.5
from basketball_simulator import KellyCriterion
spread_prob_tcu = tcu_cover_pct / 100
spread_prob_kstate = kstate_cover_pct / 100

print(f"\n   TCU -{spread} (-110 odds):")
kelly_tcu = KellyCriterion.calculate_kelly(spread_prob_tcu, american_odds=-110)
if kelly_tcu > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_tcu)
    edge = ((1.909 * spread_prob_tcu) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_tcu*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_tcu*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

print(f"\n   Kansas State +{spread} (-110 odds):")
kelly_kstate = KellyCriterion.calculate_kelly(spread_prob_kstate, american_odds=-110)
if kelly_kstate > 0:
    recommendation = KellyCriterion.get_recommendation(kelly_kstate)
    edge = ((1.909 * spread_prob_kstate) - 1) * 100
    print(f"   → Recommendation: {recommendation}")
    print(f"   → Full Kelly: {kelly_kstate*100:.2f}% of bankroll")
    print(f"   → Half Kelly: {kelly_kstate*50:.2f}% of bankroll (recommended)")
    print(f"   → Edge: {edge:+.2f}%")
else:
    print(f"   → Recommendation: NO BET (no edge)")

# Total: 151.5
total_line = 151.5
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
