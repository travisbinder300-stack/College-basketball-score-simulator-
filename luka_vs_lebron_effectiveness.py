"""
Comprehensive Luka Doncic vs LeBron James Prop Effectiveness Analysis
Shows how Luka Doncic performs effectively compared to LeBron James in prop betting
"""

from player_comparison import (
    PlayerComparator, create_luka_doncic_profile, create_lebron_james_profile
)
from lineup_impact import LineupImpactAnalyzer, LineupConfiguration
import json


def load_lineup_data():
    """Load lineup impact data from JSON"""
    with open('lineup_impact_data.json', 'r') as f:
        data = json.load(f)
    return data


def analyze_luka_effectiveness():
    """Comprehensive analysis of how Luka Doncic is effective compared to LeBron James in props"""
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " LUKA DONCIC vs LEBRON JAMES - PROP EFFECTIVENESS ANALYSIS ".center(78) + "║")
    print("║" + " 2025-26 NBA Season ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Create player profiles
    luka = create_luka_doncic_profile()
    lebron = create_lebron_james_profile()
    
    # Initialize comparator
    comparator = PlayerComparator()
    
    # Compare players
    comparison = comparator.compare_players(luka, lebron)
    
    # Section 1: Basic Statistical Dominance
    print("┌" + "─" * 78 + "┐")
    print("│" + " 1. STATISTICAL DOMINANCE ".ljust(78) + "│")
    print("├" + "─" * 78 + "┤")
    
    print("│ " + "Scoring:".ljust(77) + "│")
    print("│ " + f"  Luka: {luka.points_per_game:.1f} PPG".ljust(77) + "│")
    print("│ " + f"  LeBron: {lebron.points_per_game:.1f} PPG".ljust(77) + "│")
    print("│ " + f"  → Luka scores {luka.points_per_game - lebron.points_per_game:.1f} more PPG (+{((luka.points_per_game/lebron.points_per_game - 1) * 100):.1f}%)".ljust(77) + "│")
    print("│".ljust(79) + "│")
    
    print("│ " + "Playmaking:".ljust(77) + "│")
    print("│ " + f"  Luka: {luka.assists_per_game:.1f} APG".ljust(77) + "│")
    print("│ " + f"  LeBron: {lebron.assists_per_game:.1f} APG".ljust(77) + "│")
    print("│ " + f"  → Luka leads by {luka.assists_per_game - lebron.assists_per_game:.1f} APG".ljust(77) + "│")
    print("│".ljust(79) + "│")
    
    print("│ " + "Usage Rate:".ljust(77) + "│")
    print("│ " + f"  Luka: {luka.usage_rate:.1%}".ljust(77) + "│")
    print("│ " + f"  LeBron: {lebron.usage_rate:.1%}".ljust(77) + "│")
    print("│ " + f"  → Luka has {(luka.usage_rate - lebron.usage_rate):.1%} higher usage".ljust(77) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Section 2: Prop Hit Rate Analysis
    print("┌" + "─" * 78 + "┐")
    print("│" + " 2. PROP HIT RATE EFFECTIVENESS ".ljust(78) + "│")
    print("├" + "─" * 78 + "┤")
    
    # Points props
    print("│ " + "POINTS PROPS:".ljust(77) + "│")
    for line in [30.5, 32.5]:
        luka_rate = luka.prop_hit_rates.get("points", {}).get(line)
        lebron_rate = lebron.prop_hit_rates.get("points", {}).get(line)
        
        if luka_rate:
            print("│ " + f"  O/U {line} Points:".ljust(77) + "│")
            print("│ " + f"    Luka: {luka_rate:.1%} hit rate".ljust(77) + "│")
            
            if lebron_rate:
                print("│ " + f"    LeBron: {lebron_rate:.1%} hit rate".ljust(77) + "│")
                diff = luka_rate - lebron_rate
                if diff > 0:
                    print("│ " + f"    → Luka MORE EFFECTIVE by {diff:.1%}".ljust(77) + "│")
                else:
                    print("│ " + f"    → LeBron more effective by {abs(diff):.1%}".ljust(77) + "│")
            else:
                print("│ " + f"    LeBron: Line too high (avg {lebron.points_per_game:.1f})".ljust(77) + "│")
                print("│ " + f"    → Luka MUCH MORE EFFECTIVE - can hit higher lines".ljust(77) + "│")
        print("│".ljust(79) + "│")
    
    # Assists props
    print("│ " + "ASSISTS PROPS:".ljust(77) + "│")
    for line in [9.5, 10.5]:
        luka_rate = luka.prop_hit_rates.get("assists", {}).get(line)
        lebron_rate = lebron.prop_hit_rates.get("assists", {}).get(line)
        
        if luka_rate and lebron_rate:
            print("│ " + f"  O/U {line} Assists:".ljust(77) + "│")
            print("│ " + f"    Luka: {luka_rate:.1%} hit rate".ljust(77) + "│")
            print("│ " + f"    LeBron: {lebron_rate:.1%} hit rate".ljust(77) + "│")
            diff = luka_rate - lebron_rate
            if diff > 0:
                print("│ " + f"    → Luka MORE EFFECTIVE by {diff:.1%}".ljust(77) + "│")
            else:
                print("│ " + f"    → LeBron more effective by {abs(diff):.1%}".ljust(77) + "│")
            print("│".ljust(79) + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Section 3: Lineup Impact Analysis
    print("┌" + "─" * 78 + "┐")
    print("│" + " 3. LINEUP IMPACT EFFECTIVENESS ".ljust(78) + "│")
    print("├" + "─" * 78 + "┤")
    
    lineup_data = load_lineup_data()
    
    # Find Luka's lineup stats
    luka_with_kyrie = None
    luka_without_kyrie = None
    lebron_with_reaves = None
    lebron_without_reaves = None
    
    for stat in lineup_data['lineup_impact_stats']:
        if stat['player_id'] == '1629029':
            if 'WITH_IRVING' in stat['config_id']:
                luka_with_kyrie = stat
            elif 'WITHOUT_IRVING' in stat['config_id']:
                luka_without_kyrie = stat
        elif stat['player_id'] == '2544':
            if 'WITH_REAVES' in stat['config_id']:
                lebron_with_reaves = stat
            elif 'WITHOUT_REAVES' in stat['config_id']:
                lebron_without_reaves = stat
    
    if luka_without_kyrie:
        print("│ " + "Luka WITHOUT Kyrie Irving (Solo Carry):".ljust(77) + "│")
        print("│ " + f"  PPG: {luka_without_kyrie['performance']['points_per_game']:.1f}".ljust(77) + "│")
        print("│ " + f"  APG: {luka_without_kyrie['performance']['assists_per_game']:.1f}".ljust(77) + "│")
        print("│ " + f"  Usage: {luka_without_kyrie['usage_rate']:.1%}".ljust(77) + "│")
        print("│ " + f"  Hit Rate (32.5 pts): {luka_without_kyrie['hit_rates']['points']['32.5']:.1%}".ljust(77) + "│")
        print("│".ljust(79) + "│")
    
    if lebron_without_reaves:
        print("│ " + "LeBron WITHOUT Austin Reaves (Solo Carry):".ljust(77) + "│")
        print("│ " + f"  PPG: {lebron_without_reaves['performance']['points_per_game']:.1f}".ljust(77) + "│")
        print("│ " + f"  APG: {lebron_without_reaves['performance']['assists_per_game']:.1f}".ljust(77) + "│")
        print("│ " + f"  Usage: {lebron_without_reaves['usage_rate']:.1%}".ljust(77) + "│")
        print("│ " + f"  Hit Rate (25.5 pts): {lebron_without_reaves['hit_rates']['points']['25.5']:.1%}".ljust(77) + "│")
        print("│".ljust(79) + "│")
    
    if luka_without_kyrie and lebron_without_reaves:
        print("│ " + "SOLO CARRY COMPARISON:".ljust(77) + "│")
        ppg_diff = luka_without_kyrie['performance']['points_per_game'] - lebron_without_reaves['performance']['points_per_game']
        usage_diff = luka_without_kyrie['usage_rate'] - lebron_without_reaves['usage_rate']
        print("│ " + f"  → Luka scores {ppg_diff:.1f} more PPG when solo".ljust(77) + "│")
        print("│ " + f"  → Luka has {usage_diff:.1%} higher usage when solo".ljust(77) + "│")
        print("│ " + f"  → Luka MORE EFFECTIVE as solo star".ljust(77) + "│")
    
    print("└" + "─" + "─" * 78 + "┘")
    print()
    
    # Section 4: Overall Prop Betting Effectiveness
    print("┌" + "─" * 78 + "┐")
    print("│" + " 4. OVERALL PROP BETTING EFFECTIVENESS ".ljust(78) + "│")
    print("├" + "─" * 78 + "┤")
    print("│".ljust(79) + "│")
    print("│ " + "WHY LUKA IS MORE EFFECTIVE FOR PROPS:".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "✓ Higher Volume: Luka averages 33.9 PPG vs LeBron's 25.5 PPG".ljust(77) + "│")
    print("│ " + "   → Can consistently hit higher prop lines".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "✓ Elite Usage: 36.8% usage rate (6.3% higher than LeBron)".ljust(77) + "│")
    print("│ " + "   → Touches the ball more, more opportunities to score".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "✓ Better Efficiency: 61.8% TS% vs LeBron's 58.8%".ljust(77) + "│")
    print("│ " + "   → High volume WITH high efficiency = elite prop value".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "✓ Solo Dominance: 35.8 PPG without Kyrie vs LeBron's 27.2 without Reaves".ljust(77) + "│")
    print("│ " + "   → Elite when teammates are out".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "✓ Consistent Hit Rates: 68% at 30.5 pts, 58% at 32.5 pts".ljust(77) + "│")
    print("│ " + "   → Reliable for high-line props".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Section 5: Prop Recommendations
    print("┌" + "─" * 78 + "┐")
    print("│" + " 5. PROP BETTING RECOMMENDATIONS ".ljust(78) + "│")
    print("├" + "─" * 78 + "┤")
    print("│".ljust(79) + "│")
    print("│ " + "LUKA DONCIC PROPS:".ljust(77) + "│")
    print("│ " + "  • POINTS: Target 30.5-32.5 range for best value".ljust(77) + "│")
    print("│ " + "  • ASSISTS: 9.5-10.5 excellent hit rates".ljust(77) + "│")
    print("│ " + "  • When Kyrie OUT: Increase lines by 3+ points".ljust(77) + "│")
    print("│ " + "  • High usage = consistent OVER hits".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "LEBRON JAMES PROPS:".ljust(77) + "│")
    print("│ " + "  • POINTS: Target 23.5-25.5 range".ljust(77) + "│")
    print("│ " + "  • ASSISTS: 9.5 provides good value".ljust(77) + "│")
    print("│ " + "  • More efficient but lower volume than Luka".ljust(77) + "│")
    print("│ " + "  • Better for lower-line props".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("│ " + "VERDICT:".ljust(77) + "│")
    print("│ " + "  → Luka MORE EFFECTIVE for high-line props".ljust(77) + "│")
    print("│ " + "  → Luka MORE EFFECTIVE as primary scorer".ljust(77) + "│")
    print("│ " + "  → Luka MORE EFFECTIVE in 2025-26 season".ljust(77) + "│")
    print("│".ljust(79) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " CONCLUSION: LUKA DONCIC IS MORE EFFECTIVE THAN LEBRON JAMES ".center(78) + "║")
    print("║" + " FOR NBA PROP BETTING IN 2025-26 ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print("✅ Analysis complete!")


if __name__ == "__main__":
    analyze_luka_effectiveness()
