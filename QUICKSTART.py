"""
QUICK START GUIDE
==================

This guide will help you get started with the College Basketball Game Simulator.

INSTALLATION
------------
1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   pip install -r requirements.txt

BASIC USAGE
-----------
Run the default simulation (Duke vs Virginia):
   python basketball_simulator.py

This will run 10,000 simulations and display:
- Win probabilities for each team
- Expected scores and distributions
- Score ranges (10th to 90th percentile)

RUNNING EXAMPLES
----------------
See multiple game scenarios:
   python examples.py

This includes:
- Elite matchup (Kentucky vs Kansas)
- Contrasting styles (Gonzaga vs Michigan)
- Upset scenario (2 seed vs 15 seed)

CREATING YOUR OWN TEAMS
-----------------------

from basketball_simulator import GameSimulator, TeamStats

# Define your team
my_team = TeamStats(
    name="My Team",
    offensive_efficiency=115.0,  # Points per 100 possessions
    defensive_efficiency=98.0,   # Points allowed per 100 possessions
    pace=70.0,                   # Possessions per 40 minutes
    three_point_rate=0.40,       # 40% of shots are 3-pointers
    three_point_percentage=0.36, # 36% from three
    two_point_percentage=0.54,   # 54% from two
    free_throw_rate=0.35,        # FTA per FGA
    free_throw_percentage=0.73,  # 73% FT shooting
    turnover_rate=0.16,          # 16% turnover rate
    offensive_rebound_rate=0.30, # 30% offensive rebound rate
    performance_variance=0.05    # 5% game-to-game variance
)

opponent = TeamStats(
    name="Opponent",
    offensive_efficiency=110.0,
    defensive_efficiency=100.0,
    pace=68.0,
    three_point_rate=0.38,
    three_point_percentage=0.35,
    two_point_percentage=0.52,
    free_throw_rate=0.33,
    free_throw_percentage=0.72,
    turnover_rate=0.17,
    offensive_rebound_rate=0.28,
    performance_variance=0.05
)

# Run simulation
simulator = GameSimulator(my_team, opponent)
results = simulator.run_simulation(num_simulations=10000)

# Access results
print(f"Win Probability: {results['team1_win_pct']:.1f}%")
print(f"Expected Score: {results['team1_avg_score']:.1f} - {results['team2_avg_score']:.1f}")

WHERE TO GET REAL STATISTICS
-----------------------------
For real team statistics, check:
- KenPom.com (subscription required) - Best for efficiency metrics
- Sports-Reference.com/CBB - Free comprehensive stats
- BartTorvik.com - Free advanced metrics
- NCAA.com - Official statistics

UNDERSTANDING THE OUTPUT
------------------------
The simulator provides:

1. Win Probability - % chance each team wins
2. Projected Scores - Mean scores with standard deviation
3. Median Scores - Middle value (50th percentile)
4. Expected Margin - Average point differential
5. Score Ranges - 10th to 90th percentile outcomes

Example interpretation:
"Duke Blue Devils: 76.4 ± 11.0 (median: 76)"
- Expected score: 76.4 points
- Standard deviation: 11.0 points
- Typical range: 65-87 points (about 68% of games)
- Median: Half of simulations scored above 76, half below

VOULGARIS-STYLE INSIGHTS
-------------------------
The simulator uses Haralabos Voulgaris's analytical principles:

1. Efficiency metrics (per 100 possessions) over raw stats
2. Pace factor determines total scoring opportunities
3. Defensive strength impacts opponent's offensive performance
4. Game-to-game variance captures "hot/cold" shooting nights
5. Probabilistic modeling through Monte Carlo simulation

KELLY CRITERION BETTING ANALYSIS
---------------------------------
The simulator includes Kelly Criterion for optimal bet sizing:

from basketball_simulator import KellyCriterion

# After running simulation
KellyCriterion.analyze_betting_opportunity(results, team=1, american_odds=+120)

This will output:
- Expected value and edge calculation
- Full Kelly, Half Kelly, and Quarter Kelly bet sizes
- Betting recommendation (NO BET, SMALL BET, MODERATE BET, LARGE BET)
- Example dollar amounts for different bankroll sizes

Kelly Criterion Formula: f* = (bp - q) / b
- f* = optimal fraction of bankroll to bet
- b = decimal odds - 1
- p = win probability from simulation
- q = probability of losing (1 - p)

**Important Notes**:
- Only bet when Kelly shows positive edge
- Many professionals use Half Kelly or Quarter Kelly for risk management
- This is for educational purposes only
- Always gamble responsibly

TROUBLESHOOTING
---------------
If you get unexpected results:
- Check that efficiency ratings are reasonable (90-125 typical range)
- Verify shooting percentages are realistic (2PT: 0.45-0.60, 3PT: 0.30-0.42)
- Ensure pace is in normal range (60-80 possessions per 40 min)
- Turnover rate should be 0.12-0.20
- Performance variance typically 0.04-0.08

For help or issues, check the README.md file.
"""

if __name__ == "__main__":
    print(__doc__)
