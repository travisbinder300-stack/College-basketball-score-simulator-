# NBA Prop Betting System - Quick Start Guide

## What is This?

This is a complete NBA prop betting system based on PropMadness.com's interfuture data structure. It helps you:
- Analyze NBA player prop bets
- Find value bets with positive expected value
- Simulate prop outcomes using Monte Carlo methods
- Build and analyze parlays

## Quick Start (30 seconds)

### 1. Run the Basic Demo
```bash
python nba_prop_data.py
```
This shows sample NBA props with all their data.

### 2. Run the Analyzer & Simulator
```bash
python nba_prop_simulator.py
```
This analyzes props, finds value bets, and runs simulations.

### 3. Load Data from JSON
```bash
python nba_prop_loader.py
```
This loads props from the interfuture JSON format.

### 4. Try All Examples
```bash
python examples.py
```
Press Enter between examples to see all features.

## Simple Usage Examples

### Find Value Bets
```python
from nba_prop_data import generate_sample_props
from nba_prop_simulator import PropAnalyzer

props = generate_sample_props()
analyzer = PropAnalyzer()

# Find props with 5%+ edge
value_bets = analyzer.find_value_bets(props, min_edge=0.05)

for prop, edge, side in value_bets:
    print(f"{prop.player.name}: {side} {prop.prop_line.line_value}")
    print(f"Edge: {edge:+.2%}\n")
```

### Simulate a Prop
```python
from nba_prop_data import generate_sample_props
from nba_prop_simulator import PropAnalyzer, PropSimulator

props = generate_sample_props()
analyzer = PropAnalyzer()
simulator = PropSimulator(analyzer)

# Simulate 10,000 outcomes
result = simulator.simulate_prop_outcome(props[0], num_simulations=10000)
print(f"Hit Rate: {result['over_hit_rate']}")
```

### Create a Parlay
```python
from nba_prop_data import generate_sample_props, PropBetSlip
from nba_prop_simulator import PropAnalyzer, PropSimulator

props = generate_sample_props()
analyzer = PropAnalyzer()
simulator = PropSimulator(analyzer)

# Create 3-leg parlay with $50 stake
parlay = PropBetSlip(
    slip_id="MY_PARLAY",
    props=props[:3],
    stake=50.0,
    bet_type="parlay"
)

# Simulate it
result = simulator.simulate_parlay(parlay, num_simulations=10000)
print(f"Expected Value: {result['expected_value']}")
print(f"ROI: {result['roi']}")
```

### Load Your Own Data
```python
from nba_prop_loader import PropDataLoader

# Load from JSON file
loader = PropDataLoader('interfuture_nba_props.json')
players, games, props = loader.load_all()

# Filter by game
game_props = loader.filter_props_by_game("NBA_2024_LAL_GSW_001")

# Filter by player
player_props = loader.filter_props_by_player("2544")  # LeBron James
```

## What's Included

| File | Description |
|------|-------------|
| `nba_prop_data.py` | Data models for players, games, and props |
| `nba_prop_simulator.py` | Analyzer and Monte Carlo simulator |
| `nba_prop_loader.py` | JSON data loader |
| `interfuture_nba_props.json` | Sample data in PropMadness format |
| `examples.py` | 7 complete usage examples |
| `README.md` | Full documentation |

## Key Features

✅ **No Dependencies** - Uses only Python standard library  
✅ **PropMadness.com Format** - Compatible with interfuture data  
✅ **Value Bet Detection** - Finds props with positive edge  
✅ **Monte Carlo Simulation** - 10,000+ run simulations  
✅ **Parlay Analysis** - Calculate expected value and ROI  
✅ **Multiple Odds Formats** - American, Decimal, Fractional  

## Supported Prop Types

- Points
- Rebounds
- Assists
- Three-Pointers Made
- Steals
- Blocks
- Turnovers
- Points + Rebounds + Assists (PRA)
- Double-Double
- Triple-Double

## Need Help?

1. Read the full README.md
2. Run examples.py to see all features
3. Check the documentation in each Python file
4. Open an issue on GitHub

## Disclaimer

This is for educational and research purposes only. Always gamble responsibly.
