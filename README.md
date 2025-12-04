# Soccer Score Simulator

A realistic soccer match simulator that generates match scores based on team statistics.

## Features

- Simulate individual soccer matches between two teams
- Simulate multiple matches to see statistical patterns
- Customizable team attack and defense ratings
- Realistic scoring using probabilistic models
- Home field advantage factor
- Detailed match statistics and summaries

## Installation

This simulator requires Python 3.6 or higher. No additional dependencies are needed as it uses only Python standard library.

```bash
# Clone the repository
git clone <your-repository-url>
cd <repository-directory>

# Make the script executable (optional)
chmod +x soccer_simulator.py
```

## Usage

### Basic Usage

Simulate a single match with default settings:

```bash
python3 soccer_simulator.py
```

### Custom Team Names

```bash
python3 soccer_simulator.py --home "Manchester United" --away "Liverpool"
```

### Custom Team Ratings

Each team has attack and defense ratings on a 0-10 scale:

```bash
python3 soccer_simulator.py \
  --home "Barcelona" --home-attack 8.5 --home-defense 7.0 \
  --away "Real Madrid" --away-attack 8.0 --away-defense 7.5
```

### Simulate Multiple Matches

Run multiple simulations to see statistical patterns:

```bash
python3 soccer_simulator.py \
  --home "Bayern Munich" --away "Borussia Dortmund" \
  --matches 10
```

### Complete Example

```bash
python3 soccer_simulator.py \
  --home "Arsenal" --home-attack 7.5 --home-defense 6.5 \
  --away "Chelsea" --away-attack 7.0 --away-defense 7.5 \
  --matches 5
```

## Command Line Options

- `--home` - Name of the home team (default: "Home Team")
- `--away` - Name of the away team (default: "Away Team")
- `--home-attack` - Home team attack rating, 0-10 (default: 5.0)
- `--home-defense` - Home team defense rating, 0-10 (default: 5.0)
- `--away-attack` - Away team attack rating, 0-10 (default: 5.0)
- `--away-defense` - Away team defense rating, 0-10 (default: 5.0)
- `--matches` - Number of matches to simulate (default: 1)

## How It Works

The simulator uses a probabilistic model based on:

1. **Team Ratings**: Each team has attack (0-10) and defense (0-10) ratings
2. **Expected Goals**: Calculated from the difference between attacker's attack rating and defender's defense rating
3. **Home Advantage**: Home teams get a small boost (~0.3 goals expected)
4. **Goal Generation**: Uses a Poisson-like distribution for realistic soccer scoring patterns
5. **Match Outcome**: Simulates the actual goals scored and determines winner/draw

## Examples

### Example 1: Even Match
```bash
python3 soccer_simulator.py --home "Team A" --away "Team B"
```

### Example 2: Strong vs Weak Team
```bash
python3 soccer_simulator.py \
  --home "Strong FC" --home-attack 9.0 --home-defense 8.0 \
  --away "Weak FC" --away-attack 3.0 --away-defense 4.0
```

### Example 3: Statistical Analysis
```bash
python3 soccer_simulator.py \
  --home "PSG" --home-attack 8.5 --home-defense 7.0 \
  --away "Marseille" --away-attack 6.5 --away-defense 6.5 \
  --matches 100
```

## License

See LICENSE file for details. 
