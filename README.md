# College Basketball Score Simulator

A comprehensive and accurate college basketball game simulator that uses realistic statistics and game mechanics to simulate basketball games with high fidelity.

## Features

- **Realistic Game Simulation**: Simulates college basketball games with accurate scoring, possessions, and game flow
- **Detailed Statistics**: Tracks field goals, 3-pointers, free throws, rebounds, assists, steals, blocks, turnovers, and fouls
- **Customizable Teams**: Configure teams with custom statistics (shooting percentages, turnover rates, etc.)
- **Multiple Simulation Modes**: 
  - Quick simulation with preset teams
  - Custom simulation with user-defined teams
  - Multiple simulations for aggregate statistics
- **Overtime Support**: Automatically simulates overtime periods when games are tied
- **Play-by-Play**: Optional detailed play-by-play commentary for each possession
- **Box Score**: Comprehensive box score with detailed team statistics

## Installation

No external dependencies required! This simulator uses only Python 3.6+ standard library.

```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

## Usage

### Basic Simulation

Run a basic simulation with preset teams:

```bash
python3 basketball_simulator.py
```

### Interactive Mode

For more control and customization options:

```bash
python3 interactive_simulator.py
```

The interactive mode offers three options:
1. **Quick Simulation**: Run a single game with preset teams
2. **Custom Simulation**: Define your own teams with custom statistics
3. **Multiple Simulations**: Run multiple games and see aggregate results

## Team Statistics

Teams can be customized with the following statistics:

- **Field Goal Percentage** (0.20-0.70): Overall shooting accuracy
- **Three-Point Percentage** (0.15-0.50): 3-point shooting accuracy
- **Free Throw Percentage** (0.50-0.95): Free throw accuracy
- **Turnover Rate** (0.05-0.30): Probability of turning the ball over
- **Offensive Rebound Rate** (0.15-0.45): Probability of getting offensive rebounds
- **Defensive Rebound Rate** (0.55-0.85): Probability of getting defensive rebounds
- **Three-Point Attempt Rate** (0.20-0.60): Percentage of shots that are 3-pointers
- **Steal Rate** (0.03-0.15): Probability of stealing the ball on defense
- **Block Rate** (0.02-0.12): Probability of blocking a shot

## Game Mechanics

The simulator accurately models:

- **Possessions**: Each team gets approximately 70 possessions per game (35 per half)
- **Shot Selection**: Teams choose between 2-point and 3-point attempts based on their strategy
- **Turnovers**: Random turnovers based on team's turnover rate
- **Fouls**: Realistic foul calling with appropriate free throw situations
- **Rebounds**: Offensive and defensive rebounding with second-chance opportunities
- **Defensive Plays**: Steals and blocks affect game outcomes
- **Overtime**: 5-possession overtime periods when games are tied

## Example Output

```
============================================================
                 COLLEGE BASKETBALL SIMULATION              
          Blue Devils           vs           Wildcats       
============================================================

Possession 1: Blue Devils has the ball
  Blue Devils scores 2 points on a 2-pointer! Score: Blue Devils 2 - Wildcats 0

...

============================================================
                         FINAL SCORE                        
============================================================
Blue Devils: 78
Wildcats: 72

Winner: Blue Devils
============================================================

                         BOX SCORE                          
============================================================

Blue Devils:
  Points: 78
  Field Goals: 22/48 (45.8%)
  3-Pointers: 8/22 (36.4%)
  Free Throws: 18/24 (75.0%)
  Rebounds: 35
  Assists: 16
  Steals: 6
  Blocks: 3
  Turnovers: 10
  Fouls: 18
```

## Accuracy

This simulator achieves high accuracy by:

1. Using realistic statistical ranges based on actual college basketball data
2. Modeling actual game flow with alternating possessions
3. Simulating realistic possession counts (~70 per game)
4. Including all major basketball events (shots, turnovers, rebounds, fouls)
5. Proper overtime handling
6. Realistic correlation between team stats and game outcomes

The default statistics are based on NCAA Division I averages, ensuring realistic final scores typically in the 60-90 point range.

## License

This project is licensed under the terms included in the LICENSE file.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the simulator.
