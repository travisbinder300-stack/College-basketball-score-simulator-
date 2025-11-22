# College Basketball Score Simulator

A Python-based simulator for college basketball games that generates realistic scores based on team statistics and random game events.

## Features

- **Realistic Game Simulation**: Simulates basketball games with 2-point shots, 3-point shots, and free throws
- **Team Statistics**: Each team has offense rating, defense rating, three-point percentage, and free throw percentage
- **Multiple Game Modes**: Simulate single games or multiple games to see statistical trends
- **Play-by-Play Option**: View detailed play-by-play commentary with the `--verbose` flag
- **Pre-configured Teams**: Includes 6 major college basketball teams with realistic statistics

## Installation

This simulator requires Python 3.6 or higher and uses only standard library modules.

1. Clone the repository:
```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

2. Make the simulator executable (optional):
```bash
chmod +x simulator.py
```

## Usage

### Basic Usage

Simulate a game between two teams:
```bash
python simulator.py duke unc
```

### List Available Teams

See all available teams and their statistics:
```bash
python simulator.py --list-teams
```

Available teams include:
- Duke Blue Devils
- North Carolina Tar Heels
- Kentucky Wildcats
- Kansas Jayhawks
- Villanova Wildcats
- Gonzaga Bulldogs

### Verbose Mode

Watch the game play-by-play:
```bash
python simulator.py duke unc --verbose
```

### Multiple Games

Simulate multiple games to see statistical trends:
```bash
python simulator.py kentucky kansas --games 100
```

This will show you:
- Win/loss record for each team
- Average scores

### Command-Line Options

```
usage: simulator.py [-h] [--verbose] [--games GAMES] [--list-teams] [home_team] [away_team]

positional arguments:
  home_team             Home team name
  away_team             Away team name

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         Show play-by-play details
  --games GAMES, -g GAMES
                        Number of games to simulate (default: 1)
  --list-teams, -l      List all available teams
```

## Examples

1. **Simple game simulation:**
```bash
python simulator.py duke unc
```
Output:
```
============================================================
FINAL SCORE
============================================================
Duke Blue Devils                    72
North Carolina Tar Heels            68
============================================================

Duke Blue Devils wins by 4 points!
```

2. **Play-by-play game:**
```bash
python simulator.py villanova gonzaga --verbose
```

3. **Season simulation (100 games):**
```bash
python simulator.py kentucky kansas --games 100
```
Output:
```
Results from 100 games:
============================================================
Kentucky Wildcats              56 wins
Kansas Jayhawks                44 wins

Average Score:
Kentucky Wildcats              74.2
Kansas Jayhawks                70.8
============================================================
```

## How It Works

The simulator uses a possession-based model:

1. **Possessions**: Each game consists of approximately 140 possessions (70 per team)
2. **Shot Types**: 
   - 25% chance of 3-point attempt
   - 50% chance of 2-point attempt
   - 25% chance of free throw attempts (from fouls)
3. **Success Rates**: Based on team offense vs defense ratings and shooting percentages
4. **Randomization**: Uses random events to create realistic game variability

## Team Statistics

Each team has four key attributes:
- **Offense Rating** (0-100): Overall offensive capability
- **Defense Rating** (0-100): Overall defensive capability
- **Three-Point Percentage** (0.0-1.0): Success rate on 3-point shots
- **Free Throw Percentage** (0.0-1.0): Success rate on free throws

## Contributing

Feel free to add more teams or modify team statistics by editing the `create_sample_teams()` function in `simulator.py`.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
