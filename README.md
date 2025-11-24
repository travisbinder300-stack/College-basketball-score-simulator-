# College Football Spread Analyzer

A Python tool for analyzing college football betting spreads to identify those with high coverage rates (80-100%). This analyzer helps find point spreads that historically have covered at a high percentage.

> **Note**: Despite the repository name referencing basketball, this tool is specifically designed for college football spread analysis.

## Features

- Analyzes historical college football game data with spreads
- Identifies spreads that cover at 80-100% rate
- **NEW: Over/Under analysis** - finds O/U lines that hit consistently
- **NEW: Wrong Favorite detection** - identifies teams that lose as favorites with 100% accuracy
- Groups analysis by specific spread values and by favorite magnitude categories
- Exports detailed results to JSON format
- Includes sample data for demonstration

## Installation

No special installation required. Just Python 3.7+ with standard library.

```bash
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-
```

## Usage

### Basic Usage

Run the analyzer with sample data:

```bash
python3 football_spread_analyzer.py
```

This will:
1. Generate sample game data if not present
2. Analyze spreads with 80-100% coverage rate
3. Display a comprehensive report
4. Export results to `spread_analysis_results.json`

### Using Your Own Data

Create a JSON file with your game data:

```json
[
  {
    "home_team": "Alabama",
    "away_team": "Tennessee",
    "home_score": 35,
    "away_score": 21,
    "spread": -7.0,
    "over_under": 52.5,
    "season": "2023",
    "week": 5
  }
]
```

Then modify the script to load your data file.

### Understanding the Output

The analyzer provides four types of analysis:

1. **By Specific Spread Value**: Groups games by exact spread values (rounded to 0.5 increments)
2. **By Favorite Magnitude**: Groups games by spread ranges:
   - Small Favorite (0 to -3)
   - Medium Favorite (-3.5 to -7)
   - Large Favorite (-7.5 to -14)
   - Heavy Favorite (-14.5 to -21)
   - Huge Favorite (-21.5+)
3. **Over/Under Analysis**: Identifies O/U lines where OVER or UNDER hits at 80-100% rate
4. **Wrong Favorites**: Finds teams that lose as favorites with 100% accuracy (trap games)

### Example Output

```
================================================================================
COLLEGE FOOTBALL SPREAD ANALYSIS REPORT
Finding spreads with 80% to 100% coverage rate
================================================================================

Total games analyzed: 34

--- ANALYSIS BY SPECIFIC SPREAD VALUE ---

1. Spread: -21.0
   Coverage Rate: 100.0% (6/6 games)

2. Spread: -14.0
   Coverage Rate: 100.0% (6/6 games)

3. Spread: -7.0
   Coverage Rate: 100.0% (9/9 games)

--- OVER/UNDER ANALYSIS ---

O/U 58.5 (OVER)
Hit Rate: 100.0% (11/11 games)

--- WRONG FAVORITES (100% ACCURACY) ---

Team: Vanderbilt (as favorite)
Favorite Loss Rate: 100.0% (3/3 games)
   → Bet AGAINST this team when they are favored!
```
   Coverage Rate: 80.0% (4/5 games)
```

## How Spread Coverage Works

- **Negative spread** (e.g., -7.0): Home team is favored. They must win by MORE than the absolute value of the spread to cover.
  - Example: Home -7, Home wins 35-21 (14 point margin) → Spread COVERED
  
- **Positive spread** (e.g., +7.0): Away team is favored. The home team must lose by LESS than the spread (or win) for the favorite to fail to cover.

## Data Structure

Each game requires:
- `home_team`: Name of home team
- `away_team`: Name of away team
- `home_score`: Final score for home team
- `away_score`: Final score for away team
- `spread`: Point spread (negative = home favored)
- `over_under`: (Optional) Total points over/under line
- `season`: Season identifier
- `week`: Week number

## Key Findings from Sample Data

Based on the sample data analysis:
- **-7 point spreads**: 100% coverage rate (9/9 games)
- **-14 point spreads**: 100% coverage rate (6/6 games)
- **-21 point spreads**: 100% coverage rate (6/6 games)
- **Over/Under 58.5 (OVER)**: 100% hit rate (11/11 games)
- **Vanderbilt as favorite**: Loses 100% of the time (3/3 games) - bet against them!

## Files Generated

- `sample_games.json`: Sample game data for testing
- `spread_analysis_results.json`: Detailed analysis results in JSON format

## Customization

You can customize the analysis by modifying parameters in the code:

```python
# Change coverage rate range
analyzer.generate_report(min_rate=0.85, max_rate=0.95)  # 85-95% instead

# Change minimum games required for analysis
results = analyzer.find_best_spreads(min_games=15, min_rate=0.80)
```

## Disclaimer

This tool is for educational and analytical purposes only. Past performance does not guarantee future results. Always gamble responsibly.

## License

See LICENSE file for details.

