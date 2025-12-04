# College Basketball Score Simulator 🏀

A comprehensive college basketball game simulator with realistic scoring mechanics, team statistics, and multiple simulation modes.

## Features

### Basic Score Simulator (`basketball_simulator.py`)
- Realistic basketball game simulation
- Team-based scoring with configurable skill levels
- Field goals (2-pointers), 3-pointers, and free throws
- Foul tracking
- Overtime support
- Play-by-play commentary

### Advanced Score Simulator (`advanced_simulator.py`)
- All features from the basic simulator, plus:
- Detailed team statistics (FG%, 3PT%, FT%, rebounds, assists, steals, blocks, turnovers)
- Dynamic momentum system affecting shooting percentages
- Timeout mechanics
- Enhanced play-by-play with emojis
- Comprehensive post-game statistics

### Interactive CLI (`run_simulator.py`)
- Easy-to-use menu interface
- Run preset simulations
- Create custom matchups with your own teams
- Choose between basic and advanced simulators

## Installation

No external dependencies required! Just Python 3.6+

```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

## Usage

### Quick Start - Interactive Mode

Run the main CLI interface:

```bash
python3 run_simulator.py
```

This will present you with a menu where you can:
1. Run basic simulator with preset teams
2. Run advanced simulator with preset teams
3. Create custom basic matchups
4. Create custom advanced matchups

### Running Individual Simulators

**Basic Simulator:**
```bash
python3 basketball_simulator.py
```

**Advanced Simulator:**
```bash
python3 advanced_simulator.py
```

### Using as a Library

**Basic Example:**
```python
from basketball_simulator import Team, BasketballGame

# Create teams
team1 = Team("Duke Blue Devils", skill_level=75)
team2 = Team("North Carolina Tar Heels", skill_level=72)

# Simulate game
game = BasketballGame(team1, team2)
game.simulate_game(verbose=True)
game.print_final_score()
```

**Advanced Example:**
```python
from advanced_simulator import AdvancedTeam, AdvancedGame

# Create teams
team1 = AdvancedTeam("Kentucky Wildcats", skill_level=78)
team2 = AdvancedTeam("Kansas Jayhawks", skill_level=76)

# Simulate game
game = AdvancedGame(team1, team2)
game.simulate_game(verbose=True)
game.print_final_stats()
```

## Team Skill Levels

Skill levels range from 0-100 and affect:
- Field goal percentage (35-85%)
- 3-point percentage (25-65%)
- Free throw percentage (60-100%)

Recommended skill levels:
- **Elite teams (75-85)**: Top-ranked NCAA Division I programs
- **Good teams (60-75)**: Mid-major conference leaders
- **Average teams (45-60)**: Typical Division I teams
- **Developing teams (30-45)**: Lower-tier programs

## Game Features

### Realistic Mechanics
- Variable possession counts (30-42 per half)
- Shot type distribution (30% 3-pointers, 70% 2-pointers)
- Foul rates (~15-18%)
- Turnover rates (~12%)
- Rebound tracking
- Assist tracking
- Steal and block mechanics

### Advanced Features (Advanced Simulator Only)
- **Momentum System**: Teams build momentum with good plays, affecting shooting percentage
- **Timeouts**: Teams automatically call timeouts when losing momentum
- **Detailed Statistics**: Complete box score with shooting percentages
- **Enhanced Commentary**: Rich play-by-play with visual indicators

## Examples

### Example Output (Basic Simulator)

```
************************************************************
COLLEGE BASKETBALL GAME
Duke Blue Devils vs North Carolina Tar Heels
************************************************************

============================================================
HALF 1
============================================================

Duke Blue Devils made a 3-pointer! +3
Score: Duke Blue Devils 3 - North Carolina Tar Heels 0

North Carolina Tar Heels made a 2-pointer! +2
Score: Duke Blue Devils 3 - North Carolina Tar Heels 2

...

************************************************************
FINAL SCORE
************************************************************
Duke Blue Devils: 78
North Carolina Tar Heels: 72
************************************************************

🏆 Duke Blue Devils wins!
```

### Example Output (Advanced Simulator)

```
======================================================================
ADVANCED COLLEGE BASKETBALL SIMULATOR
Kentucky Wildcats vs Kansas Jayhawks
======================================================================

======================================================================
HALF 1
======================================================================

🏀 Kentucky Wildcats scores! +2 (assist)
   Score: Kentucky Wildcats 2 - Kansas Jayhawks 0
   Momentum: Kentucky Wildcats [+1] | Kansas Jayhawks [0]

💨 Kansas Jayhawks steals the ball!

🔥 Kansas Jayhawks 3-POINTER! +3 (assist)
   Score: Kentucky Wildcats 2 - Kansas Jayhawks 3
   Momentum: Kentucky Wildcats [+1] | Kansas Jayhawks [+2]

...

======================================================================
DETAILED STATISTICS
======================================================================

Kentucky Wildcats:
  Field Goals: 24-52 (46.2%)
  3-Pointers: 8-22 (36.4%)
  Free Throws: 12-16 (75.0%)
  Rebounds: 28
  Assists: 15
  Steals: 7
  Blocks: 3
  Turnovers: 9
  Fouls: 16
```

## File Structure

```
College-basketball-score-simulator-/
├── basketball_simulator.py    # Basic score simulator
├── advanced_simulator.py      # Advanced score simulator with stats
├── run_simulator.py           # Interactive CLI interface
├── README.md                  # This file
└── LICENSE                    # License information
```

## Contributing

Feel free to fork this repository and submit pull requests with improvements!

## License

See LICENSE file for details.

## Author

College Basketball Score Simulator
Created for simulating exciting college basketball matchups! 🏀
