#!/usr/bin/env python3
"""
College Football Spread Analyzer
Analyzes spreads to find those with 80-100% coverage rates
"""

import json
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Game:
    """Represents a college football game with spread betting data"""
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    spread: float  # Negative means home team favored
    season: str
    week: int
    over_under: float = None  # Optional: total points over/under line
    
    def covered_spread(self) -> bool:
        """
        Determines if the spread was covered.
        For negative spreads (home favored), home must win by more than abs(spread).
        For positive spreads (away favored), away must win by more than spread.
        """
        actual_margin = self.home_score - self.away_score
        
        if self.spread < 0:
            # Home team is favored
            return actual_margin > abs(self.spread)
        else:
            # Away team is favored
            return actual_margin < -self.spread
    
    def get_margin(self) -> int:
        """Returns the actual point margin (home - away)"""
        return self.home_score - self.away_score
    
    def get_total_points(self) -> int:
        """Returns total points scored in the game"""
        return self.home_score + self.away_score
    
    def hit_over(self) -> bool:
        """Returns True if game went OVER the over/under line"""
        if self.over_under is None:
            return None
        return self.get_total_points() > self.over_under
    
    def is_wrong_favorite(self) -> bool:
        """
        Returns True if the favorite lost the game outright.
        This means the team favored to win actually lost.
        """
        actual_margin = self.home_score - self.away_score
        
        if self.spread < 0:
            # Home team was favored, wrong favorite if they lost
            return actual_margin < 0
        elif self.spread > 0:
            # Away team was favored, wrong favorite if they lost (home won)
            return actual_margin > 0
        else:
            # Pick'em game, no favorite
            return False


@dataclass
class SpreadAnalysis:
    """Analysis results for a specific spread range"""
    spread_range: str
    total_games: int
    covered_count: int
    coverage_rate: float
    games: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class FootballSpreadAnalyzer:
    """Analyzes college football spreads to find high-coverage rates"""
    
    def __init__(self):
        self.games: List[Game] = []
    
    def add_game(self, game: Game):
        """Add a game to the analysis dataset"""
        self.games.append(game)
    
    def load_games_from_json(self, filename: str):
        """Load games from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
            for game_data in data:
                game = Game(**game_data)
                self.add_game(game)
    
    def analyze_by_spread_range(self, min_rate: float = 0.80, max_rate: float = 1.00) -> List[SpreadAnalysis]:
        """
        Analyze games grouped by spread ranges and find those with coverage rates
        between min_rate and max_rate (default 80-100%)
        """
        # Group games by spread range (in 0.5 point increments)
        spread_groups = defaultdict(list)
        
        for game in self.games:
            # Round spread to nearest 0.5
            rounded_spread = round(game.spread * 2) / 2
            spread_groups[rounded_spread].append(game)
        
        # Analyze each spread group
        results = []
        for spread, games_list in sorted(spread_groups.items()):
            if len(games_list) >= 5:  # Only consider spreads with at least 5 games
                covered = sum(1 for g in games_list if g.covered_spread())
                coverage_rate = covered / len(games_list)
                
                if min_rate <= coverage_rate <= max_rate:
                    analysis = SpreadAnalysis(
                        spread_range=f"{spread:+.1f}",
                        total_games=len(games_list),
                        covered_count=covered,
                        coverage_rate=coverage_rate,
                        games=[{
                            'home_team': g.home_team,
                            'away_team': g.away_team,
                            'home_score': g.home_score,
                            'away_score': g.away_score,
                            'spread': g.spread,
                            'covered': g.covered_spread(),
                            'margin': g.get_margin()
                        } for g in games_list]
                    )
                    results.append(analysis)
        
        # Sort by coverage rate (descending)
        results.sort(key=lambda x: x.coverage_rate, reverse=True)
        return results
    
    def analyze_by_favorite_magnitude(self, min_rate: float = 0.80, max_rate: float = 1.00) -> List[SpreadAnalysis]:
        """
        Analyze games grouped by favorite magnitude (how heavily favored a team is)
        """
        # Group by spread magnitude ranges
        magnitude_groups = {
            'Small Favorite (0 to -3)': [],
            'Medium Favorite (-3.5 to -7)': [],
            'Large Favorite (-7.5 to -14)': [],
            'Heavy Favorite (-14.5 to -21)': [],
            'Huge Favorite (-21.5+)': []
        }
        
        for game in self.games:
            spread = game.spread
            if 0 >= spread >= -3:
                magnitude_groups['Small Favorite (0 to -3)'].append(game)
            elif -3.5 >= spread >= -7:
                magnitude_groups['Medium Favorite (-3.5 to -7)'].append(game)
            elif -7.5 >= spread >= -14:
                magnitude_groups['Large Favorite (-7.5 to -14)'].append(game)
            elif -14.5 >= spread >= -21:
                magnitude_groups['Heavy Favorite (-14.5 to -21)'].append(game)
            elif spread < -21.5:
                magnitude_groups['Huge Favorite (-21.5+)'].append(game)
        
        results = []
        for range_name, games_list in magnitude_groups.items():
            if len(games_list) >= 5:
                covered = sum(1 for g in games_list if g.covered_spread())
                coverage_rate = covered / len(games_list)
                
                if min_rate <= coverage_rate <= max_rate:
                    analysis = SpreadAnalysis(
                        spread_range=range_name,
                        total_games=len(games_list),
                        covered_count=covered,
                        coverage_rate=coverage_rate,
                        games=[{
                            'home_team': g.home_team,
                            'away_team': g.away_team,
                            'spread': g.spread,
                            'covered': g.covered_spread()
                        } for g in games_list]
                    )
                    results.append(analysis)
        
        results.sort(key=lambda x: x.coverage_rate, reverse=True)
        return results
    
    def find_best_spreads(self, min_games: int = 10, min_rate: float = 0.80) -> List[SpreadAnalysis]:
        """
        Find the best performing spread values with at least min_games and min_rate coverage
        """
        spread_groups = defaultdict(list)
        
        for game in self.games:
            spread_groups[game.spread].append(game)
        
        results = []
        for spread, games_list in spread_groups.items():
            if len(games_list) >= min_games:
                covered = sum(1 for g in games_list if g.covered_spread())
                coverage_rate = covered / len(games_list)
                
                if coverage_rate >= min_rate:
                    analysis = SpreadAnalysis(
                        spread_range=f"{spread:+.1f}",
                        total_games=len(games_list),
                        covered_count=covered,
                        coverage_rate=coverage_rate,
                        games=[{
                            'home_team': g.home_team,
                            'away_team': g.away_team,
                            'spread': g.spread,
                            'covered': g.covered_spread()
                        } for g in games_list]
                    )
                    results.append(analysis)
        
        results.sort(key=lambda x: x.coverage_rate, reverse=True)
        return results
    
    def analyze_over_under(self, min_rate: float = 0.80, max_rate: float = 1.00) -> List[SpreadAnalysis]:
        """
        Analyze over/under betting lines and find those with 80-100% hit rate.
        Returns over/under values where OVER consistently hits.
        """
        over_under_groups = defaultdict(list)
        
        # Group games by over/under value
        for game in self.games:
            if game.over_under is not None:
                # Round to nearest 0.5
                rounded_ou = round(game.over_under * 2) / 2
                over_under_groups[rounded_ou].append(game)
        
        results = []
        for ou_value, games_list in sorted(over_under_groups.items()):
            if len(games_list) >= 5:  # Minimum 5 games
                over_hits = sum(1 for g in games_list if g.hit_over())
                over_rate = over_hits / len(games_list)
                under_rate = 1 - over_rate
                
                # Check if OVER hits at target rate
                if min_rate <= over_rate <= max_rate:
                    analysis = SpreadAnalysis(
                        spread_range=f"O/U {ou_value:.1f} (OVER)",
                        total_games=len(games_list),
                        covered_count=over_hits,
                        coverage_rate=over_rate,
                        games=[{
                            'home_team': g.home_team,
                            'away_team': g.away_team,
                            'total_points': g.get_total_points(),
                            'over_under': g.over_under,
                            'hit_over': g.hit_over()
                        } for g in games_list]
                    )
                    results.append(analysis)
                
                # Check if UNDER hits at target rate
                elif min_rate <= under_rate <= max_rate:
                    analysis = SpreadAnalysis(
                        spread_range=f"O/U {ou_value:.1f} (UNDER)",
                        total_games=len(games_list),
                        covered_count=len(games_list) - over_hits,
                        coverage_rate=under_rate,
                        games=[{
                            'home_team': g.home_team,
                            'away_team': g.away_team,
                            'total_points': g.get_total_points(),
                            'over_under': g.over_under,
                            'hit_over': g.hit_over()
                        } for g in games_list]
                    )
                    results.append(analysis)
        
        results.sort(key=lambda x: x.coverage_rate, reverse=True)
        return results
    
    def find_wrong_favorites(self, min_rate: float = 1.00) -> List[SpreadAnalysis]:
        """
        Find spreads/teams where the favorite loses outright with 100% accuracy.
        These are "trap games" where betting against the favorite is always correct.
        """
        # Group by team when they are favored
        team_as_favorite = defaultdict(list)
        
        for game in self.games:
            if game.spread < 0:
                # Home team is favorite
                team_as_favorite[game.home_team].append(game)
            elif game.spread > 0:
                # Away team is favorite
                team_as_favorite[game.away_team].append(game)
        
        results = []
        for team, games_list in sorted(team_as_favorite.items()):
            if len(games_list) >= 3:  # At least 3 games to establish pattern
                wrong_favorite_count = sum(1 for g in games_list if g.is_wrong_favorite())
                wrong_rate = wrong_favorite_count / len(games_list)
                
                if wrong_rate >= min_rate:
                    analysis = SpreadAnalysis(
                        spread_range=f"{team} (as favorite)",
                        total_games=len(games_list),
                        covered_count=wrong_favorite_count,
                        coverage_rate=wrong_rate,
                        games=[{
                            'home_team': g.home_team,
                            'away_team': g.away_team,
                            'home_score': g.home_score,
                            'away_score': g.away_score,
                            'spread': g.spread,
                            'favorite_lost': g.is_wrong_favorite(),
                            'season': g.season,
                            'week': g.week
                        } for g in games_list]
                    )
                    results.append(analysis)
        
        results.sort(key=lambda x: x.coverage_rate, reverse=True)
        return results
    
    def generate_report(self, min_rate: float = 0.80, max_rate: float = 1.00):
        """Generate a comprehensive report of spreads with 80-100% coverage"""
        print("\n" + "="*80)
        print("COLLEGE FOOTBALL SPREAD ANALYSIS REPORT")
        print(f"Finding spreads with {min_rate*100:.0f}% to {max_rate*100:.0f}% coverage rate")
        print("="*80 + "\n")
        
        print(f"Total games analyzed: {len(self.games)}\n")
        
        # Analyze by specific spread values
        print("\n--- ANALYSIS BY SPECIFIC SPREAD VALUE ---\n")
        by_spread = self.analyze_by_spread_range(min_rate, max_rate)
        
        if by_spread:
            for i, analysis in enumerate(by_spread[:10], 1):  # Top 10
                print(f"{i}. Spread: {analysis.spread_range}")
                print(f"   Coverage Rate: {analysis.coverage_rate*100:.1f}% "
                      f"({analysis.covered_count}/{analysis.total_games} games)")
                print()
        else:
            print(f"No spreads found with {min_rate*100:.0f}%-{max_rate*100:.0f}% coverage rate.\n")
        
        # Analyze by favorite magnitude
        print("\n--- ANALYSIS BY FAVORITE MAGNITUDE ---\n")
        by_magnitude = self.analyze_by_favorite_magnitude(min_rate, max_rate)
        
        if by_magnitude:
            for analysis in by_magnitude:
                print(f"Range: {analysis.spread_range}")
                print(f"Coverage Rate: {analysis.coverage_rate*100:.1f}% "
                      f"({analysis.covered_count}/{analysis.total_games} games)")
                print()
        else:
            print(f"No magnitude ranges found with {min_rate*100:.0f}%-{max_rate*100:.0f}% coverage rate.\n")
        
        # Analyze over/under
        print("\n--- OVER/UNDER ANALYSIS ---\n")
        over_under = self.analyze_over_under(min_rate, max_rate)
        
        if over_under:
            for analysis in over_under:
                print(f"{analysis.spread_range}")
                print(f"Hit Rate: {analysis.coverage_rate*100:.1f}% "
                      f"({analysis.covered_count}/{analysis.total_games} games)")
                print()
        else:
            print(f"No over/under values found with {min_rate*100:.0f}%-{max_rate*100:.0f}% hit rate.\n")
        
        # Find wrong favorites (100% accuracy)
        print("\n--- WRONG FAVORITES (100% ACCURACY) ---\n")
        wrong_favs = self.find_wrong_favorites(min_rate=1.00)
        
        if wrong_favs:
            for analysis in wrong_favs:
                print(f"Team: {analysis.spread_range}")
                print(f"Favorite Loss Rate: {analysis.coverage_rate*100:.1f}% "
                      f"({analysis.covered_count}/{analysis.total_games} games)")
                print("   → Bet AGAINST this team when they are favored!")
                print()
        else:
            print("No teams found that lose as favorites with 100% accuracy.\n")
        
        print("="*80 + "\n")
    
    def export_results(self, filename: str, min_rate: float = 0.80, max_rate: float = 1.00):
        """Export analysis results to JSON file"""
        results = {
            'by_spread': [a.to_dict() for a in self.analyze_by_spread_range(min_rate, max_rate)],
            'by_magnitude': [a.to_dict() for a in self.analyze_by_favorite_magnitude(min_rate, max_rate)],
            'over_under': [a.to_dict() for a in self.analyze_over_under(min_rate, max_rate)],
            'wrong_favorites': [a.to_dict() for a in self.find_wrong_favorites(min_rate=1.00)]
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to {filename}")


def main():
    """Main function to demonstrate the analyzer"""
    analyzer = FootballSpreadAnalyzer()
    
    # Try to load sample data if it exists
    try:
        analyzer.load_games_from_json('sample_games.json')
    except (FileNotFoundError, json.JSONDecodeError):
        print("No sample_games.json found. Creating sample data...")
        # Create some sample games for demonstration
        create_sample_data()
        analyzer.load_games_from_json('sample_games.json')
    
    # Generate report
    analyzer.generate_report(min_rate=0.80, max_rate=1.00)
    
    # Export results
    analyzer.export_results('spread_analysis_results.json', min_rate=0.80, max_rate=1.00)


def create_sample_data():
    """Create sample game data for demonstration"""
    # Sample games with various spreads and outcomes
    sample_games = [
        # Games where -7 spread covered consistently (80%+) with over/under
        {"home_team": "Alabama", "away_team": "Tennessee", "home_score": 35, "away_score": 21, "spread": -7.0, "over_under": 52.5, "season": "2023", "week": 5},
        {"home_team": "Georgia", "away_team": "Florida", "home_score": 42, "away_score": 28, "spread": -7.0, "over_under": 58.5, "season": "2023", "week": 6},
        {"home_team": "Ohio State", "away_team": "Michigan State", "home_score": 38, "away_score": 24, "spread": -7.0, "over_under": 55.5, "season": "2023", "week": 7},
        {"home_team": "Clemson", "away_team": "NC State", "home_score": 31, "away_score": 17, "spread": -7.0, "over_under": 52.5, "season": "2023", "week": 8},
        {"home_team": "Oklahoma", "away_team": "Kansas", "home_score": 35, "away_score": 27, "spread": -7.0, "over_under": 58.5, "season": "2023", "week": 9},
        
        # Games where -14 spread covered well
        {"home_team": "Alabama", "away_team": "Vanderbilt", "home_score": 55, "away_score": 24, "spread": -14.0, "over_under": 65.5, "season": "2023", "week": 3},
        {"home_team": "Georgia", "away_team": "UAB", "home_score": 49, "away_score": 17, "spread": -14.0, "over_under": 58.5, "season": "2023", "week": 4},
        {"home_team": "Ohio State", "away_team": "Rutgers", "home_score": 52, "away_score": 21, "spread": -14.0, "over_under": 62.5, "season": "2023", "week": 5},
        {"home_team": "Michigan", "away_team": "Indiana", "home_score": 45, "away_score": 14, "spread": -14.0, "over_under": 52.5, "season": "2023", "week": 6},
        {"home_team": "USC", "away_team": "Colorado", "home_score": 48, "away_score": 21, "spread": -14.0, "over_under": 65.5, "season": "2023", "week": 7},
        {"home_team": "Texas", "away_team": "Texas Tech", "home_score": 57, "away_score": 28, "spread": -14.0, "over_under": 72.5, "season": "2023", "week": 8},
        
        # Games where -3 spread covered moderately
        {"home_team": "Florida State", "away_team": "Miami", "home_score": 27, "away_score": 20, "spread": -3.0, "over_under": 48.5, "season": "2023", "week": 9},
        {"home_team": "Penn State", "away_team": "Iowa", "home_score": 24, "away_score": 17, "spread": -3.0, "over_under": 38.5, "season": "2023", "week": 10},
        {"home_team": "Wisconsin", "away_team": "Minnesota", "home_score": 28, "away_score": 24, "spread": -3.0, "over_under": 48.5, "season": "2023", "week": 11},
        {"home_team": "Auburn", "away_team": "LSU", "home_score": 31, "away_score": 24, "spread": -3.0, "over_under": 52.5, "season": "2023", "week": 12},
        {"home_team": "Oregon", "away_team": "Washington", "home_score": 34, "away_score": 31, "spread": -3.0, "over_under": 58.5, "season": "2023", "week": 13},
        
        # Games where -21 spread covered very well (huge favorites)
        {"home_team": "Alabama", "away_team": "ULM", "home_score": 63, "away_score": 7, "spread": -21.0, "over_under": 62.5, "season": "2023", "week": 1},
        {"home_team": "Georgia", "away_team": "UT Martin", "home_score": 56, "away_score": 7, "spread": -21.0, "over_under": 58.5, "season": "2023", "week": 2},
        {"home_team": "Ohio State", "away_team": "Youngstown State", "home_score": 52, "away_score": 10, "spread": -21.0, "over_under": 58.5, "season": "2023", "week": 1},
        {"home_team": "Clemson", "away_team": "Charleston Southern", "home_score": 66, "away_score": 17, "spread": -21.0, "over_under": 68.5, "season": "2023", "week": 2},
        {"home_team": "Texas", "away_team": "Rice", "home_score": 58, "away_score": 14, "spread": -21.0, "over_under": 62.5, "season": "2023", "week": 1},
        {"home_team": "USC", "away_team": "Nevada", "home_score": 66, "away_score": 14, "spread": -21.0, "over_under": 68.5, "season": "2023", "week": 1},
        
        # Additional -7 spreads for 80%+ rate
        {"home_team": "Notre Dame", "away_team": "Navy", "home_score": 35, "away_score": 21, "spread": -7.0, "over_under": 52.5, "season": "2023", "week": 10},
        {"home_team": "Texas A&M", "away_team": "Mississippi State", "home_score": 31, "away_score": 20, "spread": -7.0, "over_under": 48.5, "season": "2023", "week": 11},
        {"home_team": "Utah", "away_team": "UCLA", "home_score": 28, "away_score": 17, "spread": -7.0, "over_under": 42.5, "season": "2023", "week": 12},
        {"home_team": "Kentucky", "away_team": "South Carolina", "home_score": 31, "away_score": 17, "spread": -7.0, "over_under": 45.5, "season": "2023", "week": 13},
        
        # Wrong favorites - team that always loses as favorite (Vanderbilt example)
        {"home_team": "Vanderbilt", "away_team": "Kentucky", "home_score": 17, "away_score": 24, "spread": -3.0, "over_under": 45.5, "season": "2023", "week": 4},
        {"home_team": "Vanderbilt", "away_team": "South Carolina", "home_score": 20, "away_score": 28, "spread": -2.5, "over_under": 48.5, "season": "2023", "week": 7},
        {"home_team": "Missouri", "away_team": "Vanderbilt", "home_score": 33, "away_score": 14, "spread": 3.5, "over_under": 52.5, "season": "2023", "week": 10},
        
        # More over/under examples that hit consistently at 58.5
        {"home_team": "Baylor", "away_team": "TCU", "home_score": 35, "away_score": 28, "spread": -4.0, "over_under": 58.5, "season": "2023", "week": 8},
        {"home_team": "Oklahoma State", "away_team": "Kansas State", "home_score": 38, "away_score": 31, "spread": -3.5, "over_under": 58.5, "season": "2023", "week": 9},
        {"home_team": "West Virginia", "away_team": "Texas Tech", "home_score": 42, "away_score": 31, "spread": -5.0, "over_under": 58.5, "season": "2023", "week": 10},
        {"home_team": "Arizona State", "away_team": "Arizona", "home_score": 35, "away_score": 28, "spread": -3.0, "over_under": 58.5, "season": "2023", "week": 11},
        {"home_team": "Washington State", "away_team": "Oregon State", "home_score": 38, "away_score": 35, "spread": -4.0, "over_under": 58.5, "season": "2023", "week": 12},
    ]
    
    with open('sample_games.json', 'w') as f:
        json.dump(sample_games, f, indent=2)
    
    print("Sample data created in sample_games.json")


if __name__ == '__main__':
    main()
